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
  RefreshCw,
  Star
} from 'lucide-react';

interface BlogRevision {
  id: string;
  keyword?: string;  // For keyword searches
  url?: string;      // For traditional blog searches
  search_time: string;
  total_articles_found: number;
  processed_articles: number;
  is_active: boolean;
  removed_articles: string[];
  scholar_papers?: number;  // For keyword searches
  patents?: number;         // For keyword searches
  is_starred?: boolean;     // Star status for priority matching
  search_type?: string;     // 'blog_upload' or 'keyword_search'
}

interface ThesisRevision {
  id: string;
  filename: string;
  content: string;
  full_content?: string;  // Full thesis content for display
  original_content: string;
  upload_time: string;
  file_type: string;
  is_active: boolean;
  title: string;
  has_changes: boolean;
  is_starred?: boolean;  // Star status for priority matching
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
  }, [API_BASE_URL]); // Only re-run if API_BASE_URL changes

  const fetchRevisions = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch comprehensive history from the new endpoint
      const historyResponse = await fetch(`${API_BASE_URL}/api/history`);
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        console.log('📚 Fetched comprehensive history:', historyData);
        
        // Process all content types
        const blogs: BlogRevision[] = [];
        const theses: ThesisRevision[] = [];
        const articlesList: Article[] = [];
        
        historyData.forEach((item: any) => {
          console.log(`🔍 Processing item: ${item.type} - ${item.id}`);
          if (item.type === 'blog_upload') {
            // This is a blog URL upload
            console.log(`✅ Adding blog upload: ${item.url}`);
            blogs.push({
              id: item.id,
              url: item.url || 'Unknown',
              search_time: item.timestamp,
              total_articles_found: item.total_articles || 0,
              processed_articles: item.processed_articles || 0,
              is_active: true, // All blog uploads are active by default
              removed_articles: [],
              search_type: 'blog_upload',
              is_starred: item.is_starred || false
            });
          } else if (item.type === 'keyword_search') {
            // This is a keyword search
            blogs.push({
              id: item.id,
              keyword: item.keyword || 'Unknown',
              search_time: item.timestamp,
              total_articles_found: item.total_sources || 0,
              processed_articles: item.processed_sources || 0,
              is_active: true, // All keyword searches are active by default
              removed_articles: [],
              scholar_papers: item.scholar_papers || 0,
              patents: item.patents || 0,
              search_type: 'keyword_search',
              is_starred: item.is_starred || false
            });
          } else if (item.type === 'thesis') {
            console.log(`📝 Processing thesis: ${item.id}, is_starred: ${item.is_starred}`);
            theses.push({
              id: item.id,
              filename: item.title.replace('Thesis: ', ''),
              content: item.content || '',
              full_content: item.full_content || item.content || '',  // Use full_content if available
              original_content: item.content || '',
              upload_time: item.timestamp,
              file_type: 'text',
              is_active: true,
              title: item.title.replace('Thesis: ', ''),
              has_changes: false,
              is_starred: item.is_starred || false
            });
          } else if (item.type === 'source') {
            articlesList.push({
              id: item.id,
              url: item.url,
              title: item.title,
              summary: item.summary,
              source_blog: item.source_blog || item.source_type || 'Unknown Source',
              is_removed: false
            });
          }
        });
        
        setBlogRevisions(blogs);
        setThesisRevisions(theses);
        setArticles(articlesList);
        
        console.log(`📊 Processed: ${blogs.length} blogs, ${theses.length} theses, ${articlesList.length} articles`);
        console.log(`📝 Blog revisions:`, blogs);
        console.log(`📚 Thesis revisions:`, theses);
        console.log(`📰 Articles:`, articlesList);
        
        // Debug: Show star status for each thesis
        theses.forEach((thesis, index) => {
          console.log(`⭐ Thesis ${index + 1}: ${thesis.title}, is_starred: ${thesis.is_starred}`);
        });
      } else {
        throw new Error(`History fetch failed: ${historyResponse.status}`);
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

  const removeArticle = async (articleId: string) => {
    try {
      console.log(`🗑️  Removing article: ${articleId}`);
      
      // Call backend to remove the article
      const response = await fetch(`${API_BASE_URL}/api/history/${articleId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Remove from local state
        setArticles(prev => prev.filter(article => article.id !== articleId));
        setHasUnsavedChanges(true);
        console.log(`✅ Article ${articleId} removed successfully`);
        
        // Clear any previous errors
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to remove article');
      }
    } catch (err) {
      console.error('❌ Error removing article:', err);
      // Don't set the main error state - just show a temporary message
      // This prevents the "error loading revisions" screen from appearing
      const tempError = `Failed to remove article: ${err.message}`;
      console.warn(tempError);
      
      // Optionally show a toast notification instead of setting the main error
      // For now, just log the error without breaking the UI
    }
  };

  const starBlog = async (blogId: string) => {
    try {
      // Call backend to star/unstar the blog
      const response = await fetch(`${API_BASE_URL}/api/blogs/star/${blogId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log(`⭐ Blog ${blogId} starred/unstarred:`, result);
        
        // Update local state
        setBlogRevisions(prev => 
          prev.map(blog => 
            blog.id === blogId 
              ? { ...blog, is_starred: result.is_starred }
              : blog
          )
        );
        
        // Clear any previous errors
        setError(null);
      } else {
        throw new Error('Failed to star blog');
      }
    } catch (err) {
      console.error('❌ Error starring blog:', err);
      const tempError = `Failed to star blog: ${err.message}`;
      console.warn(tempError);
    }
  };

  const deactivateBlog = async (blogId: string) => {
    try {
      console.log(`🗑️  Removing blog: ${blogId}`);
      
      // Call backend to remove the blog
      const response = await fetch(`${API_BASE_URL}/api/history/${blogId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Remove from local state
        setBlogRevisions(prev => prev.filter(blog => blog.id !== blogId));
        setHasUnsavedChanges(true);
        console.log(`✅ Blog ${blogId} removed successfully`);
        
        // Clear any previous errors
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to remove blog');
      }
    } catch (err) {
      console.error('❌ Error removing blog:', err);
      // Don't set the main error state - just show a temporary message
      const tempError = `Failed to remove blog: ${err.message}`;
      console.warn(tempError);
    }
  };

  const starThesis = async (thesisId: string) => {
    try {
      console.log(`⭐ Starring/unstarring thesis: ${thesisId}`);
      
      // Call backend to star/unstar the thesis
      const response = await fetch(`${API_BASE_URL}/api/thesis/star/${thesisId}`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log(`⭐ Thesis ${thesisId} starred/unstarred:`, result);
        
        // Update local state
        setThesisRevisions(prev => 
          prev.map(thesis => 
            thesis.id === thesisId 
              ? { ...thesis, is_starred: result.is_starred }
              : thesis
          )
        );
        
        // Clear any previous errors
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to star thesis');
      }
    } catch (err) {
      console.error('❌ Error starring thesis:', err);
      const tempError = `Failed to star thesis: ${err.message}`;
      console.warn(tempError);
    }
  };

  const deactivateThesis = async (thesisId: string) => {
    try {
      console.log(`🗑️  Removing thesis: ${thesisId}`);
      
      // Call backend to remove the thesis
      const response = await fetch(`${API_BASE_URL}/api/history/${thesisId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Remove from local state
        setThesisRevisions(prev => prev.filter(thesis => thesis.id !== thesisId));
        setHasUnsavedChanges(true);
        console.log(`✅ Thesis ${thesisId} removed successfully`);
        
        // Clear any previous errors
        setError(null);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to remove thesis');
      }
    } catch (err) {
      console.error('❌ Error removing thesis:', err);
      // Don't set the main error state - just show a temporary message
      const tempError = `Failed to remove thesis: ${err.message}`;
      console.warn(tempError);
    }
  };

  const commitRevisions = async () => {
    try {
      setIsLoading(true);
      
      // Since we're now permanently removing items, just refresh matches
      // The backend already has the updated state
      console.log('🔄 Committing revisions - refreshing matches...');
      
      // Trigger matches refresh by dispatching a custom event
      window.dispatchEvent(new CustomEvent('revisionsCommitted', { 
        detail: { 
          blogs: blogRevisions, 
          theses: thesisRevisions, 
          articles: articles 
        } 
      }));
      
      setHasUnsavedChanges(false);
      alert('✅ Revisions committed successfully! Check the Matches tab for updated results.');
      
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
    const activeBlogs = blogRevisions.length;
    const activeTheses = thesisRevisions.length;
    const activeArticles = articles.length;
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
                <h3 className="text-lg font-semibold mb-2">No Blog Uploads Yet</h3>
                <p className="text-muted-foreground">
                  Upload blogs or perform keyword searches to see them in revisions
                </p>
              </CardContent>
            </Card>
          ) : (
            blogRevisions.map((blog) => (
              <Card key={blog.id} className="transition-all duration-200 hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <Globe className="h-4 w-4 text-blue-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {blog.search_type === 'blog_upload' ? blog.url : blog.keyword || 'Unknown Search'}
                        </CardTitle>
                        <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                          {blog.search_type === 'blog_upload' ? 'Blog Upload' : 'Keyword Search'}
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
                        
                        {blog.scholar_papers && blog.scholar_papers > 0 && (
                          <span className="text-purple-600">
                            {blog.scholar_papers} Scholar papers
                          </span>
                        )}
                        
                        {blog.patents && blog.patents > 0 && (
                          <span className="text-orange-600">
                            {blog.patents} Patents
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => starBlog(blog.id)}
                        className={`${blog.is_starred ? 'text-yellow-600 bg-yellow-50' : 'text-yellow-600 hover:bg-yellow-50'}`}
                      >
                        <Star className={`h-4 w-4 ${blog.is_starred ? 'fill-current' : ''}`} />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => deactivateBlog(blog.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <X className="h-4 w-4" />
                      </Button>
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
              <Card key={thesis.id} className="transition-all duration-200 hover:shadow-md">
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
                        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                          Active
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
                            onClick={() => starThesis(thesis.id)}
                            className={`${thesis.is_starred ? 'text-yellow-600 bg-yellow-50' : 'text-yellow-600 hover:bg-yellow-50'}`}
                          >
                            <Star className={`h-4 w-4 ${thesis.is_starred ? 'fill-current' : ''}`} />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => startEditingThesis(thesis.id)}
                            className="text-blue-600 hover:bg-blue-50"
                          >
                            <Edit3 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => deactivateThesis(thesis.id)}
                            className="text-red-600 hover:bg-red-50"
                          >
                            <X className="h-4 w-4" />
                          </Button>
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
                        <strong>Full Thesis Content:</strong>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 leading-relaxed">
                          {thesis.full_content || thesis.content || "No content available"}
                        </pre>
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
              <Card key={article.id} className="transition-all duration-200 hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4 text-green-600" />
                        <CardTitle className="text-lg font-semibold line-clamp-2">
                          {article.title}
                        </CardTitle>
                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                          Active
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
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeArticle(article.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <X className="h-4 w-4" />
                      </Button>
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
