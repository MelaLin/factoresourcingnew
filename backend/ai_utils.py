import openai
import os
import random
import re
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_text(text):
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Use the advanced fallback system
        try:
            from fallback_matcher import fallback_matcher
            summary = fallback_matcher.generate_smart_summary(text, 300)
            keywords = fallback_matcher.extract_keywords(text, 8)
            print(f"📝 Generated smart fallback summary: {len(summary)} characters")
            return (summary, keywords)
        except ImportError:
            # Fallback to basic text analysis
            words = text.split()
            
            # Create a more intelligent summary
            if len(words) > 200:
                # Take first 150 words and last 50 words for better context
                first_part = ' '.join(words[:150])
                last_part = ' '.join(words[-50:])
                summary = f"{first_part}... {last_part}"
            elif len(words) > 100:
                summary = ' '.join(words[:100]) + "..."
            else:
                summary = text
            
            # Extract basic keywords
            keywords = extract_keywords_from_text(text)
            
            print(f"📝 Generated basic fallback summary: {len(summary)} characters")
            return (summary, keywords)
    
    # Use pattern-based summary generation instead of GPT
    try:
        # Enhanced pattern-based summary generation
        words = text.split()
        
        # Extract key business indicators
        business_keywords = ['funding', 'investment', 'raise', 'million', 'billion', 'acquisition', 'merger', 'ipo', 'revenue', 'profit', 'startup', 'venture', 'capital', 'series', 'round']
        financial_keywords = ['dollars', 'euros', 'funding', 'investment', 'valuation', 'market cap', 'revenue', 'profit', 'loss', 'growth']
        company_keywords = ['company', 'startup', 'firm', 'corporation', 'inc', 'corp', 'llc', 'ltd']
        
        # Find sentences with business indicators
        sentences = text.split('.')
        business_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in business_keywords + financial_keywords + company_keywords):
                business_sentences.append(sentence.strip())
        
        # Generate summary based on content analysis
        if len(words) > 200:
            # Take first 150 words and last 50 words for better context
            first_part = ' '.join(words[:150])
            last_part = ' '.join(words[-50:])
            summary = f"{first_part}... {last_part}"
        elif len(words) > 100:
            summary = ' '.join(words[:100]) + "..."
        else:
            summary = text
        
        # If we found business sentences, use them to enhance summary
        if business_sentences:
            business_summary = '. '.join(business_sentences[:2])  # Use top 2 business sentences
            if len(business_summary) < len(summary):
                summary = business_summary
        
        # Extract basic keywords
        keywords = extract_keywords_from_text(text)
        
        print(f"📝 Generated pattern-based summary: {len(summary)} characters")
        return summary, keywords
        
    except Exception as e:
        print(f"Error in pattern-based summary: {e}")
        # Fallback to mock response
        # Enhanced fallback summary
        words = text.split()
        if len(words) > 200:
            # Take first 150 words and last 50 words for better context
            first_part = ' '.join(words[:150])
            last_part = ' '.join(words[-50:])
            summary = f"{first_part}... {last_part}"
        elif len(words) > 100:
            summary = ' '.join(words[:100]) + "..."
        else:
            summary = text
        
        # Extract basic keywords
        keywords = extract_keywords_from_text(text)
        
        print(f"📝 Generated enhanced fallback summary: {len(summary)} characters")
        return summary, keywords

def generate_title_from_url(url: str) -> str:
    """Generate a descriptive title from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.netloc
        
        # Extract meaningful parts from the path
        path_parts = [part for part in parsed.path.split('/') if part and len(part) > 2]
        
        if path_parts:
            # Use the last meaningful path segment
            last_part = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
            return f"{last_part} - {hostname}"
        else:
            return f"Content from {hostname}"
    except Exception:
        return f"Content from {url}"

def extract_companies_from_url(url: str) -> list:
    """Extract company names from URL path"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = [part for part in parsed.path.split('/') if part and len(part) > 2]
        
        # Look for company-like patterns in URL
        companies = []
        for part in path_parts:
            if any(word in part.lower() for word in ['inc', 'corp', 'llc', 'tech', 'solutions']):
                companies.append(part.replace('-', ' ').replace('_', ' ').title())
        
        return companies[:3]  # Return max 3 companies
    except Exception:
        return []

def extract_companies(text, max_companies=10):
    """Extract company names with improved accuracy and filtering"""
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Fallback: simple company extraction when API is not available
        companies = []
        words = text.split()
        
        # Look for company-like patterns
        for i, word in enumerate(words):
            word_clean = word.strip('.,!?;:').strip()
            if len(word_clean) > 3:
                # Check for company suffixes
                if any(suffix in word_clean.lower() for suffix in ['inc', 'corp', 'llc', 'ltd', 'co', 'company']):
                    companies.append(word_clean)
                # Check for capitalized words that might be company names
                elif word_clean[0].isupper() and len(word_clean) > 4:
                    # Look for adjacent capitalized words (multi-word company names)
                    if i > 0 and words[i-1][0].isupper():
                        companies.append(f"{words[i-1]} {word_clean}")
                    elif i < len(words) - 1 and words[i+1][0].isupper():
                        companies.append(f"{word_clean} {words[i+1]}")
                    else:
                        companies.append(word_clean)
        
        # Clean up and filter results
        cleaned_companies = []
        for company in companies:
            # Remove common business words that aren't company names
            if company.lower() not in ['inc', 'corp', 'llc', 'ltd', 'co', 'company', 'companies']:
                # Clean up punctuation
                clean_company = company.strip('.,!?;:').strip()
                if len(clean_company) > 2:
                    cleaned_companies.append(clean_company)
        
        # Remove duplicates and limit results
        unique_companies = list(set(cleaned_companies))
        print(f"🏢 Generated fallback companies: {unique_companies[:max_companies]}")
        return unique_companies[:max_companies]
    
    try:
        # Use pattern-based company extraction instead of GPT
        try:
            # Enhanced pattern-based company detection
            words = text.split()
            companies = []
            
            # Look for company patterns
            for i, word in enumerate(words):
                word_clean = word.strip('.,!?;:').strip()
                if len(word_clean) > 3:
                    # Check for company suffixes
                    if any(suffix in word_clean.lower() for suffix in ['inc', 'corp', 'llc', 'ltd', 'co', 'company']):
                        # Get the full company name (previous word + current word)
                        if i > 0:
                            company_name = f"{words[i-1]} {word_clean}"
                            if company_name not in companies:
                                companies.append(company_name)
                        else:
                            if word_clean not in companies:
                                companies.append(word_clean)
                    
                    # Look for capitalized words that might be company names
                    elif word_clean[0].isupper() and len(word_clean) > 4:
                        # Check if it's not a common word
                        common_words = {'the', 'and', 'or', 'for', 'with', 'from', 'this', 'that', 'they', 'have', 'will', 'been', 'said', 'time', 'year', 'people', 'government', 'business', 'technology', 'energy', 'market', 'industry', 'company', 'investment', 'funding', 'startup', 'venture', 'capital'}
                        if word_clean.lower() not in common_words:
                            if word_clean not in companies:
                                companies.append(word_clean)
            
            # Filter out generic terms
            generic_terms = {
                'capital', 'company', 'corp', 'inc', 'llc', 'ltd', 'group', 'holdings',
                'energy', 'solutions', 'industries', 'green', 'sustainable', 'renewable',
                'technology', 'tech', 'systems', 'services', 'partners', 'ventures',
                'fund', 'investment', 'management', 'consulting', 'advisory'
            }
            
            filtered_companies = []
            for company in companies:
                company_lower = company.lower()
                # Skip if it's just generic terms
                if any(term in company_lower for term in generic_terms):
                    continue
                # Skip if it's too short
                if len(company) < 3:
                    continue
                filtered_companies.append(company)
            
            print(f"🔍 Pattern-based company extraction found {len(filtered_companies)} companies")
            return filtered_companies[:max_companies]
            
        except Exception as e:
            print(f"Error in pattern-based company extraction: {e}")
            return []
            
    except Exception as e:
        print(f"Error extracting companies: {e}")
        return []

def embed_text(text):
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Simple hash-based embedding when API is not available
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        # Generate a 1536-dimensional vector from hash
        embedding = []
        for i in range(1536):
            # Use different parts of the hash for each dimension
            start = (i * 4) % len(hash_obj.hexdigest())
            end = start + 4
            if end <= len(hash_obj.hexdigest()):
                embedding.append(float(int(hash_obj.hexdigest()[start:end], 16)) / 100000.0)
            else:
                embedding.append(0.0)
        return embedding
    
    try:
        response = openai.Embedding.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to mock embedding
        return [random.random() for _ in range(1536)]

def parse_thesis(thesis_text):
    """Parse thesis text into meaningful points and extract key concepts"""
    if not openai.api_key:
        # Simple thesis parsing when API is not available
        points = []
        lines = thesis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Only meaningful lines
                points.append(line)
        
        # Extract keywords from the thesis text
        keywords = extract_keywords_from_text(thesis_text, max_keywords=8)
        
        print(f"Simple thesis parsing: {len(points)} points, {len(keywords)} keywords")
        return points, keywords
    
    # Use pattern-based thesis parsing instead of GPT
    try:
        # Enhanced pattern-based thesis parsing
        points = []
        lines = thesis_text.split('\n')
        
        # Look for meaningful content
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Only meaningful lines
                # Skip common headers and metadata
                skip_patterns = ['abstract:', 'introduction:', 'conclusion:', 'references:', 'bibliography:', 'chapter', 'section']
                if not any(pattern in line.lower() for pattern in skip_patterns):
                    points.append(line)
        
        # If we don't have enough points, split longer lines
        if len(points) < 3:
            # Split very long lines into smaller points
            new_points = []
            for point in points:
                if len(point) > 200:
                    # Split by sentences
                    sentences = point.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 20:
                            new_points.append(sentence)
                else:
                    new_points.append(point)
            points = new_points
        
        # Extract keywords using pattern analysis
        keywords = extract_keywords_from_text(thesis_text, max_keywords=8)
        
        print(f"Pattern-based thesis parsing: {len(points)} points, {len(keywords)} keywords")
        return points, keywords
        
    except Exception as e:
        print(f"Error parsing thesis: {e}")
        # Fallback parsing
        points = []
        lines = thesis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                points.append(line)
        return points, ["thesis", "analysis", "content"]

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using pattern-based analysis (no GPT required)"""
    try:
        # Advanced pattern-based similarity calculation
        from difflib import SequenceMatcher
        import re
        
        # Clean and normalize texts
        def clean_text(text):
            # Remove HTML tags, extra whitespace, and normalize
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip().lower()
            return text
        
        clean_text1 = clean_text(text1)
        clean_text2 = clean_text(text2)
        
        # Method 1: Sequence similarity (character-level)
        sequence_similarity = SequenceMatcher(None, clean_text1, clean_text2).ratio()
        
        # Method 2: Word overlap (Jaccard similarity)
        words1 = set(re.findall(r'\b\w+\b', clean_text1))
        words2 = set(re.findall(r'\b\w+\b', clean_text2))
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            jaccard_similarity = len(intersection) / len(union) if union else 0.0
        else:
            jaccard_similarity = 0.0
        
        # Method 3: N-gram similarity (3-grams)
        def get_ngrams(text, n=3):
            words = text.split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        ngrams1 = set(get_ngrams(clean_text1, 3))
        ngrams2 = set(get_ngrams(clean_text2, 3))
        
        if ngrams1 and ngrams2:
            ngram_intersection = ngrams1.intersection(ngrams2)
            ngram_union = ngrams1.union(ngrams2)
            ngram_similarity = len(ngram_intersection) / len(ngram_union) if ngram_union else 0.0
        else:
            ngram_similarity = 0.0
        
        # Method 4: Keyword density similarity
        def get_keyword_density(text):
            words = re.findall(r'\b\w+\b', text)
            word_freq = {}
            for word in words:
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            return word_freq
        
        density1 = get_keyword_density(clean_text1)
        density2 = get_keyword_density(clean_text2)
        
        # Calculate keyword overlap
        common_keywords = set(density1.keys()) & set(density2.keys())
        total_keywords = set(density1.keys()) | set(density2.keys())
        
        if total_keywords:
            keyword_similarity = len(common_keywords) / len(total_keywords)
        else:
            keyword_similarity = 0.0
        
        # Weighted combination of all methods
        final_similarity = (
            sequence_similarity * 0.3 +
            jaccard_similarity * 0.3 +
            ngram_similarity * 0.2 +
            keyword_similarity * 0.2
        )
        
        print(f"🔍 Pattern-based similarity: sequence={sequence_similarity:.3f}, jaccard={jaccard_similarity:.3f}, ngram={ngram_similarity:.3f}, keyword={keyword_similarity:.3f}, final={final_similarity:.3f}")
        
        return min(max(final_similarity, 0.0), 1.0)
        
    except Exception as e:
        print(f"Error in pattern-based similarity: {e}")
        # Ultimate fallback: simple word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        if len(union) == 0:
            return 0.0
        return len(intersection) / len(union)

def extract_keywords_from_text(text, max_keywords=8):
    """Extract keywords from text using simple text analysis"""
    try:
        # Simple keyword extraction based on word frequency
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords]]
        
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return ["content", "article", "information"]

def analyze_thesis_alignment(article_text: str, thesis_points: list, thesis_keywords: list) -> dict:
    """Analyze how well an article aligns with the user's thesis using pattern-based analysis"""
    try:
        print(f"🎯 Analyzing thesis alignment using pattern-based system...")
        
        # Use the new pattern-based similarity function
        alignment_score = 0.0
        matched_points = []
        alignment_reasons = []
        
        # Method 1: Keyword matching with pattern analysis
        article_lower = article_text.lower()
        thesis_keywords_lower = [kw.lower() for kw in thesis_keywords]
        
        # Calculate keyword similarity using pattern matching
        keyword_matches = 0
        for keyword in thesis_keywords_lower:
            if keyword in article_lower:
                keyword_matches += 1
        
        keyword_score = 0.0
        if thesis_keywords:
            keyword_score = keyword_matches / len(thesis_keywords)
            alignment_score += keyword_score * 0.4
            alignment_reasons.append(f"Keyword match: {keyword_matches}/{len(thesis_keywords)} ({keyword_score:.2f})")
        
        # Method 2: Thesis point matching using similarity
        point_scores = []
        for point in thesis_points:
            point_similarity = calculate_text_similarity(point, article_text)
            point_scores.append(point_similarity)
            if point_similarity > 0.3:  # Threshold for considering a point matched
                matched_points.append(point)
                alignment_score += point_similarity * 0.3
        
        # Method 3: Overall content similarity
        thesis_content = ' '.join(thesis_points + thesis_keywords)
        content_similarity = calculate_text_similarity(thesis_content, article_text)
        alignment_score += content_similarity * 0.3
        
        # Method 4: Domain-specific scoring
        domain_keywords = {
            'renewable': ['solar', 'wind', 'battery', 'energy', 'sustainable', 'green'],
            'tech': ['startup', 'funding', 'venture', 'capital', 'innovation', 'technology'],
            'business': ['market', 'company', 'investment', 'growth', 'revenue', 'profit']
        }
        
        domain_score = 0.0
        for domain, keywords in domain_keywords.items():
            domain_matches = sum(1 for kw in keywords if kw in article_lower)
            if keywords:
                domain_score += (domain_matches / len(keywords)) * 0.1
        
        alignment_score += domain_score
        
        # Ensure score is between 0 and 1
        final_score = min(max(alignment_score, 0.0), 1.0)
        
        avg_point_similarity = sum(point_scores)/len(point_scores) if point_scores else 0.0
        print(f"🎯 Pattern-based thesis alignment: keyword_score={keyword_score:.3f}, point_similarity={avg_point_similarity:.3f}, content_similarity={content_similarity:.3f}, final_score={final_score:.3f}")
        
        return {
            "overall_score": final_score,
            "matched_points": matched_points,
            "alignment_reasons": alignment_reasons,
            "analysis_type": "pattern_based_analysis",
            "detailed_scores": {
                "keyword_score": keyword_score,
                "point_similarity": avg_point_similarity,
                "content_similarity": content_similarity,
                "domain_score": domain_score
            }
        }
        
    except Exception as e:
        print(f"Error in pattern-based thesis alignment: {e}")
        # Ultimate fallback
        return {
            "overall_score": 0.5,
            "matched_points": [],
            "alignment_reasons": ["Fallback analysis due to error"],
            "analysis_type": "fallback_error",
            "detailed_scores": {}
        }

def extract_keywords_from_summary(summary, max_keywords=8):
    """Extract relevant keywords from a summary"""
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Fallback: simple word extraction when API is not available
        words = summary.lower().split()
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        print(f"🔑 Generated fallback keywords: {keywords[:max_keywords]}")
        return keywords[:max_keywords]
    
    # Use pattern-based keyword extraction instead of GPT
    try:
        # Enhanced pattern-based keyword extraction
        words = summary.lower().split()
        
        # Define important keyword categories
        technical_terms = ['technology', 'innovation', 'startup', 'funding', 'investment', 'venture', 'capital', 'series', 'round', 'acquisition', 'merger', 'ipo', 'revenue', 'profit', 'growth', 'market', 'industry', 'sector']
        renewable_terms = ['solar', 'wind', 'battery', 'energy', 'sustainable', 'green', 'renewable', 'climate', 'carbon', 'emissions', 'efficiency', 'storage', 'grid', 'power', 'electric', 'vehicle', 'ev']
        business_terms = ['company', 'startup', 'firm', 'corporation', 'inc', 'corp', 'llc', 'ltd', 'fund', 'management', 'consulting', 'advisory', 'partners', 'ventures', 'holdings', 'group']
        
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Score words based on importance
        word_scores = {}
        for word in words:
            word_clean = word.strip('.,!?;:').strip()
            if len(word_clean) > 3 and word_clean not in stop_words:
                score = 1
                
                # Boost score for important terms
                if word_clean in technical_terms:
                    score += 3
                if word_clean in renewable_terms:
                    score += 3
                if word_clean in business_terms:
                    score += 2
                
                # Boost score for longer words (likely technical terms)
                if len(word_clean) > 6:
                    score += 1
                
                # Boost score for capitalized words (likely proper nouns)
                if word_clean[0].isupper():
                    score += 2
                
                word_scores[word_clean] = score
        
        # Sort by score and return top keywords
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, score in sorted_words[:max_keywords]]
        
        print(f"🔑 Pattern-based keyword extraction found {len(keywords)} keywords")
        return keywords
        
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        # Fallback: simple word extraction
        words = summary.lower().split()
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:max_keywords]
