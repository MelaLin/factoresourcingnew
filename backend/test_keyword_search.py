#!/usr/bin/env python3
"""
Test script for keyword search functionality
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_keyword_search():
    """Test the keyword search functionality"""
    try:
        print("🧪 Testing Keyword Search Functionality")
        print("=" * 50)
        
        # Import the search functions
        from scraper import search_google_scholar, search_google_patents
        
        # Test keyword
        test_keyword = "solar"
        print(f"🔍 Testing with keyword: '{test_keyword}'")
        
        # Test Google Scholar search
        print("\n📚 Testing Google Scholar search...")
        try:
            scholar_results = await search_google_scholar(test_keyword, max_results=5)
            print(f"   ✅ Google Scholar: Found {len(scholar_results)} results")
            if scholar_results:
                print(f"   📖 First result: {scholar_results[0].get('title', 'No title')[:60]}...")
        except Exception as e:
            print(f"   ❌ Google Scholar failed: {e}")
        
        # Test Google Patents search
        print("\n🔬 Testing Google Patents search...")
        try:
            patent_results = await search_google_patents(test_keyword, max_results=5)
            print(f"   ✅ Google Patents: Found {len(patent_results)} results")
            if patent_results:
                print(f"   📄 First result: {patent_results[0].get('title', 'No title')[:60]}...")
        except Exception as e:
            print(f"   ❌ Google Patents failed: {e}")
        
        # Test fallback scraping
        print("\n🔄 Testing fallback scraping...")
        try:
            from scraper import fallback_scrape_blog_articles
            fallback_results = await fallback_scrape_blog_articles("https://example.com", max_articles=3)
            print(f"   ✅ Fallback scraping: Found {len(fallback_results)} results")
        except Exception as e:
            print(f"   ❌ Fallback scraping failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Keyword search test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_keyword_search())
