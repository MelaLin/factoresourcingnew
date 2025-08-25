import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { FileText, Send } from 'lucide-react';

interface ThesisTextInputProps {
  onSubmitThesis: (text: string, title: string) => void;
  isLoading?: boolean;
}

export const ThesisTextInput = ({ onSubmitThesis, isLoading = false }: ThesisTextInputProps) => {
  const [thesisText, setThesisText] = useState('');
  const [thesisTitle, setThesisTitle] = useState('');
  const { toast } = useToast();

  const handleSubmit = () => {
    if (!thesisTitle.trim()) {
      toast({
        title: "Title Required",
        description: "Please enter a title for your thesis",
        variant: "destructive",
      });
      return;
    }

    if (!thesisText.trim()) {
      toast({
        title: "No Thesis Text",
        description: "Please enter your thesis content",
        variant: "destructive",
      });
      return;
    }

    if (thesisText.trim().length < 50) {
      toast({
        title: "Thesis Too Short",
        description: "Please provide a more detailed thesis (at least 50 characters)",
        variant: "destructive",
      });
      return;
    }

    onSubmitThesis(thesisText.trim(), thesisTitle.trim());
    
    toast({
      title: "Thesis Submitted",
      description: "Your company thesis has been submitted successfully",
    });
  };

  const clearText = () => {
    setThesisText('');
    setThesisTitle('');
  };

  return (
    <Card className="bg-gradient-to-br from-card to-secondary/10 border-border/50 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <FileText className="h-5 w-5 text-secondary" />
          Paste Company Thesis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Thesis Title Input */}
        <div className="space-y-2">
          <Label htmlFor="thesis-title" className="text-sm font-medium">
            Thesis Title
          </Label>
          <input
            id="thesis-title"
            type="text"
            value={thesisTitle}
            onChange={(e) => setThesisTitle(e.target.value)}
            placeholder="Enter a descriptive title for your thesis..."
            className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-secondary/20 focus:border-secondary transition-all duration-200"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="thesis-text" className="text-sm font-medium">
            Company Investment Thesis
          </Label>
          <Textarea
            id="thesis-text"
            value={thesisText}
            onChange={(e) => setThesisText(e.target.value)}
            placeholder="Paste your company's investment thesis here. Include key areas of focus, investment criteria, target markets, and strategic priorities..."
            className="min-h-[200px] resize-none"
          />
          <div className="flex justify-between items-center text-xs text-muted-foreground">
            <span>{thesisText.length} characters</span>
            {thesisText && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearText}
                className="h-auto p-1 text-xs hover:bg-destructive/10"
              >
                Clear
              </Button>
            )}
          </div>
        </div>

        <Button
          onClick={handleSubmit}
          disabled={!thesisText.trim() || isLoading}
          className="w-full bg-gradient-to-r from-secondary to-success hover:opacity-90 transition-all duration-200 shadow-md"
        >
          <Send className="h-4 w-4 mr-2" />
          {isLoading ? "Processing..." : "Submit Thesis"}
        </Button>
      </CardContent>
    </Card>
  );
};