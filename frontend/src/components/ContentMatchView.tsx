import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Calendar, TrendingUp, Tag, Building2 } from 'lucide-react';

interface MatchedContent {
  id: string;
  title: string;
  url: string;
  source: string;
  publishDate: string;
  summary: string;
  relevanceScore: number;
  matchedKeywords: string[];
  companies: string[];
  thesisAlignment: string;
}

interface ContentMatchViewProps {
  matchedContent: MatchedContent[];
  isLoading?: boolean;
}

export const ContentMatchView = ({ matchedContent, isLoading = false }: ContentMatchViewProps) => {
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
                <div className="h-3 bg-muted rounded w-2/3"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (matchedContent.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Matches Yet</h3>
          <p className="text-muted-foreground">
            Add content sources and upload your thesis to see relevant matches
          </p>
        </CardContent>
      </Card>
    );
  }

  const getRelevanceColor = (score: number) => {
    if (score >= 80) return 'bg-success text-success-foreground';
    if (score >= 60) return 'bg-secondary text-secondary-foreground';
    return 'bg-muted text-muted-foreground';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Matched Content</h2>
        <Badge variant="outline" className="text-sm">
          {matchedContent.length} matches found
        </Badge>
      </div>
      
      <div className="space-y-4">
        {matchedContent.map((content) => (
          <Card 
            key={content.id} 
            className="transition-all duration-200 hover:shadow-lg border-border/50 bg-gradient-to-br from-card to-accent/5"
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <CardTitle className="text-lg font-semibold mb-2 line-clamp-2">
                    {content.title}
                  </CardTitle>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="font-medium">{content.source}</span>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(content.publishDate).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge className={getRelevanceColor(content.relevanceScore)}>
                    {content.relevanceScore}% match
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    asChild
                    className="hover:bg-primary/10"
                  >
                    <a 
                      href={content.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-1"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <p className="text-sm text-foreground/80 leading-relaxed">
                {content.summary}
              </p>
              
              {content.companies.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Building2 className="h-3 w-3" />
                    Notable Companies
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {content.companies.map((company, index) => (
                      <Badge 
                        key={index} 
                        variant="outline" 
                        className="text-xs bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100"
                      >
                        {company}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {content.thesisAlignment && (
                <div className="bg-accent/30 rounded-lg p-3">
                  <h4 className="text-sm font-semibold text-secondary mb-2">
                    Thesis Alignment
                  </h4>
                  <div className="space-y-2">
                    {/* Parse and display individual metrics */}
                    {content.thesisAlignment.includes('|') ? (
                      // Split by | and display each metric separately
                      content.thesisAlignment.split('|').map((metric, index) => {
                        const trimmedMetric = metric.trim();
                        if (trimmedMetric) {
                          return (
                            <div key={index} className="text-xs text-foreground/70 bg-accent/20 rounded px-2 py-1">
                              {trimmedMetric}
                            </div>
                          );
                        }
                        return null;
                      })
                    ) : (
                      // Single metric
                      <div className="text-sm text-foreground/80">
                        {content.thesisAlignment}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {content.matchedKeywords.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Tag className="h-3 w-3" />
                    Matched Keywords
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {content.matchedKeywords.map((keyword, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary" 
                        className="text-xs bg-primary/10 text-primary hover:bg-primary/20"
                      >
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};