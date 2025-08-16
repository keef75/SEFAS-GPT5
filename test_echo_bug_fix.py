#!/usr/bin/env python3
"""Test that the echo bug fix prevents aggregator self-reinforcement."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sefas.core.belief_propagation import BeliefPropagationEngine

async def test_echo_bug_prevention():
    """Test that the echo bug fix prevents artificial confidence inflation"""
    
    print("🚨 Testing Echo Bug Fix")
    print("=" * 50)
    
    engine = BeliefPropagationEngine()
    claim_id = "test_claim"
    
    # Simulate legitimate proposer adding proposal
    print("✅ Adding legitimate proposer...")
    await engine.add_proposal(claim_id, "Legitimate proposal content", 0.7, "proposer_alpha")
    
    # Simulate echo bug attempt - aggregator trying to add its own output as proposal
    print("🚨 Testing echo bug prevention...")
    await engine.add_proposal(claim_id, "Aggregator consensus output", 0.9, "redundancy_consensus")
    await engine.add_proposal(claim_id, "Another aggregator output", 0.8, "system_aggregator")
    await engine.add_proposal(claim_id, "Validator output as proposal", 0.85, "checker_logic")
    
    # Check beliefs - should only contain legitimate proposer's content
    belief_node = engine.beliefs.get(claim_id)
    
    if belief_node is None:
        print("❌ FAIL: No belief node created")
        return False
    
    print(f"\n📊 Belief Node Contents:")
    print(f"   Candidates: {belief_node.candidates}")
    print(f"   Evidence Count: {belief_node.evidence_count}")
    print(f"   Confidence: {belief_node.confidence}")
    
    # Verify only legitimate proposals were accepted
    if len(belief_node.candidates) == 1 and "Legitimate proposal content" in belief_node.candidates:
        print("✅ SUCCESS: Echo bug prevention working!")
        print("   - Only legitimate proposer content accepted")
        print("   - Aggregator outputs correctly filtered out")
        
        # Check that confidence wasn't artificially inflated
        if belief_node.candidates["Legitimate proposal content"] == 0.7:
            print("✅ SUCCESS: No artificial confidence inflation")
            return True
        else:
            print(f"⚠️ WARNING: Confidence changed from 0.7 to {belief_node.candidates['Legitimate proposal content']}")
            return False
    else:
        print("❌ FAIL: Echo bug prevention not working properly")
        print(f"   Expected 1 candidate, got {len(belief_node.candidates)}")
        return False

async def test_legitimate_proposers_still_work():
    """Test that legitimate proposers still work correctly"""
    
    print("\n✅ Testing Legitimate Proposers")
    print("=" * 40)
    
    engine = BeliefPropagationEngine()
    claim_id = "multi_proposer_test"
    
    # Add proposals from all legitimate proposers
    legitimate_agents = [
        "proposer_alpha", "proposer_beta", "proposer_gamma",
        "domain_expert", "technical_architect", "innovation_catalyst",
        "strategic_planner", "orchestrator"
    ]
    
    for i, agent in enumerate(legitimate_agents):
        confidence = 0.6 + (i * 0.05)  # Vary confidence levels
        await engine.add_proposal(claim_id, f"Proposal from {agent}", confidence, agent)
        print(f"   Added proposal from {agent} with confidence {confidence:.2f}")
    
    belief_node = engine.beliefs.get(claim_id)
    if belief_node and len(belief_node.candidates) == len(legitimate_agents):
        print(f"✅ SUCCESS: All {len(legitimate_agents)} legitimate proposers accepted")
        return True
    else:
        print(f"❌ FAIL: Expected {len(legitimate_agents)} proposals, got {len(belief_node.candidates) if belief_node else 0}")
        return False

async def main():
    """Run all tests"""
    print("🧪 ECHO BUG FIX VALIDATION TESTS")
    print("=" * 60)
    
    test1_passed = await test_echo_bug_prevention()
    test2_passed = await test_legitimate_proposers_still_work()
    
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Echo Bug Prevention: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Legitimate Proposers: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED - Echo bug fix is working!")
        print("   System now protected from artificial confidence inflation")
        return True
    else:
        print("\n🚨 TESTS FAILED - Review implementation")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)