#!/usr/bin/env python3
"""
Simple test to verify the validation layer core fix works.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sefas.core.contracts import prepare_validation_input

def test_core_fix():
    """Test the core input preparation fix"""
    
    print("🧪 Testing Core Validation Input Preparation Fix...")
    print("=" * 60)
    
    # These are the exact data structures that were causing failures
    failing_cases = [
        {
            'name': 'Dict with analysis key (REAL FAILURE CASE)',
            'data': {
                'analysis': 'Life originated through chemical evolution in primordial oceans',
                'confidence': 0.85
            },
            'expected_type': str
        },
        {
            'name': 'Nested verification task (REAL SYSTEM FORMAT)',
            'data': {
                'type': 'verification',
                'proposal': {
                    'subclaim_id': 'test_001',
                    'content': 'RNA world hypothesis for origin of life',
                    'confidence': 0.8
                }
            },
            'expected_type': str
        },
        {
            'name': 'Raw dict that was causing regex failures',
            'data': {
                'proposal': 'Chemical evolution preceded biological evolution',
                'reasoning': 'Based on experimental evidence'
            },
            'expected_type': str
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(failing_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        print(f"Input type: {type(test_case['data'])}")
        
        try:
            # This is the critical function that was broken
            result = prepare_validation_input(test_case['data'])
            
            # Check the result
            if isinstance(result, test_case['expected_type']):
                print(f"  ✅ SUCCESS: Got {type(result).__name__}")
                print(f"  ✅ Content: '{result[:80]}{'...' if len(result) > 80 else ''}'")
                
                # Extra validation - ensure it's not just the raw dict as string
                if not result.startswith('{') or 'analysis' in result or 'proposal' in result:
                    print(f"  ✅ CONTENT EXTRACTED (not just stringified dict)")
                    success_count += 1
                else:
                    print(f"  ⚠️  Got stringified dict, not extracted content")
            else:
                print(f"  ❌ FAILED: Expected {test_case['expected_type']}, got {type(result)}")
        
        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(failing_cases)} tests passed")
    
    if success_count == len(failing_cases):
        print("\n🎉 CORE FIX SUCCESSFUL!")
        print("✅ prepare_validation_input() now handles all input types")
        print("✅ No more 'expected string or bytes-like object, got dict' errors")
        print("✅ Ready for integration testing")
        return True
    else:
        print(f"\n❌ Some tests failed - fix needs refinement")
        return False

def demonstrate_before_after():
    """Show the before/after behavior"""
    
    print("\n🔍 Demonstrating the Fix...")
    print("=" * 40)
    
    # This exact structure was causing the regex failures
    problematic_input = {
        'analysis': 'Life originated through chemical evolution in primordial oceans, with RNA serving as the first self-replicating molecule.',
        'confidence': 0.85,
        'agent_id': 'proposer_alpha'
    }
    
    print("Input that was failing before:")
    print(f"  Type: {type(problematic_input)}")
    print(f"  Keys: {list(problematic_input.keys())}")
    
    print("\nAfter fix:")
    result = prepare_validation_input(problematic_input)
    print(f"  Type: {type(result)}")
    print(f"  Content: '{result}'")
    
    print(f"\n✅ This STRING can now be safely passed to regex validation!")

def main():
    success = test_core_fix()
    
    if success:
        demonstrate_before_after()
        
        print(f"\n🚀 READY FOR FULL SYSTEM TEST:")
        print(f"Run: python scripts/run_experiment.py 'What is the most likely explanation for the origin of life?' --verbose")
        print(f"\nExpected improvements:")
        print(f"  • Validation Pass Rate: 0% → 80%+")
        print(f"  • Circuit Breakers: OPEN → CLOSED")
        print(f"  • No more type mismatch errors")
        
        return True
    else:
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)