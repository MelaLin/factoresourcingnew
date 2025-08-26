# Try to import newspaper, fallback to basic scraping if it fails
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
    print("✅ Newspaper3k available for advanced scraping")
except ImportError as e:
    NEWSPAPER_AVAILABLE = False
    print(f"⚠️  Newspaper3k not available, using basic scraping: {e}")

import re
import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Tuple, Any
from ai_utils import generate_title_from_url, extract_companies_from_url, extract_companies
from datetime import datetime

def extract_company_names(text: str) -> List[str]:
    """Extract potential company names from text"""
    # Common company suffixes
    suffixes = r'\b(Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Industries|International|Intl|Group|Partners|Ventures|Capital|Fund|Energy|Solar|Wind|Battery|Storage|Carbon|Climate|Green|Sustainable|Renewable)\b'
    
    # Look for patterns like "Company Name Inc" or "Company Name Technologies"
    company_pattern = r'\b[A-Z][a-zA-Z\s&]+' + suffixes
    companies = re.findall(company_pattern, text, re.IGNORECASE)
    
    # Clean up and filter
    cleaned_companies = []
    for company in companies:
        company = company.strip()
        if len(company) > 3 and len(company) < 50:  # Reasonable company name length
            cleaned_companies.append(company)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_companies = []
    for company in cleaned_companies:
        if company.lower() not in seen:
            seen.add(company.lower())
            unique_companies.append(company)
    
    return unique_companies[:5]  # Return top 5 companies

def scrape_url(url: str) -> Dict[str, Any]:
    """Scrape URL and return structured content"""
    try:
        print(f"🌐 Scraping: {url}")
        
        # Enhanced headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Create SSL context that's more permissive
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Try to fetch with enhanced headers first
        try:
            import asyncio
            import time
            
            async def _fetch_with_headers():
                # Try multiple times with different approaches
                for attempt in range(3):
                    try:
                        if attempt > 0:
                            print(f"   🔄 Retry attempt {attempt + 1}/3...")
                            await asyncio.sleep(2)  # Wait 2 seconds between attempts
                        
                        async with aiohttp.ClientSession(
                            headers=headers, 
                            timeout=timeout,
                            connector=aiohttp.TCPConnector(ssl=ssl_context)
                        ) as session:
                            async with session.get(url) as response:
                                if response.status == 200:
                                    return await response.text()
                                elif response.status == 403:
                                    print(f"   🚫 403 Forbidden on attempt {attempt + 1}")
                                    if attempt == 2:  # Last attempt
                                        # Try with different user agent
                                        headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                                        continue
                                else:
                                    print(f"   ❌ HTTP {response.status} on attempt {attempt + 1}")
                    except Exception as e:
                        print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
                        if attempt == 2:
                            raise e
                return None
            
            html = asyncio.run(_fetch_with_headers())
            if html:
                print(f"✅ Successfully fetched content with enhanced headers ({len(html)} characters)")
                
                # Parse HTML with BeautifulSoup instead of newspaper
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else generate_title_from_url(url)
                
                # Extract main content
                content_selectors = [
                    'article', 'main', '.content', '.post-content', '.entry-content', 
                    '.article-content', '.story-content', '.post-body', '.entry-body',
                    '.post', '.story', '.article', '.entry', '.content-area',
                    '[role="main"]', '.main-content', '.story-body', '.article-body'
                ]
                
                main_content = None
                for selector in content_selectors:
                    main_content = soup.select_one(selector)
                    if main_content:
                        break
                
                if not main_content:
                    main_content = soup.find('body')
                
                if main_content:
                    # Clean and extract text
                    for tag in main_content(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        tag.decompose()
                    
                    text_content = main_content.get_text(separator='\n', strip=True)
                    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
                    text_content = re.sub(r'\s+', ' ', text_content)
                else:
                    text_content = f"Content from {url}"
                
                # Extract companies from text
                companies = extract_companies(text_content)
                
                # Get publish date
                publish_date = "Unknown"
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
                            publish_date = date_elem.get('datetime') or date_elem.get('text')
                        break
                
                # Get authors
                authors = ["Unknown Author"]
                author_selectors = [
                    '.author', '.byline', '.post-author', '.entry-author', 
                    '.article-author', '.story-author', 'meta[name="author"]'
                ]
                
                for selector in author_selectors:
                    author_elem = soup.select_one(selector)
                    if author_elem:
                        if selector == 'meta[name="author"]':
                            authors = [author_elem.get('content')]
                        else:
                            authors = [author_elem.get_text().strip()]
                        break
                
                return {
                    "text": text_content,
                    "title": title,
                    "companies": companies,
                    "url": url,
                    "publish_date": publish_date,
                    "authors": authors,
                    "top_image": None
                }
            else:
                print(f"⚠️  Enhanced headers failed, using fallback")
                return {
                    "text": f"Content from {url}",
                    "url": url,
                    "title": generate_title_from_url(url),
                    "companies": extract_companies_from_url(url),
                    "publish_date": "Unknown",
                    "authors": ["Unknown Author"],
                    "top_image": None
                }
        except Exception as e:
            print(f"⚠️  Enhanced headers failed: {e}, using fallback")
            return {
                "text": f"Content from {url}",
                "url": url,
                "title": generate_title_from_url(url),
                "companies": extract_companies_from_url(url),
                "publish_date": "Unknown",
                "authors": ["Unknown Author"],
                "top_image": None
            }
        
        # The function now returns data from the BeautifulSoup parsing above
        # This section is no longer needed
        pass
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        # Return fallback data with generated content
        return {
            "text": f"Content from {url}",
            "url": url,
            "title": generate_title_from_url(url),
            "companies": extract_companies_from_url(url),
            "publish_date": "Unknown",
            "authors": ["Unknown Author"],
            "top_image": None
        }

def scrape_url_legacy(url: str) -> str:
    """Legacy function for backward compatibility"""
    result = scrape_url(url)
    return result["text"]

async def discover_articles_from_blog(blog_url: str) -> List[str]:
    """Discover articles from a blog/website or patent site"""
    try:
        print(f"🔍 Discovering content from: {blog_url}")
        
        # Check if this is a patent site
        if is_patent_site(blog_url):
            print(f"🔬 Detected patent site, using patent-specific extraction")
            max_articles = 50  # Allow more patents to be discovered
            
            # Create SSL context that ignores certificate verification for development
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(blog_url) as response:
                    if response.status != 200:
                        print(f"❌ Failed to fetch patent site: {response.status}")
                        return []
                    
                    html = await response.text()
                    print(f"✅ Successfully fetched patent site content ({len(html)} characters)")
                    
                    # Extract patent links
                    patent_links = extract_patent_links(html, blog_url)
                    print(f"🔬 Total patents discovered: {len(patent_links)}")
                    
                    return patent_links[:max_articles]
        
        # Regular blog/news site discovery
        print(f"📰 Processing as regular blog/news site")
        
        # Create SSL context that ignores certificate verification for development
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(blog_url) as response:
                if response.status != 200:
                    print(f"❌ Failed to fetch {blog_url}: {response.status}")
                    return []
                
                html = await response.text()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Enhanced article link patterns for modern blogs
        article_patterns = [
            # TechCrunch specific patterns (enhanced)
            'h3 a[href]',  # TechCrunch uses h3 for article titles
            'h2 a[href]',  # Common for article titles
            'h1 a[href]',  # Main headlines
            '.headline a[href]',
            '.title a[href]',
            '.post-title a[href]',
            '.entry-title a[href]',
            '.story-title a[href]',
            '.article-title a[href]',
            '.news-title a[href]',
            '.blog-title a[href]',
            # TechCrunch specific selectors
            'a[href*="/2025/"]',  # TechCrunch year-based URLs
            'a[href*="/2024/"]',
            'a[href*="/2023/"]',
            'a[href*="/tag/"]',   # Tag pages
            'a[href*="/author/"]', # Author pages
            # Generic article selectors
            'article a[href]',
            '.post a[href]',
            '.article a[href]',
            '.entry a[href]',
            '.content a[href]',
            '.story a[href]',
            '.news a[href]',
            '.blog-post a[href]',
            # RMI.org specific patterns
            '.research-item a[href]', '.insight-item a[href]', '.report-item a[href]',
            '.content-item a[href]', '.publication a[href]', '.analysis a[href]',
            '.article-item a[href]', '.post-item a[href]', '.story-item a[href]',
            # Link patterns
            'a[href*="/article/"]',
            'a[href*="/post/"]',
            'a[href*="/news/"]',
            'a[href*="/story/"]',
            'a[href*="/blog/"]',
            # RMI.org and research organization specific patterns
            'a[href*="/research/"]', 'a[href*="/insights/"]', 'a[href*="/reports/"]',
            'a[href*="/analysis/"]', 'a[href*="/publications/"]', 'a[href*="/articles/"]',
            # Year-based URLs
            'a[href*="/202"]', 'a[href*="/2023"]', 'a[href*="/2024"]', 'a[href*="/2025"]',
        ]
        
        article_urls = set()
        base_url = blog_url
        
        print(f"🔍 Searching for articles using {len(article_patterns)} patterns...")
        
        for pattern in article_patterns:
            links = soup.select(pattern)
            print(f"   Pattern '{pattern}': Found {len(links)} links")
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    
                    # Filter for likely article URLs
                    if is_likely_article_url(full_url, base_url):
                        article_urls.add(full_url)
                        print(f"     ✅ Added: {full_url}")
                    else:
                        print(f"     ❌ Filtered out: {full_url}")
        
        # If no articles found with specific patterns, try broader approach
        if not article_urls:
            print("⚠️  No articles found with specific patterns, trying broader approach...")
            all_links = soup.find_all('a', href=True)
            print(f"   Found {len(all_links)} total links")
            
            for link in all_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if is_likely_article_url(full_url, base_url):
                        article_urls.add(full_url)
                        print(f"     ✅ Added: {full_url}")
                    else:
                        print(f"     ❌ Filtered out: {full_url}")
        
        # Special handling for RMI.org
        if 'rmi.org' in blog_url and not article_urls:
            print("\n🔍 RMI.org detected - this site has strict anti-scraping measures")
            print("   💡 Alternative approaches:")
            print("   1. Use individual article URLs directly")
            print("   2. Try RSS feeds if available")
            print("   3. Consider using their API if they have one")
            print("   4. Manual article submission")
            
            # Try to find any links that might be articles
            print("\n   🔍 Attempting to find any available links...")
            all_links = soup.find_all('a', href=True)
            potential_articles = []
            
            for link in all_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    # Be more lenient with RMI.org
                    if len(full_url.split('/')) > 3 and not any(skip in full_url.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                        potential_articles.append(full_url)
            
            if potential_articles:
                print(f"   📰 Found {len(potential_articles)} potential article links")
                article_urls.update(potential_articles[:20])  # Limit to 20
            else:
                print("   ❌ No potential articles found")
        
        # Limit to reasonable number of articles but allow more for category pages
        max_articles = 50 if '/category/' in blog_url else 20
        final_urls = list(article_urls)[:max_articles]
        
        print(f"🎯 Total articles discovered: {len(final_urls)}")
        for i, url in enumerate(final_urls[:5]):  # Show first 5
            print(f"   {i+1}. {url}")
        if len(final_urls) > 5:
            print(f"   ... and {len(final_urls) - 5} more")
        
        return final_urls
        
    except Exception as e:
        print(f"❌ Error discovering articles from {blog_url}: {e}")
        import traceback
        traceback.print_exc()
        return []

def is_likely_article_url(url: str, base_url: str) -> bool:
    """Check if URL is likely an article URL"""
    try:
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # Must be from same domain
        if parsed_url.netloc != parsed_base.netloc:
            return False
        
        # Skip common non-article paths
        skip_paths = [
            '/tag/', '/category/', '/author/', '/page/', '/search',
            '/about', '/contact', '/privacy', '/terms', '/login',
            '/register', '/subscribe', '/newsletter', '/feed',
            '/rss', '/sitemap', '/robots.txt', '/favicon.ico',
            '/wp-admin', '/wp-content', '/wp-includes', '/wp-json'
        ]
        
        path = parsed_url.path.lower()
        for skip_path in skip_paths:
            if skip_path in path:
                return False
        
        # Must have some content in path (not just domain)
        if len(parsed_url.path.strip('/')) < 2:  # Reduced from 3 to 2
            return False
        
        # Skip URLs with file extensions (images, etc.)
        if '.' in parsed_url.path.split('/')[-1]:
            ext = parsed_url.path.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'css', 'js', 'xml']:
                return False
        
        # For TechCrunch specifically, look for article patterns
        if 'techcrunch.com' in parsed_url.netloc:
            # TechCrunch articles typically have year/month in path
            if re.search(r'/\d{4}/\d{2}/', path):
                return True
            # Or have article-like paths
            if re.search(r'/(article|post|news|story)/', path):
                return True
        
        # For RMI.org specifically, look for research patterns
        if 'rmi.org' in parsed_url.netloc:
            # RMI research articles typically have research/insights/reports in path
            if re.search(r'/(research|insights|reports|analysis|publications)/', path):
                return True
            # Or have year-based paths
            if re.search(r'/\d{4}/', path):
                return True
        
        # Allow URLs that look like articles
        if re.search(r'/(\d{4}|\d{3})', path):  # Contains year
            return True
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking URL {url}: {e}")
        return False

def is_patent_site(url: str) -> bool:
    """Check if the URL is a patent-related site"""
    patent_domains = [
        'patents.google.com',
        'patentscope.wipo.int',
        'epo.org',
        'uspto.gov',
        'espacenet.com'
    ]
    
    parsed_url = urlparse(url)
    return any(domain in parsed_url.netloc.lower() for domain in patent_domains)

def get_patent_search_urls(base_url: str, query: str = None) -> List[str]:
    """Generate direct patent URLs for known patent sites"""
    patent_urls = []
    
    if 'patents.google.com' in base_url:
        # For Google Patents, we need to construct individual patent URLs
        # Since the search results are loaded via JavaScript, we'll use a different approach
        
        # Extract search query from URL if present
        if query:
            # Generate some common patent patterns for the given query
            # This is a fallback since we can't scrape the dynamic results
            print(f"🔬 Google Patents detected with query: {query}")
            print(f"   Note: Google Patents uses JavaScript to load results dynamically")
            print(f"   Consider using direct patent URLs or alternative patent databases")
            
            # For now, return the base URL so the user knows it was processed
            patent_urls.append(base_url)
        else:
            # If no specific query, suggest using the search interface
            print(f"🔬 Google Patents detected")
            print(f"   To scrape specific patents, provide individual patent URLs")
            print(f"   Example: https://patents.google.com/patent/US12345678")
            patent_urls.append(base_url)
    
    elif 'uspto.gov' in base_url:
        # USPTO patent URLs
        if '/patft/' in base_url or '/patents/' in base_url:
            patent_urls.append(base_url)
    
    elif 'epo.org' in base_url:
        # European Patent Office
        if '/patents/' in base_url:
            patent_urls.append(base_url)
    
    return patent_urls

async def search_google_scholar(keyword: str, max_results: int = 10) -> List[Dict]:
    """Search Google Scholar for academic papers"""
    try:
        print(f"🔍 Searching Google Scholar for: {keyword}")
        
        # Google Scholar search URL
        search_url = f"https://scholar.google.com/scholar?q={keyword.replace(' ', '+')}"
        
        # Enhanced headers for Google Scholar
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(
            headers=headers, 
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    print(f"❌ Failed to fetch Google Scholar: {response.status}")
                    return []
                
                html = await response.text()
                print(f"✅ Successfully fetched Google Scholar results ({len(html)} characters)")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                # Look for Google Scholar result divs
                scholar_results = soup.find_all('div', class_='gs_r gs_or gs_scl')
                
                for i, result in enumerate(scholar_results[:max_results]):
                    try:
                        # Extract title and link
                        title_elem = result.find('h3', class_='gs_rt')
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        link_elem = title_elem.find('a')
                        url = link_elem.get('href') if link_elem else ""
                        
                        # Extract authors and year
                        authors_elem = result.find('div', class_='gs_a')
                        authors = []
                        year = None
                        if authors_elem:
                            authors_text = authors_elem.get_text(strip=True)
                            # Parse authors and year from text like "J Smith, A Johnson - 2023"
                            if ' - ' in authors_text:
                                authors_part = authors_text.split(' - ')[0]
                                authors = [author.strip() for author in authors_part.split(',')]
                                
                                # Try to extract year
                                year_match = re.search(r'(\d{4})', authors_text)
                                if year_match:
                                    year = int(year_match.group(1))
                        
                        # Extract abstract
                        abstract_elem = result.find('div', class_='gs_rs')
                        abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
                        
                        # Extract citation count
                        citations_elem = result.find('div', class_='gs_fl')
                        citations = 0
                        if citations_elem:
                            citations_text = citations_elem.get_text()
                            citations_match = re.search(r'Cited by (\d+)', citations_text)
                            if citations_match:
                                citations = int(citations_match.group(1))
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "authors": authors,
                            "abstract": abstract,
                            "year": year,
                            "citations": citations,
                            "source": "Google Scholar"
                        })
                        
                        print(f"   📚 Found: {title[:50]}...")
                        
                    except Exception as e:
                        print(f"   ❌ Error parsing result {i}: {e}")
                        continue
                
                print(f"✅ Google Scholar search completed: {len(results)} results found")
                return results
                
    except Exception as e:
        print(f"❌ Error searching Google Scholar: {e}")
        import traceback
        traceback.print_exc()
        return []

async def search_google_patents(keyword: str, max_results: int = 10) -> List[Dict]:
    """Search Google Patents for patent documents using a more robust approach"""
    try:
        print(f"🔍 Searching Google Patents for: {keyword}")
        
        # Try multiple search approaches
        results = []
        
        # Approach 1: Try USPTO API (more reliable)
        try:
            uspto_results = await search_uspto_patents(keyword, max_results)
            if uspto_results:
                results.extend(uspto_results)
                print(f"✅ USPTO search found {len(uspto_results)} patents")
        except Exception as e:
            print(f"⚠️  USPTO search failed: {e}")
        
        # Approach 2: Try Google Patents with different search patterns
        if len(results) < max_results:
            try:
                google_results = await search_google_patents_direct(keyword, max_results - len(results))
                if google_results:
                    results.extend(google_results)
                    print(f"✅ Google Patents search found {len(google_results)} patents")
            except Exception as e:
                print(f"⚠️  Google Patents search failed: {e}")
        
        # Approach 3: Return empty results if no patents found
        if not results:
            print(f"⚠️  No patents found via APIs")
            return []
        
        print(f"✅ Patent search completed: {len(results)} patents found")
        return results
        
    except Exception as e:
        print(f"❌ Error searching Google Patents: {e}")
        import traceback
        traceback.print_exc()
        return []

async def search_uspto_patents(keyword: str, max_results: int = 10) -> List[Dict]:
    """Search USPTO patents using their public API"""
    try:
        print(f"🔍 Searching USPTO patents for: {keyword}")
        
        # USPTO patent search endpoint
        search_url = "https://developer.uspto.gov/ds-api/patents/v3/grants"
        
        # Search parameters
        params = {
            "searchText": keyword,
            "maxRec": min(max_results, 50),  # USPTO limit
            "startRec": 0
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(search_url, params=params) as response:
                if response.status != 200:
                    print(f"❌ USPTO API failed: {response.status}")
                    return []
                
                data = await response.json()
                patents = data.get('results', [])
                
                results = []
                for patent in patents[:max_results]:
                    try:
                        # Extract patent information
                        title = patent.get('patentTitle', f"Patent for {keyword}")
                        patent_number = patent.get('patentNumber', '')
                        inventors = patent.get('inventorNameArray', ['Unknown Inventor'])
                        abstract = patent.get('abstractText', f"Patent related to {keyword}")
                        year = patent.get('patentDate', '')[:4] if patent.get('patentDate') else None
                        
                        # Create patent URL
                        url = f"https://patents.google.com/patent/{patent_number}" if patent_number else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "inventors": inventors,
                            "abstract": abstract,
                            "year": year,
                            "patent_number": patent_number,
                            "source": "USPTO"
                        })
                        
                        print(f"   🔬 Found USPTO patent: {title[:50]}...")
                        
                    except Exception as e:
                        print(f"   ❌ Error processing USPTO patent: {e}")
                        continue
                
                return results
                
    except Exception as e:
        print(f"❌ Error searching USPTO patents: {e}")
        return []

async def search_google_patents_direct(keyword: str, max_results: int = 10) -> List[Dict]:
    """Try direct Google Patents search with enhanced selectors"""
    try:
        print(f"🔍 Trying direct Google Patents search for: {keyword}")
        
        # Try different Google Patents search URLs
        search_urls = [
            f"https://patents.google.com/?q={keyword}",
            f"https://patents.google.com/?q=({keyword})",
            f"https://patents.google.com/?q=%22{keyword}%22"
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/'
        }
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(
            headers=headers, 
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=ssl_context)
        ) as session:
            
            for search_url in search_urls:
                try:
                    async with session.get(search_url) as response:
                        if response.status != 200:
                            continue
                        
                        html = await response.text()
                        
                        # Try to find patent links
                        soup = BeautifulSoup(html, 'html.parser')
                        patent_links = soup.find_all('a', href=re.compile(r'/patent/'))
                        
                        if patent_links:
                            results = []
                            for link in patent_links[:max_results]:
                                try:
                                    href = link.get('href', '')
                                    if href and '/patent/' in href:
                                        patent_url = "https://patents.google.com" + href if not href.startswith('http') else href
                                        title = link.get_text(strip=True) or f"Patent for {keyword}"
                                        
                                        results.append({
                                            "title": title,
                                            "url": patent_url,
                                            "inventors": ["Unknown Inventor"],
                                            "abstract": f"Patent related to {keyword}",
                                            "year": None,
                                            "patent_number": href.split('/patent/')[-1] if '/' in href else "",
                                            "source": "Google Patents"
                                        })
                                        
                                        print(f"   🔬 Found Google patent: {title[:50]}...")
                                        
                                except Exception as e:
                                    continue
                            
                            if results:
                                return results
                
                except Exception as e:
                    continue
            
            return []
            
    except Exception as e:
        print(f"❌ Error in direct Google Patents search: {e}")
        return []



def fallback_scrape_blog_articles(blog_url: str, max_articles: int = 50) -> List[Dict[str, Any]]:
    """
    Fallback scraping function for blogs containing many articles.
    This function provides multiple fallback strategies when primary scraping fails.
    """
    try:
        print(f"🔄 Starting fallback scraping for blog: {blog_url}")
        print(f"   Target: Up to {max_articles} articles")
        
        # Strategy 1: Try newspaper3k if available
        if NEWSPAPER_AVAILABLE:
            print("   📰 Strategy 1: Attempting newspaper3k extraction...")
            try:
                from newspaper import build
                news_site = build(blog_url, memoize_articles=False)
                news_site.download()
                news_site.parse()
                
                if news_site.articles:
                    print(f"   ✅ Newspaper3k found {len(news_site.articles)} articles")
                    articles = []
                    
                    for i, article in enumerate(news_site.articles[:max_articles]):
                        try:
                            # Download and parse individual article
                            article.download()
                            article.parse()
                            
                            if article.text and len(article.text) > 100:
                                article_data = {
                                    "url": article.url or f"{blog_url}/article_{i+1}",
                                    "title": article.title or f"Article {i+1} from {blog_url}",
                                    "text": article.text,
                                    "publish_date": article.publish_date.isoformat() if article.publish_date else None,
                                    "authors": article.authors or ["Unknown Author"],
                                    "companies": extract_company_names(article.text),
                                    "top_image": article.top_image,
                                    "scraping_method": "newspaper3k"
                                }
                                articles.append(article_data)
                                print(f"     ✅ Processed article {i+1}: {article_data['title'][:50]}...")
                            
                        except Exception as e:
                            print(f"     ⚠️  Error processing article {i+1}: {e}")
                            continue
                    
                    if articles:
                        print(f"   🎯 Newspaper3k strategy successful: {len(articles)} articles")
                        return articles
                    else:
                        print("   ⚠️  Newspaper3k found articles but couldn't process them")
                else:
                    print("   ⚠️  Newspaper3k found no articles")
                    
            except Exception as e:
                print(f"   ❌ Newspaper3k strategy failed: {e}")
        
        # Strategy 2: Enhanced BeautifulSoup with multiple selectors
        print("   🔍 Strategy 2: Enhanced BeautifulSoup extraction...")
        try:
            import aiohttp
            import asyncio
            
            async def _fetch_with_enhanced_bs():
                # Enhanced headers for better compatibility
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
                
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                timeout = aiohttp.ClientTimeout(total=30, connect=10)
                
                async with aiohttp.ClientSession(
                    headers=headers, 
                    timeout=timeout,
                    connector=aiohttp.TCPConnector(ssl=ssl_context)
                ) as session:
                    async with session.get(blog_url) as response:
                        if response.status != 200:
                            print(f"     ❌ HTTP {response.status} for {blog_url}")
                            return None
                        return await response.text()
            
            # Run the async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            html_content = loop.run_until_complete(_fetch_with_enhanced_bs())
            loop.close()
            
            if html_content:
                print(f"     ✅ Successfully fetched HTML ({len(html_content)} characters)")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Comprehensive article detection patterns
                article_patterns = [
                    # Modern blog patterns
                    'article', '.post', '.article', '.entry', '.story', '.news',
                    '.blog-post', '.content-item', '.research-item', '.insight-item',
                    # Header patterns
                    'h1', 'h2', 'h3', 'h4',
                    # Link patterns
                    'a[href*="/article/"]', 'a[href*="/post/"]', 'a[href*="/news/"]',
                    'a[href*="/story/"]', 'a[href*="/blog/"]', 'a[href*="/research/"]',
                    'a[href*="/insights/"]', 'a[href*="/reports/"]', 'a[href*="/analysis/"]',
                    # Year-based patterns
                    'a[href*="/2025/"]', 'a[href*="/2024/"]', 'a[href*="/2023/"]',
                    'a[href*="/2022/"]', 'a[href*="/2021/"]',
                    # Generic content patterns
                    '.content', '.main-content', '.post-content', '.article-content'
                ]
                
                articles = []
                processed_urls = set()
                
                for pattern in article_patterns:
                    if len(articles) >= max_articles:
                        break
                        
                    elements = soup.select(pattern)
                    print(f"       Pattern '{pattern}': Found {len(elements)} elements")
                    
                    for element in elements:
                        if len(articles) >= max_articles:
                            break
                            
                        try:
                            # Extract article data based on element type
                            if pattern.startswith('a[href'):
                                # Link-based extraction
                                href = element.get('href')
                                if href and href not in processed_urls:
                                    full_url = urljoin(blog_url, href)
                                    if is_likely_article_url(full_url, blog_url):
                                        # Try to extract title and content
                                        title = element.get_text(strip=True) or f"Article from {full_url}"
                                        
                                        article_data = {
                                            "url": full_url,
                                            "title": title,
                                            "text": f"Content from {title}. Visit {full_url} for full article.",
                                            "publish_date": None,
                                            "authors": ["Unknown Author"],
                                            "companies": [],
                                            "top_image": None,
                                            "scraping_method": "beautifulsoup_links"
                                        }
                                        articles.append(article_data)
                                        processed_urls.add(href)
                                        print(f"         ✅ Added link-based article: {title[:50]}...")
                            
                            elif pattern in ['article', '.post', '.article', '.entry', '.story', '.news']:
                                # Content-based extraction
                                title_elem = element.find(['h1', 'h2', 'h3', 'h4', '.title', '.headline'])
                                title = title_elem.get_text(strip=True) if title_elem else f"Article {len(articles)+1}"
                                
                                # Extract text content
                                text_content = ""
                                for text_elem in element.find_all(['p', 'div', 'span']):
                                    text = text_elem.get_text(strip=True)
                                    if len(text) > 20:  # Only meaningful text
                                        text_content += text + " "
                                
                                if text_content and len(text_content) > 100:
                                    article_data = {
                                        "url": f"{blog_url}/article_{len(articles)+1}",
                                        "title": title,
                                        "text": text_content[:2000],  # Limit text length
                                        "publish_date": None,
                                        "authors": ["Unknown Author"],
                                        "companies": extract_company_names(text_content),
                                        "top_image": None,
                                        "scraping_method": "beautifulsoup_content"
                                    }
                                    articles.append(article_data)
                                    print(f"         ✅ Added content-based article: {title[:50]}...")
                        
                        except Exception as e:
                            print(f"         ⚠️  Error processing element: {e}")
                            continue
                
                if articles:
                    print(f"     🎯 BeautifulSoup strategy successful: {len(articles)} articles")
                    return articles
                else:
                    print("     ⚠️  BeautifulSoup found no articles")
            else:
                print("     ❌ Failed to fetch HTML content")
                
        except Exception as e:
            print(f"   ❌ BeautifulSoup strategy failed: {e}")
        
        # Strategy 3: RSS Feed detection and parsing
        print("   📡 Strategy 3: RSS Feed detection...")
        try:
            rss_urls = [
                f"{blog_url}/feed",
                f"{blog_url}/rss",
                f"{blog_url}/rss.xml",
                f"{blog_url}/feed.xml",
                f"{blog_url}/atom.xml",
                f"{blog_url}/rss/",
                f"{blog_url}/feed/"
            ]
            
            for rss_url in rss_urls:
                try:
                    import aiohttp
                    import asyncio
                    
                    async def _fetch_rss():
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        timeout = aiohttp.ClientTimeout(total=15, connect=5)
                        
                        async with aiohttp.ClientSession(
                            headers=headers, 
                            timeout=timeout,
                            connector=aiohttp.TCPConnector(ssl=ssl_context)
                        ) as session:
                            async with session.get(rss_url) as response:
                                if response.status == 200:
                                    return await response.text()
                                return None
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    rss_content = loop.run_until_complete(_fetch_rss())
                    loop.close()
                    
                    if rss_content and ('<rss' in rss_content or '<feed' in rss_content):
                        print(f"     ✅ Found RSS feed: {rss_url}")
                        
                        # Parse RSS content
                        soup = BeautifulSoup(rss_content, 'xml')
                        items = soup.find_all(['item', 'entry'])
                        
                        if items:
                            articles = []
                            for i, item in enumerate(items[:max_articles]):
                                try:
                                    title = item.find(['title', 'name'])
                                    title_text = title.get_text(strip=True) if title else f"RSS Article {i+1}"
                                    
                                    link = item.find(['link', 'url'])
                                    link_url = link.get('href') if link else f"{blog_url}/rss_article_{i+1}"
                                    
                                    description = item.find(['description', 'summary', 'content'])
                                    desc_text = description.get_text(strip=True) if description else f"Content from {title_text}"
                                    
                                    pub_date = item.find(['pubDate', 'published', 'updated'])
                                    date_text = pub_date.get_text(strip=True) if pub_date else None
                                    
                                    article_data = {
                                        "url": link_url,
                                        "title": title_text,
                                        "text": desc_text,
                                        "publish_date": date_text,
                                        "authors": ["Unknown Author"],
                                        "companies": extract_company_names(desc_text),
                                        "top_image": None,
                                        "scraping_method": "rss_feed"
                                    }
                                    articles.append(article_data)
                                    
                                except Exception as e:
                                    print(f"         ⚠️  Error processing RSS item {i+1}: {e}")
                                    continue
                            
                            if articles:
                                print(f"     🎯 RSS strategy successful: {len(articles)} articles")
                                return articles
                            else:
                                print("     ⚠️  RSS found items but couldn't process them")
                        
                        break  # Found RSS feed, no need to check others
                        
                except Exception as e:
                    print(f"     ⚠️  Error checking RSS {rss_url}: {e}")
                    continue
            
            print("     ⚠️  No RSS feeds found")
            
        except Exception as e:
            print(f"   ❌ RSS strategy failed: {e}")
        
        # Strategy 4: Sitemap detection and parsing
        print("   🗺️  Strategy 4: Sitemap detection...")
        try:
            sitemap_urls = [
                f"{blog_url}/sitemap.xml",
                f"{blog_url}/sitemap_index.xml",
                f"{blog_url}/sitemap-posts.xml",
                f"{blog_url}/sitemap-articles.xml",
                f"{blog_url}/sitemap/",
                f"{blog_url}/sitemap.xml.gz"
            ]
            
            for sitemap_url in sitemap_urls:
                try:
                    import aiohttp
                    import asyncio
                    
                    async def _fetch_sitemap():
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        timeout = aiohttp.ClientTimeout(total=15, connect=5)
                        
                        async with aiohttp.ClientSession(
                            headers=headers, 
                            timeout=timeout,
                            connector=aiohttp.TCPConnector(ssl=ssl_context)
                        ) as session:
                            async with session.get(sitemap_url) as response:
                                if response.status == 200:
                                    return await response.text()
                                return None
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sitemap_content = loop.run_until_complete(_fetch_sitemap())
                    loop.close()
                    
                    if sitemap_content and ('<urlset' in sitemap_content or '<sitemapindex' in sitemap_content):
                        print(f"     ✅ Found sitemap: {sitemap_url}")
                        
                        # Parse sitemap content
                        soup = BeautifulSoup(sitemap_content, 'xml')
                        urls = soup.find_all('url')
                        
                        if urls:
                            articles = []
                            for i, url_elem in enumerate(urls[:max_articles]):
                                try:
                                    loc = url_elem.find('loc')
                                    if loc:
                                        url = loc.get_text(strip=True)
                                        if is_likely_article_url(url, blog_url):
                                            title = f"Sitemap Article {i+1}"
                                            
                                            article_data = {
                                                "url": url,
                                                "title": title,
                                                "text": f"Article found via sitemap: {url}",
                                                "publish_date": None,
                                                "authors": ["Unknown Author"],
                                                "companies": [],
                                                "top_image": None,
                                                "scraping_method": "sitemap"
                                            }
                                            articles.append(article_data)
                                    
                                except Exception as e:
                                    print(f"         ⚠️  Error processing sitemap URL {i+1}: {e}")
                                    continue
                            
                            if articles:
                                print(f"     🎯 Sitemap strategy successful: {len(articles)} articles")
                                return articles
                            else:
                                print("     ⚠️  Sitemap found URLs but couldn't process them")
                        
                        break  # Found sitemap, no need to check others
                        
                except Exception as e:
                    print(f"     ⚠️  Error checking sitemap {sitemap_url}: {e}")
                    continue
            
            print("     ⚠️  No sitemaps found")
            
        except Exception as e:
            print(f"   ❌ Sitemap strategy failed: {e}")
        
        # Strategy 5: Last resort - generate placeholder articles
        print("   🆘 Strategy 5: Generating placeholder articles...")
        try:
            articles = []
            for i in range(min(5, max_articles)):  # Limit to 5 placeholder articles
                article_data = {
                    "url": f"{blog_url}/fallback_article_{i+1}",
                    "title": f"Fallback Article {i+1} from {blog_url}",
                    "text": f"This is a fallback article generated when scraping failed. The original blog at {blog_url} could not be processed using standard methods. Consider manually submitting individual article URLs or checking if the site has changed its structure.",
                    "publish_date": None,
                    "authors": ["System Generated"],
                    "companies": [],
                    "top_image": None,
                    "scraping_method": "fallback_placeholder"
                }
                articles.append(article_data)
            
            print(f"     🎯 Generated {len(articles)} placeholder articles")
            return articles
            
        except Exception as e:
            print(f"   ❌ Placeholder strategy failed: {e}")
        
        print("   ❌ All fallback strategies failed")
        return []
        
    except Exception as e:
        print(f"❌ Critical error in fallback scraping: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_fallback_scraping(blog_url: str) -> Dict[str, Any]:
    """
    Test function to evaluate fallback scraping capabilities for a given blog URL.
    This helps diagnose what strategies work for different types of blogs.
    """
    try:
        print(f"🧪 Testing fallback scraping for: {blog_url}")
        results = {
            "url": blog_url,
            "test_time": datetime.now().isoformat(),
            "strategies_tested": [],
            "successful_strategies": [],
            "total_articles_found": 0,
            "articles_per_strategy": {},
            "recommendations": []
        }
        
        # Test Strategy 1: Newspaper3k
        if NEWSPAPER_AVAILABLE:
            print("   📰 Testing Strategy 1: Newspaper3k...")
            try:
                from newspaper import build
                news_site = build(blog_url, memoize_articles=False)
                news_site.download()
                news_site.parse()
                
                if news_site.articles:
                    results["strategies_tested"].append("newspaper3k")
                    results["articles_per_strategy"]["newspaper3k"] = len(news_site.articles)
                    results["successful_strategies"].append("newspaper3k")
                    print(f"     ✅ Newspaper3k: {len(news_site.articles)} articles")
                else:
                    results["strategies_tested"].append("newspaper3k")
                    results["articles_per_strategy"]["newspaper3k"] = 0
                    print("     ❌ Newspaper3k: No articles found")
            except Exception as e:
                results["strategies_tested"].append("newspaper3k")
                results["articles_per_strategy"]["newspaper3k"] = 0
                print(f"     ❌ Newspaper3k: Error - {e}")
        
        # Test Strategy 2: BeautifulSoup
        print("   🔍 Testing Strategy 2: BeautifulSoup...")
        try:
            import aiohttp
            import asyncio
            
            async def _test_bs():
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                timeout = aiohttp.ClientTimeout(total=15, connect=5)
                
                async with aiohttp.ClientSession(
                    headers=headers, 
                    timeout=timeout,
                    connector=aiohttp.TCPConnector(ssl=ssl_context)
                ) as session:
                    async with session.get(blog_url) as response:
                        if response.status == 200:
                            return await response.text()
                        return None
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            html_content = loop.run_until_complete(_test_bs())
            loop.close()
            
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Test various selectors
                test_selectors = [
                    'article', '.post', '.article', '.entry', '.story', '.news',
                    'h1', 'h2', 'h3', 'h4',
                    'a[href*="/article/"]', 'a[href*="/post/"]', 'a[href*="/news/"]'
                ]
                
                total_elements = 0
                for selector in test_selectors:
                    elements = soup.select(selector)
                    total_elements += len(elements)
                
                results["strategies_tested"].append("beautifulsoup")
                results["articles_per_strategy"]["beautifulsoup"] = total_elements
                
                if total_elements > 0:
                    results["successful_strategies"].append("beautifulsoup")
                    print(f"     ✅ BeautifulSoup: {total_elements} potential elements found")
                else:
                    print("     ❌ BeautifulSoup: No elements found")
            else:
                results["strategies_tested"].append("beautifulsoup")
                results["articles_per_strategy"]["beautifulsoup"] = 0
                print("     ❌ BeautifulSoup: Failed to fetch HTML")
                
        except Exception as e:
            results["strategies_tested"].append("beautifulsoup")
            results["articles_per_strategy"]["beautifulsoup"] = 0
            print(f"     ❌ BeautifulSoup: Error - {e}")
        
        # Test Strategy 3: RSS
        print("   📡 Testing Strategy 3: RSS...")
        try:
            rss_urls = [
                f"{blog_url}/feed", f"{blog_url}/rss", f"{blog_url}/rss.xml",
                f"{blog_url}/feed.xml", f"{blog_url}/atom.xml"
            ]
            
            rss_found = False
            for rss_url in rss_urls:
                try:
                    import aiohttp
                    import asyncio
                    
                    async def _test_rss():
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        timeout = aiohttp.ClientTimeout(total=10, connect=3)
                        
                        async with aiohttp.ClientSession(
                            headers=headers, 
                            timeout=timeout,
                            connector=aiohttp.TCPConnector(ssl=ssl_context)
                        ) as session:
                            async with session.get(rss_url) as response:
                                if response.status == 200:
                                    return await response.text()
                                return None
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    rss_content = loop.run_until_complete(_test_rss())
                    loop.close()
                    
                    if rss_content and ('<rss' in rss_content or '<feed' in rss_content):
                        rss_found = True
                        soup = BeautifulSoup(rss_content, 'xml')
                        items = soup.find_all(['item', 'entry'])
                        results["articles_per_strategy"]["rss"] = len(items)
                        results["successful_strategies"].append("rss")
                        print(f"     ✅ RSS ({rss_url}): {len(items)} items found")
                        break
                        
                except Exception as e:
                    continue
            
            results["strategies_tested"].append("rss")
            if not rss_found:
                results["articles_per_strategy"]["rss"] = 0
                print("     ❌ RSS: No feeds found")
                
        except Exception as e:
            results["strategies_tested"].append("rss")
            results["articles_per_strategy"]["rss"] = 0
            print(f"     ❌ RSS: Error - {e}")
        
        # Test Strategy 4: Sitemap
        print("   🗺️  Testing Strategy 4: Sitemap...")
        try:
            sitemap_urls = [
                f"{blog_url}/sitemap.xml", f"{blog_url}/sitemap_index.xml",
                f"{blog_url}/sitemap-posts.xml", f"{blog_url}/sitemap-articles.xml"
            ]
            
            sitemap_found = False
            for sitemap_url in sitemap_urls:
                try:
                    import aiohttp
                    import asyncio
                    
                    async def _test_sitemap():
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = False
                        ssl_context.verify_mode = ssl.CERT_NONE
                        
                        timeout = aiohttp.ClientTimeout(total=10, connect=3)
                        
                        async with aiohttp.ClientSession(
                            headers=headers, 
                            timeout=timeout,
                            connector=aiohttp.TCPConnector(ssl=ssl_context)
                        ) as session:
                            async with session.get(sitemap_url) as response:
                                if response.status == 200:
                                    return await response.text()
                                return None
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    sitemap_content = loop.run_until_complete(_test_sitemap())
                    loop.close()
                    
                    if sitemap_content and ('<urlset' in sitemap_content or '<sitemapindex' in sitemap_content):
                        sitemap_found = True
                        soup = BeautifulSoup(sitemap_content, 'xml')
                        urls = soup.find_all('url')
                        results["articles_per_strategy"]["sitemap"] = len(urls)
                        results["successful_strategies"].append("sitemap")
                        print(f"     ✅ Sitemap ({sitemap_url}): {len(urls)} URLs found")
                        break
                        
                except Exception as e:
                    continue
            
            results["strategies_tested"].append("sitemap")
            if not sitemap_found:
                results["articles_per_strategy"]["sitemap"] = 0
                print("     ❌ Sitemap: No sitemaps found")
                
        except Exception as e:
            results["strategies_tested"].append("sitemap")
            results["articles_per_strategy"]["sitemap"] = 0
            print(f"     ❌ Sitemap: Error - {e}")
        
        # Calculate totals and generate recommendations
        total_articles = sum(results["articles_per_strategy"].values())
        results["total_articles_found"] = total_articles
        
        print(f"   📊 Test Results Summary:")
        print(f"     Total articles found: {total_articles}")
        print(f"     Successful strategies: {len(results['successful_strategies'])}")
        
        # Generate recommendations
        if total_articles == 0:
            results["recommendations"].append("All scraping strategies failed. Consider manual article submission.")
            results["recommendations"].append("Check if the site has anti-scraping measures.")
        elif total_articles < 5:
            results["recommendations"].append("Limited content found. Consider using individual article URLs.")
            results["recommendations"].append("Try the fallback scraping endpoint for better results.")
        else:
            results["recommendations"].append("Multiple strategies successful. Use fallback scraping for comprehensive results.")
        
        if "newspaper3k" in results["successful_strategies"]:
            results["recommendations"].append("Newspaper3k works well for this site.")
        if "rss" in results["successful_strategies"]:
            results["recommendations"].append("RSS feed available - consider using it for updates.")
        if "sitemap" in results["successful_strategies"]:
            results["recommendations"].append("Sitemap available - good for comprehensive article discovery.")
        
        print(f"     💡 Recommendations: {len(results['recommendations'])} generated")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical error in test function: {e}")
        import traceback
        traceback.print_exc()
        return {
            "url": blog_url,
            "error": str(e),
            "test_time": datetime.now().isoformat(),
            "status": "test_failed"
        }

def extract_patent_links(html_content: str, base_url: str) -> List[str]:
    """Extract patent links from patent search results"""
    soup = BeautifulSoup(html_content, 'html.parser')
    patent_links = []
    
    print(f"🔍 Analyzing HTML content for patent links...")
    print(f"   HTML length: {len(html_content)} characters")
    
    # Google Patents specific selectors
    if 'patents.google.com' in base_url:
        print(f"   🔬 Using Google Patents specific extraction")
        
        # Look for various patent result patterns
        patent_selectors = [
            'a[href*="/patent/"]',  # Direct patent links
            'a[href*="/patents/"]',  # Alternative patent paths
            'article a[href]',       # Article elements with links
            '.result a[href]',       # Result class links
            '.patent a[href]',       # Patent class links
            'h3 a[href]',            # Header links (common for patent titles)
            'h2 a[href]',            # Alternative header links
            '.title a[href]',        # Title class links
            '.headline a[href]',     # Headline class links
        ]
        
        for selector in patent_selectors:
            links = soup.select(selector)
            print(f"     Selector '{selector}': Found {len(links)} links")
            
            for link in links:
                href = link.get('href', '')
                if href:
                    # Filter for actual patent URLs
                    if '/patent/' in href and '?q=' not in href and '&oq=' not in href:
                        full_url = urljoin(base_url, href)
                        if full_url not in patent_links:
                            patent_links.append(full_url)
                            print(f"       ✅ Added patent: {full_url}")
        
        # If no patents found with specific selectors, try broader approach
        if not patent_links:
            print(f"     ⚠️  No patents found with specific selectors, trying broader approach...")
            all_links = soup.find_all('a', href=True)
            print(f"       Found {len(all_links)} total links")
            
            for link in all_links:
                href = link.get('href', '')
                if href and '/patent/' in href and '?q=' not in href:
                    full_url = urljoin(base_url, href)
                    if full_url not in patent_links:
                        patent_links.append(full_url)
                        print(f"         ✅ Added patent: {full_url}")
        
        # If still no patents found, this is likely a JavaScript-loaded page
        if not patent_links:
            print(f"     🔍 No patent links found - this appears to be a JavaScript-loaded page")
            print(f"     💡 Consider using direct patent URLs instead of search results")
    
    # Generic patent link patterns for other sites
    else:
        print(f"   🔬 Using generic patent extraction")
        patent_patterns = [
            r'/patent/[A-Z0-9\-]+',
            r'/patents/[A-Z0-9\-]+',
            r'/publication/[A-Z0-9\-]+'
        ]
        
        for pattern in patent_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                full_url = urljoin(base_url, match)
                if full_url not in patent_links:
                    patent_links.append(full_url)
                    print(f"       ✅ Added patent: {full_url}")
    
    print(f"   🎯 Total patent links extracted: {len(patent_links)}")
    return patent_links[:50]  # Limit to 50 patents
