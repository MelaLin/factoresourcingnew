#!/usr/bin/env python3
"""
Comprehensive test for keyword search API endpoint
"""

import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_keyword_search_api():
    """Test the complete keyword search API workflow"""
    try:
        print("🧪 Testing Complete Keyword Search API Workflow")
        print("=" * 60)
        
        # Import the main functions
        from main import search_by_keyword
        
        # Test data
        test_request = {
            "keyword": "solar energy"
        }
        
        print(f"🔍 Testing keyword: '{test_request['keyword']}'")
        print(f"📊 Expected: 25 Google Scholar papers + 25 Google Patents = 50 total sources")
        print()
        
        # Simulate the API call
        print("📡 Calling search_by_keyword API endpoint...")
        try:
            result = await search_by_keyword(test_request)
            
            print("✅ API call successful!")
            print(f"📊 Results Summary:")
            print(f"   Scholar Papers: {result.get('scholar_papers_found', 0)}")
            print(f"   Patents: {result.get('patents_found', 0)}")
            print(f"   Total Sources: {result.get('total_sources', 0)}")
            print(f"   Processed Sources: {result.get('processed_sources', 0)}")
            print(f"   Thesis Matches: {result.get('matches_found', 0)}")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            # Show sample sources
            sources = result.get('sources', [])
            if sources:
                print(f"\n📚 Sample Sources:")
                for i, source in enumerate(sources[:3]):  # Show first 3
                    print(f"   {i+1}. {source.get('title', 'No title')[:60]}...")
                    print(f"      Type: {source.get('source_type', 'unknown')}")
                    print(f"      Keywords: {', '.join(source.get('keywords', [])[:3])}")
                    print(f"      Companies: {', '.join(source.get('companies', [])[:2])}")
                    print()
                
                if len(sources) > 3:
                    print(f"   ... and {len(sources) - 3} more sources")
            
            # Check if sources were added to global articles
            print(f"\n💾 Storage Check:")
            try:
                from main import articles
                print(f"   Global articles count: {len(articles)}")
                if len(articles) > 0:
                    recent_articles = articles[-min(3, len(articles)):]
                    print(f"   Recent articles:")
                    for i, article in enumerate(recent_articles):
                        print(f"     {i+1}. {article.get('title', 'No title')[:50]}...")
            except Exception as e:
                print(f"   ❌ Could not check global articles: {e}")
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("✅ Comprehensive API test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_keyword_search_api())
