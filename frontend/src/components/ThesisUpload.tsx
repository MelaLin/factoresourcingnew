import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { Upload, FileText, X } from 'lucide-react';

interface ThesisUploadProps {
  onUploadThesis: (file: File) => void;
  isLoading?: boolean;
}

export const ThesisUpload = ({ onUploadThesis, isLoading = false }: ThesisUploadProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = (file: File) => {
    // Validate file type (PDF, DOC, DOCX, TXT)
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];

    if (!allowedTypes.includes(file.type)) {
      toast({
        title: "Invalid File Type",
        description: "Please upload a PDF, Word document, or text file",
        variant: "destructive",
      });
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File Too Large",
        description: "Please upload a file smaller than 10MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = () => {
    if (!selectedFile) {
      toast({
        title: "No File Selected",
        description: "Please select a thesis file to upload",
        variant: "destructive",
      });
      return;
    }

    onUploadThesis(selectedFile);
    
    toast({
      title: "Thesis Uploaded",
      description: "Your company thesis has been uploaded successfully",
    });
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card className="bg-gradient-to-br from-card to-secondary/10 border-border/50 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <FileText className="h-5 w-5 text-secondary" />
          Upload Company Thesis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className={`
            border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200
            ${dragActive 
              ? 'border-secondary bg-secondary/5' 
              : 'border-border/60 hover:border-secondary/60 hover:bg-secondary/5'
            }
          `}
          onDrop={handleDrop}
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileInput}
            accept=".pdf,.doc,.docx,.txt"
            className="hidden"
            id="thesis-upload"
          />
          
          {selectedFile ? (
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-3 text-sm font-medium text-foreground">
                <FileText className="h-5 w-5 text-secondary" />
                {selectedFile.name}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearFile}
                  className="h-auto p-1 hover:bg-destructive/10"
                >
                  <X className="h-4 w-4 text-destructive" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <Upload className="h-8 w-8 text-muted-foreground mx-auto" />
              <div className="space-y-1">
                <p className="text-sm font-medium">Drop your thesis file here</p>
                <p className="text-xs text-muted-foreground">
                  or{' '}
                  <Label 
                    htmlFor="thesis-upload" 
                    className="text-secondary hover:underline cursor-pointer"
                  >
                    browse files
                  </Label>
                </p>
              </div>
              <p className="text-xs text-muted-foreground">
                Supports PDF, Word documents, and text files (max 10MB)
              </p>
            </div>
          )}
        </div>

        <Button
          onClick={handleUpload}
          disabled={!selectedFile || isLoading}
          className="w-full bg-gradient-to-r from-secondary to-success hover:opacity-90 transition-all duration-200 shadow-md"
        >
          <Upload className="h-4 w-4 mr-2" />
          {isLoading ? "Uploading..." : "Upload Thesis"}
        </Button>
      </CardContent>
    </Card>
  );
};