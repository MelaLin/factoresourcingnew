import faiss
import numpy as np
from ai_utils import embed_text, parse_thesis, calculate_text_similarity, analyze_thesis_alignment

DIM = 1536
index = faiss.IndexFlatL2(DIM)
thesis_embeddings = []
thesis_keywords = []
thesis_points = []

def add_thesis(thesis_text):
    """Add thesis with improved parsing and analysis"""
    global thesis_embeddings, thesis_keywords, thesis_points
    
    print(f"🧠 Processing thesis text of length: {len(thesis_text)}")
    
    # Parse thesis into meaningful points and keywords
    points, keywords = parse_thesis(thesis_text)
    thesis_points = points
    thesis_keywords = keywords
    
    print(f"📊 Parsed thesis into {len(points)} points and {len(keywords)} keywords")
    
    # Clear existing embeddings
    thesis_embeddings = []
    index.reset()
    
    # Add each point as an embedding
    for i, point in enumerate(points):
        if point.strip():
            print(f"🔍 Processing thesis point {i+1}: {point[:100]}...")
            try:
                emb = embed_text(point)
                thesis_embeddings.append((point, np.array(emb, dtype='float32')))
                index.add(np.array([emb], dtype='float32'))
                print(f"   ✅ Point {i+1} embedded successfully")
            except Exception as e:
                print(f"   ❌ Error embedding point {i+1}: {e}")
    
    print(f"🎯 Added {len(thesis_embeddings)} thesis points and {len(keywords)} keywords to vector store")
    
    # Print summary of thesis analysis
    if thesis_keywords:
        print(f"🔑 Top keywords: {', '.join(thesis_keywords[:10])}")
    if thesis_points:
        print(f"📝 Key points: {len(thesis_points)} main concepts identified")

def find_relevant_articles(articles):
    """Find relevant articles using multiple matching strategies with enhanced analysis"""
    matches = []
    
    print(f"🔍 Finding relevant articles from {len(articles)} articles")
    print(f"📚 Thesis has {len(thesis_embeddings)} embeddings and {len(thesis_keywords)} keywords")
    
    # If no thesis embeddings exist, return articles with default scores
    if len(thesis_embeddings) == 0:
            print("⚠️  No thesis uploaded yet, returning default matches")
            for article in articles:
                matches.append({
                    "url": article["url"],
                    "title": article.get("title", f"Content from {article['url']}"),
                    "summary": article["summary"],
                    "full_content": article.get("full_content", "Full content not available"),
                    "keywords": article["keywords"],
                    "companies": article.get("companies", []),
                    "matched_thesis_points": ["No thesis uploaded yet"],
                    "relevance_score": 1.0,
                    "match_reason": "No thesis available for comparison",
                    "detailed_scores": {
                        "vector_similarity": 0.0,
                        "keyword_overlap": 0.0,
                        "semantic_similarity": 0.0,
                        "content_quality": 0.0
                    }
                })
            return sorted(matches, key=lambda x: x["relevance_score"], reverse=True)
    
    for i, article in enumerate(articles):
        print(f"📄 Processing article {i+1}/{len(articles)}: {article.get('title', 'Unknown')}")
        
        match_scores = []
        matched_points = []
        match_reasons = []
        detailed_scores = {}
        
        # Strategy 1: Vector similarity with thesis points
        try:
            D, I = index.search(np.array([article['embedding']], dtype='float32'), min(3, len(thesis_embeddings)))
            best_vector_score = 0.0
            for j, (distance, idx) in enumerate(zip(D[0], I[0])):
                if idx < len(thesis_embeddings):
                    similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                    match_scores.append(similarity_score * 0.4)  # 40% weight
                    matched_points.append(thesis_embeddings[idx][0])
                    best_vector_score = max(best_vector_score, similarity_score)
                    detailed_scores["vector_similarity"] = best_vector_score
            
            if best_vector_score > 0:
                match_reasons.append(f"Vector similarity: {best_vector_score:.2f}")
        except Exception as e:
            print(f"   ❌ Vector search error: {e}")
            detailed_scores["vector_similarity"] = 0.0
        
        # Strategy 2: Keyword overlap
        if thesis_keywords and article.get('keywords'):
            article_keywords = set([k.lower() for k in article['keywords']])
            thesis_keywords_set = set([k.lower() for k in thesis_keywords])
            keyword_overlap = len(article_keywords.intersection(thesis_keywords_set))
            keyword_score = keyword_overlap / max(len(thesis_keywords_set), 1)
            match_scores.append(keyword_score * 0.3)  # 30% weight
            if keyword_overlap > 0:
                match_reasons.append(f"Keyword overlap: {keyword_score:.2f} ({keyword_overlap} shared)")
            detailed_scores["keyword_overlap"] = keyword_score
        else:
            detailed_scores["keyword_overlap"] = 0.0
        
        # Strategy 3: Text similarity with thesis points
        text_scores = []
        best_text_score = 0.0
        best_text_point = ""
        for point in thesis_points[:3]:  # Check top 3 points
            try:
                similarity = calculate_text_similarity(article['summary'], point)
                text_scores.append(similarity)
                match_scores.append(similarity * 0.2)  # 20% weight
                if similarity > best_text_score:
                    best_text_score = similarity
                    best_text_point = point[:50]
            except Exception as e:
                print(f"   ❌ Text similarity error: {e}")
        
        detailed_scores["text_similarity"] = max(text_scores) if text_scores else 0.0
        
        if best_text_score > 0:
            match_reasons.append(f"Text similarity: {best_text_score:.2f}")
        
        # Strategy 4: Content relevance (summary length and quality)
        summary_length = len(article['summary'])
        content_score = min(summary_length / 500.0, 1.0)  # Normalize to 0-1
        match_scores.append(content_score * 0.1)  # 10% weight
        if content_score > 0.3:  # Only show if content is substantial
            match_reasons.append(f"Content quality: {content_score:.2f}")
        detailed_scores["content_quality"] = content_score
        
        # Strategy 5: Enhanced thesis alignment analysis (works offline)
        if thesis_points and thesis_keywords:
            try:
                # Try AI analysis first, fallback to text analysis if it fails
                try:
                    alignment_analysis = analyze_thesis_alignment(
                        article.get('full_content', article.get('summary', '')),
                        thesis_points,
                        thesis_keywords
                    )
                except Exception as ai_error:
                    print(f"   ⚠️  AI analysis failed, using fallback: {ai_error}")
                    # Use fallback matcher
                    from fallback_matcher import fallback_matcher
                    alignment_analysis = fallback_matcher.analyze_thesis_alignment(
                        article.get('full_content', article.get('summary', '')),
                        ' '.join(thesis_points),
                        thesis_keywords
                    )
                
                # Add alignment score to match scores
                alignment_score = alignment_analysis.get('overall_score', 0.0)
                match_scores.append(alignment_score * 0.3)  # 30% weight for thesis alignment
                detailed_scores["thesis_alignment"] = alignment_score
                
                # Update matched points with analysis
                if alignment_analysis.get('matched_points'):
                    matched_points = alignment_analysis['matched_points']
                
                # Add alignment reasons to match reasons
                if alignment_analysis.get('alignment_reasons'):
                    match_reasons.extend(alignment_analysis['alignment_reasons'])
                
                print(f"   🎯 Thesis alignment score: {alignment_score:.2f}")
                
            except Exception as e:
                print(f"   ❌ Thesis alignment analysis failed: {e}")
        
        # Calculate final relevance score
        final_score = sum(match_scores) if match_scores else 0.0
        
        # Create enhanced match object
        match_obj = {
            "url": article["url"],
            "title": article.get("title", f"Content from {article['url']}"),
            "summary": article["summary"],
            "full_content": article.get("full_content", "Full content not available"),
            "keywords": article["keywords"],
            "companies": article.get("companies", []),
            "matched_thesis_points": matched_points[:3],  # Top 3 matched points
            "relevance_score": final_score,
            "match_reason": " | ".join(match_reasons[:3]),  # Top 3 reasons
            "detailed_scores": detailed_scores,
            "analysis": {
                "total_score": final_score,
                "strategies_used": len(match_scores),
                "best_match_type": "vector" if detailed_scores.get("vector_similarity", 0) > 0.5 else "keyword" if detailed_scores.get("keyword_overlap", 0) > 0.3 else "text"
            }
        }
        
        matches.append(match_obj)
        print(f"   ✅ Match score: {final_score:.3f} | Points: {len(matched_points)} | Keywords: {detailed_scores.get('keyword_overlap', 0):.2f}")
    
    # Sort by relevance score (highest first)
    sorted_matches = sorted(matches, key=lambda x: x["relevance_score"], reverse=True)
    
    print(f"🎯 Found {len(sorted_matches)} matches, sorted by relevance")
    for i, match in enumerate(sorted_matches[:3]):
        print(f"   #{i+1}: {match['title'][:50]}... (Score: {match['relevance_score']:.3f})")
    
    return sorted_matches
