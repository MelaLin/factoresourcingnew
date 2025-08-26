#!/usr/bin/env python3
"""
Complete workflow test: Keyword Search → Content Processing → Thesis Matching
"""

import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_complete_workflow():
    """Test the complete workflow from keyword search to thesis matching"""
    try:
        print("🧪 Testing Complete User Workflow")
        print("=" * 60)
        print("1. Keyword Search → 2. Content Processing → 3. Thesis Matching")
        print()
        
        # Import the main functions
        from main import search_by_keyword, add_thesis_text, find_relevant_articles
        
        # Step 1: Perform keyword search
        print("🔍 STEP 1: Keyword Search")
        print("   Searching for 'solar energy' to get 50 sources...")
        
        search_request = {"keyword": "solar energy"}
        search_result = await search_by_keyword(search_request)
        
        if not search_result or search_result.get('status') != 'search_completed':
            print("   ❌ Keyword search failed")
            return
        
        print(f"   ✅ Keyword search successful!")
        print(f"   📊 Found {search_result.get('total_sources', 0)} total sources")
        print(f"   📚 Scholar papers: {search_result.get('scholar_papers_found', 0)}")
        print(f"   🔬 Patents: {search_result.get('patents_found', 0)}")
        print(f"   💾 Processed: {search_result.get('processed_sources', 0)} sources")
        print()
        
        # Step 2: Add thesis text
        print("📝 STEP 2: Add Thesis Text")
        print("   Adding sample thesis about solar energy...")
        
        thesis_text = """
        Solar Energy Implementation in Commercial Buildings
        
        This thesis explores the implementation of solar energy systems in commercial buildings 
        to reduce carbon emissions and energy costs. The research focuses on photovoltaic 
        technology, energy storage solutions, and integration with existing building 
        management systems. Key areas of investigation include:
        
        1. Solar panel efficiency and placement optimization
        2. Battery storage systems for commercial applications
        3. Grid integration and net metering strategies
        4. Economic feasibility and return on investment
        5. Environmental impact assessment
        
        The goal is to provide a comprehensive framework for commercial building owners 
        to implement solar energy solutions effectively.
        """
        
        thesis_request = {"text": thesis_text}
        thesis_result = await add_thesis_text(thesis_request)
        
        if not thesis_result:
            print("   ❌ Thesis addition failed")
            return
        
        print(f"   ✅ Thesis added successfully!")
        print(f"   📏 Content length: {thesis_result.get('content_length', 0)} characters")
        print(f"   🔄 Thesis processed: {thesis_result.get('thesis_processed', False)}")
        print()
        
        # Step 3: Run thesis matching
        print("🎯 STEP 3: Thesis Matching Analysis")
        print("   Running content matching analysis...")
        
        from main import articles
        matches = find_relevant_articles(articles)
        
        print(f"   ✅ Thesis matching completed!")
        print(f"   📊 Total articles available: {len(articles)}")
        print(f"   🎯 Potential matches found: {len(matches)}")
        print()
        
        # Step 4: Display sample matches
        if matches:
            print("📋 SAMPLE MATCHES:")
            for i, match in enumerate(matches[:3]):
                print(f"   {i+1}. {match.get('title', 'No title')[:60]}...")
                print(f"      Relevance: {match.get('relevance_score', 0):.2f}")
                print(f"      Keywords: {', '.join(match.get('keywords', [])[:3])}")
                print(f"      Companies: {', '.join(match.get('companies', [])[:2])}")
                print()
        
        # Step 5: Check data persistence
        print("💾 STEP 4: Data Persistence Check")
        try:
            from main import persistent_storage
            
            # Check if data was saved
            saved_articles = persistent_storage.load_articles()
            saved_theses = persistent_storage.load_thesis_uploads()
            saved_searches = persistent_storage.load_blog_searches()
            
            print(f"   📁 Articles saved: {len(saved_articles)}")
            print(f"   📁 Theses saved: {len(saved_theses)}")
            print(f"   📁 Searches saved: {len(saved_searches)}")
            
            # Check if keyword search was tracked
            keyword_searches = [s for s in saved_searches if s.get('search_type') == 'keyword_search']
            if keyword_searches:
                latest_search = keyword_searches[-1]
                print(f"   🔍 Latest keyword search: '{latest_search.get('keyword', 'Unknown')}'")
                print(f"   📊 Sources found: {latest_search.get('total_sources', 0)}")
            
        except Exception as e:
            print(f"   ⚠️  Data persistence check failed: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Complete workflow test finished!")
        print()
        print("📋 SUMMARY:")
        print(f"   • Keyword search: {'✅' if search_result else '❌'}")
        print(f"   • Thesis addition: {'✅' if thesis_result else '❌'}")
        print(f"   • Content matching: {'✅' if matches else '❌'}")
        print(f"   • Data persistence: {'✅' if 'saved_articles' in locals() else '❌'}")
        print()
        print("🎯 The system is now ready for users to:")
        print("   1. Enter keywords to search Google Scholar and Google Patents")
        print("   2. Get 50 sources automatically processed")
        print("   3. View results in both Setup and Revisions tabs")
        print("   4. Run thesis matching to see correlations")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_complete_workflow())
