import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, Calendar, Globe, FileText, Monitor, RefreshCw } from 'lucide-react';
import { useState, useEffect } from 'react';

interface HistoryItem {
  id: string;
  type: 'blog_search' | 'source' | 'thesis';
  content: string;
  timestamp: string;
  details: {
    title: string;
    summary?: string;
    keywords?: string[];
    companies?: string[];
    source?: string;
    total_articles_found?: number;
    processed_articles?: number;
    is_starred?: boolean;
    last_monitored?: string;
    file_type?: string;
    content_length?: number;
    preview?: string;
  };
}

interface StarredBlog {
  id: string;
  url: string;
  search_time: string;
  total_articles_found: number;
  last_monitored: string;
  monitoring_frequency: string;
  is_active: boolean;
}

export const History = () => {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [starredBlogs, setStarredBlogs] = useState<StarredBlog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchHistory();
    fetchStarredBlogs();
  }, []);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/history`);
      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      setHistoryItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStarredBlogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs/starred`);
      if (!response.ok) throw new Error('Failed to fetch starred blogs');
      const data = await response.json();
      setStarredBlogs(data.starred_blogs || []);
    } catch (err) {
      console.error('Failed to fetch starred blogs:', err);
    }
  };

  const toggleStar = async (blogId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/blogs/star/${blogId}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to toggle star');
      
      // Refresh both history and starred blogs
      await fetchHistory();
      await fetchStarredBlogs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle star');
    }
  };

  const monitorStarredBlogs = async () => {
    try {
      setIsMonitoring(true);
      const response = await fetch(`${API_BASE_URL}/api/blogs/monitor`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to monitor blogs');
      
      const result = await response.json();
      console.log('Monitoring result:', result);
      
      // Refresh data after monitoring
      await fetchHistory();
      await fetchStarredBlogs();
      
      // Show success message
      alert(`Monitoring completed! Found ${result.total_new_articles} new articles.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to monitor blogs');
    } finally {
      setIsMonitoring(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'blog_search':
        return <Globe className="h-4 w-4" />;
      case 'source':
        return <FileText className="h-4 w-4" />;
      case 'thesis':
        return <FileText className="h-4 w-4" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'blog_search':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'source':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'thesis':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown date';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
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
      <Card className="text-center py-12">
        <CardContent>
          <div className="text-red-500 mb-4">❌ Error: {error}</div>
          <Button onClick={fetchHistory}>Try Again</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Starred Blogs Section */}
      {starredBlogs.length > 0 && (
        <Card className="border-2 border-yellow-200 bg-yellow-50">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-yellow-600 fill-current" />
                Starred Blogs ({starredBlogs.length})
              </CardTitle>
              <Button 
                onClick={monitorStarredBlogs} 
                disabled={isMonitoring}
                className="bg-yellow-600 hover:bg-yellow-700"
              >
                {isMonitoring ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Monitoring...
                  </>
                ) : (
                  <>
                    <Monitor className="h-4 w-4 mr-2" />
                    Monitor Now
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {starredBlogs.map((blog) => (
                <div key={blog.id} className="flex items-center justify-between p-2 bg-white rounded border">
                  <div className="flex-1">
                    <div className="font-medium text-sm">{blog.url}</div>
                    <div className="text-xs text-gray-600">
                      Last monitored: {formatTimestamp(blog.last_monitored)}
                    </div>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {blog.total_articles_found} articles
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* History Items */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">History</h2>
          <Badge variant="outline">
            {historyItems.length} items
          </Badge>
        </div>
        
        {historyItems.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No History Yet</h3>
              <p className="text-muted-foreground">
                Start by uploading content sources or thesis to see your history
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {historyItems.map((item) => (
              <Card key={item.id} className="transition-all duration-200 hover:shadow-lg">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        {getTypeIcon(item.type)}
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {item.details.title}
                        </CardTitle>
                        <Badge className={getTypeColor(item.type)}>
                          {item.type.replace('_', ' ')}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatTimestamp(item.timestamp)}
                        </div>
                        
                        {item.type === 'blog_search' && (
                          <>
                            <span className="text-blue-600">
                              {item.details.total_articles_found} articles found
                            </span>
                            <span className="text-green-600">
                              {item.details.processed_articles} processed
                            </span>
                          </>
                        )}
                        
                        {item.type === 'source' && item.details.source && (
                          <span className="text-purple-600">
                            From: {item.details.source}
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {item.type === 'blog_search' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleStar(item.id)}
                          className={`hover:bg-yellow-100 ${
                            item.details.is_starred ? 'text-yellow-600' : 'text-gray-400'
                          }`}
                        >
                          <Star className={`h-4 w-4 ${item.details.is_starred ? 'fill-current' : ''}`} />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-3">
                  {item.details.summary && (
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      {item.details.summary}
                    </p>
                  )}
                  
                  {item.details.keywords && item.details.keywords.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">Keywords</div>
                      <div className="flex flex-wrap gap-2">
                        {item.details.keywords.map((keyword, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {item.details.companies && item.details.companies.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-muted-foreground">Companies</div>
                      <div className="flex flex-wrap gap-2">
                        {item.details.companies.map((company, index) => (
                          <Badge key={index} variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                            {company}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {item.type === 'thesis' && item.details.preview && (
                    <div className="bg-accent/30 rounded-lg p-3">
                      <div className="text-sm font-medium text-secondary mb-1">Thesis Preview</div>
                      <p className="text-sm text-foreground/80">{item.details.preview}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
