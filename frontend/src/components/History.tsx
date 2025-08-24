import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, Globe, Calendar, FileText, RefreshCw, AlertCircle, ExternalLink } from 'lucide-react';

interface BlogUpload {
  id: string;
  url: string;
  search_time: string;
  total_articles_found: number;
  processed_articles: number;
  is_starred: boolean;
  last_monitored?: string;
}

interface Source {
  id: string;
  url: string;
  title: string;
  summary: string;
  keywords: string[];
  companies: string[];
  timestamp: string;
  is_starred: boolean;
  source_blog?: string;
}

interface Thesis {
  id: string;
  filename: string;
  content_length: number;
  upload_time: string;
  file_type: string;
}

export const History = () => {
  const [blogUploads, setBlogUploads] = useState<BlogUpload[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [thesisUploads, setThesisUploads] = useState<Thesis[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'blogs' | 'sources' | 'thesis'>('blogs');

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  useEffect(() => {
    fetchAllHistory();
  }, []);

  const fetchAllHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch blog uploads
      const blogsResponse = await fetch(`${API_BASE_URL}/api/blogs/starred`);
      if (blogsResponse.ok) {
        const blogsData = await blogsResponse.json();
        setBlogUploads(blogsData.starred_blogs || []);
      }
      
      // Fetch sources
      const sourcesResponse = await fetch(`${API_BASE_URL}/api/history/sources`);
      if (sourcesResponse.ok) {
        const sourcesData = await sourcesResponse.json();
        setSources(sourcesData || []);
      }
      
      // Fetch thesis uploads
      const thesisResponse = await fetch(`${API_BASE_URL}/api/history/thesis`);
      if (thesisResponse.ok) {
        const thesisData = await thesisResponse.json();
        setThesisUploads(thesisData || []);
      }
      
    } catch (err) {
      console.error('❌ History fetch error:', err);
      setError('Failed to fetch history data');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleBlogStar = async (blogId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs/star/${blogId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to toggle blog star');
      }

      // Refresh blog data
      const blogsResponse = await fetch(`${API_BASE_URL}/api/blogs/starred`);
      if (blogsResponse.ok) {
        const blogsData = await blogsResponse.json();
        setBlogUploads(blogsData.starred_blogs || []);
      }
      
    } catch (err) {
      console.error('❌ Blog star toggle error:', err);
      setError('Failed to toggle blog star');
    }
  };

  const toggleSourceStar = async (sourceId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sources/star/${sourceId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to toggle source star');
      }

      // Refresh sources data
      const sourcesResponse = await fetch(`${API_BASE_URL}/api/history/sources`);
      if (sourcesResponse.ok) {
        const sourcesData = await sourcesResponse.json();
        setSources(sourcesData || []);
      }
      
    } catch (err) {
      console.error('❌ Source star toggle error:', err);
      setError('Failed to toggle source star');
    }
  };

  const formatDate = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid date';
    }
  };

  const getStarredCount = () => {
    const starredBlogs = blogUploads.filter(blog => blog.is_starred).length;
    const starredSources = sources.filter(source => source.is_starred).length;
    return starredBlogs + starredSources;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">History</h2>
          <Button variant="outline" size="sm" disabled>
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            Loading...
          </Button>
        </div>
        
        {Array.from({ length: 3 }, (_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-muted rounded w-3/4"></div>
              <div className="h-3 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-3 bg-muted rounded"></div>
                <div className="h-3 bg-muted rounded w-5/6"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">History</h2>
          <Button variant="outline" size="sm" onClick={fetchAllHistory}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <div>
                <h3 className="font-semibold">Error Loading History</h3>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">History</h2>
          <p className="text-muted-foreground">
            {getStarredCount()} starred items • {blogUploads.length} blogs • {sources.length} sources • {thesisUploads.length} thesis
          </p>
        </div>
        
        <Button variant="outline" size="sm" onClick={fetchAllHistory}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg">
        <Button
          variant={activeTab === 'blogs' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('blogs')}
          className="flex-1"
        >
          <Globe className="h-4 w-4 mr-2" />
          Blog Uploads ({blogUploads.length})
        </Button>
        <Button
          variant={activeTab === 'sources' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('sources')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Sources ({sources.length})
        </Button>
        <Button
          variant={activeTab === 'thesis' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('thesis')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Thesis ({thesisUploads.length})
        </Button>
      </div>

      {/* Blog Uploads Tab */}
      {activeTab === 'blogs' && (
        <div className="space-y-4">
          {blogUploads.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Blog Uploads Yet</h3>
                <p className="text-muted-foreground">
                  Upload blogs to see them in your history
                </p>
              </CardContent>
            </Card>
          ) : (
            blogUploads.map((blog) => (
              <Card key={blog.id} className="transition-all duration-200 hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Globe className="h-4 w-4 text-blue-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {blog.url}
                        </CardTitle>
                        <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                          Blog
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(blog.search_time)}
                        </div>
                        
                        <span className="text-blue-600">
                          {blog.total_articles_found} articles found
                        </span>
                        
                        <span className="text-green-600">
                          {blog.processed_articles} processed
                        </span>
                        
                        {blog.last_monitored && (
                          <span className="text-purple-600">
                            Last monitored: {formatDate(blog.last_monitored)}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleBlogStar(blog.id)}
                      className={`hover:bg-yellow-100 ${
                        blog.is_starred ? 'text-yellow-600' : 'text-gray-400'
                      }`}
                    >
                      <Star className={`h-4 w-4 ${blog.is_starred ? 'fill-current' : ''}`} />
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Sources Tab */}
      {activeTab === 'sources' && (
        <div className="space-y-4">
          {sources.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Sources Yet</h3>
                <p className="text-muted-foreground">
                  Add content sources to see them in your history
                </p>
              </CardContent>
            </Card>
          ) : (
            sources.map((source) => (
              <Card key={source.id} className="transition-all duration-200 hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-green-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {source.title}
                        </CardTitle>
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          Source
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(source.timestamp)}
                        </div>
                        
                        <div className="flex items-center gap-1 text-blue-600">
                          <Globe className="h-3 w-3" />
                          <span className="truncate max-w-xs">{source.url}</span>
                        </div>
                        
                        {source.source_blog && (
                          <span className="text-purple-600">
                            From: {source.source_blog}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSourceStar(source.id)}
                      className={`hover:bg-yellow-100 ${
                        source.is_starred ? 'text-yellow-600' : 'text-gray-400'
                      }`}
                    >
                      <Star className={`h-4 w-4 ${source.is_starred ? 'fill-current' : ''}`} />
                    </Button>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-3">
                  {/* Summary */}
                  {source.summary && (
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      {source.summary}
                    </p>
                  )}
                  
                  {/* Keywords */}
                  {source.keywords && source.keywords.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">Keywords</div>
                      <div className="flex flex-wrap gap-2">
                        {source.keywords.map((keyword, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Companies */}
                  {source.companies && source.companies.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">Companies</div>
                      <div className="flex flex-wrap gap-2">
                        {source.companies.map((company, index) => (
                          <Badge key={index} variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                            {company}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Thesis Tab */}
      {activeTab === 'thesis' && (
        <div className="space-y-4">
          {thesisUploads.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Thesis Uploads Yet</h3>
                <p className="text-muted-foreground">
                  Upload thesis files to see them in your history
                </p>
              </CardContent>
            </Card>
          ) : (
            thesisUploads.map((thesis) => (
              <Card key={thesis.id} className="transition-all duration-200 hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-purple-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {thesis.filename}
                        </CardTitle>
                        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                          Thesis
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(thesis.upload_time)}
                        </div>
                        
                        <span className="text-purple-600">
                          {thesis.content_length.toLocaleString()} characters
                        </span>
                        
                        <span className="text-gray-600">
                          {thesis.file_type} file
                        </span>
                      </div>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
};
