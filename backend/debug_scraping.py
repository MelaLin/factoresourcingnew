#!/usr/bin/env python3
"""
Debug script to inspect Google Scholar and Google Patents HTML structure
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
import re

async def debug_google_scholar():
    """Debug Google Scholar HTML structure"""
    try:
        print("🔍 Debugging Google Scholar HTML structure...")
        
        keyword = "solar energy"
        search_url = f"https://scholar.google.com/scholar?q={keyword.replace(' ', '+')}"
        
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
                    return
                
                html = await response.text()
                print(f"✅ Successfully fetched Google Scholar results ({len(html)} characters)")
                
                # Save HTML for inspection
                with open('debug_scholar.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("💾 Saved HTML to debug_scholar.html")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try different selectors
                print("\n🔍 Testing different selectors:")
                
                # Test 1: Original selector
                scholar_results = soup.find_all('div', class_='gs_r gs_or gs_scl')
                print(f"   Original selector 'gs_r gs_or gs_scl': {len(scholar_results)} results")
                
                # Test 2: Look for any div with 'gs_' in class
                gs_divs = soup.find_all('div', class_=re.compile(r'gs_'))
                print(f"   Any div with 'gs_' in class: {len(gs_divs)} results")
                
                # Test 3: Look for h3 elements (article titles)
                h3_elements = soup.find_all('h3')
                print(f"   H3 elements: {len(h3_elements)} results")
                
                # Test 4: Look for links
                links = soup.find_all('a', href=True)
                print(f"   Links with href: {len(links)} results")
                
                # Test 5: Look for specific patterns
                if h3_elements:
                    print("\n📋 Sample H3 elements:")
                    for i, h3 in enumerate(h3_elements[:5]):
                        print(f"   {i+1}. Class: {h3.get('class', 'No class')}")
                        print(f"      Text: {h3.get_text(strip=True)[:100]}...")
                        print(f"      Has link: {bool(h3.find('a'))}")
                
                # Test 6: Look for any text containing "solar" or "energy"
                solar_texts = soup.find_all(text=re.compile(r'solar|energy', re.IGNORECASE))
                print(f"\n🔍 Text elements containing 'solar' or 'energy': {len(solar_texts)} results")
                
                if solar_texts:
                    print("   Sample texts:")
                    for i, text in enumerate(solar_texts[:5]):
                        clean_text = text.strip()[:100]
                        if clean_text:
                            print(f"     {i+1}. {clean_text}...")
                
    except Exception as e:
        print(f"❌ Error debugging Google Scholar: {e}")
        import traceback
        traceback.print_exc()

async def debug_google_patents():
    """Debug Google Patents HTML structure"""
    try:
        print("\n🔬 Debugging Google Patents HTML structure...")
        
        keyword = "solar energy"
        search_url = f"https://patents.google.com/?q={keyword.replace(' ', '+')}&sort=new"
        
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
                    print(f"❌ Failed to fetch Google Patents: {response.status}")
                    return
                
                html = await response.text()
                print(f"✅ Successfully fetched Google Patents results ({len(html)} characters)")
                
                # Save HTML for inspection
                with open('debug_patents.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print("💾 Saved HTML to debug_patents.html")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try different selectors
                print("\n🔍 Testing different selectors:")
                
                # Test 1: Look for patent result containers
                patent_results = soup.find_all('article')
                print(f"   Article elements: {len(patent_results)} results")
                
                # Test 2: Look for divs with patent-related classes
                patent_divs = soup.find_all('div', class_=re.compile(r'patent|result|item', re.IGNORECASE))
                print(f"   Divs with patent/result/item in class: {len(patent_divs)} results")
                
                # Test 3: Look for links to patents
                patent_links = soup.find_all('a', href=re.compile(r'/patent/'))
                print(f"   Links to patents: {len(patent_links)} results")
                
                # Test 4: Look for any text containing "patent" or "invention"
                patent_texts = soup.find_all(text=re.compile(r'patent|invention', re.IGNORECASE))
                print(f"   Text elements containing 'patent' or 'invention': {len(patent_texts)} results")
                
                # Test 5: Look for specific patent elements
                if patent_links:
                    print("\n📋 Sample patent links:")
                    for i, link in enumerate(patent_links[:5]):
                        print(f"   {i+1}. Href: {link.get('href', 'No href')}")
                        print(f"      Text: {link.get_text(strip=True)[:100]}...")
                        print(f"      Class: {link.get('class', 'No class')}")
                
    except Exception as e:
        print(f"❌ Error debugging Google Patents: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run both debug functions"""
    print("🐛 Starting scraping debug session...")
    print("=" * 60)
    
    await debug_google_scholar()
    await debug_google_patents()
    
    print("\n" + "=" * 60)
    print("✅ Debug session completed!")
    print("📁 Check debug_scholar.html and debug_patents.html for HTML content")

if __name__ == "__main__":
    asyncio.run(main())
