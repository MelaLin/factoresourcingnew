import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Plus, Globe } from 'lucide-react';

interface SourceInputProps {
  onAddSource: (url: string) => void;
  isLoading?: boolean;
}

export const SourceInput = ({ onAddSource, isLoading = false }: SourceInputProps) => {
  const [url, setUrl] = useState('');
  const { toast } = useToast();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      toast({
        title: "URL Required",
        description: "Please enter a valid blog or website URL",
        variant: "destructive",
      });
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid URL starting with http:// or https://",
        variant: "destructive",
      });
      return;
    }

    onAddSource(url);
    setUrl('');
    
    toast({
      title: "Source Added",
      description: "Blog source has been added for monitoring",
    });
  };

  return (
    <Card className="bg-gradient-to-br from-card to-accent/20 border-border/50 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <Globe className="h-5 w-5 text-primary" />
          Add Content Source
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="blog-url" className="text-sm font-medium">
              Blog or Website URL
            </Label>
            <Input
              id="blog-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/blog"
              className="transition-all duration-200 focus:ring-2 focus:ring-primary/20 bg-background border-border/60"
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-primary to-primary-glow hover:opacity-90 transition-all duration-200 shadow-md"
          >
            <Plus className="h-4 w-4 mr-2" />
            {isLoading ? "Adding Source..." : "Add Source"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};