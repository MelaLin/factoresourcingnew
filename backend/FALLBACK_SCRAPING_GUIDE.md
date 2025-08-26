# Fallback Scraping Function Guide

## Overview

The fallback scraping function (`fallback_scrape_blog_articles`) is a comprehensive solution for extracting articles from blogs when primary scraping methods fail. It implements multiple fallback strategies to ensure maximum content discovery.

## 🎯 Purpose

This function addresses common scraping challenges:
- Sites with anti-scraping measures (like RMI.org)
- JavaScript-heavy sites that don't load content immediately
- Sites with complex HTML structures
- Sites that block automated requests
- Sites that require specific user agents or headers

## 🔧 How It Works

The function implements a **5-strategy fallback approach**:

### Strategy 1: Newspaper3k (Primary Fallback)
- **When**: If newspaper3k library is available
- **How**: Uses the newspaper3k library to build and parse the site
- **Advantages**: Excellent at extracting article content, handles many site types
- **Output**: Full article text, titles, authors, publish dates
- **Method**: `scraping_method: "newspaper3k"`

### Strategy 2: Enhanced BeautifulSoup
- **When**: Newspaper3k fails or isn't available
- **How**: Uses sophisticated HTML parsing with multiple selectors
- **Selectors**: 
  - Modern blog patterns: `article`, `.post`, `.article`, `.entry`
  - Header patterns: `h1`, `h2`, `h3`, `h4`
  - Link patterns: `a[href*="/article/"]`, `a[href*="/post/"]`
  - Year-based patterns: `a[href*="/2025/"]`, `a[href*="/2024/"]`
- **Output**: Article titles, content snippets, links
- **Method**: `scraping_method: "beautifulsoup_content"` or `"beautifulsoup_links"`

### Strategy 3: RSS Feed Detection
- **When**: HTML parsing finds limited content
- **How**: Checks common RSS feed URLs and parses XML content
- **Feed URLs**: `/feed`, `/rss`, `/rss.xml`, `/feed.xml`, `/atom.xml`
- **Output**: Article titles, descriptions, links, publish dates
- **Method**: `scraping_method: "rss_feed"`

### Strategy 4: Sitemap Detection
- **When**: RSS feeds aren't available
- **How**: Checks common sitemap URLs and parses XML content
- **Sitemap URLs**: `/sitemap.xml`, `/sitemap_index.xml`, `/sitemap-posts.xml`
- **Output**: Article URLs, basic metadata
- **Method**: `scraping_method: "sitemap"`

### Strategy 5: Placeholder Generation
- **When**: All other strategies fail
- **How**: Generates informative placeholder articles
- **Output**: Helpful messages explaining the scraping failure
- **Method**: `scraping_method: "fallback_placeholder"`

## 🚀 Usage

### 1. Automatic Integration
The fallback function is automatically called when:
- Primary scraping finds no articles
- Primary scraping finds very few articles (< 5)

### 2. Manual API Endpoints

#### Test Fallback Capabilities
```bash
POST /api/blog/test-fallback
{
    "url": "https://example-blog.com"
}
```

#### Direct Fallback Scraping
```bash
POST /api/blog/fallback-scrape
{
    "url": "https://example-blog.com"
}
```

### 3. Programmatic Usage
```python
from scraper import fallback_scrape_blog_articles

# Get up to 50 articles using fallback methods
articles = fallback_scrape_blog_articles("https://example-blog.com", max_articles=50)

# Process the results
for article in articles:
    print(f"Title: {article['title']}")
    print(f"Method: {article['scraping_method']}")
    print(f"Content: {article['text'][:200]}...")
```

## 📊 Output Format

Each article returned contains:
```python
{
    "url": "https://example.com/article/123",
    "title": "Article Title",
    "text": "Article content...",
    "publish_date": "2024-01-15T10:30:00",
    "authors": ["Author Name"],
    "companies": ["Company Name"],
    "top_image": "https://example.com/image.jpg",
    "scraping_method": "newspaper3k"  # or other method
}
```

## 🔍 Testing and Diagnostics

### Test Function
Use `test_fallback_scraping()` to evaluate what strategies work for a specific blog:

```python
from scraper import test_fallback_scraping

results = test_fallback_scraping("https://example-blog.com")
print(f"Strategies tested: {results['strategies_tested']}")
print(f"Successful strategies: {results['successful_strategies']}")
print(f"Total articles found: {results['total_articles_found']}")
print(f"Recommendations: {results['recommendations']}")
```

### Test Results Include:
- **Strategies tested**: All attempted methods
- **Successful strategies**: Methods that found content
- **Articles per strategy**: Count of articles found by each method
- **Total articles found**: Sum across all strategies
- **Recommendations**: Actionable advice for the specific site

## 🛠️ Configuration

### Environment Variables
- `NEWSPAPER_AVAILABLE`: Set to `False` to disable newspaper3k strategy
- SSL verification can be disabled for development (not recommended for production)

### Customization
- Modify `max_articles` parameter (default: 50)
- Add custom selectors in Strategy 2
- Extend RSS/sitemap URL patterns
- Customize placeholder article content

## 📈 Performance Considerations

### Timeouts
- **Newspaper3k**: No explicit timeout (can be slow for large sites)
- **BeautifulSoup**: 30 seconds total, 10 seconds connect
- **RSS/Sitemap**: 10-15 seconds total, 3-5 seconds connect

### Memory Usage
- Articles are processed one at a time to minimize memory usage
- Text content is limited to 2000 characters for BeautifulSoup strategy
- Large sites may take longer but won't overwhelm memory

## 🚨 Error Handling

### Graceful Degradation
- If one strategy fails, others are attempted
- Individual article processing errors don't stop the entire process
- Comprehensive error logging for debugging

### Common Issues
- **SSL errors**: Handled with permissive SSL context
- **Timeout errors**: Each strategy has appropriate timeouts
- **Parsing errors**: Fallback to simpler extraction methods
- **Network errors**: Retry logic in some strategies

## 🔧 Troubleshooting

### Debug Mode
Enable detailed logging by setting log level to DEBUG:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Problems
1. **No articles found**: Check if site has anti-scraping measures
2. **SSL errors**: Verify SSL certificate or disable verification (development only)
3. **Timeout errors**: Increase timeout values for slow sites
4. **Memory issues**: Reduce `max_articles` parameter

### Site-Specific Issues
- **RMI.org**: Known to block scrapers, use fallback methods
- **TechCrunch**: Requires specific selectors, handled in Strategy 2
- **Patent sites**: Use specialized patent extraction functions

## 📚 Examples

### Example 1: Basic Usage
```python
# Simple fallback scraping
articles = fallback_scrape_blog_articles("https://techcrunch.com")
print(f"Found {len(articles)} articles")
```

### Example 2: Custom Configuration
```python
# Limit articles and get detailed results
articles = fallback_scrape_blog_articles("https://example.com", max_articles=20)
for article in articles:
    print(f"{article['scraping_method']}: {article['title']}")
```

### Example 3: Testing Before Scraping
```python
# Test what strategies work before attempting full scrape
test_results = test_fallback_scraping("https://example.com")
if test_results['total_articles_found'] > 0:
    articles = fallback_scrape_blog_articles("https://example.com")
```

## 🔮 Future Enhancements

### Planned Features
- **Machine learning**: Learn from successful scraping patterns
- **Rate limiting**: Intelligent delays between requests
- **Proxy support**: Rotate IP addresses for blocked sites
- **Content validation**: Verify article quality before returning
- **Caching**: Store successful scraping patterns for reuse

### Extensibility
The function is designed to be easily extended:
- Add new strategies by implementing the same interface
- Customize selectors for specific site types
- Integrate with external scraping services
- Add content filtering and validation

## 📝 Best Practices

### For Developers
1. **Always test** with `test_fallback_scraping()` first
2. **Handle errors gracefully** - the function returns empty list on failure
3. **Monitor performance** - some strategies can be slow
4. **Respect robots.txt** and site terms of service
5. **Use appropriate timeouts** for production environments

### For Users
1. **Try primary scraping first** - fallback is slower
2. **Use test endpoint** to understand what works for your site
3. **Consider manual submission** for sites that block all methods
4. **Check site policies** before scraping
5. **Report issues** with specific error messages

## 🔗 Related Functions

- `discover_articles_from_blog()`: Primary article discovery
- `real_scrape_url()`: Individual article scraping
- `extract_company_names()`: Company extraction from text
- `is_likely_article_url()`: URL validation for articles

## 📞 Support

For issues or questions:
1. Check the test results for specific error messages
2. Review the console logs for detailed debugging info
3. Use the test endpoint to diagnose site-specific issues
4. Consider the site's anti-scraping measures

---

*This fallback scraping function provides a robust, multi-layered approach to content extraction, ensuring maximum success even when primary methods fail.*
