#!/usr/bin/env python3
"""Test confidence calibration improvements for SEFAS belief propagation system."""

import asyncio
import time
from sefas.core.belief_propagation import BeliefPropagationEngine

async def test_confidence_calibration():
    """Test the improved confidence calibration system"""
    
    print("🧪 Testing Enhanced Confidence Calibration System")
    print("=" * 60)
    
    # Initialize belief propagation engine
    engine = BeliefPropagationEngine()
    
    # Test scenario: Multiple agents providing proposals for a task
    claim_id = "test_claim_1"
    
    # Add diverse proposals with different confidence levels (using legitimate proposer names)
    proposals = [
        ("Proposal A: Use microservices architecture", 0.8, "technical_architect"),
        ("Proposal A: Use microservices architecture", 0.7, "proposer_beta"),  # Same content, different confidence
        ("Proposal B: Use monolithic architecture", 0.6, "proposer_gamma"),
        ("Proposal A: Use microservices architecture", 0.9, "domain_expert"),  # Same content again
        ("Proposal C: Use hybrid approach", 0.5, "proposer_alpha"),
    ]
    
    print("📝 Adding proposals:")
    for content, confidence, agent_id in proposals:
        await engine.add_proposal(claim_id, content, confidence, agent_id)
        print(f"  • {agent_id}: {confidence:.2f} confidence")
    
    # Add validation results
    validations = [
        ("validator_1", {"valid": True, "confidence": 0.8, "evidence": "Good architectural choice"}),
        ("validator_2", {"valid": True, "confidence": 0.7, "evidence": "Scalable solution"}),
        ("validator_3", {"valid": False, "confidence": 0.6, "evidence": "Complexity concerns"}),
    ]
    
    print("\n🔍 Adding validations:")
    for validator_id, result in validations:
        await engine.add_validation(claim_id, validator_id, result)
        print(f"  • {validator_id}: {result['valid']} ({result['confidence']:.2f})")
    
    # Run belief propagation
    print("\n⚙️ Running belief propagation...")
    start_time = time.time()
    
    result = await engine.propagate()
    
    execution_time = time.time() - start_time
    
    # Display results
    print(f"\n📊 Results (executed in {execution_time:.3f}s):")
    print(f"  System Confidence: {result['system_confidence']:.3f}")
    print(f"  Converged: {result['converged']}")
    print(f"  Iterations: {result['iterations']}")
    
    print("\n📋 Consensus Details:")
    consensus = result['consensus']
    for claim_id, claim_result in consensus.items():
        print(f"  Claim {claim_id}:")
        print(f"    • Best Content: {claim_result['content'][:50]}...")
        print(f"    • Confidence: {claim_result['confidence']:.3f}")
        print(f"    • Converged: {claim_result['converged']}")
        
        print(f"    • Alternatives:")
        for i, (content, prob) in enumerate(claim_result['alternatives'][:2]):
            print(f"      {i+1}. {content[:40]}... ({prob:.3f})")
    
    # Test confidence calibration patterns
    print("\n🎯 Confidence Calibration Analysis:")
    
    beliefs = result['beliefs']
    for claim_id, belief in beliefs.items():
        print(f"  Claim {claim_id}:")
        for content, confidence in belief['candidates'].items():
            print(f"    • {content[:40]}...: {confidence:.3f}")
    
    # Calculate improvement metrics
    initial_confidences = [p[1] for p in proposals]
    final_confidences = [belief['confidence'] for belief in beliefs.values()]
    
    avg_initial = sum(initial_confidences) / len(initial_confidences)
    avg_final = sum(final_confidences) / len(final_confidences)
    
    print(f"\n📈 Calibration Metrics:")
    print(f"  • Average Initial Confidence: {avg_initial:.3f}")
    print(f"  • Average Final Confidence: {avg_final:.3f}")
    print(f"  • Confidence Delta: {avg_final - avg_initial:+.3f}")
    print(f"  • System Confidence: {result['system_confidence']:.3f}")
    
    # Assess improvement
    if result['system_confidence'] > 0.5:
        print("✅ Confidence calibration appears healthy (>0.5)")
    else:
        print("⚠️ Confidence calibration may need further tuning (<0.5)")
    
    if result['converged']:
        print("✅ System converged successfully")
    else:
        print("⚠️ System did not converge - may need more iterations")
    
    return result

async def test_confidence_edge_cases():
    """Test edge cases for confidence calibration"""
    
    print("\n🔬 Testing Edge Cases")
    print("=" * 40)
    
    engine = BeliefPropagationEngine()
    
    # Test case 1: Very low initial confidences
    claim_id = "edge_case_1"
    await engine.add_proposal(claim_id, "Low confidence proposal", 0.1, "proposer_alpha")
    await engine.add_proposal(claim_id, "Another low confidence", 0.2, "proposer_beta")
    
    # Add positive validation
    await engine.add_validation(claim_id, "validator", {"valid": True, "confidence": 0.9, "evidence": "Actually good"})
    
    result1 = await engine.propagate()
    print(f"Test 1 - Low initial, high validation: {result1['system_confidence']:.3f}")
    
    # Test case 2: High initial confidences with negative validation
    engine2 = BeliefPropagationEngine()
    claim_id2 = "edge_case_2"
    await engine2.add_proposal(claim_id2, "High confidence proposal", 0.9, "domain_expert")
    await engine2.add_proposal(claim_id2, "Another high confidence", 0.8, "technical_architect")
    
    # Add negative validation
    await engine2.add_validation(claim_id2, "validator", {"valid": False, "confidence": 0.9, "evidence": "Actually problematic"})
    
    result2 = await engine2.propagate()
    print(f"Test 2 - High initial, negative validation: {result2['system_confidence']:.3f}")
    
    return [result1, result2]

if __name__ == "__main__":
    async def main():
        result = await test_confidence_calibration()
        edge_results = await test_confidence_edge_cases()
        
        print(f"\n🏁 Test Summary:")
        print(f"  Main test system confidence: {result['system_confidence']:.3f}")
        print(f"  Edge case 1 confidence: {edge_results[0]['system_confidence']:.3f}")
        print(f"  Edge case 2 confidence: {edge_results[1]['system_confidence']:.3f}")
        
        # Check if improvements are working
        if result['system_confidence'] > 0.4:
            print("✅ Confidence calibration improvements are working!")
        else:
            print("❌ Confidence calibration still needs work")
    
    asyncio.run(main())