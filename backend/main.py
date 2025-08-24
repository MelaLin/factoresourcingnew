from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from ai_utils import summarize_text, extract_keywords_from_text

import json
import asyncio
import tempfile
import os
from pathlib import Path
import time
from datetime import datetime
import traceback

# Real scraping functions with legal compliance and error handling
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def is_scraping_allowed(url: str) -> tuple[bool, str]:
    """Check if scraping is legally allowed for a given URL"""
    try:
        # Check robots.txt
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            robots_response = requests.get(robots_url, timeout=5)
            if robots_response.status_code == 200:
                robots_content = robots_response.text.lower()
                if "disallow: /" in robots_content or "noindex" in robots_content:
                    return False, "Scraping blocked by robots.txt"
        except:
            pass  # Continue if robots.txt check fails
        
        # Check for common anti-scraping patterns
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                return False, "Access forbidden (403) - site blocks scraping"
            elif response.status_code == 429:
                return False, "Rate limited (429) - too many requests"
            elif response.status_code >= 400:
                return False, f"HTTP error {response.status_code} - site not accessible"
            
            # Check for anti-bot measures
            content = response.text.lower()
            if any(term in content for term in ["access denied", "blocked", "captcha", "cloudflare"]):
                return False, "Site has anti-bot protection"
                
            return True, "Scraping allowed"
            
        except requests.exceptions.Timeout:
            return False, "Request timeout - site may be blocking access"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - site may be blocking access"
        except Exception as e:
            return False, f"Error checking site: {str(e)}"
            
    except Exception as e:
        return False, f"Error analyzing site: {str(e)}"



def extract_companies_from_text(text: str) -> list[str]:
    """Extract company names from text content"""
    try:
        # Common company indicators
        company_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Group|Technologies|Solutions|Systems|Software|AI|ML|Tech|Ventures|Capital|Partners|Associates|Consulting|Services)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+&\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z][a-z]+\b'
        ]
        
        companies = set()
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        for pattern in company_patterns:
            matches = re.findall(pattern, clean_text)
            for match in matches:
                if len(match.split()) >= 2 and len(match) > 5:  # Filter out single words
                    companies.add(match.strip())
        
        # Convert to list and limit results
        company_list = list(companies)[:10]  # Max 10 companies
        
        if not company_list:
            # Fallback: look for capitalized word sequences
            words = clean_text.split()
            potential_companies = []
            for i in range(len(words) - 1):
                if (words[i][0].isupper() and words[i+1][0].isupper() and 
                    len(words[i]) > 2 and len(words[i+1]) > 2):
                    potential_companies.append(f"{words[i]} {words[i+1]}")
            
            company_list = list(set(potential_companies))[:5]
        
        return company_list
        
    except Exception as e:
        print(f"Error extracting companies: {e}")
        return []

def real_scrape_url(url: str) -> dict:
    """Real URL scraping - simplified for content matching"""
    print(f"🚀 REAL_SCRAPE_URL CALLED for: {url}")
    try:
        print(f"🌐 Attempting to scrape: {url}")
        
        # Always attempt scraping for content matching
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else f"Content from {url}"
        
        # Extract main content (try multiple selectors)
        content_selectors = [
            'article', 'main', '.content', '.post-content', '.entry-content', 
            '.article-content', '.story-content', '.post-body', '.entry-body'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # Fallback to body content
            main_content = soup.find('body')
        
        if main_content:
            # Clean and extract text
            for tag in main_content(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            text_content = main_content.get_text(separator=' ', strip=True)
            # Clean up whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
        else:
            text_content = "Content could not be extracted from this page."
        
        # Extract keywords and companies from real content
        keywords = extract_keywords_from_text(text_content)
        companies = extract_companies_from_text(text_content)
        
        # Try to extract publish date
        publish_date = None
        date_selectors = [
            'time[datetime]', '.publish-date', '.post-date', '.entry-date', 
            '.article-date', '.story-date', 'meta[property="article:published_time"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if selector == 'meta[property="article:published_time"]':
                    publish_date = date_elem.get('content')
                else:
                    publish_date = date_elem.get('datetime') or date_elem.get_text()
                break
        
        if not publish_date:
            publish_date = datetime.now().isoformat()
        
        # Try to extract authors
        authors = []
        author_selectors = [
            '.author', '.byline', '.post-author', '.entry-author', 
            '.article-author', '.story-author', 'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if selector == 'meta[name="author"]':
                    authors.append(author_elem.get('content'))
                else:
                    authors.append(author_elem.get_text().strip())
                break
        
        if not authors:
            authors = ["Unknown Author"]
        
        print(f"✅ Successfully scraped: {title}")
        print(f"   📝 Content length: {len(text_content)} characters")
        print(f"   🔑 Keywords found: {keywords[:5]}")
        print(f"   🏢 Companies found: {companies[:5]}")
        
        return {
            "title": title,
            "text": text_content,
            "keywords": keywords,
            "companies": companies,
            "publish_date": publish_date,
            "authors": authors,
            "scraping_allowed": True,
            "warning": None
        }
        
    except requests.exceptions.Timeout:
        return {
            "title": f"⚠️ Scraping Timeout: {url}",
            "text": "This website took too long to respond and may be blocking automated access.",
            "companies": [],
            "publish_date": datetime.now().isoformat(),
            "authors": [],
            "scraping_allowed": True,
            "warning": "Request timeout - site may be blocking access"
        }
    except requests.exceptions.ConnectionError:
        return {
            "title": f"⚠️ Connection Error: {url}",
            "text": "Unable to connect to this website. It may be down or blocking access.",
            "companies": [],
            "publish_date": datetime.now().isoformat(),
            "authors": [],
            "scraping_allowed": True,
            "warning": "Connection error - site may be blocking access"
        }
    except Exception as e:
        return {
            "title": f"⚠️ Scraping Error: {url}",
            "text": f"An error occurred while scraping this website: {str(e)}",
            "keywords": [],
            "companies": [],
            "publish_date": datetime.now().isoformat(),
            "authors": [],
            "scraping_allowed": True,
            "warning": f"Scraping error: {str(e)}"
        }



def embed_text(text: str) -> list[float]:
    """Generate embedding for text content"""
    try:
        from ai_utils import embed_text as ai_embed_text
        return ai_embed_text(text)
    except ImportError:
        # Fallback to simple embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        return [float(int(hash_obj.hexdigest()[:8], 16)) / 100000000.0]

def add_thesis(text: str) -> None:
    """Add thesis to vector store"""
    try:
        from vector_store import add_thesis as vs_add_thesis
        vs_add_thesis(text)
    except ImportError:
        print(f"Vector store not available, storing thesis in memory: {len(text)} characters")

def find_relevant_articles(articles_list: list) -> list:
    """Find relevant articles using vector store"""
    try:
        from vector_store import find_relevant_articles as vs_find_articles
        return vs_find_articles(articles_list)
    except ImportError:
        print("Vector store not available, returning first 3 articles")
        return articles_list[:3]

def parse_file(file_path: str) -> str:
    """Parse file content using file parser"""
    try:
        from file_parser import parse_file as fp_parse_file
        return fp_parse_file(file_path)
    except ImportError:
        print(f"File parser not available, reading as text: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return f"Error reading {file_path}"





app = FastAPI(title="FactorESourcing API", description="Content sourcing and matching API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://factoresourcing.onrender.com",  # Your frontend service URL
        "https://factoresourcingnew.onrender.com",  # Alternative frontend URL
        "http://localhost:5173",  # Local development
        "http://localhost:3000",  # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React frontend (for local development)
# In production, frontend will be served separately
frontend_path = Path(__file__).parent / "frontend"

print(f"🔍 Frontend path: {frontend_path}")
print(f"🔍 Frontend exists: {frontend_path.exists()}")

# Only mount static files if the directory exists (local development)
if frontend_path.exists() and (frontend_path / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    print(f"✅ Static files mounted from: {frontend_path / 'assets'} (local development)")
else:
    print(f"ℹ️  Static files not mounted - frontend will be served separately in production")

# Data models
class SourceRequest(BaseModel):
    url: str

class ScrapeRequest(BaseModel):
    url: str

class SourceResponse(BaseModel):
    url: str
    title: str
    summary: str
    keywords: List[str]
    companies: List[str]
    status: str

class MatchResponse(BaseModel):
    url: str
    title: str
    summary: str
    keywords: List[str]
    companies: List[str]
    relevance_score: float
    matched_thesis_points: List[str]
    match_reason: str
    detailed_scores: Optional[Dict[str, float]] = None

class BlogUploadRequest(BaseModel):
    url: str

class BlogUploadResponse(BaseModel):
    message: str
    total_articles: int
    processed_articles: int
    articles: List[Dict]

class BlogSearch(BaseModel):
    id: str
    url: str
    search_time: str
    total_articles_found: int
    processed_articles: int
    is_starred: bool = False
    last_monitored: str = None

class StarredBlog(BaseModel):
    id: str
    url: str
    search_time: str
    total_articles_found: int
    last_monitored: str
    monitoring_frequency: str = "daily"  # daily, weekly, monthly
    is_active: bool = True

class ScholarSearch(BaseModel):
    keyword: str
    max_results: int = 10

class ScholarResult(BaseModel):
    title: str
    authors: List[str]
    abstract: str
    url: str
    year: Optional[int]
    citations: Optional[int]
    source: str



# Global storage (in production, use a proper database)
articles = []
thesis_uploads = []  # Track thesis uploads for history
blog_searches = []  # Track blog search queries for starring
starred_blogs = []  # Track starred blogs for continuous monitoring

# Example API route
@app.get("/api/hello")
async def hello():
    """Example API endpoint"""
    return {"message": "Hello from FactorESourcing API!", "status": "healthy"}

@app.post("/api/sources", response_model=SourceResponse)
async def add_source(request: SourceRequest):
    """Add new content source"""
    try:
        print(f"🔍 Starting add_source for URL: {request.url}")
        # Use real scraping function
        print(f"📞 Calling real_scrape_url...")
        scraped_data = real_scrape_url(request.url)
        print(f"📊 Scraped data received: {scraped_data.keys() if isinstance(scraped_data, dict) else 'Not a dict'}")
        
        # Always process scraped data for content matching
        summary, keywords = summarize_text(scraped_data["text"])
        embedding = embed_text(summary)
        
        article = {
            "url": request.url,
            "title": scraped_data["title"],
            "summary": summary,
            "keywords": keywords,
            "companies": scraped_data["companies"],
            "embedding": embedding,
            "publish_date": scraped_data["publish_date"],
            "authors": scraped_data["authors"],
            "scraping_allowed": True,
            "warning": scraped_data.get("warning"),
            "upload_time": datetime.now().isoformat()
        }
        articles.append(article)
        
        return SourceResponse(
            url=request.url,
            title=scraped_data["title"],
            summary=summary,
            keywords=keywords,
            companies=scraped_data["companies"],
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing source: {str(e)}")

@app.post("/api/thesis/upload")
async def upload_thesis(file: UploadFile = File(...)):
    """Upload thesis file (PDF, Word, or text)"""
    try:
        # Create temporary file to parse
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Parse the file content
            text = parse_file(temp_file_path)
            if text is None:
                raise HTTPException(status_code=400, detail="Could not parse file content")
            
            print(f"✅ Successfully parsed {file.filename}")
            print(f"   File type: {os.path.splitext(file.filename)[1]}")
            print(f"   Text length: {len(text)} characters")
            print(f"   First 200 chars: {text[:200]}...")
            
            # Add thesis to vector store
            add_thesis(text)
            
            # Track thesis upload for history
            thesis_info = {
                "id": f"thesis_{len(thesis_uploads) + 1}",
                "filename": file.filename,
                "file_type": os.path.splitext(file.filename)[1],
                "content_length": len(text),
                "upload_time": datetime.now().isoformat(),
                "summary": f"Processed {len(text)} characters from {file.filename}"
            }
            thesis_uploads.append(thesis_info)
            print(f"📝 Thesis tracked for history: {thesis_info}")
            
            # Trigger immediate content matching analysis
            print("🔄 Triggering content matching analysis...")
            matches = find_relevant_articles(articles)
            print(f"   Found {len(matches)} potential matches")
            
            return {
                "message": "Thesis uploaded successfully and content matching completed", 
                "filename": file.filename,
                "content_length": len(text),
                "file_type": os.path.splitext(file.filename)[1],
                "thesis_processed": True,
                "matches_found": len(matches),
                "thesis_summary": f"Processed {len(text)} characters from {file.filename}"
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error uploading thesis: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading thesis: {str(e)}")

@app.post("/api/blog/upload", response_model=BlogUploadResponse)
async def upload_blog(request: BlogUploadRequest):
    """Upload blog/website and discover articles"""
    try:
        print(f"Starting blog upload for: {request.url}")
        
        # Discover articles from the blog
        from scraper import discover_articles_from_blog
        article_urls = await discover_articles_from_blog(request.url)
        print(f"Discovered {len(article_urls)} articles")
        
        # Check if this is a patent site that needs special handling
        from scraper import is_patent_site
        
        if is_patent_site(request.url) and len(article_urls) <= 1:
            return BlogUploadResponse(
                message="Patent site detected. For Google Patents and similar sites, please provide individual patent URLs instead of search result pages, as these use JavaScript to load content dynamically.",
                total_articles=0,
                processed_articles=0,
                articles=[],
                status="patent_site_js",
                suggestion="Try uploading individual patent URLs like: https://patents.google.com/patent/US12345678"
            )
        
        if not article_urls:
            return BlogUploadResponse(
                message="No articles found on the blog/website",
                total_articles=0,
                processed_articles=0,
                articles=[]
            )
        
        processed_articles = []
        total_articles = len(article_urls)
        
        # Process each article
        for i, article_url in enumerate(article_urls):
            try:
                print(f"Processing article {i+1}/{total_articles}: {article_url}")
                
                # Scrape the article with unique processing
                scraped_data = real_scrape_url(article_url)
                
                # Ensure we have unique content for each article
                if not scraped_data.get("text") or len(scraped_data["text"]) < 100:
                    print(f"   ⚠️  Article {i+1} has insufficient content, skipping")
                    processed_articles.append({
                        "url": article_url,
                        "title": f"Insufficient content for {article_url}",
                        "summary": "Content too short or empty",
                        "keywords": [],
                        "companies": [],
                        "status": "insufficient_content"
                    })
                    continue
                
                # Generate unique summary and keywords for each article
                summary, keywords = summarize_text(scraped_data["text"])
                embedding = embed_text(summary)
                
                # Extract companies from the specific article content
                companies = scraped_data.get("companies", [])
                if not companies:
                    # Fallback to keyword-based company extraction
                    companies = extract_companies_from_text(scraped_data.get("text", ""))
                
                # Create article object with unique content
                article = {
                    "url": article_url,
                    "title": scraped_data["title"] or f"Article {i+1} from {request.url}",
                    "summary": summary,
                    "keywords": keywords,
                    "companies": companies,
                    "embedding": embedding,
                    "publish_date": scraped_data["publish_date"] or datetime.now().isoformat(),
                    "authors": scraped_data["authors"] or ["Unknown Author"],
                    "source_blog": request.url,  # Track which blog this came from
                    "article_index": i + 1  # Track position in blog
                }
                
                # Add to global articles list
                articles.append(article)
                
                # Add to processed articles for response
                processed_articles.append({
                    "url": article_url,
                    "title": article["title"],
                    "summary": summary,
                    "keywords": keywords,
                    "companies": companies,
                    "status": "success",
                    "article_index": i + 1
                })
                
                print(f"   ✅ Successfully processed: {article['title']}")
                print(f"   📝 Summary length: {len(summary)} chars")
                print(f"   🏢 Companies found: {companies}")
                
            except Exception as e:
                print(f"   ❌ Error processing article {article_url}: {e}")
                import traceback
                traceback.print_exc()
                # Add error info to processed articles
                processed_articles.append({
                    "url": article_url,
                    "title": f"Error processing {article_url}",
                    "summary": "",
                    "keywords": [],
                    "companies": [],
                    "status": "error",
                    "error": str(e)
                })
        
        successful_count = len([a for a in processed_articles if a['status'] == 'success'])
        print(f"Blog upload completed: {successful_count}/{total_articles} articles processed successfully")
        
        # Track this blog search for history and starring
        blog_search = {
            "id": f"blog_{len(blog_searches)}_{int(time.time())}",
            "url": request.url,
            "search_time": datetime.now().isoformat(),
            "total_articles_found": total_articles,
            "processed_articles": successful_count,
            "is_starred": False,
            "last_monitored": datetime.now().isoformat()
        }
        blog_searches.append(blog_search)
        print(f"📝 Blog search tracked for history: {blog_search['id']}")
        print(f"📊 Current blog_searches count: {len(blog_searches)}")
        print(f"📊 Current articles count: {len(articles)}")
        
        # Verify the blog search was added
        if blog_search in blog_searches:
            print(f"✅ Blog search successfully added to tracking")
        else:
            print(f"❌ Blog search was NOT added to tracking!")
        
        return BlogUploadResponse(
            message=f"Successfully processed {successful_count} out of {total_articles} articles",
            total_articles=total_articles,
            processed_articles=successful_count,
            articles=processed_articles
        )
        
    except Exception as e:
        print(f"Blog upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing blog: {str(e)}")

@app.post("/api/thesis/text")
async def add_thesis_text(request: dict):
    """Add thesis text directly (for copy-paste)"""
    try:
        text = request.get("text", "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Thesis text cannot be empty")
        
        print(f"✅ Adding thesis text input")
        print(f"   Text length: {len(text)} characters")
        print(f"   First 200 chars: {text[:200]}...")
        
        # Add thesis to vector store
        add_thesis(text)
        
        # Track thesis upload for history
        thesis_info = {
            "id": f"thesis_text_{len(thesis_uploads) + 1}",
            "filename": "Text Input",
            "file_type": ".txt",
            "content_length": len(text),
            "upload_time": datetime.now().isoformat(),
            "summary": f"Processed {len(text)} characters from text input"
        }
        thesis_uploads.append(thesis_info)
        print(f"📝 Thesis text tracked for history: {thesis_info}")
        
        # Trigger immediate content matching analysis
        print("🔄 Triggering content matching analysis...")
        matches = find_relevant_articles(articles)
        print(f"   Found {len(matches)} potential matches")
        
        return {
            "message": "Thesis text added successfully and content matching completed",
            "content_length": len(text),
            "thesis_processed": True,
            "matches_found": len(matches)
        }
        
    except Exception as e:
        print(f"❌ Error adding thesis text: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing thesis text: {str(e)}")

@app.get("/api/matches", response_model=List[MatchResponse])
async def get_matches():
    """Get matched content"""
    try:
        matches = find_relevant_articles(articles)
        return [
            MatchResponse(
                url=match["url"],
                title=match.get("title", f"Content from {match['url']}"),
                summary=match["summary"],
                keywords=match["keywords"],
                companies=match.get("companies", []),
                relevance_score=match.get("relevance_score", 0.0),
                matched_thesis_points=match.get("matched_thesis_points", []),
                match_reason=match.get("match_reason", "No reason provided"),
                detailed_scores=match.get("detailed_scores", {})
            )
            for match in matches
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving matches: {str(e)}")

@app.post("/api/sources/star/{source_id}")
async def star_source(source_id: str):
    """Star/unstar an individual source"""
    try:
        # Find the source by ID
        source_index = int(source_id.replace("source_", ""))
        if source_index < 0 or source_index >= len(articles):
            raise HTTPException(status_code=404, detail="Source not found")
        
        article = articles[source_index]
        
        # Toggle star status
        article["is_starred"] = not article.get("is_starred", False)
        
        if article["is_starred"]:
            print(f"⭐ Source starred: {article['url']}")
        else:
            print(f"⭐ Source unstarred: {article['url']}")
        
        return {
            "message": f"Source {'starred' if article['is_starred'] else 'unstarred'} successfully",
            "source_id": source_id,
            "is_starred": article["is_starred"],
            "url": article["url"]
        }
        
    except (ValueError, IndexError):
        raise HTTPException(status_code=404, detail="Invalid source ID")
    except Exception as e:
        print(f"Error starring source: {e}")
        raise HTTPException(status_code=500, detail=f"Error starring source: {str(e)}")

@app.post("/api/blogs/star/{blog_id}")
async def star_blog(blog_id: str):
    """Star a blog for continuous monitoring"""
    try:
        # Find the blog search
        blog_search = next((blog for blog in blog_searches if blog['id'] == blog_id), None)
        if not blog_search:
            raise HTTPException(status_code=404, detail="Blog search not found")
        
        # Toggle star status
        blog_search['is_starred'] = not blog_search.get('is_starred', False)
        
        if blog_search['is_starred']:
            # Add to starred blogs
            starred_blog = {
                "id": blog_search['id'],
                "url": blog_search['url'],
                "search_time": blog_search['search_time'],
                "total_articles_found": blog_search['total_articles_found'],
                "last_monitored": blog_search['last_monitored'],
                "monitoring_frequency": "daily",
                "is_active": True
            }
            
            # Check if already in starred list
            existing_starred = next((blog for blog in starred_blogs if blog['id'] == blog_id), None)
            if not existing_starred:
                starred_blogs.append(starred_blog)
                print(f"⭐ Blog starred: {blog_search['url']}")
            else:
                existing_starred['is_active'] = True
                print(f"⭐ Blog re-activated: {blog_search['url']}")
        else:
            # Remove from starred blogs
            starred_blogs[:] = [blog for blog in starred_blogs if blog['id'] != blog_id]
            print(f"⭐ Blog unstarred: {blog_search['url']}")
        
        return {
            "message": f"Blog {'starred' if blog_search['is_starred'] else 'unstarred'} successfully",
            "blog_id": blog_id,
            "is_starred": blog_search['is_starred']
        }
        
    except Exception as e:
        print(f"Error starring blog: {e}")
        raise HTTPException(status_code=500, detail=f"Error starring blog: {str(e)}")

@app.get("/api/sources/starred")
async def get_starred_sources():
    """Get all starred sources"""
    starred_sources = [article for article in articles if article.get("is_starred", False)]
    return {
        "starred_sources": starred_sources,
        "total_starred": len(starred_sources)
    }

@app.get("/api/blogs/starred")
async def get_starred_blogs():
    """Get all starred blogs"""
    return {
        "starred_blogs": starred_blogs,
        "total_starred": len(starred_blogs)
    }

@app.post("/api/blogs/monitor")
async def monitor_starred_blogs():
    """Monitor all starred blogs for new articles"""
    try:
        from datetime import datetime, timedelta
        
        monitored_results = []
        total_new_articles = 0
        
        for starred_blog in starred_blogs:
            if not starred_blog['is_active']:
                continue
                
            print(f"🔍 Monitoring starred blog: {starred_blog['url']}")
            
            try:
                # Check for new articles
                article_urls = await discover_articles_from_blog(starred_blog['url'])
                
                # Find new articles (not already in our database)
                existing_urls = {article['url'] for article in articles}
                new_urls = [url for url in article_urls if url not in existing_urls]
                
                if new_urls:
                    print(f"   📰 Found {len(new_urls)} new articles")
                    
                    # Process new articles
                    for article_url in new_urls[:10]:  # Limit to 10 new articles per blog
                        try:
                            scraped_data = real_scrape_url(article_url)
                            summary, keywords = summarize_text(scraped_data["text"])
                            embedding = embed_text(summary)
                            
                            article = {
                                "url": article_url,
                                "title": scraped_data["title"],
                                "summary": summary,
                                "keywords": keywords,
                                "companies": scraped_data["companies"],
                                "embedding": embedding,
                                "publish_date": scraped_data["publish_date"],
                                "authors": scraped_data["authors"],
                                "source_blog": starred_blog['url']
                            }
                            
                            articles.append(article)
                            total_new_articles += 1
                            
                        except Exception as e:
                            print(f"   ❌ Error processing new article {article_url}: {e}")
                    
                    monitored_results.append({
                        "blog_url": starred_blog['url'],
                        "new_articles_found": len(new_urls),
                        "new_articles_processed": len([url for url in new_urls if url in [a['url'] for a in articles]]),
                        "status": "success"
                    })
                else:
                    monitored_results.append({
                        "blog_url": starred_blog['url'],
                        "new_articles_found": 0,
                        "new_articles_processed": 0,
                        "status": "no_new_articles"
                    })
                
                # Update last monitored time
                starred_blog['last_monitored'] = datetime.now().isoformat()
                
            except Exception as e:
                print(f"   ❌ Error monitoring blog {starred_blog['url']}: {e}")
                monitored_results.append({
                    "blog_url": starred_blog['url'],
                    "new_articles_found": 0,
                    "new_articles_processed": 0,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "message": f"Monitoring completed. Found {total_new_articles} new articles",
            "monitored_blogs": len(starred_blogs),
            "total_new_articles": total_new_articles,
            "results": monitored_results
        }
        
    except Exception as e:
        print(f"Error monitoring starred blogs: {e}")
        raise HTTPException(status_code=500, detail=f"Error monitoring starred blogs: {str(e)}")

@app.get("/api/matches/starred")
async def get_matches_starred_only():
    """Get matches only from starred blogs"""
    try:
        # Get URLs from starred blogs
        starred_urls = {blog['url'] for blog in starred_blogs}
        
        # Filter articles to only those from starred blogs
        starred_articles = [
            article for article in articles 
            if article.get('source_blog') in starred_urls or 
               any(blog['url'] in article['url'] for blog in starred_blogs)
        ]
        
        if not starred_articles:
            return {
                "message": "No articles from starred blogs found",
                "matches": [],
                "total_articles": 0
            }
        
        # Run matching on starred articles only
        matches = find_relevant_articles(starred_articles)
        
        return {
            "message": f"Found {len(matches)} matches from starred blogs",
            "matches": matches,
            "total_articles": len(starred_articles),
            "starred_blogs_count": len(starred_blogs)
        }
        
    except Exception as e:
        print(f"Error getting starred matches: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting starred matches: {str(e)}")

@app.post("/api/scholar/search")
async def search_scholar(request: ScholarSearch):
    """Search Google Scholar for academic papers"""
    try:
        print(f"🔍 Searching Google Scholar for: {request.keyword}")
        
        # Use the existing scraper to search Google Scholar
        from scraper import search_google_scholar
        
        results = await search_google_scholar(request.keyword, request.max_results)
        
        if not results:
            return {
                "message": f"No results found for '{request.keyword}'",
                "results": [],
                "total_found": 0
            }
        
        # Process each result
        processed_results = []
        for result in results:
            try:
                # Generate summary and keywords
                summary, keywords = summarize_text(result.get("abstract", ""))
                embedding = embed_text(summary)
                
                # Extract companies/organizations
                companies = extract_companies(result.get("abstract", ""))
                
                # Create article object
                article = {
                    "url": result["url"],
                    "title": result["title"],
                    "summary": summary,
                    "keywords": keywords,
                    "companies": companies,
                    "embedding": embedding,
                    "publish_date": str(result.get("year", "Unknown")),
                    "authors": result.get("authors", ["Unknown Author"]),
                    "source": "Google Scholar",
                    "citations": result.get("citations", 0),
                    "abstract": result.get("abstract", "")
                }
                
                # Add to global articles list
                articles.append(article)
                processed_results.append(article)
                
                print(f"   ✅ Processed: {result['title']}")
                
            except Exception as e:
                print(f"   ❌ Error processing result: {e}")
                continue
        
        print(f"Scholar search completed: {len(processed_results)} results processed")
        
        return {
            "message": f"Found {len(processed_results)} results for '{request.keyword}'",
            "results": processed_results,
            "total_found": len(processed_results),
            "keyword": request.keyword
        }
        
    except Exception as e:
        print(f"Error searching Google Scholar: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching Google Scholar: {str(e)}")

@app.post("/api/patents/search")
async def search_patents(request: ScholarSearch):
    """Search Google Patents for patent documents"""
    try:
        print(f"🔍 Searching Google Patents for: {request.keyword}")
        
        # Use the existing scraper to search Google Patents
        from scraper import search_google_patents
        
        results = await search_google_patents(request.keyword, request.max_results)
        
        if not results:
            return {
                "message": f"No patents found for '{request.keyword}'",
                "results": [],
                "total_found": 0
            }
        
        # Process each patent
        processed_results = []
        for result in results:
            try:
                # Generate summary and keywords
                summary, keywords = summarize_text(result.get("abstract", ""))
                embedding = embed_text(summary)
                
                # Extract companies/organizations
                companies = extract_companies(result.get("abstract", ""))
                
                # Create article object
                article = {
                    "url": result["url"],
                    "title": result["title"],
                    "summary": summary,
                    "keywords": keywords,
                    "companies": companies,
                    "embedding": embedding,
                    "publish_date": str(result.get("year", "Unknown")),
                    "authors": result.get("inventors", ["Unknown Inventor"]),
                    "source": "Google Patents",
                    "patent_number": result.get("patent_number", ""),
                    "abstract": result.get("abstract", "")
                }
                
                # Add to global articles list
                articles.append(article)
                processed_results.append(article)
                
                print(f"   ✅ Processed patent: {result['title']}")
                
            except Exception as e:
                print(f"   ❌ Error processing patent: {e}")
                continue
        
        print(f"Patent search completed: {len(processed_results)} patents processed")
        
        return {
            "message": f"Found {len(processed_results)} patents for '{request.keyword}'",
            "results": processed_results,
            "total_found": len(processed_results),
            "keyword": request.keyword
        }
        
    except Exception as e:
        print(f"Error searching Google Patents: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching Google Patents: {str(e)}")

@app.post("/api/scrape")
async def trigger_scraping(request: ScrapeRequest):
    """Trigger content scraping"""
    try:
        scraped_data = real_scrape_url(request.url)
        summary, keywords = summarize_text(scraped_data["text"])
        
        return {
            "url": request.url,
            "title": scraped_data["title"],
            "companies": scraped_data["companies"],
            "scraped_text_length": len(scraped_data["text"]),
            "summary": summary,
            "keywords": keywords,
            "status": "scraped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping content: {str(e)}")



@app.get("/api/")
async def api_root():
    """API root endpoint with API information"""
    return {
        "message": "FactorESourcing API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/sources": "Add new content source",
            "POST /api/thesis/upload": "Upload thesis file",
            "GET /api/matches": "Get matched content",
            "POST /api/scrape": "Trigger content scraping",
            "GET /api/docs": "API documentation"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "articles_count": len(articles)}

@app.get("/api/")
async def api_info():
    """API information endpoint"""
    return {
        "message": "FactorESourcing API",
        "status": "Backend service running",
        "version": "1.0.0",
        "api_endpoints": {
            "GET /api/": "API information",
            "GET /api/health": "Health check",
            "GET /api/docs": "API documentation",
            "POST /api/sources": "Add content source",
            "POST /api/thesis/upload": "Upload thesis",
            "GET /api/matches": "Get content matches"
        },
        "documentation": "/api/docs"
    }

@app.get("/api/history")
async def get_history():
    """Get simplified history focused on sources"""
    print(f"📚 History requested - Current state:")
    print(f"   Articles: {len(articles)}")
    print(f"   Thesis uploads: {len(thesis_uploads)}")
    
    history_items = []
    
    # Add sources (individual articles) - this is what you want to see
    for i, article in enumerate(articles):
        print(f"   📰 Processing article {i+1}: {article.get('url', 'No URL')}")
        
        # Check if this source is starred
        is_starred = article.get("is_starred", False)
        
        history_items.append({
            "id": f"source_{i}",
            "type": "source",
            "url": article["url"],
            "title": article.get("title", f"Content from {article['url']}"),
            "summary": article.get("summary", ""),
            "keywords": article.get("keywords", []),
            "companies": article.get("companies", []),
            "timestamp": article.get("publish_date", article.get("upload_time", datetime.now().isoformat())),
            "is_starred": is_starred,
            "source_type": "individual_source"
        })
    
    # Add thesis uploads (for reference)
    for thesis in thesis_uploads:
        history_items.append({
            "id": thesis["id"],
            "type": "thesis",
            "title": f"Thesis: {thesis['filename'] or 'Text Input'}",
            "content_length": thesis["content_length"],
            "timestamp": thesis["upload_time"],
            "is_starred": False,  # Thesis can't be starred
            "source_type": "thesis"
        })
    
    # Sort by timestamp (newest first)
    history_items.sort(key=lambda x: x["timestamp"], reverse=True)
    
    print(f"📚 Returning {len(history_items)} history items")
    return history_items

@app.get("/api/history/sources")
async def get_sources_history():
    """Get sources history"""
    history_items = []
    for article in articles:
        # Always show the actual publish date when available, fallback to upload time
        timestamp = article.get("publish_date", article.get("upload_time", datetime.now().isoformat()))
        
        # Create history item with enhanced details
        history_item = {
            "id": f"source_{len(history_items)}",
            "type": "source",
            "content": article["url"],
            "timestamp": timestamp,
            "details": {
                "title": article.get("title", f"Content from {article['url']}"),
                "summary": article.get("summary", ""),
                "keywords": article.get("keywords", []),
                "companies": article.get("companies", []),
                "source": article["url"],
                "warning": article.get("warning"),
                "authors": article.get("authors", []),
                "upload_time": article.get("upload_time", timestamp)
            }
        }
        
        # Always show success status since scraping is always attempted
        history_item["status"] = "success"
        
        history_items.append(history_item)
    
    return history_items

@app.get("/api/history/thesis")
async def get_thesis_history():
    """Get thesis history"""
    history_items = []
    for thesis in thesis_uploads:
        history_items.append({
            "id": thesis["id"],
            "type": "thesis",
            "content": thesis["filename"] or "Thesis Text",
            "timestamp": thesis["upload_time"],
            "details": {
                "title": f"Thesis: {thesis['filename'] or 'Text Input'}",
                "content_length": thesis["content_length"],
                "file_type": thesis["file_type"],
                "preview": thesis["summary"]
            }
        })
    
    print(f"📚 Returning {len(history_items)} thesis items from history")
    return history_items

@app.get("/api/debug/state")
async def debug_state():
    """Debug endpoint to check current state"""
    return {
        "blog_searches_count": len(blog_searches),
        "starred_blogs_count": len(starred_blogs),
        "articles_count": len(articles),
        "thesis_uploads_count": len(thesis_uploads),
        "blog_searches": blog_searches,
        "starred_blogs": starred_blogs,
        "articles_urls": [article.get('url', 'No URL') for article in articles[:5]],  # First 5
        "thesis_uploads": thesis_uploads
    }

@app.get("/api/test/history")
async def test_history():
    """Test endpoint to return sample history data"""
    return [
        {
            "id": "test_1",
            "type": "source",
            "content": "https://example.com/test-article",
            "timestamp": "2024-01-28T10:00:00Z",
            "details": {
                "title": "Test Article",
                "summary": "This is a test article for debugging the history functionality.",
                "keywords": ["test", "debug", "history"],
                "companies": ["Test Company Inc"],
                "source": "https://example.com/test-article"
            }
        }
    ]

@app.post("/api/test/populate")
async def populate_test_data():
    """Populate test data for debugging"""
    global articles, thesis_uploads
    
    # Add a test article
    test_article = {
        "url": "https://example.com/test-article",
        "title": "Test Article for Debugging",
        "summary": "This is a test article to help debug the history functionality.",
        "keywords": ["test", "debug", "history", "content"],
        "companies": ["Test Company Inc", "Debug Corp"],
        "embedding": [0.1, 0.2, 0.3],
        "publish_date": datetime.now().isoformat(),
        "authors": ["Test Author"],
        "scraping_allowed": True,
        "warning": None,
        "upload_time": datetime.now().isoformat()
    }
    articles.append(test_article)
    
    # Add a test thesis
    test_thesis = {
        "id": "thesis_test_1",
        "filename": "test-thesis.txt",
        "file_type": ".txt",
        "content_length": 500,
        "upload_time": datetime.now().isoformat(),
        "summary": "Test thesis for debugging history functionality"
    }
    thesis_uploads.append(test_thesis)
    
    print(f"🧪 Test data populated: {len(articles)} articles, {len(thesis_uploads)} thesis uploads")
    
    return {
        "message": "Test data populated successfully",
        "articles_count": len(articles),
        "thesis_count": len(thesis_uploads)
    }

# Serve frontend static files
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page"""
    return FileResponse("frontend/index.html")

@app.get("/assets/{file_path:path}")
async def serve_assets(file_path: str):
    """Serve frontend assets (CSS, JS, images)"""
    asset_path = f"frontend/assets/{file_path}"
    if os.path.exists(asset_path):
        return FileResponse(asset_path)
    else:
        raise HTTPException(status_code=404, detail="Asset not found")

# Catch-all route for frontend routes (SPA routing)
@app.get("/{full_path:path}")
async def catch_all_routes(full_path: str):
    """Catch-all route for frontend SPA routing"""
    # Don't serve frontend for API routes
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # For all other routes, serve the frontend (SPA routing)
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FactorESourcing API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
