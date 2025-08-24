import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Star, Globe, Calendar, FileText, RefreshCw, AlertCircle } from 'lucide-react';

interface Source {
  id: string;
  type: 'source';
  url: string;
  title: string;
  summary: string;
  keywords: string[];
  companies: string[];
  timestamp: string;
  is_starred: boolean;
  source_type: string;
}

interface Thesis {
  id: string;
  type: 'thesis';
  title: string;
  content_length: number;
  timestamp: string;
  is_starred: boolean;
  source_type: string;
}

type HistoryItem = Source | Thesis;

export const History = () => {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showStarredOnly, setShowStarredOnly] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log('🔍 Fetching history from:', `${API_BASE_URL}/api/history`);
      
      const response = await fetch(`${API_BASE_URL}/api/history`);
      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📊 History data received:', data);
      
      if (Array.isArray(data)) {
        setHistoryItems(data);
      } else {
        throw new Error('Invalid data format - expected array');
      }
      
    } catch (err) {
      console.error('❌ History fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleStar = async (itemId: string) => {
    try {
      const item = historyItems.find(item => item.id === itemId);
      if (!item || item.type !== 'source') return;

      const response = await fetch(`${API_BASE_URL}/api/sources/star/${itemId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to toggle star');
      }

      // Refresh history to get updated star status
      await fetchHistory();
      
    } catch (err) {
      console.error('❌ Star toggle error:', err);
      setError('Failed to toggle star');
    }
  };

  const filteredItems = showStarredOnly 
    ? historyItems.filter(item => item.is_starred)
    : historyItems;

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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'source':
        return <Globe className="h-4 w-4 text-blue-600" />;
      case 'thesis':
        return <FileText className="h-4 w-4 text-purple-600" />;
      default:
        return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case 'source':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Source</Badge>;
      case 'thesis':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800">Thesis</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">History</h2>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" disabled>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Loading...
            </Button>
          </div>
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
          <Button variant="outline" size="sm" onClick={fetchHistory}>
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
            {filteredItems.length} item{filteredItems.length !== 1 ? 's' : ''}
            {showStarredOnly && ' (starred only)'}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant={showStarredOnly ? "default" : "outline"}
            size="sm"
            onClick={() => setShowStarredOnly(!showStarredOnly)}
          >
            <Star className={`h-4 w-4 mr-2 ${showStarredOnly ? 'fill-current' : ''}`} />
            {showStarredOnly ? 'Show All' : 'Starred Only'}
          </Button>
          
          <Button variant="outline" size="sm" onClick={fetchHistory}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Empty State */}
      {filteredItems.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {showStarredOnly ? 'No Starred Items' : 'No History Yet'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {showStarredOnly 
                ? 'Star some sources to see them here'
                : 'Start by uploading content sources or thesis to see your history'
              }
            </p>
            {!showStarredOnly && (
              <Button onClick={fetchHistory} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* History Items */}
      {filteredItems.length > 0 && (
        <div className="space-y-4">
          {filteredItems.map((item) => (
            <Card key={item.id} className="transition-all duration-200 hover:shadow-md">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      {getTypeIcon(item.type)}
                      <CardTitle className="text-lg font-semibold line-clamp-2">
                        {item.title}
                      </CardTitle>
                      {getTypeBadge(item.type)}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(item.timestamp)}
                      </div>
                      
                      {item.type === 'source' && (
                        <div className="flex items-center gap-1 text-blue-600">
                          <Globe className="h-3 w-3" />
                          <span className="truncate max-w-xs">{item.url}</span>
                        </div>
                      )}
                      
                      {item.type === 'thesis' && (
                        <span className="text-purple-600">
                          {item.content_length.toLocaleString()} characters
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Star Button for Sources */}
                  {item.type === 'source' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleStar(item.id)}
                      className={`hover:bg-yellow-100 ${
                        item.is_starred ? 'text-yellow-600' : 'text-gray-400'
                      }`}
                    >
                      <Star className={`h-4 w-4 ${item.is_starred ? 'fill-current' : ''}`} />
                    </Button>
                  )}
                </div>
              </CardHeader>
              
              {/* Content */}
              <CardContent className="space-y-3">
                {/* Summary */}
                {item.type === 'source' && item.summary && (
                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {item.summary}
                  </p>
                )}
                
                {/* Keywords */}
                {item.type === 'source' && item.keywords && item.keywords.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-muted-foreground">Keywords</div>
                    <div className="flex flex-wrap gap-2">
                      {item.keywords.map((keyword, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {keyword}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Companies */}
                {item.type === 'source' && item.companies && item.companies.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-muted-foreground">Companies</div>
                    <div className="flex flex-wrap gap-2">
                      {item.companies.map((company, index) => (
                        <Badge key={index} variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                          {company}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
