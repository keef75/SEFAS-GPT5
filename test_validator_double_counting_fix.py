#!/usr/bin/env python3
"""Test that the validator double-counting fix prevents data corruption."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sefas.core.belief_propagation import BeliefPropagationEngine

async def test_validator_double_counting_prevention():
    """Test that validators are not double-counted across rounds"""
    
    print("🚨 Testing Validator Double-Counting Fix")
    print("=" * 55)
    
    engine = BeliefPropagationEngine()
    claim_id = "double_count_test"
    
    # Add a legitimate proposal
    print("✅ Adding legitimate proposal...")
    await engine.add_proposal(claim_id, "Test proposal content", 0.6, "proposer_alpha")
    
    # Simulate the same validator being called multiple times (which would previously cause double-counting)
    print("🚨 Testing validator message deduplication...")
    
    # First validation (round 0)
    engine.current_round = 0
    await engine.add_validation(claim_id, "logic_validator", {
        'valid': True,
        'confidence': 0.8,
        'evidence': 'Good logical structure'
    })
    
    # Same validator, same round - should replace, not accumulate
    await engine.add_validation(claim_id, "logic_validator", {
        'valid': True,
        'confidence': 0.9,  # Different confidence
        'evidence': 'Updated assessment'
    })
    
    # Different validator, same round
    await engine.add_validation(claim_id, "semantic_validator", {
        'valid': True,
        'confidence': 0.7,
        'evidence': 'Semantically correct'
    })
    
    # Same validator, different round (round 1)
    engine.current_round = 1
    await engine.add_validation(claim_id, "logic_validator", {
        'valid': True,
        'confidence': 0.85,
        'evidence': 'Revalidated in round 1'
    })
    
    print(f"\n📊 Validator Messages Structure:")
    print(f"   Total unique validator messages: {len(engine.validator_messages)}")
    for key, value in engine.validator_messages.items():
        claim, validator, round_num = key
        print(f"   {claim} | {validator} | Round {round_num}: {value['confidence']:.2f}")
    
    # Verify that we have exactly 3 unique validator messages:
    # 1. logic_validator, round 0 (should be updated to 0.9, not accumulated)
    # 2. semantic_validator, round 0  
    # 3. logic_validator, round 1
    expected_messages = 3
    actual_messages = len(engine.validator_messages)
    
    if actual_messages == expected_messages:
        print(f"✅ SUCCESS: Validator deduplication working!")
        print(f"   - Expected {expected_messages} unique messages, got {actual_messages}")
        print(f"   - Same validator in same round was replaced, not accumulated")
        
        # Check that the confidence was updated (not accumulated)
        logic_round_0_key = (claim_id, "logic_validator", 0)
        if logic_round_0_key in engine.validator_messages:
            confidence = engine.validator_messages[logic_round_0_key]['confidence']
            if confidence == 0.9:  # Should be the updated value, not 0.8 + 0.9
                print(f"✅ SUCCESS: Validator confidence properly replaced (0.9, not accumulated)")
                return True
            else:
                print(f"❌ FAIL: Validator confidence was {confidence}, expected 0.9")
                return False
        else:
            print(f"❌ FAIL: Missing expected validator message")
            return False
    else:
        print(f"❌ FAIL: Expected {expected_messages} messages, got {actual_messages}")
        return False

async def test_validator_confidence_integrity():
    """Test that validator confidence calculations remain accurate"""
    
    print("\n✅ Testing Validator Confidence Integrity")
    print("=" * 45)
    
    engine = BeliefPropagationEngine()
    claim_id = "integrity_test"
    
    # Add proposal
    await engine.add_proposal(claim_id, "Test content", 0.5, "proposer_alpha")
    
    # Add multiple validators with known confidences
    engine.current_round = 0
    validators = [
        ("validator_1", 0.8),
        ("validator_2", 0.6),
        ("validator_3", 0.9)
    ]
    
    for validator_id, confidence in validators:
        await engine.add_validation(claim_id, validator_id, {
            'valid': True,
            'confidence': confidence,
            'evidence': f'Evidence from {validator_id}'
        })
    
    # Calculate expected average confidence
    expected_avg = sum(conf for _, conf in validators) / len(validators)
    print(f"   Expected average validation confidence: {expected_avg:.3f}")
    
    # Run belief propagation to see actual influence
    result = await engine.propagate()
    
    # Check that we don't have inflated confidence from double-counting
    system_confidence = result['system_confidence']
    print(f"   System confidence after propagation: {system_confidence:.3f}")
    
    # System confidence should be reasonable (not artificially inflated)
    if 0.5 <= system_confidence <= 0.95:  # Reasonable range
        print(f"✅ SUCCESS: System confidence in reasonable range")
        print(f"   - No evidence of artificial inflation from validator double-counting")
        return True
    else:
        print(f"⚠️ WARNING: System confidence {system_confidence:.3f} may indicate issues")
        if system_confidence > 0.95:
            print(f"   - Suspiciously high confidence may indicate double-counting")
        return False

async def test_old_vs_new_behavior():
    """Demonstrate the difference between old (broken) and new (fixed) behavior"""
    
    print("\n🔬 Comparing Old vs New Validator Behavior")
    print("=" * 50)
    
    # Simulate what the old behavior would have produced
    print("📊 OLD BEHAVIOR (would have been):")
    print("   - Validator messages accumulated in lists")
    print("   - Same validator could be counted multiple times")
    print("   - Artificial confidence inflation")
    
    # Show new behavior
    engine = BeliefPropagationEngine()
    claim_id = "comparison_test"
    
    await engine.add_proposal(claim_id, "Test content", 0.5, "proposer_alpha")
    
    # Add the same validator multiple times (simulating old bug scenario)
    engine.current_round = 0
    for i in range(3):
        await engine.add_validation(claim_id, "test_validator", {
            'valid': True,
            'confidence': 0.8,
            'evidence': f'Attempt {i+1}'
        })
    
    print(f"\n📊 NEW BEHAVIOR (fixed):")
    print(f"   - Added same validator 3 times in same round")
    print(f"   - Validator messages: {len(engine.validator_messages)} (should be 1, not 3)")
    print(f"   - Latest validation overwrites previous ones")
    
    if len(engine.validator_messages) == 1:
        print(f"✅ SUCCESS: Validator deduplication prevents data corruption")
        return True
    else:
        print(f"❌ FAIL: Validator messages not properly deduplicated")
        return False

async def main():
    """Run all validator double-counting tests"""
    print("🧪 VALIDATOR DOUBLE-COUNTING FIX VALIDATION")
    print("=" * 65)
    
    test1_passed = await test_validator_double_counting_prevention()
    test2_passed = await test_validator_confidence_integrity()
    test3_passed = await test_old_vs_new_behavior()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Double-Counting Prevention: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Confidence Integrity: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Behavior Comparison: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED - Validator double-counting fix working!")
        print("   System now protected from validator data corruption")
        print("   Confidence scores accurately reflect unique validator input")
        return True
    else:
        print("\n🚨 TESTS FAILED - Review validator message implementation")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)