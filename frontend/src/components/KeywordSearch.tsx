import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Loader2, Search, BookOpen, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

interface SearchResult {
  url: string;
  title: string;
  summary: string;
  keywords: string[];
  companies: string[];
  source_type: 'google_scholar' | 'google_patent';
  article_index: number;
}

interface KeywordSearchResponse {
  message: string;
  keyword: string;
  scholar_papers_found: number;
  patents_found: number;
  total_sources: number;
  processed_sources: number;
  sources: SearchResult[];
  matches_found: number;
  status: string;
}

const KeywordSearch: React.FC = () => {
  const [keyword, setKeyword] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<KeywordSearchResponse | null>(null);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const { toast } = useToast();

  const handleSearch = async () => {
    if (!keyword.trim()) {
      toast({
        title: "Error",
        description: "Please enter a search keyword",
        variant: "destructive",
      });
      return;
    }

    setIsSearching(true);
    setSearchResults(null);

    try {
      const response = await fetch('/api/search/keyword', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword.trim() }),
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data: KeywordSearchResponse = await response.json();
      setSearchResults(data);
      
      // Add to search history
      if (!searchHistory.includes(keyword.trim())) {
        setSearchHistory(prev => [keyword.trim(), ...prev.slice(0, 9)]);
      }

      toast({
        title: "Search Completed",
        description: `Found ${data.total_sources} sources (${data.scholar_papers_found} papers, ${data.patents_found} patents)`,
      });

    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search Failed",
        description: error instanceof Error ? error.message : "An error occurred during search",
        variant: "destructive",
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getSourceIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'google_scholar':
        return <BookOpen className="w-4 h-4" />;
      case 'google_patent':
        return <FileText className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getSourceBadge = (sourceType: string) => {
    switch (sourceType) {
      case 'google_scholar':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Scholar</Badge>;
      case 'google_patent':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Patent</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Keyword Search
          </CardTitle>
          <CardDescription>
            Search Google Scholar and Google Patents simultaneously for the 25 most recent papers and patents.
            Results will be automatically processed through thesis matching.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter search keyword (e.g., solar, battery, renewable energy)"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button 
              onClick={handleSearch} 
              disabled={isSearching || !keyword.trim()}
              className="min-w-[120px]"
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </div>

          {/* Search History */}
          {searchHistory.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Recent searches:</p>
              <div className="flex flex-wrap gap-2">
                {searchHistory.map((term, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => setKeyword(term)}
                    className="text-xs"
                  >
                    {term}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Search Results for "{searchResults.keyword}"
            </CardTitle>
            <CardDescription>
              Found {searchResults.total_sources} sources with {searchResults.matches_found} potential thesis matches
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{searchResults.scholar_papers_found}</div>
                <div className="text-sm text-blue-600">Scholar Papers</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{searchResults.patents_found}</div>
                <div className="text-sm text-green-600">Patents</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{searchResults.matches_found}</div>
                <div className="text-sm text-purple-600">Thesis Matches</div>
              </div>
            </div>

            {/* Results List */}
            <div className="space-y-4">
              {searchResults.sources.map((source, index) => (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          {getSourceIcon(source.source_type)}
                          {getSourceBadge(source.source_type)}
                          <span className="text-sm text-muted-foreground">
                            #{source.article_index}
                          </span>
                        </div>
                        
                        <h3 className="font-semibold text-lg leading-tight">
                          <a 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="hover:text-blue-600 transition-colors"
                          >
                            {source.title}
                          </a>
                        </h3>
                        
                        <p className="text-sm text-muted-foreground line-clamp-3">
                          {source.summary}
                        </p>
                        
                        {/* Keywords */}
                        {source.keywords.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {source.keywords.slice(0, 5).map((keyword, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                {keyword}
                              </Badge>
                            ))}
                            {source.keywords.length > 5 && (
                              <span className="text-xs text-muted-foreground">
                                +{source.keywords.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                        
                        {/* Companies */}
                        {source.companies.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            <span className="text-xs text-muted-foreground">Companies:</span>
                            {source.companies.slice(0, 3).map((company, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {company}
                              </Badge>
                            ))}
                            {source.companies.length > 3 && (
                              <span className="text-xs text-muted-foreground">
                                +{source.companies.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Thesis Matching Notice */}
            {searchResults.matches_found > 0 && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2 text-green-800">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">
                    Thesis Matching Complete!
                  </span>
                </div>
                <p className="text-green-700 text-sm mt-1">
                  {searchResults.matches_found} sources have been identified as potential matches for your thesis. 
                  These results are now available in the Revisions section and can be used for content matching analysis.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              1
            </div>
            <div>
              <strong>Enter Keyword:</strong> Type a search term like "solar", "battery", or "renewable energy"
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              2
            </div>
            <div>
              <strong>Automatic Search:</strong> System searches both Google Scholar (25 papers) and Google Patents (25 patents)
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              3
            </div>
            <div>
              <strong>Content Processing:</strong> Each source is analyzed for keywords, companies, and thesis alignment
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              4
            </div>
            <div>
              <strong>Thesis Matching:</strong> Sources are automatically compared against your thesis for relevance
            </div>
          </div>
          
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
              5
            </div>
            <div>
              <strong>Results Available:</strong> All sources appear in Revisions section for further analysis
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default KeywordSearch;
