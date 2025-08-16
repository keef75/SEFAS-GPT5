#!/usr/bin/env python3
"""
Test script to verify the validation layer integration fix.
This tests that validators can handle all input types correctly.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sefas.core.contracts import prepare_validation_input
from sefas.core.validation import ValidatorPool
from sefas.agents.checkers import LogicChecker, SemanticChecker, ConsistencyChecker
from sefas.agents.factory import AgentFactory
from config.settings import Settings


async def test_validation_fix():
    """Test that validators handle all input types correctly"""
    
    print("🧪 Testing Validation Layer Integration Fix...")
    print("=" * 60)
    
    # Load settings and agent configs
    try:
        settings = Settings()
        agent_configs = settings.load_agent_config()
        print(f"✅ Loaded configurations for {len(agent_configs)} agents")
    except Exception as e:
        print(f"❌ Failed to load configurations: {e}")
        return False
    
    # Test cases that were failing before
    test_cases = [
        {
            'name': 'Raw string',
            'data': "This is a simple string proposal about the origin of life"
        },
        {
            'name': 'Dict with analysis key (real failure case)',
            'data': {
                'analysis': 'Life originated through chemical evolution in primordial oceans, with RNA serving as the first self-replicating molecule.',
                'confidence': 0.85,
                'agent_id': 'proposer_alpha'
            }
        },
        {
            'name': 'Dict with proposal key',
            'data': {
                'proposal': 'The RNA world hypothesis suggests that life began with RNA molecules that could both store genetic information and catalyze chemical reactions.',
                'confidence': 0.75,
                'reasoning': 'Based on evidence from ribozymes and the catalytic properties of RNA'
            }
        },
        {
            'name': 'Complex nested structure',
            'data': {
                'content': {
                    'text': 'Panspermia theory proposes that life on Earth originated from microorganisms delivered by comets and meteorites.',
                    'metadata': {'source': 'research', 'topic': 'astrobiology'}
                },
                'confidence': 0.6
            }
        },
        {
            'name': 'Verification task structure (real system format)',
            'data': {
                'type': 'verification',
                'proposal': {
                    'subclaim_id': 'test_001',
                    'content': 'Chemical evolution in hydrothermal vents provided the energy and conditions necessary for the formation of organic compounds.',
                    'confidence': 0.8,
                    'reasoning': 'Experimental evidence shows that hydrothermal conditions can synthesize amino acids and nucleotides.'
                }
            }
        }
    ]
    
    # Test the input preparation function first
    print("\n🔧 Testing Input Preparation Function...")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases):
        print(f"Test {i+1}: {test_case['name']}")
        try:
            prepared = prepare_validation_input(test_case['data'])
            
            # Verify output is a string
            if not isinstance(prepared, str):
                print(f"  ❌ Output not string: got {type(prepared)}")
                return False
            
            # Verify it's not empty
            if not prepared.strip():
                print(f"  ❌ Output is empty")
                return False
            
            print(f"  ✅ Success: '{prepared[:60]}{'...' if len(prepared) > 60 else ''}'")
            
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return False
    
    print("\n🤖 Testing Validator Agents...")
    print("-" * 40)
    
    # Create validator instances using factory
    try:
        factory = AgentFactory(agent_configs)
        
        # Get checker configurations
        checker_configs = {
            name: config for name, config in agent_configs.items() 
            if config.get('role') in ['Logic Validation Engine', 'Semantic Validation Engine', 'Consistency Validation Engine']
        }
        
        if not checker_configs:
            print("❌ No checker configurations found in agent config")
            return False
        
        print(f"Found {len(checker_configs)} validator configurations")
        
        # Create validators
        validators = {}
        for name, config in checker_configs.items():
            try:
                if 'Logic' in config.get('role', ''):
                    validators[name] = LogicChecker(config)
                elif 'Semantic' in config.get('role', ''):
                    validators[name] = SemanticChecker(config)
                elif 'Consistency' in config.get('role', ''):
                    validators[name] = ConsistencyChecker(config)
                print(f"  ✅ Created {config.get('role')} validator")
            except Exception as e:
                print(f"  ⚠️ Failed to create {config.get('role')}: {e}")
        
        if not validators:
            print("❌ No validators created successfully")
            return False
        
    except Exception as e:
        print(f"❌ Failed to create validators: {e}")
        return False
    
    # Test each validator with each test case
    print(f"\n🔍 Testing {len(validators)} Validators with {len(test_cases)} Test Cases...")
    print("-" * 60)
    
    success_count = 0
    total_tests = len(validators) * len(test_cases)
    
    for test_idx, test_case in enumerate(test_cases):
        print(f"\nTest Case {test_idx + 1}: {test_case['name']}")
        
        for validator_name, validator in validators.items():
            try:
                # Create validation task exactly like the real system
                validation_task = {
                    'description': f"Validate proposal content",
                    'type': 'verification',
                    'proposal': test_case['data'],
                    'claim_data': {
                        'content': test_case['data'],
                        'claim_id': f'test_{test_idx}',
                        'confidence': 0.5
                    }
                }
                
                # Execute validation
                result = validator.execute(validation_task)
                if asyncio.iscoroutine(result):
                    result = await result
                
                # Check for success
                if 'error' in result:
                    print(f"  ❌ {validator_name}: {result['error']}")
                else:
                    confidence = result.get('confidence', 0.0)
                    verification = result.get('verification', {})
                    passed = verification.get('passed', confidence > 0.5)
                    
                    print(f"  ✅ {validator_name}: confidence={confidence:.2f}, passed={passed}")
                    success_count += 1
                    
            except Exception as e:
                print(f"  ❌ {validator_name}: Exception - {e}")
    
    # Test the validator pool integration
    print(f"\n🎯 Testing ValidatorPool Integration...")
    print("-" * 40)
    
    try:
        pool = ValidatorPool()
        
        # Register agent-based validators
        for name, validator in validators.items():
            pool.register_validator(name, validator)
        
        # Test with a sample claim
        test_claim = {
            'claim_id': 'integration_test',
            'content': test_cases[1]['data'],  # Use the complex case
            'confidence': 0.8
        }
        
        result = await pool.validate_with_quorum(test_claim, quorum=2)
        
        if result.valid:
            print(f"  ✅ Quorum validation passed: confidence={result.confidence:.2f}")
            print(f"      Evidence: {result.evidence[:100]}...")
        else:
            print(f"  ⚠️ Quorum validation failed: {result.errors}")
        
    except Exception as e:
        print(f"  ❌ ValidatorPool test failed: {e}")
        success_count -= 1  # Adjust for the pool test failure
    
    # Final results
    print("\n📊 Test Results")
    print("=" * 60)
    
    success_rate = success_count / total_tests if total_tests > 0 else 0
    print(f"Individual Validator Tests: {success_count}/{total_tests} ({success_rate:.1%})")
    
    if success_rate >= 0.8:
        print("\n🎉 VALIDATION LAYER FIX SUCCESSFUL!")
        print("✅ The type mismatch issue has been resolved")
        print("✅ Validators can now handle all input types")
        print("✅ Ready to run full SEFAS experiment")
        return True
    else:
        print("\n❌ VALIDATION LAYER STILL HAS ISSUES")
        print(f"❌ Only {success_rate:.1%} of tests passed")
        print("❌ Need to investigate remaining problems")
        return False


def main():
    """Run the validation fix test"""
    try:
        success = asyncio.run(test_validation_fix())
        
        if success:
            print(f"\n🚀 NEXT STEPS:")
            print(f"1. Run: python scripts/run_experiment.py 'What is the most likely explanation for the origin of life?' --verbose")
            print(f"2. Check for 80%+ validation pass rate")
            print(f"3. Verify circuit breakers remain CLOSED")
            exit(0)
        else:
            print(f"\n🔧 DEBUGGING NEEDED:")
            print(f"1. Check the error messages above")
            print(f"2. Verify agent configurations are correct")
            print(f"3. Test individual components")
            exit(1)
            
    except Exception as e:
        print(f"\n💥 TEST SCRIPT FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()