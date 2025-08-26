#!/usr/bin/env python3
"""
Mock data system for Google Scholar and Google Patents
Provides realistic sample data when real scraping fails due to anti-bot measures
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Sample data for different research areas
RESEARCH_AREAS = {
    "solar": {
        "scholar_papers": [
            {
                "title": "Recent Advances in Perovskite Solar Cell Technology",
                "url": "https://scholar.google.com/scholar?cluster=123456789",
                "authors": ["Zhang, L.", "Wang, H.", "Chen, X."],
                "abstract": "This paper reviews recent developments in perovskite solar cell technology, focusing on efficiency improvements and stability enhancements.",
                "year": 2024,
                "citations": 45,
                "source": "Google Scholar"
            },
            {
                "title": "Machine Learning Applications in Solar Energy Forecasting",
                "url": "https://scholar.google.com/scholar?cluster=987654321",
                "authors": ["Johnson, M.", "Brown, A.", "Davis, R."],
                "abstract": "We present a novel machine learning approach for predicting solar energy production using weather data and historical performance metrics.",
                "year": 2024,
                "citations": 23,
                "source": "Google Scholar"
            },
            {
                "title": "Grid Integration Challenges for Large-Scale Solar Installations",
                "url": "https://scholar.google.com/scholar?cluster=456789123",
                "authors": ["Smith, J.", "Wilson, E.", "Taylor, P."],
                "abstract": "Analysis of technical challenges and solutions for integrating large-scale solar installations into existing power grids.",
                "year": 2023,
                "citations": 67,
                "source": "Google Scholar"
            },
            {
                "title": "Economic Viability of Residential Solar Systems",
                "url": "https://scholar.google.com/scholar?cluster=789123456",
                "authors": ["Anderson, K.", "Miller, S.", "Thompson, L."],
                "abstract": "Comprehensive cost-benefit analysis of residential solar installations across different geographic regions and market conditions.",
                "year": 2024,
                "citations": 34,
                "source": "Google Scholar"
            },
            {
                "title": "Environmental Impact Assessment of Solar Manufacturing",
                "url": "https://scholar.google.com/scholar?cluster=321654987",
                "authors": ["Garcia, M.", "Rodriguez, C.", "Martinez, F."],
                "abstract": "Life cycle assessment of environmental impacts associated with solar panel manufacturing and deployment.",
                "year": 2023,
                "citations": 56,
                "source": "Google Scholar"
            }
        ],
        "patents": [
            {
                "title": "Flexible Solar Panel with Enhanced Durability",
                "url": "https://patents.google.com/patent/US12345678A1/en",
                "authors": ["Inventors: Lee, J.", "Inventors: Kim, S."],
                "abstract": "A flexible solar panel design incorporating novel materials and construction methods for improved durability and efficiency.",
                "publish_date": "2024-01-15",
                "patent_number": "US12345678A1",
                "source": "Google Patents"
            },
            {
                "title": "Solar Tracking System with AI Optimization",
                "url": "https://patents.google.com/patent/EP98765432B1/en",
                "authors": ["Inventors: Müller, H.", "Inventors: Schmidt, A."],
                "abstract": "Intelligent solar tracking system that uses artificial intelligence to optimize panel orientation for maximum energy capture.",
                "publish_date": "2024-02-20",
                "patent_number": "EP98765432B1",
                "source": "Google Patents"
            },
            {
                "title": "Hybrid Solar-Wind Energy Storage System",
                "url": "https://patents.google.com/patent/CN112233445B/en",
                "authors": ["Inventors: Wang, L.", "Inventors: Li, X."],
                "abstract": "Integrated energy storage system combining solar and wind power generation with advanced battery technology.",
                "publish_date": "2024-03-10",
                "patent_number": "CN112233445B",
                "source": "Google Patents"
            },
            {
                "title": "Solar Panel Cleaning Robot with Water Conservation",
                "url": "https://patents.google.com/patent/JP2024001234A/en",
                "authors": ["Inventors: Tanaka, Y.", "Inventors: Suzuki, K."],
                "abstract": "Automated cleaning system for solar panels that minimizes water usage while maintaining optimal performance.",
                "publish_date": "2024-01-30",
                "patent_number": "JP2024001234A",
                "source": "Google Patents"
            },
            {
                "title": "Transparent Solar Windows for Buildings",
                "url": "https://patents.google.com/patent/KR2024005678A/en",
                "authors": ["Inventors: Park, J.", "Inventors: Choi, M."],
                "abstract": "Transparent solar cell technology integrated into building windows for dual-purpose energy generation and natural lighting.",
                "publish_date": "2024-02-15",
                "patent_number": "KR2024005678A",
                "source": "Google Patents"
            }
        ]
    },
    "battery": {
        "scholar_papers": [
            {
                "title": "Next-Generation Lithium-Ion Battery Technology",
                "url": "https://scholar.google.com/scholar?cluster=111222333",
                "authors": ["Chen, Y.", "Liu, W.", "Zhang, Q."],
                "abstract": "Breakthrough developments in lithium-ion battery technology focusing on energy density and safety improvements.",
                "year": 2024,
                "citations": 89,
                "source": "Google Scholar"
            },
            {
                "title": "Solid-State Battery Manufacturing Processes",
                "url": "https://scholar.google.com/scholar?cluster=444555666",
                "authors": ["Williams, R.", "Johnson, T.", "Brown, M."],
                "abstract": "Scalable manufacturing processes for solid-state batteries with improved performance characteristics.",
                "year": 2024,
                "citations": 45,
                "source": "Google Scholar"
            }
        ],
        "patents": [
            {
                "title": "Solid-State Battery with Enhanced Safety",
                "url": "https://patents.google.com/patent/US87654321A1/en",
                "authors": ["Inventors: Johnson, A.", "Inventors: Smith, B."],
                "abstract": "Advanced solid-state battery design incorporating multiple safety features and improved thermal management.",
                "publish_date": "2024-03-01",
                "patent_number": "US87654321A1",
                "source": "Google Patents"
            }
        ]
    },
    "ai": {
        "scholar_papers": [
            {
                "title": "Transformer Architecture Improvements for Natural Language Processing",
                "url": "https://scholar.google.com/scholar?cluster=777888999",
                "authors": ["Kumar, A.", "Singh, R.", "Patel, N."],
                "abstract": "Novel modifications to transformer architecture for improved efficiency and performance in NLP tasks.",
                "year": 2024,
                "citations": 123,
                "source": "Google Scholar"
            }
        ],
        "patents": [
            {
                "title": "AI-Powered Energy Management System",
                "url": "https://patents.google.com/patent/EP111222333B1/en",
                "authors": ["Inventors: Schmidt, K.", "Inventors: Weber, M."],
                "abstract": "Intelligent energy management system using machine learning for optimal power distribution and consumption.",
                "publish_date": "2024-02-28",
                "patent_number": "EP111222333B1",
                "source": "Google Patents"
            }
        ]
    }
}

def get_mock_scholar_results(keyword: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """Get mock Google Scholar results for a given keyword"""
    keyword_lower = keyword.lower()
    
    # Find matching research area
    matching_area = None
    for area, data in RESEARCH_AREAS.items():
        if area in keyword_lower:
            matching_area = area
            break
    
    if not matching_area:
        # Default to solar if no specific match
        matching_area = "solar"
    
    # Get papers for the matching area
    papers = RESEARCH_AREAS[matching_area]["scholar_papers"]
    
    # Randomize and limit results
    random.shuffle(papers)
    results = papers[:min(max_results, len(papers))]
    
    # Add some randomization to make it feel more realistic
    for result in results:
        # Randomize citations slightly
        result["citations"] = max(1, result["citations"] + random.randint(-10, 10))
        # Randomize year slightly
        result["year"] = max(2020, result["year"] + random.randint(-1, 1))
    
    return results

def get_mock_patent_results(keyword: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """Get mock Google Patents results for a given keyword"""
    keyword_lower = keyword.lower()
    
    # Find matching research area
    matching_area = None
    for area, data in RESEARCH_AREAS.items():
        if area in keyword_lower:
            matching_area = area
            break
    
    if not matching_area:
        # Default to solar if no specific match
        matching_area = "solar"
    
    # Get patents for the matching area
    patents = RESEARCH_AREAS[matching_area]["patents"]
    
    # Randomize and limit results
    random.shuffle(patents)
    results = patents[:min(max_results, len(patents))]
    
    # Add some randomization to make it feel more realistic
    for result in results:
        # Randomize publish date slightly
        base_date = datetime.strptime(result["publish_date"], "%Y-%m-%d")
        random_days = random.randint(-30, 30)
        new_date = base_date + timedelta(days=random_days)
        result["publish_date"] = new_date.strftime("%Y-%m-%d")
    
    return results

def get_mock_results_summary(keyword: str) -> Dict[str, Any]:
    """Get a summary of mock results for a keyword"""
    scholar_results = get_mock_scholar_results(keyword, 25)
    patent_results = get_mock_patent_results(keyword, 25)
    
    return {
        "keyword": keyword,
        "scholar_papers_found": len(scholar_results),
        "patents_found": len(patent_results),
        "total_sources": len(scholar_results) + len(patent_results),
        "scholar_results": scholar_results,
        "patent_results": patent_results,
        "is_mock_data": True,
        "note": "Using mock data due to anti-bot measures on Google Scholar and Google Patents"
    }

if __name__ == "__main__":
    # Test the mock data system
    print("🧪 Testing Mock Data System")
    print("=" * 40)
    
    test_keywords = ["solar energy", "battery technology", "artificial intelligence"]
    
    for keyword in test_keywords:
        print(f"\n🔍 Keyword: '{keyword}'")
        summary = get_mock_results_summary(keyword)
        
        print(f"   📚 Scholar papers: {summary['scholar_papers_found']}")
        print(f"   🔬 Patents: {summary['patents_found']}")
        print(f"   📊 Total sources: {summary['total_sources']}")
        print(f"   📝 Note: {summary['note']}")
        
        if summary['scholar_results']:
            print(f"   📖 Sample paper: {summary['scholar_results'][0]['title'][:50]}...")
        if summary['patent_results']:
            print(f"   📄 Sample patent: {summary['patent_results'][0]['title'][:50]}...")
    
    print("\n✅ Mock data system test completed!")
