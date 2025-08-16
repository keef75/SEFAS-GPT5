"""
Quick test to verify improvements are working
"""

import asyncio
import sys
sys.path.append('.')

from sefas.core.belief_propagation import BeliefPropagationEngine
from sefas.core.validation import ValidatorPool
from sefas.core.redundancy import RedundancyOrchestrator

async def test_improvements():
    print("Testing belief propagation...")
    bp = BeliefPropagationEngine()
    
    # Add test proposals
    await bp.add_proposal("claim_1", "Solution A", 0.8, "agent_1")
    await bp.add_proposal("claim_1", "Solution A", 0.7, "agent_2")
    await bp.add_proposal("claim_1", "Solution B", 0.4, "agent_3")
    
    # Run propagation
    result = await bp.propagate()
    print(f"✅ Belief propagation working! Confidence: {result['system_confidence']:.2%}")
    
    print("\nTesting validation...")
    validator = ValidatorPool()
    test_claim = {
        'claim_id': 'test_1',
        'content': 'This is a test solution for validation',
        'confidence': 0.7,
        'evidence': ['Evidence 1', 'Evidence 2']
    }
    
    validation = await validator.validate_with_quorum(test_claim)
    print(f"✅ Validation working! Confidence: {validation.confidence:.2%}")
    
    print("\nTesting redundancy...")
    ro = RedundancyOrchestrator()
    
    # Mock provider
    class MockProvider:
        def __init__(self, name):
            self.name = name
        
        async def execute(self, task, **kwargs):
            return {
                'content': f"Solution from {self.name}",
                'confidence': 0.6 + (hash(self.name) % 30) / 100
            }
    
    providers = [MockProvider(f"provider_{i}") for i in range(5)]
    
    result = await ro.execute_with_redundancy(
        providers=providers,
        task="Test task",
        strategy="reliable"
    )
    
    print(f"✅ Redundancy working! Consensus confidence: {result['result']['confidence']:.2%}")
    print("\n🎉 All improvements tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_improvements())