#!/usr/bin/env python3
"""
Test script to verify document analysis features work correctly.
"""

import sys
import tempfile
import json
from datetime import datetime

def test_analysis_utils():
    """Test analysis utilities functions."""
    print("Testing Analysis Utilities...")
    try:
        from analysis_utils import (
            extract_keywords,
            predict_categories,
            predict_severity,
            predict_title_simple,
            extract_text_statistics
        )
        
        # Sample business/technical document
        sample_text = """
        # Technical Business Proposal
        
        This is an urgent proposal for developing a new software system.
        We need to implement this critical project immediately to meet important deadlines.
        
        Key requirements:
        - Software development and system integration
        - API development and technical documentation
        - Budget allocation and financial planning
        - Legal compliance and contract management
        
        Total Budget: $100,000
        Timeline: 3 months
        Priority: High - Critical for business operations
        """
        
        # Test keyword extraction
        keywords = extract_keywords(sample_text, max_keywords=10)
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        print(f"✓ Keywords extracted: {keywords[:5]}...")
        
        # Test category prediction
        categories = predict_categories(sample_text, max_categories=3)
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert 'category' in categories[0]
        assert 'confidence' in categories[0]
        print(f"✓ Categories predicted: {[c['category'] for c in categories]}")
        
        # Test severity prediction
        severity = predict_severity(sample_text)
        assert isinstance(severity, dict)
        assert 'severity' in severity
        assert 'confidence' in severity
        assert severity['severity'] in ['Critical', 'Important', 'Normal', 'Low Priority']
        print(f"✓ Severity predicted: {severity['severity']} (confidence: {severity['confidence']:.2f})")
        
        # Test title prediction
        title = predict_title_simple(sample_text)
        assert isinstance(title, str) or title is None
        if title:
            print(f"✓ Title predicted: {title}")
        else:
            print("✓ Title prediction returned None (acceptable)")
        
        # Test text statistics
        stats = extract_text_statistics(sample_text)
        assert isinstance(stats, dict)
        assert 'characters' in stats
        assert 'words' in stats
        print(f"✓ Statistics extracted: {stats['words']} words, {stats['sentences']} sentences")
        
        print("✓ All analysis utility tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Analysis utils test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_database_integration():
    """Test database integration with new fields."""
    print("Testing Database Integration...")
    try:
        from models import init_db, get_session, Conversion
        import json
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db_file:
            test_db = temp_db_file.name
        
        engine = init_db(f'sqlite:///{test_db}')
        session = get_session(engine)
        
        # Create conversion with all new fields
        categories_data = json.dumps([
            {"category": "Technical", "confidence": 0.95},
            {"category": "Business", "confidence": 0.87}
        ])
        keywords_data = json.dumps(["software", "development", "system", "api"])
        
        conversion = Conversion(
            filename="test_doc.pdf",
            original_path="/tmp/test_doc.pdf",
            markdown_content="# Test Document\n\nThis is a test.",
            summary_content="This is a summary.",
            predicted_title="Test Document Title",
            categories=categories_data,
            keywords=keywords_data,
            severity="Important",
            corrected_content="# Corrected Document\n\nThis is corrected.",
            file_size=1024
        )
        session.add(conversion)
        session.commit()
        
        # Verify all fields
        saved = session.query(Conversion).first()
        assert saved.id == 1
        assert saved.predicted_title == "Test Document Title"
        assert saved.categories is not None
        assert saved.keywords is not None
        assert saved.severity == "Important"
        assert saved.corrected_content is not None
        print(f"✓ Conversion saved with all fields")
        
        # Test to_dict includes new fields
        conversion_dict = saved.to_dict()
        assert 'categories' in conversion_dict
        assert 'keywords' in conversion_dict
        assert 'severity' in conversion_dict
        assert 'corrected_content' in conversion_dict
        assert isinstance(conversion_dict['categories'], list)
        assert isinstance(conversion_dict['keywords'], list)
        print(f"✓ to_dict() includes all new fields")
        
        # Verify JSON parsing works
        assert len(conversion_dict['categories']) == 2
        assert conversion_dict['categories'][0]['category'] == 'Technical'
        assert len(conversion_dict['keywords']) == 4
        print(f"✓ JSON fields parsed correctly")
        
        # Clean up
        session.close()
        import os
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✓ All database integration tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Database integration test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_feature_combinations():
    """Test different combinations of features."""
    print("Testing Feature Combinations...")
    try:
        from analysis_utils import (
            extract_keywords,
            predict_categories,
            predict_severity,
            predict_title_simple
        )
        
        # Test with minimal text
        minimal_text = "Important: Review this document."
        
        keywords = extract_keywords(minimal_text, max_keywords=5)
        categories = predict_categories(minimal_text, max_categories=2)
        severity = predict_severity(minimal_text)
        title = predict_title_simple(minimal_text)
        
        print(f"✓ Minimal text processed: keywords={len(keywords)}, categories={len(categories)}")
        
        # Test with very long text
        long_text = "Business report. " * 1000  # Repetitive long text
        
        keywords = extract_keywords(long_text, max_keywords=10)
        categories = predict_categories(long_text, max_categories=3)
        
        assert len(keywords) <= 10
        assert len(categories) <= 3
        print(f"✓ Long text processed with limits respected")
        
        # Test with Indonesian text
        indonesian_text = """
        # Laporan Bisnis Tahunan
        
        Ini adalah laporan penting untuk perusahaan.
        Kami perlu segera menindaklanjuti proposal ini.
        Anggaran yang dibutuhkan adalah Rp 500.000.000.
        """
        
        keywords = extract_keywords(indonesian_text, max_keywords=10)
        categories = predict_categories(indonesian_text, max_categories=3)
        severity = predict_severity(indonesian_text)
        
        print(f"✓ Indonesian text processed successfully")
        
        print("✓ All feature combination tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Feature combination test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing Edge Cases...")
    try:
        from analysis_utils import (
            extract_keywords,
            predict_categories,
            predict_severity,
            predict_title_simple
        )
        
        # Test with empty text
        empty_text = ""
        keywords = extract_keywords(empty_text)
        assert isinstance(keywords, list)
        print(f"✓ Empty text handled: {len(keywords)} keywords")
        
        # Test with only whitespace
        whitespace_text = "   \n\n   \t  "
        categories = predict_categories(whitespace_text)
        assert isinstance(categories, list)
        print(f"✓ Whitespace text handled: {len(categories)} categories")
        
        # Test with special characters
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        severity = predict_severity(special_text)
        assert isinstance(severity, dict)
        print(f"✓ Special characters handled: severity={severity['severity']}")
        
        # Test with numbers only
        numbers_text = "123456789 000 111 222"
        title = predict_title_simple(numbers_text)
        # Title may be None for numbers-only text, which is acceptable
        print(f"✓ Numbers-only text handled")
        
        print("✓ All edge case tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Edge case test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Document Analysis Features Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Analysis Utilities", test_analysis_utils),
        ("Database Integration", test_database_integration),
        ("Feature Combinations", test_feature_combinations),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}\n")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print()
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
