#!/usr/bin/env python3
"""
Test that the regex methods can handle dict inputs without crashing.
This tests the exact issue that was causing validation failures.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sefas.agents.checkers import LogicChecker, SemanticChecker, ConsistencyChecker

def test_regex_methods_with_dicts():
    """Test that all regex methods handle dict inputs safely"""
    
    print("🧪 Testing Regex Methods with Dict Inputs")
    print("=" * 50)
    
    # Create test instances
    try:
        # Use minimal configs for testing
        test_config = {
            'role': 'Logic Validation Engine',
            'model': 'gpt-4o-mini',
            'temperature': 0.1,
            'provider': 'openai'
        }
        
        checker = LogicChecker(test_config)
        print("✅ LogicChecker created successfully")
    except Exception as e:
        print(f"❌ Failed to create LogicChecker: {e}")
        return False
    
    # Test cases that were causing failures
    test_dicts = [
        {
            'analysis': 'Life originated through chemical evolution. Confidence: 0.85. Score: 8.5/10',
            'confidence': 0.85
        },
        {
            'proposal': 'RNA world hypothesis suggests early life. Rating: 7.2. Logic: sound reasoning',
            'reasoning': 'Based on experimental evidence'
        },
        {
            'content': 'Chemical evolution theory. Overall: 0.75. Issues: needs more evidence',
            'metadata': {'source': 'research'}
        }
    ]
    
    methods_to_test = [
        '_extract_confidence',
        '_extract_score', 
        '_extract_aspect_scores',
        '_extract_issues',
        '_extract_recommendations'
    ]
    
    success_count = 0
    total_tests = len(test_dicts) * len(methods_to_test)
    
    for i, test_dict in enumerate(test_dicts):
        print(f"\nTest Dict {i+1}: {list(test_dict.keys())}")
        
        for method_name in methods_to_test:
            try:
                method = getattr(checker, method_name)
                result = method(test_dict)
                
                print(f"  ✅ {method_name}: {type(result).__name__} - {str(result)[:50]}...")
                success_count += 1
                
            except Exception as e:
                print(f"  ❌ {method_name}: FAILED - {e}")
    
    success_rate = success_count / total_tests
    print(f"\n📊 Results: {success_count}/{total_tests} ({success_rate:.1%}) methods handled dicts successfully")
    
    if success_rate == 1.0:
        print("🎉 ALL REGEX METHODS NOW HANDLE DICT INPUTS!")
        print("✅ No more 'expected string or bytes-like object, got dict' errors")
        return True
    else:
        print("❌ Some methods still failing with dict inputs")
        return False

def test_actual_validation_execution():
    """Test the full validation execution path"""
    
    print("\n🔧 Testing Full Validation Execution Path")
    print("=" * 50)
    
    try:
        test_config = {
            'role': 'Logic Validation Engine',
            'model': 'gpt-4o-mini',
            'temperature': 0.1,
            'provider': 'openai'
        }
        
        checker = LogicChecker(test_config)
        
        # This is the exact structure that was causing failures
        problematic_task = {
            'type': 'verification',
            'proposal': {
                'analysis': 'Life originated through chemical evolution in primordial oceans',
                'confidence': 0.85,
                'agent_id': 'proposer_alpha'
            }
        }
        
        print("Testing problematic task structure...")
        print(f"  Task type: {problematic_task['type']}")
        print(f"  Proposal keys: {list(problematic_task['proposal'].keys())}")
        
        # This should NOT crash with the fix
        result = checker.execute(problematic_task)
        
        print(f"✅ Execution successful!")
        print(f"  Result type: {type(result)}")
        print(f"  Has verification: {'verification' in result}")
        print(f"  Confidence: {result.get('confidence', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all regex fix tests"""
    
    print("🚀 Testing Complete Regex Fix for SEFAS")
    print("=" * 60)
    
    # Test 1: Regex methods handle dicts
    regex_success = test_regex_methods_with_dicts()
    
    # Test 2: Full execution path works
    execution_success = test_actual_validation_execution()
    
    print("\n" + "=" * 60)
    print("🎯 REGEX FIX TEST SUMMARY")
    print("=" * 60)
    
    print(f"Regex Methods Handle Dicts: {'✅' if regex_success else '❌'}")
    print(f"Full Execution Path Works: {'✅' if execution_success else '❌'}")
    
    overall_success = regex_success and execution_success
    
    if overall_success:
        print(f"\n🎉 REGEX FIX SUCCESSFUL!")
        print(f"✅ No more type mismatch errors in validation")
        print(f"✅ System ready for full validation testing")
        return True
    else:
        print(f"\n❌ REGEX FIX INCOMPLETE")
        print(f"❌ Still have type mismatch issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)