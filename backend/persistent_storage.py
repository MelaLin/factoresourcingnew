"""
Persistent Storage System - Saves all data to JSON files
Ensures data survives redeployments and server restarts
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import traceback

class PersistentStorage:
    """Manages persistent storage of all application data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # File paths for different data types
        self.articles_file = os.path.join(data_dir, "articles.json")
        self.thesis_file = os.path.join(data_dir, "thesis_uploads.json")
        self.blogs_file = os.path.join(data_dir, "blog_searches.json")
        
        print(f"📁 Persistent storage initialized in: {os.path.abspath(data_dir)}")
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"📁 Created data directory: {self.data_dir}")
    
    def save_articles(self, articles: List[Dict[str, Any]]):
        """Save articles to JSON file"""
        try:
            with open(self.articles_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Saved {len(articles)} articles to {self.articles_file}")
        except Exception as e:
            print(f"❌ Error saving articles: {e}")
            traceback.print_exc()
    
    def load_articles(self) -> List[Dict[str, Any]]:
        """Load articles from JSON file"""
        try:
            if os.path.exists(self.articles_file):
                with open(self.articles_file, 'r', encoding='utf-8') as f:
                    articles = json.load(f)
                print(f"📂 Loaded {len(articles)} articles from {self.articles_file}")
                return articles
            else:
                print(f"📂 No articles file found, starting with empty list")
                return []
        except Exception as e:
            print(f"❌ Error loading articles: {e}")
            traceback.print_exc()
            return []
    
    def save_thesis_uploads(self, thesis_uploads: List[Dict[str, Any]]):
        """Save thesis uploads to JSON file"""
        try:
            with open(self.thesis_file, 'w', encoding='utf-8') as f:
                json.dump(thesis_uploads, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Saved {len(thesis_uploads)} thesis uploads to {self.thesis_file}")
        except Exception as e:
            print(f"❌ Error saving thesis uploads: {e}")
            traceback.print_exc()
    
    def load_thesis_uploads(self) -> List[Dict[str, Any]]:
        """Load thesis uploads from JSON file"""
        try:
            if os.path.exists(self.thesis_file):
                with open(self.thesis_file, 'r', encoding='utf-8') as f:
                    thesis_uploads = json.load(f)
                print(f"📂 Loaded {len(thesis_uploads)} thesis uploads from {self.thesis_file}")
                return thesis_uploads
            else:
                print(f"📂 No thesis file found, starting with empty list")
                return []
        except Exception as e:
            print(f"❌ Error loading thesis uploads: {e}")
            traceback.print_exc()
            return []
    
    def save_blog_searches(self, blog_searches: List[Dict[str, Any]]):
        """Save blog searches to JSON file"""
        try:
            with open(self.blogs_file, 'w', encoding='utf-8') as f:
                json.dump(blog_searches, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Saved {len(blog_searches)} blog searches to {self.blogs_file}")
        except Exception as e:
            print(f"❌ Error saving blog searches: {e}")
            traceback.print_exc()
    
    def load_blog_searches(self) -> List[Dict[str, Any]]:
        """Load blog searches from JSON file"""
        try:
            if os.path.exists(self.blogs_file):
                with open(self.blogs_file, 'r', encoding='utf-8') as f:
                    blog_searches = json.load(f)
                print(f"📂 Loaded {len(blog_searches)} blog searches from {self.blogs_file}")
                return blog_searches
            else:
                print(f"📂 No blog searches file found, starting with empty list")
                return []
        except Exception as e:
            print(f"❌ Error loading blog searches: {e}")
            traceback.print_exc()
            return []
    
    def save_all_data(self, articles: List[Dict[str, Any]], 
                      thesis_uploads: List[Dict[str, Any]], 
                      blog_searches: List[Dict[str, Any]]):
        """Save all data types at once"""
        try:
            self.save_articles(articles)
            self.save_thesis_uploads(thesis_uploads)
            self.save_blog_searches(blog_searches)
            print(f"💾 All data saved successfully")
        except Exception as e:
            print(f"❌ Error saving all data: {e}")
            traceback.print_exc()
    
    def load_all_data(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Load all data types at once"""
        try:
            articles = self.load_articles()
            thesis_uploads = self.load_thesis_uploads()
            blog_searches = self.load_blog_searches()
            print(f"📂 All data loaded successfully")
            return articles, thesis_uploads, blog_searches
        except Exception as e:
            print(f"❌ Error loading all data: {e}")
            traceback.print_exc()
            return [], [], []
    
    def backup_data(self, backup_dir: str = "backups"):
        """Create a backup of all data"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            os.makedirs(backup_path)
            
            # Copy all data files to backup
            import shutil
            for file_path in [self.articles_file, self.thesis_file, self.blogs_file]:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    backup_file = os.path.join(backup_path, filename)
                    shutil.copy2(file_path, backup_file)
            
            print(f"💾 Backup created at: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            traceback.print_exc()
            return None

# Global instance
persistent_storage = PersistentStorage()
