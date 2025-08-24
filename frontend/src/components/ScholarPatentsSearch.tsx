import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Search, BookOpen, FileText, Loader2, ExternalLink } from 'lucide-react';

interface ScholarResult {
  title: string;
  url: string;
  authors: string[];
  abstract: string;
  year?: number;
  citations?: number;
  source: string;
}

interface PatentResult {
  title: string;
  url: string;
  authors: string[];
  abstract: string;
  publish_date?: string;
  patent_number: string;
  source: string;
}

interface ScholarPatentsSearchProps {
  onResultsFound: (results: any[]) => void;
}

export const ScholarPatentsSearch = ({ onResultsFound }: ScholarPatentsSearchProps) => {
  const [keyword, setKeyword] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [scholarResults, setScholarResults] = useState<ScholarResult[]>([]);
  const [patentResults, setPatentResults] = useState<PatentResult[]>([]);
  const [activeTab, setActiveTab] = useState('scholar');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const searchScholar = async () => {
    if (!keyword.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/scholar/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword.trim(), max_results: 10 }),
      });

      if (response.ok) {
        const data = await response.json();
        setScholarResults(data.results || []);
        if (data.results && data.results.length > 0) {
          onResultsFound(data.results);
        }
        console.log('Scholar search results:', data);
      } else {
        console.error('Scholar search failed:', response.status);
      }
    } catch (error) {
      console.error('Error searching Google Scholar:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const searchPatents = async () => {
    if (!keyword.trim()) return;
    
    console.log('🔍 Starting patents search for:', keyword);
    setIsSearching(true);
    
    try {
      console.log('📡 Making API request to:', `${API_BASE_URL}/api/patents/search`);
      
      const response = await fetch(`${API_BASE_URL}/api/patents/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword.trim(), max_results: 10 }),
      });

      console.log('📥 Response received:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Parsed data:', data);
        console.log('📋 Results array:', data.results);
        
        // Set results safely
        const safeResults = data.results || [];
        console.log('🛡️ Safe results:', safeResults);
        
        setPatentResults(safeResults);
        
        if (safeResults.length > 0) {
          console.log('✅ Calling onResultsFound with:', safeResults);
          onResultsFound(safeResults);
        }
        
        console.log('🎯 Patent search completed successfully');
      } else {
        const errorText = await response.text();
        console.error('❌ Patent search failed:', response.status, errorText);
      }
    } catch (error) {
      console.error('💥 Error searching Google Patents:', error);
    } finally {
      console.log('🏁 Setting isSearching to false');
      setIsSearching(false);
    }
  };

  const handleSearch = () => {
    if (activeTab === 'scholar') {
      searchScholar();
    } else {
      searchPatents();
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Academic & Patent Search
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="keyword" className="sr-only">
              Search Keyword
            </Label>
            <Input
              id="keyword"
              placeholder="Enter keyword (e.g., HVAC, solar energy, AI)"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button 
            onClick={handleSearch} 
            disabled={isSearching || !keyword.trim()}
            className="min-w-[120px]"
          >
            {isSearching ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Search
              </>
            )}
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="scholar" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Google Scholar
            </TabsTrigger>
            <TabsTrigger value="patents" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Google Patents
            </TabsTrigger>
          </TabsList>

          <TabsContent value="scholar" className="mt-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Academic Papers</h3>
                <Badge variant="outline">
                  {scholarResults.length} results
                </Badge>
              </div>
              
              {scholarResults.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  Search for academic papers using Google Scholar
                </p>
              ) : (
                <div className="space-y-3">
                  {scholarResults.map((result, index) => (
                    <Card key={index} className="p-3">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-sm line-clamp-2">
                            {result.title}
                          </h4>
                          <a 
                            href={result.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-8 px-3 flex-shrink-0"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                        
                        {result.authors.length > 0 && (
                          <p className="text-xs text-muted-foreground">
                            Authors: {result.authors.join(', ')}
                          </p>
                        )}
                        
                        {result.abstract && (
                          <p className="text-xs text-foreground/80 line-clamp-3">
                            {result.abstract}
                          </p>
                        )}
                        
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          {result.year && (
                            <Badge variant="outline" className="text-xs">
                              {result.year}
                            </Badge>
                          )}
                          {result.citations && (
                            <Badge variant="outline" className="text-xs">
                              {result.citations} citations
                            </Badge>
                          )}
                          <Badge variant="secondary" className="text-xs">
                            {result.source}
                          </Badge>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="patents" className="mt-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Patent Documents</h3>
                <Badge variant="outline">
                  {patentResults.length} results
                </Badge>
              </div>
              
              {patentResults.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  Search for patents using Google Patents
                </p>
              ) : (
                <div className="space-y-3">
                  {patentResults.map((result, index) => {
                    // Safe rendering with error handling
                    try {
                      return (
                        <Card key={index} className="p-3">
                          <div className="space-y-2">
                            <div className="flex items-start justify-between gap-2">
                              <h4 className="font-medium text-sm line-clamp-2">
                                {result?.title || 'Untitled Patent'}
                              </h4>
                              <a 
                                href={result?.url || '#'} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-8 px-3 flex-shrink-0"
                              >
                                <ExternalLink className="h-3 w-3" />
                              </a>
                            </div>
                            
                                                    {result?.authors && Array.isArray(result.authors) && result.authors.length > 0 && (
                          <p className="text-xs text-muted-foreground">
                            Inventors: {result.authors.join(', ')}
                          </p>
                        )}
                            
                            {result?.abstract && (
                              <p className="text-xs text-foreground/80 line-clamp-3">
                                {result.abstract}
                              </p>
                            )}
                            
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              {result?.patent_number && (
                                <Badge variant="outline" className="text-xs">
                                  {result.patent_number}
                                </Badge>
                              )}
                              {result?.publish_date && (
                                <Badge variant="outline" className="text-xs">
                                  {result.publish_date}
                                </Badge>
                              )}
                              <Badge variant="secondary" className="text-xs">
                                {result?.source || 'Google Patents'}
                              </Badge>
                            </div>
                          </div>
                        </Card>
                      );
                    } catch (renderError) {
                      console.error('💥 Error rendering patent result:', renderError, result);
                      return (
                        <Card key={index} className="p-3 border-red-200 bg-red-50">
                          <p className="text-red-600 text-sm">Error displaying patent result</p>
                        </Card>
                      );
                    }
                  })}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
