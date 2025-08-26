import { useState, useEffect } from 'react';
import { SourceInput } from '@/components/SourceInput';
import { ThesisTextInput } from '@/components/ThesisTextInput';
import { ContentMatchView } from '@/components/ContentMatchView';
import { BlogUpload } from '@/components/BlogUpload';

import { ScholarPatentsSearch } from '@/components/ScholarPatentsSearch';
import { Revisions } from '@/components/Revisions';
import KeywordSearch from '@/components/KeywordSearch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, FileSearch, Zap, Star, Globe, FileText, Search } from 'lucide-react';

// API base URL - when served from backend, use relative paths
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Empty initial state for matched content
const initialMatchedContent: any[] = [];

const Index = () => {
  const [sources, setSources] = useState<string[]>([]);
  const [thesisText, setThesisText] = useState<string>('');
  const [isLoadingSource, setIsLoadingSource] = useState(false);
  const [isLoadingThesis, setIsLoadingThesis] = useState(false);
  const [isLoadingBlog, setIsLoadingBlog] = useState(false);
  const [matchedContent, setMatchedContent] = useState(initialMatchedContent);
  const [keywordSearchResults, setKeywordSearchResults] = useState<any[]>([]);

  // Listen for revisions committed event
  useEffect(() => {
    const handleRevisionsCommitted = (event: CustomEvent) => {
      console.log('🔄 Revisions committed, refreshing matches...');
      fetchMatches();
    };
    
    window.addEventListener('revisionsCommitted', handleRevisionsCommitted as EventListener);
    
    return () => {
      window.removeEventListener('revisionsCommitted', handleRevisionsCommitted as EventListener);
    };
  }, []);

  const fetchMatches = async () => {
    try {
      console.log('Fetching matches from API...');
      const response = await fetch(`${API_BASE_URL}/api/matches`);
      
      console.log('Matches response status:', response.status);
      
      if (response.ok) {
        const matches = await response.json();
        console.log('Received matches data:', matches);
        console.log('Number of matches:', matches?.length || 'Not an array');
        
        // Transform API response to match frontend format
        const transformedMatches = matches.map((match: any, index: number) => ({
          id: String(index + 1),
          title: match.title || `Content from ${new URL(match.url).hostname}`,
          url: match.url,
          source: new URL(match.url).hostname,
          publishDate: new Date().toISOString().split('T')[0],
          summary: match.summary,
          fullContent: match.full_content || "Full content not available",
          relevanceScore: Math.round(match.relevance_score * 100),
          matchedKeywords: match.keywords || [],
          companies: match.companies || [],
          thesisAlignment: match.match_reason || 'No alignment information available'
        }));
        
        setMatchedContent(transformedMatches);
              } else {
          const errorText = await response.text();
          console.error('Matches API error:', response.status, errorText);
          // Keep current data if API fails
        }
    } catch (error) {
      console.error('Error fetching matches:', error);
      // Keep current data if API fails
    }
  };

  const handleAddSource = async (url: string) => {
    setIsLoadingSource(true);
    
    try {
      console.log('Attempting to add source:', url);
      const response = await fetch(`${API_BASE_URL}/api/sources`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      });
      
      console.log('Source API response status:', response.status);
      
      if (response.ok) {
        setSources(prev => [...prev, url]);
        console.log('Source added successfully:', url);
        // Fetch updated matches after adding source
        await fetchMatches();
      } else {
        const errorData = await response.text();
        console.error('Source API error response:', errorData);
        throw new Error(`Failed to add source: ${response.status} - ${errorData}`);
      }
    } catch (error) {
      console.error('Error adding source:', error);
      // You can add toast notification here for error handling
    } finally {
      setIsLoadingSource(false);
    }
  };



  const handleSubmitThesis = async (text: string, title: string) => {
    setIsLoadingThesis(true);
    
    try {
      console.log('Attempting to submit thesis text:', text.substring(0, 100) + '...');
      
      // Create a temporary file from the text
      const blob = new Blob([text], { type: 'text/plain' });
      const file = new File([blob], 'thesis.txt', { type: 'text/plain' });
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title);
      
      const response = await fetch(`${API_BASE_URL}/api/thesis/upload`, {
        method: 'POST',
        body: formData
      });
      
      console.log('Thesis text response status:', response.status);
      
      if (response.ok) {
        setThesisText(text);
        console.log('Thesis text submitted successfully');
        // Trigger content matching after thesis submission
        await fetchMatches();
      } else {
        const errorData = await response.text();
        console.error('Thesis text error response:', errorData);
        throw new Error(`Failed to submit thesis: ${response.status} - ${errorData}`);
      }
    } catch (error) {
      console.error('Error submitting thesis text:', error);
      // You can add toast notification here for error handling
    } finally {
      setIsLoadingThesis(false);
    }
  };

  const handleUploadBlog = async (url: string) => {
    setIsLoadingBlog(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/blog/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Blog upload result:', result);
        await fetchMatches(); // Trigger update
      } else {
        console.error('Failed to upload blog');
      }
    } catch (error) {
      console.error('Error uploading blog:', error);
    } finally {
      setIsLoadingBlog(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/10">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary to-primary-glow text-primary-foreground py-8 mb-8">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-3 mb-3">
            <TrendingUp className="h-8 w-8" />
            <h1 className="text-3xl font-bold">FactorESourcing</h1>
          </div>
          <p className="text-primary-foreground/80 text-lg">
            Monitor content sources and match against your investment thesis
          </p>
        </div>
      </div>

      <div className="container mx-auto px-6 pb-12">
        <Tabs defaultValue="setup" className="space-y-8">
          <TabsList className="grid w-full grid-cols-3 max-w-md mx-auto">
            <TabsTrigger value="setup" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Setup
            </TabsTrigger>

            <TabsTrigger value="keyword-search" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Keyword Search
            </TabsTrigger>

            <TabsTrigger value="revisions" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Revisions
            </TabsTrigger>

            <TabsTrigger value="matches" className="flex items-center gap-2">
              <FileSearch className="h-4 w-4" />
              Matches
            </TabsTrigger>
          </TabsList>

          <TabsContent value="setup" className="space-y-8">
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Source Input */}
              <div className="space-y-4">
                <SourceInput 
                  onAddSource={handleAddSource}
                  isLoading={isLoadingSource}
                />
                
                {/* Sources List */}
                {sources.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Active Sources</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {sources.map((source, index) => (
                          <div 
                            key={index}
                            className="flex items-center gap-2 p-2 bg-accent/30 rounded text-sm"
                          >
                            <div className="w-2 h-2 bg-success rounded-full"></div>
                            <span className="font-mono text-xs truncate">{source}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Blog Upload */}
              <div className="space-y-4">
                <BlogUpload 
                  onUploadBlog={handleUploadBlog}
                  isLoading={isLoadingBlog}
                />
              </div>

              {/* Scholar & Patents Search */}
              <div className="space-y-4">
                <ScholarPatentsSearch 
                  onResultsFound={(results) => {
                    console.log('Scholar/Patents results found:', results);
                    
                    // Store the keyword search results
                    if (results && results.length > 0) {
                      setKeywordSearchResults(results);
                      
                      // Extract URLs from results
                      const newUrls = results.map((result: any) => result.url).filter(Boolean);
                      setSources(prev => [...new Set([...prev, ...newUrls])]);
                      
                      // Show success message
                      console.log(`✅ Added ${results.length} new sources from keyword search`);
                    }
                    
                    // Trigger matches refresh to show new content
                    fetchMatches();
                  }}
                />
                
                {/* Keyword Search Results Display */}
                {keywordSearchResults.length > 0 && (
                  <Card className="border-l-4 border-l-blue-500">
                    <CardHeader>
                      <CardTitle className="text-lg text-blue-600">
                        🔍 Keyword Search Results ({keywordSearchResults.length} sources)
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {keywordSearchResults.slice(0, 5).map((result, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                            <div className="flex-1">
                              <h4 className="font-medium text-sm">
                                <a 
                                  href={result.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="hover:text-blue-600 transition-colors"
                                >
                                  {result.title || `Source ${index + 1}`}
                                </a>
                              </h4>
                              <p className="text-xs text-gray-600 mt-1">
                                {result.summary?.substring(0, 100)}...
                              </p>
                              <div className="flex gap-2 mt-2">
                                <Badge variant="outline" className="text-xs">
                                  {result.source_type || 'Unknown'}
                                </Badge>
                                {result.keywords?.slice(0, 3).map((keyword: string, idx: number) => (
                                  <Badge key={idx} variant="secondary" className="text-xs">
                                    {keyword}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                        ))}
                        {keywordSearchResults.length > 5 && (
                          <p className="text-sm text-gray-500 text-center">
                            ... and {keywordSearchResults.length - 5} more sources
                          </p>
                        )}
                        <div className="text-center mt-4">
                          <p className="text-sm text-green-600">
                            ✅ All sources have been processed and added to the system
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Check the Revisions tab to see all sources, or go to Matches to see thesis correlations
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>



              {/* Thesis Input */}
              <div className="space-y-4">
                <ThesisTextInput 
                  onSubmitThesis={handleSubmitThesis}
                  isLoading={isLoadingThesis}
                />
                
                {/* Thesis Status */}
                {thesisText && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Thesis Status</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-success rounded-full"></div>
                        <div>
                          <p className="font-medium text-sm">Thesis text submitted</p>
                          <p className="text-xs text-muted-foreground">
                            Text processed - Ready for content matching ({thesisText.length} characters)
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>

            {/* API Status */}
            <Card className="bg-gradient-to-r from-accent/20 to-secondary/10 border-secondary/30">
              <CardHeader>
                <CardTitle className="text-lg text-secondary">
                  API Connection Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-success rounded-full"></div>
                  <span>Connected to backend at: {API_BASE_URL}</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  The frontend is now connected to your local backend API. Add sources and upload your thesis to see real matches!
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keyword-search" className="space-y-8">
            <KeywordSearch />
          </TabsContent>

          <TabsContent value="revisions" className="space-y-8">
            <Revisions />
          </TabsContent>

          <TabsContent value="matches">
            <div className="space-y-6">
              {/* Starred Blogs Matching Section */}
              <Card className="border-2 border-yellow-200 bg-yellow-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Star className="h-5 w-5 text-yellow-600 fill-current" />
                    Starred Blogs Matching
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4">
                    <p className="text-sm text-gray-700">
                      Run content matching exclusively on your starred blogs and their articles.
                    </p>
                    <Button 
                      onClick={async () => {
                        try {
                          const response = await fetch(`${API_BASE_URL}/api/matches/starred`);
                          if (response.ok) {
                            const data = await response.json();
                            if (data.matches && data.matches.length > 0) {
                              // Transform starred matches to include full content
                              const transformedStarredMatches = data.matches.map((match: any, index: number) => ({
                                id: String(index + 1),
                                title: match.title || `Content from ${new URL(match.url).hostname}`,
                                url: match.url,
                                source: new URL(match.url).hostname,
                                publishDate: new Date().toISOString().split('T')[0],
                                summary: match.summary,
                                fullContent: match.full_content || "Full content not available",
                                relevanceScore: Math.round(match.relevance_score * 100),
                                matchedKeywords: match.keywords || [],
                                companies: match.companies || [],
                                thesisAlignment: match.match_reason || 'No alignment information available'
                              }));
                              setMatchedContent(transformedStarredMatches);
                              alert(`Found ${data.matches.length} matches from starred blogs!`);
                            } else {
                              alert('No matches found from starred blogs. Try uploading a thesis first.');
                            }
                          } else {
                            alert('Failed to get starred matches. Make sure you have starred blogs.');
                          }
                        } catch (error) {
                          console.error('Error getting starred matches:', error);
                          alert('Error getting starred matches. Check console for details.');
                        }
                      }}
                      className="bg-yellow-600 hover:bg-yellow-700"
                    >
                      <Star className="h-4 w-4 mr-2" />
                      Match Starred Blogs
                    </Button>
                  </div>
                </CardContent>
              </Card>
              
              {/* Regular Matches */}
              <ContentMatchView 
                matchedContent={matchedContent}
                isLoading={false}
              />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;