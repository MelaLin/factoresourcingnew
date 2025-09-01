import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, BookOpen, FileText, Loader2, ExternalLink } from 'lucide-react';

interface SearchResult {
  title: string;
  url: string;
  authors: string[];
  abstract: string;
  source: string;
}

export const SimpleSearch = () => {
  const [keyword, setKeyword] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [scholarResults, setScholarResults] = useState<SearchResult[]>([]);
  const [patentResults, setPatentResults] = useState<SearchResult[]>([]);
  const [activeTab, setActiveTab] = useState('scholar');

  // Direct API URL - no environment variables
  const API_URL = 'https://factoresourcing-app.onrender.com';

  const performSearch = async () => {
    if (!keyword.trim()) return;
    
    setIsSearching(true);
    setScholarResults([]);
    setPatentResults([]);
    
    try {
      console.log('🔍 SIMPLE SEARCH: Starting search for:', keyword);
      console.log('🔍 SIMPLE SEARCH: API URL:', `${API_URL}/api/search/keyword`);
      
      const response = await fetch(`${API_URL}/api/search/keyword`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword.trim() }),
      });

      console.log('🔍 SIMPLE SEARCH: Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ SIMPLE SEARCH: Success!', data);
        
        // Extract scholar results
        const scholarSources = data.sources?.filter((source: any) => source.source_type === 'google_scholar') || [];
        setScholarResults(scholarSources.map((source: any) => ({
          title: source.title,
          url: source.url,
          authors: source.authors || ['Author information available'],
          abstract: source.summary,
          source: 'Google Scholar'
        })));
        
        // Extract patent results
        const patentSources = data.sources?.filter((source: any) => source.source_type === 'google_patent') || [];
        setPatentResults(patentSources.map((source: any) => ({
          title: source.title,
          url: source.url,
          authors: source.authors || ['Inventor information available'],
          abstract: source.summary,
          source: 'Google Patents'
        })));
        
        console.log(`📊 SIMPLE SEARCH: Found ${scholarSources.length} scholar papers and ${patentSources.length} patents`);
        
        if (scholarSources.length > 0 || patentSources.length > 0) {
          alert(`✅ Search successful! Found ${scholarSources.length} papers and ${patentSources.length} patents.`);
        } else {
          alert('⚠️ Search completed but no results found. Check the backend logs.');
        }
      } else {
        const errorText = await response.text();
        console.error('❌ SIMPLE SEARCH: Failed:', response.status, errorText);
        alert(`❌ Search failed: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('❌ SIMPLE SEARCH: Error:', error);
      alert(`❌ Search error: ${error.message}`);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-5 w-5" />
          Simple Google Search (Direct)
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              placeholder="Enter keyword (e.g., HVAC, solar energy, AI)"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && performSearch()}
            />
          </div>
          <Button 
            onClick={performSearch} 
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

        {/* Debug Info */}
        <div className="p-3 bg-gray-50 rounded-lg border">
          <h4 className="text-sm font-medium mb-2">Debug Info</h4>
          <div className="text-xs space-y-1">
            <div>API URL: {API_URL}</div>
            <div>Keyword: {keyword || 'None'}</div>
            <div>Scholar Results: {scholarResults.length}</div>
            <div>Patent Results: {patentResults.length}</div>
            <div>Is Searching: {isSearching ? 'Yes' : 'No'}</div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="scholar" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Google Scholar ({scholarResults.length})
            </TabsTrigger>
            <TabsTrigger value="patents" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Google Patents ({patentResults.length})
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
                  {isSearching ? 'Searching...' : 'Search for academic papers using Google Scholar'}
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
                  {isSearching ? 'Searching...' : 'Search for patents using Google Patents'}
                </p>
              ) : (
                <div className="space-y-3">
                  {patentResults.map((result, index) => (
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
                            Inventors: {result.authors.join(', ')}
                          </p>
                        )}
                        
                        {result.abstract && (
                          <p className="text-xs text-foreground/80 line-clamp-3">
                            {result.abstract}
                          </p>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
