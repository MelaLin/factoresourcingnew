import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Globe, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface BlogUploadProps {
  onUploadBlog: (url: string) => Promise<void>;
  isLoading: boolean;
}

interface ScrapedArticle {
  url: string;
  title: string;
  summary: string;
  keywords: string[];
  companies: string[];
  relevanceScore: number;
  status: 'pending' | 'scraping' | 'completed' | 'error';
  error?: string;
}

export const BlogUpload = ({ onUploadBlog, isLoading }: BlogUploadProps) => {
  const [blogUrl, setBlogUrl] = useState('');
  const [scrapedArticles, setScrapedArticles] = useState<ScrapedArticle[]>([]);
  const [isScraping, setIsScraping] = useState(false);
  const [progress, setProgress] = useState(0);
  const [totalArticles, setTotalArticles] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!blogUrl.trim()) return;

    setIsScraping(true);
    setProgress(0);
    setScrapedArticles([]);

    try {
      await onUploadBlog(blogUrl);
    } catch (error) {
      console.error('Error uploading blog:', error);
    } finally {
      setIsScraping(false);
    }
  };

  const updateArticleProgress = (articleUrl: string, status: ScrapedArticle['status'], data?: Partial<ScrapedArticle>) => {
    setScrapedArticles(prev => {
      const updated = prev.map(article => 
        article.url === articleUrl 
          ? { ...article, status, ...data }
          : article
      );
      
      // Update progress
      const completed = updated.filter(a => a.status === 'completed').length;
      const total = updated.length;
      if (total > 0) {
        setProgress((completed / total) * 100);
      }
      
      return updated;
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          Upload Blog/Website
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="blog-url" className="text-sm font-medium">
              Blog/Website URL
            </label>
            <Input
              id="blog-url"
              type="url"
              placeholder="https://techcrunch.com/tag/climate-tech/"
              value={blogUrl}
              onChange={(e) => setBlogUrl(e.target.value)}
              disabled={isLoading || isScraping}
            />
            <p className="text-xs text-muted-foreground">
              Enter a blog or website URL that contains multiple articles. The system will automatically discover and analyze each article.
            </p>
          </div>

          <Button 
            type="submit" 
            disabled={!blogUrl.trim() || isLoading || isScraping}
            className="w-full"
          >
            {isLoading || isScraping ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {isScraping ? 'Scraping Articles...' : 'Uploading...'}
              </>
            ) : (
              <>
                <FileText className="h-4 w-4 mr-2" />
                Upload Blog & Analyze Articles
              </>
            )}
          </Button>
        </form>

        {/* Progress Section */}
        {isScraping && (
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span>Scraping Articles</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-muted-foreground">
              Found {totalArticles} articles • {scrapedArticles.filter(a => a.status === 'completed').length} completed
            </p>
          </div>
        )}

        {/* Articles List */}
        {scrapedArticles.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Scraped Articles</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {scrapedArticles.map((article, index) => (
                <div key={index} className="p-3 border rounded-lg space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-sm truncate">{article.title}</h5>
                      <p className="text-xs text-muted-foreground truncate">{article.url}</p>
                    </div>
                    <div className="ml-2">
                      {article.status === 'pending' && (
                        <Badge variant="secondary" className="text-xs">
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Pending
                        </Badge>
                      )}
                      {article.status === 'scraping' && (
                        <Badge variant="secondary" className="text-xs">
                          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                          Scraping
                        </Badge>
                      )}
                      {article.status === 'completed' && (
                        <Badge variant="default" className="text-xs">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          {article.relevanceScore}% Match
                        </Badge>
                      )}
                      {article.status === 'error' && (
                        <Badge variant="destructive" className="text-xs">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Error
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  {article.status === 'completed' && (
                    <div className="space-y-2">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {article.summary}
                      </p>
                      {article.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {article.keywords.slice(0, 3).map((keyword, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      )}
                      {article.companies.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {article.companies.slice(0, 2).map((company, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {company}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  
                  {article.status === 'error' && article.error && (
                    <Alert variant="destructive" className="py-2">
                      <AlertDescription className="text-xs">
                        {article.error}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
