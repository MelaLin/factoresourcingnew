"""
Fallback Matching System - Works entirely offline without OpenAI API
Uses advanced text analysis techniques for content matching
"""

import re
import math
from collections import Counter
from typing import List, Dict, Tuple
import hashlib

class FallbackMatcher:
    """Advanced text-based matching system that works without AI"""
    
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'from', 'into', 'during', 'including', 'until', 'against', 'among', 'throughout',
            'despite', 'towards', 'upon', 'concerning', 'about', 'over', 'above', 'below',
            'inside', 'outside', 'within', 'without', 'before', 'after', 'since', 'while',
            'because', 'although', 'unless', 'whereas', 'whenever', 'wherever', 'however',
            'therefore', 'moreover', 'furthermore', 'nevertheless', 'consequently'
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 15) -> List[str]:
        """Extract meaningful keywords from text using TF-IDF principles"""
        # Clean and normalize text
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter out stop words and short words
        meaningful_words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        # Count word frequencies
        word_counts = Counter(meaningful_words)
        
        # Calculate word importance (simple TF-IDF approximation)
        total_words = len(meaningful_words)
        word_scores = {}
        
        for word, count in word_counts.items():
            # Higher score for words that appear multiple times but not too frequently
            frequency = count / total_words
            if frequency > 0.001 and frequency < 0.1:  # Sweet spot for importance
                word_scores[word] = count * (1 - frequency)
            else:
                word_scores[word] = count * 0.5
        
        # Return top keywords by score
        sorted_keywords = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        return [word for word, score in sorted_keywords[:max_keywords]]
    
    def extract_companies(self, text: str, max_companies: int = 10) -> List[str]:
        """Extract company names using pattern matching"""
        companies = set()
        
        # Common company patterns
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Group|Technologies|Solutions|Systems|Software|AI|ML|Tech|Ventures|Capital|Partners|Associates|Consulting|Services)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+&\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z][a-z]+\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match.split()) >= 2 and len(match) > 5:
                    companies.add(match.strip())
        
        # Fallback: look for capitalized word sequences
        words = text.split()
        for i in range(len(words) - 1):
            if (words[i][0].isupper() and words[i+1][0].isupper() and 
                len(words[i]) > 2 and len(words[i+1]) > 2):
                potential_company = f"{words[i]} {words[i+1]}"
                if len(potential_company) > 5:
                    companies.add(potential_company)
        
        return list(companies)[:max_companies]
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using multiple metrics"""
        # Normalize texts
        text1 = text1.lower()
        text2 = text2.lower()
        
        # Extract keywords from both texts
        keywords1 = set(self.extract_keywords(text1, 20))
        keywords2 = set(self.extract_keywords(text2, 20))
        
        # Jaccard similarity for keyword overlap
        if keywords1 and keywords2:
            intersection = len(keywords1.intersection(keywords2))
            union = len(keywords1.union(keywords2))
            keyword_similarity = intersection / union if union > 0 else 0
        else:
            keyword_similarity = 0
        
        # Word overlap similarity
        words1 = set(re.findall(r'\b\w+\b', text1))
        words2 = set(re.findall(r'\b\w+\b', text2))
        
        if words1 and words2:
            word_intersection = len(words1.intersection(words2))
            word_union = len(words1.union(words2))
            word_similarity = word_intersection / word_union if word_union > 0 else 0
        else:
            word_similarity = 0
        
        # Content length similarity (prefer articles of similar length to thesis)
        length1, length2 = len(text1), len(text2)
        if length1 > 0 and length2 > 0:
            length_similarity = 1 - abs(length1 - length2) / max(length1, length2)
        else:
            length_similarity = 0
        
        # Weighted combination of similarities
        final_similarity = (keyword_similarity * 0.5 + 
                           word_similarity * 0.3 + 
                           length_similarity * 0.2)
        
        return min(final_similarity, 1.0)
    
    def analyze_thesis_alignment(self, article_text: str, thesis_text: str, thesis_keywords: List[str] = None) -> Dict:
        """Analyze how well an article aligns with a thesis using text analysis"""
        if not thesis_keywords:
            thesis_keywords = self.extract_keywords(thesis_text, 15)
        
        # Calculate overall similarity
        overall_similarity = self.calculate_text_similarity(article_text, thesis_text)
        
        # Find matched keywords
        article_keywords = set(self.extract_keywords(article_text, 20))
        thesis_keywords_set = set(thesis_keywords)
        matched_keywords = list(article_keywords.intersection(thesis_keywords_set))
        
        # Calculate keyword match score
        keyword_score = len(matched_keywords) / max(len(thesis_keywords_set), 1)
        
        # Find matched concepts (longer phrases)
        thesis_concepts = self.extract_concepts(thesis_text)
        article_concepts = self.extract_concepts(article_text)
        matched_concepts = []
        
        for concept in thesis_concepts:
            if any(concept.lower() in article_text.lower() for concept in [concept]):
                matched_concepts.append(concept)
        
        # Calculate final alignment score
        alignment_score = (overall_similarity * 0.4 + 
                          keyword_score * 0.4 + 
                          (len(matched_concepts) / max(len(thesis_concepts), 1)) * 0.2)
        
        return {
            "overall_score": min(alignment_score, 1.0),
            "matched_keywords": matched_keywords,
            "matched_concepts": matched_concepts,
            "alignment_reasons": [
                f"Text similarity: {overall_similarity:.2f}",
                f"Keyword matches: {len(matched_keywords)}/{len(thesis_keywords_set)}",
                f"Concept matches: {len(matched_concepts)}/{len(thesis_concepts)}"
            ],
            "analysis_type": "fallback_text_analysis"
        }
    
    def extract_concepts(self, text: str) -> List[str]:
        """Extract meaningful concepts (phrases) from text"""
        # Look for noun phrases and technical terms
        concepts = []
        
        # Find capitalized phrases
        capitalized_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        for phrase in capitalized_phrases:
            if len(phrase.split()) >= 2 and len(phrase) > 5:
                concepts.append(phrase)
        
        # Find technical terms in quotes or parentheses
        quoted_terms = re.findall(r'"([^"]{5,})"', text)
        concepts.extend(quoted_terms)
        
        # Find terms in parentheses
        parenthetical_terms = re.findall(r'\(([^)]{5,})\)', text)
        concepts.extend(parenthetical_terms)
        
        return list(set(concepts))[:10]  # Limit to top 10 concepts
    
    def generate_smart_summary(self, text: str, max_length: int = 300) -> str:
        """Generate a smart summary without AI"""
        if len(text) <= max_length:
            return text
        
        # Extract first and last portions for better context
        first_part = text[:max_length//2]
        last_part = text[-max_length//2:]
        
        # Find a good breaking point (end of sentence)
        first_break = first_part.rfind('.')
        if first_break > max_length//3:
            first_part = first_part[:first_break + 1]
        
        last_break = last_part.find('.')
        if last_break > max_length//3:
            last_part = last_part[last_break + 1:]
        
        summary = f"{first_part.strip()}... {last_part.strip()}"
        
        # Ensure we don't exceed max length
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def create_embedding(self, text: str) -> List[float]:
        """Create a simple embedding vector without AI"""
        # Use hash-based approach for consistent embeddings
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Generate a 1536-dimensional vector (same as OpenAI embeddings)
        embedding = []
        for i in range(1536):
            # Use different parts of the hash for each dimension
            start = (i * 4) % len(hash_hex)
            end = start + 4
            if end <= len(hash_hex):
                embedding.append(float(int(hash_hex[start:end], 16)) / 100000.0)
            else:
                embedding.append(0.0)
        
        return embedding

# Global instance
fallback_matcher = FallbackMatcher()
