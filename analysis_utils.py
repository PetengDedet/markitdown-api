"""Document analysis utilities for feature extraction and classification.

This module provides lightweight, local-execution tools for document analysis:
- Category Prediction: Multi-label classification
- Keyword Extraction: TF-IDF and frequency-based extraction
- Severity Classification: Document importance/urgency classification
- Title Prediction: Rule-based and pattern-based title generation
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter
import string

logger = logging.getLogger(__name__)

# Pre-defined categories for document classification
DEFAULT_CATEGORIES = [
    "Business",
    "Technical",
    "Legal",
    "Financial",
    "Educational",
    "Medical",
    "Report",
    "Proposal",
    "Invoice",
    "Contract",
    "Research",
    "Manual",
    "Correspondence",
    "Other"
]

# Severity levels
SEVERITY_LEVELS = [
    "Critical",
    "Important",
    "Normal",
    "Low Priority"
]

# Keywords for category detection (simple rule-based approach)
CATEGORY_KEYWORDS = {
    "Business": ["business", "strategy", "management", "marketing", "sales", "revenue", "profit"],
    "Technical": ["technical", "software", "hardware", "system", "code", "programming", "development", "API"],
    "Legal": ["legal", "contract", "agreement", "law", "compliance", "regulation", "clause", "liability"],
    "Financial": ["financial", "invoice", "payment", "budget", "cost", "expense", "accounting", "tax"],
    "Educational": ["education", "learning", "course", "training", "student", "teacher", "curriculum"],
    "Medical": ["medical", "health", "patient", "diagnosis", "treatment", "clinical", "hospital"],
    "Report": ["report", "summary", "analysis", "findings", "conclusion", "results", "data"],
    "Proposal": ["proposal", "plan", "recommendation", "suggest", "objective", "goal"],
    "Invoice": ["invoice", "bill", "payment due", "total amount", "items", "quantity"],
    "Contract": ["contract", "agreement", "parties", "terms", "conditions", "effective date"],
    "Research": ["research", "study", "experiment", "hypothesis", "methodology", "literature"],
    "Manual": ["manual", "guide", "instructions", "how to", "steps", "procedure"],
    "Correspondence": ["dear", "sincerely", "regards", "letter", "memo", "email"]
}

# Keywords for severity detection
SEVERITY_KEYWORDS = {
    "Critical": ["urgent", "critical", "emergency", "immediate", "asap", "deadline", "priority high"],
    "Important": ["important", "significant", "priority", "attention", "required", "action needed"],
    "Normal": ["normal", "standard", "regular", "routine"],
    "Low Priority": ["low priority", "optional", "fyi", "for your information", "non-urgent"]
}


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract important keywords from text using frequency analysis.
    
    Args:
        text: Input text content
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of extracted keywords
    """
    try:
        # Convert to lowercase and remove special characters
        text = text.lower()
        
        # Common stop words (English and some Indonesian)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
            'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'don',
            'now', 'yang', 'dan', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada',
            'adalah', 'ini', 'itu', 'akan', 'telah', 'dapat', 'juga', 'ada'
        }
        
        # Extract words (alphanumeric only)
        words = re.findall(r'\b[a-z]{3,}\b', text)
        
        # Filter stop words and count frequency
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Get top keywords
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        logger.info(f"Extracted {len(keywords)} keywords from text")
        return keywords
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []


def predict_categories(text: str, max_categories: int = 3, threshold: float = 0.1) -> List[Dict[str, any]]:
    """
    Predict document categories using keyword matching.
    
    Args:
        text: Input text content
        max_categories: Maximum number of categories to return
        threshold: Minimum score threshold (0-1)
        
    Returns:
        List of category predictions with scores
    """
    try:
        text_lower = text.lower()
        category_scores = {}
        
        # Calculate score for each category
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                # Count occurrences of keyword
                count = text_lower.count(keyword.lower())
                if count > 0:
                    score += count
                    matches.append(keyword)
            
            # Normalize score by text length (per 1000 chars)
            text_length = len(text)
            if text_length > 0:
                normalized_score = (score / text_length) * 1000
                category_scores[category] = {
                    'score': normalized_score,
                    'matches': matches[:5]  # Keep top 5 matches
                }
        
        # Sort by score and filter by threshold
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Get top categories above threshold
        results = []
        for category, data in sorted_categories[:max_categories]:
            if data['score'] >= threshold:
                results.append({
                    'category': category,
                    'confidence': min(data['score'] / 10, 1.0),  # Cap at 1.0
                    'matches': data['matches']
                })
        
        # If no categories meet threshold, return "Other"
        if not results:
            results.append({
                'category': 'Other',
                'confidence': 0.5,
                'matches': []
            })
        
        logger.info(f"Predicted {len(results)} categories")
        return results
        
    except Exception as e:
        logger.error(f"Error predicting categories: {str(e)}")
        return [{'category': 'Other', 'confidence': 0.5, 'matches': []}]


def predict_severity(text: str) -> Dict[str, any]:
    """
    Predict document severity/importance level.
    
    Args:
        text: Input text content
        
    Returns:
        Dictionary with severity level and confidence
    """
    try:
        text_lower = text.lower()
        severity_scores = {}
        
        # Calculate score for each severity level
        for severity, keywords in SEVERITY_KEYWORDS.items():
            score = 0
            matches = []
            
            for keyword in keywords:
                count = text_lower.count(keyword.lower())
                if count > 0:
                    score += count
                    matches.append(keyword)
            
            severity_scores[severity] = {
                'score': score,
                'matches': matches
            }
        
        # Find highest scoring severity
        max_severity = max(severity_scores.items(), key=lambda x: x[1]['score'])
        
        # If no keywords found, default to Normal
        if max_severity[1]['score'] == 0:
            return {
                'severity': 'Normal',
                'confidence': 0.5,
                'matches': []
            }
        
        # Calculate confidence based on score
        total_score = sum(s['score'] for s in severity_scores.values())
        confidence = max_severity[1]['score'] / total_score if total_score > 0 else 0.5
        
        return {
            'severity': max_severity[0],
            'confidence': min(confidence, 1.0),
            'matches': max_severity[1]['matches'][:3]
        }
        
    except Exception as e:
        logger.error(f"Error predicting severity: {str(e)}")
        return {'severity': 'Normal', 'confidence': 0.5, 'matches': []}


def predict_title_simple(text: str, max_length: int = 100) -> Optional[str]:
    """
    Predict document title using simple heuristics.
    Fallback for when LLM is not available.
    
    Args:
        text: Input text content
        max_length: Maximum title length
        
    Returns:
        Predicted title or None
    """
    try:
        lines = text.strip().split('\n')
        
        # Strategy 1: Look for markdown heading
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('#'):
                # Extract heading text
                title = re.sub(r'^#+\s*', '', line).strip()
                if title and len(title) <= max_length:
                    return title
        
        # Strategy 2: Look for patterns like "Title:", "Subject:", etc.
        for line in lines[:10]:
            line = line.strip()
            match = re.match(r'^(title|subject|re|topic|document):\s*(.+)$', line, re.IGNORECASE)
            if match:
                title = match.group(2).strip()
                if title and len(title) <= max_length:
                    return title
        
        # Strategy 3: Use first non-empty line
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) <= max_length:
                # Clean up
                title = re.sub(r'[^\w\s\-,.:()]', '', line)
                if len(title) > 10:  # Minimum meaningful length
                    return title[:max_length]
        
        # Strategy 4: Extract from first sentence
        first_text = ' '.join(lines[:3])
        sentences = re.split(r'[.!?]\s+', first_text)
        if sentences:
            title = sentences[0].strip()
            if len(title) > 10 and len(title) <= max_length:
                return title[:max_length]
        
        logger.info("Could not predict title using simple heuristics")
        return None
        
    except Exception as e:
        logger.error(f"Error predicting title: {str(e)}")
        return None


def extract_text_statistics(text: str) -> Dict[str, any]:
    """
    Extract basic statistics about the text.
    
    Args:
        text: Input text content
        
    Returns:
        Dictionary with text statistics
    """
    try:
        # Basic counts
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        
        # Sentence count (approximate)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Paragraph count (approximate - blank line separated)
        paragraphs = re.split(r'\n\s*\n', text)
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        return {
            'characters': char_count,
            'words': word_count,
            'lines': line_count,
            'sentences': sentence_count,
            'paragraphs': paragraph_count,
            'avg_words_per_sentence': round(word_count / sentence_count, 1) if sentence_count > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error extracting text statistics: {str(e)}")
        return {}


# Test function
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    # Business Proposal for Technical Development
    
    This is an urgent proposal for developing a new software system.
    We need to implement this project immediately to meet critical deadlines.
    
    Key requirements:
    - Software development
    - System integration
    - API development
    - Technical documentation
    
    Budget: $100,000
    Timeline: 3 months
    Priority: High
    """
    
    print("Testing Document Analysis Utilities")
    print("=" * 60)
    
    print("\n1. Keywords:")
    keywords = extract_keywords(sample_text)
    print(f"   {keywords}")
    
    print("\n2. Categories:")
    categories = predict_categories(sample_text)
    for cat in categories:
        print(f"   {cat['category']}: {cat['confidence']:.2f} - {cat['matches']}")
    
    print("\n3. Severity:")
    severity = predict_severity(sample_text)
    print(f"   {severity['severity']}: {severity['confidence']:.2f} - {severity['matches']}")
    
    print("\n4. Title:")
    title = predict_title_simple(sample_text)
    print(f"   {title}")
    
    print("\n5. Statistics:")
    stats = extract_text_statistics(sample_text)
    for key, value in stats.items():
        print(f"   {key}: {value}")
