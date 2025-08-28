#!/usr/bin/env python3
"""
Mock data module for providing fallback results when real scraping fails
"""

def get_mock_scholar_results(keyword: str, max_results: int = 30) -> list:
    """Generate mock Google Scholar results for testing"""
    mock_results = []
    
    research_areas = {
        'solar': ['Solar Energy Systems', 'Photovoltaic Technology', 'Solar Panel Efficiency', 'Renewable Energy Integration'],
        'wind': ['Wind Power Generation', 'Turbine Technology', 'Offshore Wind Farms', 'Wind Energy Storage'],
        'battery': ['Battery Technology', 'Energy Storage Systems', 'Lithium-ion Batteries', 'Grid-scale Storage'],
        'energy': ['Renewable Energy', 'Energy Efficiency', 'Smart Grid Technology', 'Sustainable Power Systems'],
        'startup': ['Startup Funding', 'Venture Capital', 'Innovation Ecosystems', 'Entrepreneurship'],
        'technology': ['Emerging Technologies', 'Digital Innovation', 'AI and Machine Learning', 'Blockchain Applications']
    }
    
    # Get relevant research areas for the keyword
    relevant_areas = []
    for area, topics in research_areas.items():
        if area.lower() in keyword.lower():
            relevant_areas.extend(topics)
    
    # If no specific areas match, use general topics
    if not relevant_areas:
        relevant_areas = ['Technology Innovation', 'Research and Development', 'Scientific Discovery', 'Industry Applications']
    
    for i in range(min(max_results, 20)):  # Limit to 20 mock results
        area = relevant_areas[i % len(relevant_areas)]
        mock_results.append({
            "title": f"{area}: {keyword.title()} Research and Applications",
            "url": f"https://scholar.google.com/mock_{i+1}",
            "authors": [f"Dr. {area.split()[0]} Researcher", f"Prof. {keyword.title()} Expert"],
            "abstract": f"This research paper explores the applications of {keyword} in {area.lower()}. The study investigates various approaches and methodologies for implementing {keyword} technologies in modern systems. Results show significant improvements in efficiency and performance.",
            "year": 2024 - (i % 5),
            "citations": max(0, 150 - i * 8),
            "source": "Google Scholar (Mock)"
        })
    
    return mock_results

def get_mock_patent_results(keyword: str, max_results: int = 30) -> list:
    """Generate mock Google Patents results for testing"""
    mock_results = []
    
    patent_types = {
        'solar': ['Solar Panel Mounting System', 'Photovoltaic Cell Assembly', 'Solar Energy Collection Device'],
        'wind': ['Wind Turbine Blade Design', 'Offshore Wind Platform', 'Wind Energy Storage System'],
        'battery': ['Battery Management System', 'Energy Storage Device', 'Lithium Battery Assembly'],
        'energy': ['Energy Distribution System', 'Power Management Device', 'Renewable Energy Controller'],
        'startup': ['Business Process Method', 'Innovation Management System', 'Startup Analytics Platform'],
        'technology': ['Digital Processing System', 'Information Management Device', 'Technology Integration Platform']
    }
    
    # Get relevant patent types for the keyword
    relevant_types = []
    for area, types in patent_types.items():
        if area.lower() in keyword.lower():
            relevant_types.extend(types)
    
    # If no specific types match, use general patent types
    if not relevant_types:
        relevant_types = ['Innovation System', 'Technology Device', 'Process Method', 'Application Platform']
    
    for i in range(min(max_results, 20)):  # Limit to 20 mock results
        patent_type = relevant_types[i % len(relevant_types)]
        mock_results.append({
            "title": f"{patent_type} for {keyword.title()} Applications",
            "url": f"https://patents.google.com/patent/MOCK{i+1:06d}",
            "description": f"This patent describes a {patent_type.lower()} specifically designed for {keyword} applications. The invention provides improved efficiency, reliability, and performance in {keyword}-related systems.",
            "inventors": [f"Inventor {i+1} Name", f"Co-Inventor {i+1} Name"],
            "filing_date": f"{2024 - (i % 5)}",
            "publication_date": f"{2024 - (i % 3)}",
            "assignee": f"Company {i+1} Inc.",
            "source": "Google Patents (Mock)"
        })
    
    return mock_results

def get_mock_results_summary(keyword: str) -> dict:
    """Get a summary of mock results for a keyword"""
    scholar_results = get_mock_scholar_results(keyword, 5)
    patent_results = get_mock_patent_results(keyword, 5)
    
    return {
        "keyword": keyword,
        "scholar_papers": len(scholar_results),
        "patents": len(patent_results),
        "total_sources": len(scholar_results) + len(patent_results),
        "sample_scholar": scholar_results[0] if scholar_results else None,
        "sample_patent": patent_results[0] if patent_results else None
    }
