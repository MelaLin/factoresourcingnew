import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { 
  FileText, 
  Globe, 
  Calendar, 
  Edit3, 
  X, 
  Save, 
  RotateCcw, 
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

interface BlogRevision {
  id: string;
  url: string;
  search_time: string;
  total_articles_found: number;
  processed_articles: number;
  is_active: boolean;
  removed_articles: string[];
}

interface ThesisRevision {
  id: string;
  filename: string;
  content: string;
  original_content: string;
  upload_time: string;
  file_type: string;
  is_active: boolean;
  title: string;
  has_changes: boolean;
}

interface Article {
  id: string;
  url: string;
  title: string;
  summary: string;
  source_blog: string;
  is_removed: boolean;
}

export const Revisions = () => {
  const [blogRevisions, setBlogRevisions] = useState<BlogRevision[]>([]);
  const [thesisRevisions, setThesisRevisions] = useState<ThesisRevision[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'blogs' | 'theses' | 'articles'>('blogs');
  const [editingThesis, setEditingThesis] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState<string>('');
  const [editingContent, setEditingContent] = useState<string>('');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

  useEffect(() => {
    fetchRevisions();
  }, []);

  const fetchRevisions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch blog revisions
      const blogsResponse = await fetch(`${API_BASE_URL}/api/blogs/starred`);
      if (blogsResponse.ok) {
        const blogsData = await blogsResponse.json();
        const blogs = (blogsData.starred_blogs || []).map((blog: any) => ({
          ...blog,
          is_active: true,
          removed_articles: []
        }));
        setBlogRevisions(blogs);
      }
      
      // Fetch thesis revisions
      const thesisResponse = await fetch(`${API_BASE_URL}/api/history/thesis`);
      if (thesisResponse.ok) {
        const thesisData = await thesisResponse.json();
        const theses = (thesisData || []).map((thesis: any) => ({
          ...thesis,
          content: thesis.content || thesis.original_content || '',
          original_content: thesis.content || thesis.original_content || '',
          is_active: true,
          title: thesis.filename || 'Untitled Thesis',
          has_changes: false
        }));
        setThesisRevisions(theses);
      }
      
      // Fetch articles
      const articlesResponse = await fetch(`${API_BASE_URL}/api/history/sources`);
      if (articlesResponse.ok) {
        const articlesData = await articlesResponse.json();
        const articlesList = (articlesData || []).map((article: any) => ({
          id: article.id,
          url: article.url,
          title: article.title,
          summary: article.summary,
          source_blog: article.source_blog || 'Unknown Source',
          is_removed: false
        }));
        setArticles(articlesList);
      }
      
    } catch (err) {
      console.error('❌ Revisions fetch error:', err);
      setError('Failed to fetch revisions data');
    } finally {
      setIsLoading(false);
    }
  };

  const startEditingThesis = (thesisId: string) => {
    const thesis = thesisRevisions.find(t => t.id === thesisId);
    if (thesis) {
      setEditingThesis(thesisId);
      setEditingTitle(thesis.title);
      setEditingContent(thesis.content);
      setHasUnsavedChanges(false);
    }
  };

  const saveThesisChanges = async (thesisId: string) => {
    try {
      const thesis = thesisRevisions.find(t => t.id === thesisId);
      if (!thesis) return;

      const updatedThesis = {
        ...thesis,
        title: editingTitle,
        content: editingContent,
        has_changes: true
      };

      // Update local state
      setThesisRevisions(prev => 
        prev.map(t => t.id === thesisId ? updatedThesis : t)
      );

      // Save to backend
      const response = await fetch(`${API_BASE_URL}/api/thesis/update/${thesisId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: editingTitle,
          content: editingContent
        })
      });

      if (response.ok) {
        setEditingThesis(null);
        setHasUnsavedChanges(false);
      } else {
        throw new Error('Failed to save thesis changes');
      }
      
    } catch (err) {
      console.error('❌ Thesis save error:', err);
      setError('Failed to save thesis changes');
    }
  };

  const cancelThesisEdit = () => {
    setEditingThesis(null);
    setEditingTitle('');
    setEditingContent('');
    setHasUnsavedChanges(false);
  };

  const removeArticle = (articleId: string) => {
    setArticles(prev => 
      prev.map(article => 
        article.id === articleId 
          ? { ...article, is_removed: true }
          : article
      )
    );
    setHasUnsavedChanges(true);
  };

  const restoreArticle = (articleId: string) => {
    setArticles(prev => 
      prev.map(article => 
        article.id === articleId 
          ? { ...article, is_removed: false }
          : article
      )
    );
    setHasUnsavedChanges(true);
  };

  const deactivateBlog = (blogId: string) => {
    setBlogRevisions(prev => 
      prev.map(blog => 
        blog.id === blogId 
          ? { ...blog, is_active: false }
          : blog
      )
    );
    setHasUnsavedChanges(true);
  };

  const activateBlog = (blogId: string) => {
    setBlogRevisions(prev => 
      prev.map(blog => 
        blog.id === blogId 
          ? { ...blog, is_active: true }
          : blog
      )
    );
    setHasUnsavedChanges(true);
  };

  const deactivateThesis = (thesisId: string) => {
    setThesisRevisions(prev => 
      prev.map(thesis => 
        thesis.id === thesisId 
          ? { ...thesis, is_active: false }
          : thesis
      )
    );
    setHasUnsavedChanges(true);
  };

  const activateThesis = (thesisId: string) => {
    setThesisRevisions(prev => 
      prev.map(thesis => 
        thesis.id === thesisId 
          ? { ...thesis, is_active: true }
          : thesis
      )
    );
    setHasUnsavedChanges(true);
  };

  const commitRevisions = async () => {
    try {
      setIsLoading(true);
      
      // Prepare revision data
      const revisionData = {
        blogs: blogRevisions.filter(blog => blog.is_active),
        theses: thesisRevisions.filter(thesis => thesis.is_active),
        articles: articles.filter(article => !article.is_removed)
      };

      // Send to backend to update matches
      const response = await fetch(`${API_BASE_URL}/api/revisions/commit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(revisionData)
      });

      if (response.ok) {
        setHasUnsavedChanges(false);
        // Trigger matches refresh
        window.dispatchEvent(new CustomEvent('revisionsCommitted', { detail: revisionData }));
        alert('✅ Revisions committed successfully! Check the Matches tab for updated results.');
      } else {
        throw new Error('Failed to commit revisions');
      }
      
    } catch (err) {
      console.error('❌ Commit error:', err);
      setError('Failed to commit revisions');
    } finally {
      setIsLoading(false);
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

  const getActiveCount = () => {
    const activeBlogs = blogRevisions.filter(blog => blog.is_active).length;
    const activeTheses = thesisRevisions.filter(thesis => thesis.is_active).length;
    const activeArticles = articles.filter(article => !article.is_removed).length;
    return { activeBlogs, activeTheses, activeArticles };
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Revisions</h2>
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
          <h2 className="text-2xl font-bold">Revisions</h2>
          <Button variant="outline" size="sm" onClick={fetchRevisions}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
        
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <div>
                <h3 className="font-semibold">Error Loading Revisions</h3>
                <p className="text-sm">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { activeBlogs, activeTheses, activeArticles } = getActiveCount();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Revisions</h2>
          <p className="text-muted-foreground">
            {activeBlogs} active blogs • {activeTheses} active theses • {activeArticles} active articles
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={fetchRevisions}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          
          <Button 
            onClick={commitRevisions}
            disabled={!hasUnsavedChanges || isLoading}
            className="bg-green-600 hover:bg-green-700"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            {isLoading ? 'Committing...' : 'Commit Revisions'}
          </Button>
        </div>
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
          Blogs ({blogRevisions.length})
        </Button>
        <Button
          variant={activeTab === 'theses' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('theses')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Theses ({thesisRevisions.length})
        </Button>
        <Button
          variant={activeTab === 'articles' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('articles')}
          className="flex-1"
        >
          <FileText className="h-4 w-4 mr-2" />
          Articles ({articles.length})
        </Button>
      </div>

      {/* Blogs Tab */}
      {activeTab === 'blogs' && (
        <div className="space-y-4">
          {blogRevisions.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <Globe className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Blog Revisions Yet</h3>
                <p className="text-muted-foreground">
                  Upload blogs to see them in revisions
                </p>
              </CardContent>
            </Card>
          ) : (
            blogRevisions.map((blog) => (
              <Card key={blog.id} className={`transition-all duration-200 hover:shadow-md ${
                !blog.is_active ? 'opacity-60 bg-muted/30' : ''
              }`}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Globe className="h-4 w-4 text-blue-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {blog.url}
                        </CardTitle>
                        <Badge variant={blog.is_active ? "secondary" : "outline"} 
                               className={blog.is_active ? "bg-blue-100 text-blue-800" : "bg-gray-100 text-gray-600"}>
                          {blog.is_active ? 'Active' : 'Inactive'}
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
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {blog.is_active ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deactivateBlog(blog.id)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => activateBlog(blog.id)}
                          className="text-green-600 hover:bg-green-50"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Theses Tab */}
      {activeTab === 'theses' && (
        <div className="space-y-4">
          {thesisRevisions.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Thesis Revisions Yet</h3>
                <p className="text-muted-foreground">
                  Upload thesis files to see them in revisions
                </p>
              </CardContent>
            </Card>
          ) : (
            thesisRevisions.map((thesis) => (
              <Card key={thesis.id} className={`transition-all duration-200 hover:shadow-md ${
                !thesis.is_active ? 'opacity-60 bg-muted/30' : ''
              }`}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-purple-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {editingThesis === thesis.id ? (
                            <Input
                              value={editingTitle}
                              onChange={(e) => {
                                setEditingTitle(e.target.value);
                                setHasUnsavedChanges(true);
                              }}
                              className="text-lg font-semibold"
                            />
                          ) : (
                            thesis.title
                          )}
                        </CardTitle>
                        <Badge variant={thesis.is_active ? "secondary" : "outline"} 
                               className={thesis.is_active ? "bg-purple-100 text-purple-800" : "bg-gray-100 text-gray-600"}>
                          {thesis.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        {thesis.has_changes && (
                          <Badge variant="outline" className="bg-yellow-100 text-yellow-700 border-yellow-200">
                            Modified
                          </Badge>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(thesis.upload_time)}
                        </div>
                        
                        <span className="text-purple-600">
                          {thesis.content.length.toLocaleString()} characters
                        </span>
                        
                        <span className="text-gray-600">
                          {thesis.file_type} file
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {editingThesis === thesis.id ? (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => saveThesisChanges(thesis.id)}
                            className="text-green-600 hover:bg-green-50"
                          >
                            <Save className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={cancelThesisEdit}
                            className="text-gray-600 hover:bg-gray-50"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => startEditingThesis(thesis.id)}
                            className="text-blue-600 hover:bg-blue-50"
                          >
                            <Edit3 className="h-4 w-4" />
                          </Button>
                          {thesis.is_active ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deactivateThesis(thesis.id)}
                              className="text-red-600 hover:bg-red-50"
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => activateThesis(thesis.id)}
                              className="text-green-600 hover:bg-green-50"
                            >
                              <RotateCcw className="h-4 w-4" />
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  {editingThesis === thesis.id ? (
                    <Textarea
                      value={editingContent}
                      onChange={(e) => {
                        setEditingContent(e.target.value);
                        setHasUnsavedChanges(true);
                      }}
                      placeholder="Edit thesis content..."
                      className="min-h-[200px] font-mono text-sm"
                    />
                  ) : (
                    <div className="space-y-3">
                      <div className="text-sm text-muted-foreground">
                        <strong>Content Preview:</strong> {thesis.content.substring(0, 200)}...
                      </div>
                      {thesis.has_changes && (
                        <div className="text-xs text-yellow-600 bg-yellow-50 p-2 rounded">
                          ⚠️ This thesis has been modified from its original version
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Articles Tab */}
      {activeTab === 'articles' && (
        <div className="space-y-4">
          {articles.length === 0 ? (
            <Card className="text-center py-12">
              <CardContent>
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Articles Yet</h3>
                <p className="text-muted-foreground">
                  Add content sources to see articles in revisions
                </p>
              </CardContent>
            </Card>
          ) : (
            articles.map((article) => (
              <Card key={article.id} className={`transition-all duration-200 hover:shadow-md ${
                article.is_removed ? 'opacity-60 bg-muted/30' : ''
              }`}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-green-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {article.title}
                        </CardTitle>
                        <Badge variant={article.is_removed ? "outline" : "secondary"} 
                               className={article.is_removed ? "bg-gray-100 text-gray-600" : "bg-green-100 text-green-800"}>
                          {article.is_removed ? 'Removed' : 'Active'}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1 text-blue-600">
                          <Globe className="h-3 w-3" />
                          <span className="truncate max-w-xs">{article.url}</span>
                        </div>
                        
                        <span className="text-purple-600">
                          From: {article.source_blog}
                        </span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {article.is_removed ? (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => restoreArticle(article.id)}
                          className="text-green-600 hover:bg-green-50"
                        >
                          <RotateCcw className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeArticle(article.id)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                
                <CardContent>
                  {article.summary && (
                    <p className="text-sm text-foreground/80 leading-relaxed">
                      {article.summary}
                    </p>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Commit Status */}
      {hasUnsavedChanges && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 text-yellow-800">
              <AlertCircle className="h-5 w-5" />
              <div>
                <h3 className="font-semibold">Unsaved Changes</h3>
                <p className="text-sm">
                  You have unsaved changes. Click "Commit Revisions" to apply them and update the matches.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
