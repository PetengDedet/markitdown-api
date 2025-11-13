#!/usr/bin/env python3
"""
Test script to verify the LLM integration works correctly.
This script tests the entire workflow without requiring the actual model file.
"""

import os
import sys
import tempfile
from datetime import datetime

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import app
        import models
        import llm_utils
        import ocr_utils
        print("✓ All modules imported successfully\n")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}\n")
        return False


def test_llm_utils():
    """Test LLM utilities."""
    print("Testing LLM utilities...")
    try:
        import llm_utils
        
        # Test model info
        info = llm_utils.get_model_info()
        assert isinstance(info, dict)
        assert 'loaded' in info
        assert 'model_path' in info
        assert 'model_exists' in info
        print(f"✓ get_model_info() works: {info}")
        
        # Test is_model_loaded
        loaded = llm_utils.is_model_loaded()
        assert isinstance(loaded, bool)
        print(f"✓ is_model_loaded() works: {loaded}")
        
        # Test prompt creation
        prompt = llm_utils.create_prompt("Test content", "summarize_and_correct")
        assert isinstance(prompt, str)
        assert "Test content" in prompt
        print(f"✓ create_prompt() works (length: {len(prompt)})")
        
        # Test process_document without model (should return None gracefully)
        result = llm_utils.process_document("Test content")
        assert result is None  # No model loaded, should return None
        print(f"✓ process_document() handles missing model gracefully")
        
        print("✓ All LLM utility tests passed\n")
        return True
    except Exception as e:
        print(f"✗ LLM utils test failed: {e}\n")
        return False


def test_database_model():
    """Test database model with summary_content field."""
    print("Testing database model...")
    try:
        from models import init_db, get_session, init_default_config, Conversion, AppConfig
        
        # Create temporary database
        test_db = tempfile.mktemp(suffix='.db')
        engine = init_db(f'sqlite:///{test_db}')
        session = get_session(engine)
        
        # Initialize config
        init_default_config(session)
        
        # Test LLM config values
        llm_enabled = session.query(AppConfig).filter_by(key='llm_enabled').first()
        assert llm_enabled is not None
        assert llm_enabled.value == 'false'
        print(f"✓ LLM config initialized: llm_enabled={llm_enabled.value}")
        
        llm_task = session.query(AppConfig).filter_by(key='llm_task').first()
        assert llm_task is not None
        print(f"✓ LLM config initialized: llm_task={llm_task.value}")
        
        # Test creating conversion with summary
        conversion = Conversion(
            filename="test.txt",
            original_path="/tmp/test.txt",
            markdown_content="# Original markdown",
            summary_content="Summarized content",
            file_size=100
        )
        session.add(conversion)
        session.commit()
        
        # Verify
        saved = session.query(Conversion).first()
        assert saved.id == 1
        assert saved.markdown_content == "# Original markdown"
        assert saved.summary_content == "Summarized content"
        print(f"✓ Conversion with summary saved: ID={saved.id}")
        
        # Test to_dict includes summary
        conversion_dict = saved.to_dict()
        assert 'summary_content' in conversion_dict
        assert conversion_dict['summary_content'] == "Summarized content"
        print(f"✓ to_dict() includes summary_content")
        
        # Clean up
        session.close()
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✓ All database model tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Database model test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_app_integration():
    """Test Flask app configuration."""
    print("Testing Flask app integration...")
    try:
        from app import app
        from models import init_db, get_session, init_default_config, AppConfig
        
        # Create test database
        test_db = tempfile.mktemp(suffix='.db')
        engine = init_db(f'sqlite:///{test_db}')
        session = get_session(engine)
        init_default_config(session)
        
        # Test that app has LLM-related imports
        import app as app_module
        assert hasattr(app_module, 'process_document')
        assert hasattr(app_module, 'initialize_llm')
        assert hasattr(app_module, 'get_model_info')
        print("✓ App has LLM imports")
        
        # Test app instance exists
        assert app is not None
        print("✓ Flask app instance created")
        
        # Clean up
        session.close()
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✓ All app integration tests passed\n")
        return True
    except Exception as e:
        print(f"✗ App integration test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_quality():
    """Test that prompts are well-formatted for Bahasa Indonesia."""
    print("Testing prompt quality...")
    try:
        import llm_utils
        
        # Test Bahasa Indonesia content
        indonesian_content = """
# Laporan Tahunan 2024

Perusahaan kami telah mengalami pertumbuhan yang signifikan.
Kami berkomitmen untuk memberikan pelayanan terbaik kepada pelanggan.
"""
        
        prompt = llm_utils.create_prompt(indonesian_content, "summarize_and_correct")
        
        # Check that prompt mentions Bahasa Indonesia
        assert "Bahasa Indonesia" in prompt
        print("✓ Prompt mentions Bahasa Indonesia support")
        
        # Check that it includes the content
        assert "Laporan Tahunan" in prompt
        print("✓ Prompt includes Indonesian content")
        
        # Test correct_only task
        prompt2 = llm_utils.create_prompt(indonesian_content, "correct_only")
        assert "correct" in prompt2.lower()
        assert "without summarizing" in prompt2.lower()
        print("✓ correct_only prompt properly formatted")
        
        print("✓ All prompt quality tests passed\n")
        return True
    except Exception as e:
        print(f"✗ Prompt quality test failed: {e}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM Integration Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Imports", test_imports),
        ("LLM Utilities", test_llm_utils),
        ("Database Model", test_database_model),
        ("App Integration", test_app_integration),
        ("Prompt Quality", test_prompt_quality),
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
