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
    
    try:
        prompt = f"""
        Create a comprehensive, business-focused summary of the following text. Focus on:
        - Main business development or announcement
        - Key financial figures, investments, or deal values
        - Companies, technologies, and market implications
        - Strategic significance and industry impact
        - Timeline and expected outcomes
        
        Text to summarize:
        {text[:4000]}
        
        Provide a detailed summary in 3-4 sentences that captures the business significance and key details.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o for best performance
            messages=[
                {"role": "system", "content": "You are an expert at creating accurate, informative summaries. Focus on factual information and key details."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1  # Lower temperature for more consistent, accurate output
        )
        
        summary = response.choices[0].message.content
        # Extract keywords from summary
        keywords = extract_keywords_from_summary(summary)
        return summary, keywords
    except Exception as e:
        print(f"OpenAI API error: {e}")
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
        # Enhanced prompt for better company detection
        prompt = f"""
        Extract ONLY real, specific company names from this text. 
        
        IMPORTANT RULES:
        - Return ONLY actual company names, not generic terms
        - DO NOT include words like "Capital", "Company", "Corp", "Inc", "LLC" alone
        - DO NOT include generic business terms like "Energy", "Solutions", "Industries", "Green" alone
        - DO NOT include single words that are common business terms
        - Focus on recognizable brand names, startups, and established companies
        - Include parent companies and subsidiaries when mentioned
        - If unsure, exclude rather than include
        - Return company names as they appear in the text (with proper capitalization)
        
        Text to analyze:
        {text[:4000]}
        
        Return a JSON array of company names only, no explanations.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o for best performance
            messages=[
                {"role": "system", "content": "You are an expert at identifying real company names from text. Be very selective and only return actual companies. Never return generic business terms alone."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        companies_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            companies = json.loads(companies_text)
            if isinstance(companies, list):
                # Filter out generic terms and validate
                filtered_companies = []
                generic_terms = {
                    'capital', 'company', 'corp', 'inc', 'llc', 'ltd', 'group', 'holdings',
                    'energy', 'solutions', 'industries', 'green', 'sustainable', 'renewable',
                    'technology', 'tech', 'systems', 'services', 'partners', 'ventures',
                    'fund', 'investment', 'management', 'consulting', 'advisory'
                }
                
                for company in companies:
                    if isinstance(company, str) and company.strip():
                        company_clean = company.strip()
                        # Skip if it's just a generic term
                        if company_clean.lower() in generic_terms:
                            continue
                        # Skip if it's too short or too generic
                        if len(company_clean) < 3 or company_clean.lower() in ['the', 'and', 'or', 'for', 'with']:
                            continue
                        # Skip if it's just a common word
                        if len(company_clean.split()) == 1 and company_clean.lower() in generic_terms:
                            continue
                        filtered_companies.append(company_clean)
                
                return filtered_companies[:max_companies]
        except json.JSONDecodeError:
            # Fallback: try to extract from text response
            lines = companies_text.split('\n')
            companies = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('[') and not line.startswith(']') and not line.startswith('{') and not line.startswith('}'):
                    # Remove quotes and commas
                    company = line.strip('",').strip()
                    if company and len(company) > 2:
                        companies.append(company)
            
            return companies[:max_companies]
            
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
    
    try:
        prompt = f"""
        Parse this thesis text into 3-5 key points and extract 5-8 important keywords/concepts.
        Format the response as:
        POINTS:
        - Point 1
        - Point 2
        - Point 3
        
        KEYWORDS:
        keyword1, keyword2, keyword3, keyword4, keyword5
        
        Thesis text:
        {thesis_text}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        
        content = response.choices[0].message.content
        
        # Parse points
        points_section = content.split('POINTS:')[1].split('KEYWORDS:')[0] if 'POINTS:' in content else ""
        points = []
        for line in points_section.split('\n'):
            line = line.strip()
            if line.startswith('-') and len(line) > 3:
                points.append(line[1:].strip())
        
        # Parse keywords
        keywords_section = content.split('KEYWORDS:')[1] if 'KEYWORDS:' in content else ""
        keywords = []
        if keywords_section:
            keywords = [k.strip() for k in keywords_section.split(',') if k.strip()]
        
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

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity between two texts using keyword overlap and content analysis"""
    if not openai.api_key:
        # Simple similarity calculation based on word overlap
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        # Calculate Jaccard similarity
        jaccard = len(intersection) / len(union)
        
        # Boost similarity for important keywords
        important_words = {'renewable', 'energy', 'sustainable', 'climate', 'carbon', 'technology', 'business', 'solutions', 'innovation', 'startup', 'funding', 'market'}
        important_overlap = len(intersection.intersection(important_words))
        
        # Boost score if important words match
        if important_overlap > 0:
            jaccard += (important_overlap * 0.08)
        
        return max(0.0, min(jaccard, 1.0))
    
    try:
        prompt = f"""
        Rate the semantic similarity between these two texts on a scale of 0.0 to 1.0, where 1.0 is very similar and 0.0 is completely different.
        Consider:
        - Topic overlap
        - Key concepts
        - Intent/purpose
        - Target audience
        
        Text 1: {text1}
        Text 2: {text2}
        
        Return only a number between 0.0 and 1.0.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
        )
        
        result = response.choices[0].message.content.strip()
        try:
            return float(result)
        except ValueError:
            return 0.5  # Default if parsing fails
            
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        # Fallback similarity
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
    """Analyze how well an article aligns with the user's thesis"""
    # Check if OpenAI API key is available
    if not openai.api_key:
        # Use the advanced fallback system
        try:
            from fallback_matcher import fallback_matcher
            analysis = fallback_matcher.analyze_thesis_alignment(article_text, ' '.join(thesis_points), thesis_keywords)
            print(f"🎯 Generated smart fallback thesis alignment: {analysis['overall_score']:.2f}")
            return analysis
        except ImportError:
            # Fallback to basic text analysis
            alignment_score = 0.0
            matched_points = []
            alignment_reasons = []
            
            # Simple keyword matching
            article_lower = article_text.lower()
            thesis_lower = ' '.join(thesis_keywords).lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in thesis_keywords if keyword.lower() in article_lower)
            if thesis_keywords:
                keyword_score = keyword_matches / len(thesis_keywords)
                alignment_score += keyword_score * 0.4
            
            # Simple point matching
            for point in thesis_points:
                point_lower = point.lower()
                if any(word in article_lower for word in point_lower.split() if len(word) > 3):
                    matched_points.append(point)
                    alignment_score += 0.2
            
            return {
                "overall_score": min(alignment_score, 1.0),
                "matched_points": matched_points,
                "alignment_reasons": [f"Keyword match: {keyword_matches}/{len(thesis_keywords)}", f"Point matches: {len(matched_points)}"],
                "analysis_type": "fallback_text_analysis"
            }
    
    try:
        prompt = f"""
        Analyze how well this article aligns with the user's investment thesis.
        
        USER'S THESIS POINTS:
        {chr(10).join([f"- {point}" for point in thesis_points])}
        
        USER'S KEYWORDS:
        {', '.join(thesis_keywords)}
        
        ARTICLE TEXT:
        {article_text[:3000]}
        
        Provide a detailed analysis in the following JSON format:
        {{
            "overall_score": 0.85,
            "matched_points": ["Point 1", "Point 2"],
            "alignment_reasons": [
                "Strong alignment with renewable energy focus",
                "Direct mention of AI data centers",
                "Investment scale matches thesis criteria"
            ],
            "key_insights": "Brief explanation of why this article is relevant",
            "investment_implications": "What this means for the investment thesis"
        }}
        
        Score from 0.0 (no alignment) to 1.0 (perfect alignment).
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o for best performance
            messages=[
                {"role": "system", "content": "You are an expert investment analyst who evaluates content relevance to investment theses. Provide accurate, detailed analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            # Try to parse JSON response
            import json
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError:
            # Fallback parsing
            return {
                "overall_score": 0.7,
                "matched_points": thesis_points[:2] if thesis_points else [],
                "alignment_reasons": ["AI analysis completed but parsing failed"],
                "analysis_type": "ai_analysis_parsing_failed"
            }
            
    except Exception as e:
        print(f"Error analyzing thesis alignment: {e}")
        # Fallback analysis
        return {
            "overall_score": 0.5,
            "matched_points": [],
            "alignment_reasons": [f"Analysis failed: {str(e)}"],
            "analysis_type": "error_fallback"
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
    
    try:
        prompt = f"""
        Extract 5-8 most relevant keywords from this summary. Focus on:
        - Technical terms and technologies
        - Industry-specific vocabulary
        - Key concepts and themes
        - Company or product names if mentioned
        
        Summary: {summary}
        
        Return only the keywords separated by commas, no explanations.
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",  # Use GPT-4o for best performance
            messages=[
                {"role": "system", "content": "You are an expert at extracting relevant keywords from text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        keywords_text = response.choices[0].message.content.strip()
        # Split by commas and clean up
        keywords = [kw.strip().lower() for kw in keywords_text.split(',') if kw.strip()]
        return keywords[:max_keywords]
        
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        # Fallback: simple word extraction
        words = summary.lower().split()
        # Filter out common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:max_keywords]
