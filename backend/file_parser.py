import os
from typing import Optional
from PyPDF2 import PdfReader
from docx import Document
import re

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove common PDF artifacts
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    # Normalize line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def parse_pdf(file_path: str) -> Optional[str]:
    """Extract text from PDF file with enhanced parsing"""
    try:
        reader = PdfReader(file_path)
        text = ""
        
        print(f"📄 Processing PDF with {len(reader.pages)} pages")
        
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    cleaned_text = clean_text(page_text)
                    if cleaned_text:
                        text += cleaned_text + "\n"
                        print(f"   Page {i+1}: {len(cleaned_text)} characters")
                    else:
                        print(f"   Page {i+1}: No text extracted (possibly image-based)")
                else:
                    print(f"   Page {i+1}: No text content")
            except Exception as e:
                print(f"   Page {i+1}: Error extracting text - {e}")
                continue
        
        if text.strip():
            print(f"✅ PDF parsing successful: {len(text)} total characters")
            return text.strip()
        else:
            print("⚠️  No text extracted from PDF")
            return None
            
    except Exception as e:
        print(f"❌ Error parsing PDF {file_path}: {e}")
        return None

def parse_docx(file_path: str) -> Optional[str]:
    """Extract text from Word document"""
    try:
        doc = Document(file_path)
        text = ""
        
        print(f"📝 Processing Word document")
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text.strip() + "\n"
        
        if text.strip():
            print(f"✅ Word document parsing successful: {len(text)} characters")
            return text.strip()
        else:
            print("⚠️  No text extracted from Word document")
            return None
            
    except Exception as e:
        print(f"❌ Error parsing DOCX {file_path}: {e}")
        return None

def parse_file(file_path: str) -> Optional[str]:
    """Parse file based on extension and return text content"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    print(f"🔍 Parsing file: {os.path.basename(file_path)} ({file_ext})")
    
    if file_ext == '.pdf':
        return parse_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        return parse_docx(file_path)
    elif file_ext == '.txt':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                if text:
                    print(f"✅ Text file parsing successful: {len(text)} characters")
                    return text
                else:
                    print("⚠️  Text file is empty")
                    return None
        except Exception as e:
            print(f"❌ Error reading text file {file_path}: {e}")
            return None
    else:
        print(f"❌ Unsupported file type: {file_ext}")
        return None
