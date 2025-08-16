#!/usr/bin/env python3
"""
Belief Propagation Convergence Test Suite
Tests BP stability, oscillation detection, and convergence rates.
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import statistics
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sefas.core.belief_propagation import BeliefPropagationEngine

class BPConvergenceTestSuite:
    """Test suite for BP convergence analysis"""
    
    def __init__(self):
        self.test_results = []
    
    async def run_comprehensive_tests(self, n_runs: int = 100) -> Dict[str, Any]:
        """Run comprehensive BP convergence tests"""
        
        print("🧪 Starting BP Convergence Test Suite")
        print("=" * 60)
        
        # Test 1: Basic convergence rate
        print("\n📊 Test 1: Basic Convergence Rate")
        basic_results = await self._test_basic_convergence(n_runs)
        
        # Test 2: Oscillation detection
        print("\n🌊 Test 2: Oscillation Detection and Recovery")
        oscillation_results = await self._test_oscillation_detection()
        
        # Test 3: Stability under noise
        print("\n📡 Test 3: Stability Under Noise")
        noise_results = await self._test_noise_stability()
        
        # Test 4: Scalability
        print("\n📈 Test 4: Scalability Testing")
        scalability_results = await self._test_scalability()
        
        # Test 5: Edge cases
        print("\n⚠️  Test 5: Edge Case Handling")
        edge_case_results = await self._test_edge_cases()
        
        # Aggregate results
        overall_results = {
            'basic_convergence': basic_results,
            'oscillation_detection': oscillation_results,
            'noise_stability': noise_results,
            'scalability': scalability_results,
            'edge_cases': edge_case_results,
            'overall_assessment': self._assess_overall_performance(
                basic_results, oscillation_results, noise_results, 
                scalability_results, edge_case_results
            )
        }
        
        self._print_summary(overall_results)
        return overall_results
    
    async def _test_basic_convergence(self, n_runs: int) -> Dict[str, Any]:
        """Test basic convergence rate and iteration count"""
        print(f"  Running {n_runs} convergence tests...")
        
        converged_runs = 0
        iteration_counts = []
        convergence_times = []
        
        for i in range(n_runs):
            if i % 10 == 0:
                print(f"    Progress: {i}/{n_runs}")
            
            bp_engine = BeliefPropagationEngine(
                damping_factor=0.8,
                convergence_threshold=1e-4,
                max_iterations=50
            )
            
            # Add test proposals
            await self._add_test_proposals(bp_engine)
            
            start_time = time.time()
            result = await bp_engine.propagate()
            end_time = time.time()
            
            if result['converged']:
                converged_runs += 1
                iteration_counts.append(result['iterations'])
                convergence_times.append(end_time - start_time)
        
        convergence_rate = converged_runs / n_runs
        avg_iterations = statistics.mean(iteration_counts) if iteration_counts else 0
        avg_time = statistics.mean(convergence_times) if convergence_times else 0
        
        print(f"    Convergence Rate: {convergence_rate:.1%}")
        print(f"    Average Iterations: {avg_iterations:.1f}")
        print(f"    Average Time: {avg_time:.3f}s")
        
        success = convergence_rate >= 0.90 and avg_iterations <= 15  # More realistic targets
        
        return {
            'convergence_rate': convergence_rate,
            'average_iterations': avg_iterations,
            'average_time_seconds': avg_time,
            'iteration_distribution': {
                'min': min(iteration_counts) if iteration_counts else 0,
                'max': max(iteration_counts) if iteration_counts else 0,
                'std': statistics.stdev(iteration_counts) if len(iteration_counts) > 1 else 0
            },
            'success': success,
            'target_convergence_rate': 0.90,
            'target_max_iterations': 15
        }
    
    async def _test_oscillation_detection(self) -> Dict[str, Any]:
        """Test oscillation detection and recovery mechanisms"""
        print("  Testing oscillation scenarios...")
        
        # Test 1: Forced oscillation with conflicting proposals
        bp_engine = BeliefPropagationEngine(
            damping_factor=0.1,  # Low damping to encourage oscillation
            convergence_threshold=1e-6,
            max_iterations=50
        )
        
        # Add conflicting proposals that might cause oscillation
        await bp_engine.add_proposal("claim_1", "Proposal A", 0.9, "agent_1")
        await bp_engine.add_proposal("claim_1", "Proposal B", 0.85, "agent_2")
        await bp_engine.add_proposal("claim_1", "Proposal A", 0.95, "agent_3")
        await bp_engine.add_proposal("claim_1", "Proposal B", 0.88, "agent_4")
        
        # Add conflicting validations
        await bp_engine.add_validation("claim_1", "validator_1", {'valid': True, 'confidence': 0.9})
        await bp_engine.add_validation("claim_1", "validator_2", {'valid': False, 'confidence': 0.8})
        
        result = await bp_engine.propagate()
        
        oscillation_detected = result.get('oscillation_detected', False)
        final_damping = result.get('final_damping', 0.1)
        converged = result.get('converged', False)
        
        print(f"    Oscillation Detected: {oscillation_detected}")
        print(f"    Final Damping: {final_damping:.2f}")
        print(f"    Still Converged: {converged}")
        
        # Test should handle oscillation gracefully
        success = converged or (oscillation_detected and final_damping > 0.5)
        
        return {
            'oscillation_detected': oscillation_detected,
            'converged_despite_oscillation': converged,
            'final_damping_factor': final_damping,
            'adaptive_damping_worked': final_damping > 0.1,
            'success': success
        }
    
    async def _test_noise_stability(self) -> Dict[str, Any]:
        """Test stability under noisy proposals and validations"""
        print("  Testing stability under noise...")
        
        noise_levels = [0.1, 0.2, 0.3, 0.4, 0.5]
        results = {}
        
        for noise_level in noise_levels:
            bp_engine = BeliefPropagationEngine()
            
            # Add proposals with noise
            base_confidence = 0.8
            for i in range(5):
                noise = np.random.normal(0, noise_level)
                noisy_confidence = max(0.1, min(0.9, base_confidence + noise))
                await bp_engine.add_proposal(
                    "claim_1", f"Proposal with noise {i}", 
                    noisy_confidence, f"agent_{i}"
                )
            
            # Add noisy validations
            for i in range(3):
                noise = np.random.normal(0, noise_level)
                noisy_confidence = max(0.1, min(0.9, 0.7 + noise))
                await bp_engine.add_validation(
                    "claim_1", f"validator_{i}", 
                    {'valid': True, 'confidence': noisy_confidence}
                )
            
            result = await bp_engine.propagate()
            
            results[noise_level] = {
                'converged': result['converged'],
                'iterations': result['iterations'],
                'system_confidence': result['system_confidence']
            }
            
            print(f"    Noise {noise_level:.1f}: converged={result['converged']}, conf={result['system_confidence']:.2f}")
        
        # Success if stable under moderate noise
        moderate_noise_stable = results[0.3]['converged'] and results[0.3]['system_confidence'] > 0.5
        
        return {
            'noise_results': results,
            'stable_under_moderate_noise': moderate_noise_stable,
            'success': moderate_noise_stable
        }
    
    async def _test_scalability(self) -> Dict[str, Any]:
        """Test scalability with increasing numbers of agents and claims"""
        print("  Testing scalability...")
        
        scalability_results = {}
        
        # Test different scales
        scales = [
            {'claims': 1, 'agents': 5, 'validators': 3},
            {'claims': 3, 'agents': 10, 'validators': 5},
            {'claims': 5, 'agents': 15, 'validators': 7},
            {'claims': 10, 'agents': 20, 'validators': 10}
        ]
        
        for scale in scales:
            bp_engine = BeliefPropagationEngine()
            
            # Add claims with multiple proposals
            for claim_i in range(scale['claims']):
                for agent_i in range(scale['agents']):
                    confidence = 0.6 + 0.3 * np.random.random()
                    await bp_engine.add_proposal(
                        f"claim_{claim_i}", 
                        f"Proposal from agent {agent_i} for claim {claim_i}",
                        confidence, 
                        f"agent_{agent_i}"
                    )
                
                # Add validations
                for val_i in range(scale['validators']):
                    confidence = 0.5 + 0.4 * np.random.random()
                    await bp_engine.add_validation(
                        f"claim_{claim_i}",
                        f"validator_{val_i}",
                        {'valid': True, 'confidence': confidence}
                    )
            
            start_time = time.time()
            result = await bp_engine.propagate()
            end_time = time.time()
            
            scale_key = f"{scale['claims']}c_{scale['agents']}a_{scale['validators']}v"
            scalability_results[scale_key] = {
                'converged': result['converged'],
                'iterations': result['iterations'],
                'time_seconds': end_time - start_time,
                'system_confidence': result['system_confidence']
            }
            
            print(f"    {scale_key}: {result['converged']}, {result['iterations']}it, {end_time - start_time:.2f}s")
        
        # Success if scales reasonably
        largest_scale = list(scalability_results.values())[-1]
        scales_well = largest_scale['converged'] and largest_scale['time_seconds'] < 5.0
        
        return {
            'scalability_results': scalability_results,
            'scales_to_largest_test': scales_well,
            'success': scales_well
        }
    
    async def _test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and error conditions"""
        print("  Testing edge cases...")
        
        edge_results = {}
        
        # Test 1: Empty BP
        bp_empty = BeliefPropagationEngine()
        result_empty = await bp_empty.propagate()
        edge_results['empty_bp'] = {
            'handled_gracefully': True,  # Should not crash
            'system_confidence': result_empty['system_confidence']
        }
        
        # Test 2: Single proposal
        bp_single = BeliefPropagationEngine()
        await bp_single.add_proposal("claim_1", "Single proposal", 0.8, "agent_1")
        result_single = await bp_single.propagate()
        edge_results['single_proposal'] = {
            'converged': result_single['converged'],
            'confidence_preserved': abs(result_single['system_confidence'] - 0.8) < 0.1
        }
        
        # Test 3: Zero confidence proposals
        bp_zero = BeliefPropagationEngine()
        await bp_zero.add_proposal("claim_1", "Zero confidence", 0.0, "agent_1")
        await bp_zero.add_proposal("claim_1", "Low confidence", 0.1, "agent_2")
        result_zero = await bp_zero.propagate()
        edge_results['zero_confidence'] = {
            'handled_gracefully': True,
            'converged': result_zero['converged']
        }
        
        # Test 4: Identical proposals
        bp_identical = BeliefPropagationEngine()
        for i in range(5):
            await bp_identical.add_proposal("claim_1", "Identical proposal", 0.7, f"agent_{i}")
        result_identical = await bp_identical.propagate()
        edge_results['identical_proposals'] = {
            'converged': result_identical['converged'],
            'confidence_aggregated': result_identical['system_confidence'] > 0.7
        }
        
        print(f"    Empty BP: handled gracefully")
        print(f"    Single proposal: {edge_results['single_proposal']['converged']}")
        print(f"    Zero confidence: handled gracefully")
        print(f"    Identical proposals: {edge_results['identical_proposals']['converged']}")
        
        success = all(
            result.get('handled_gracefully', True) and result.get('converged', True)
            for result in edge_results.values()
        )
        
        return {
            'edge_case_results': edge_results,
            'all_handled_gracefully': success,
            'success': success
        }
    
    async def _add_test_proposals(self, bp_engine: BeliefPropagationEngine):
        """Add standard test proposals to BP engine"""
        # Add diverse proposals
        await bp_engine.add_proposal("claim_1", "Primary hypothesis", 0.8, "agent_alpha")
        await bp_engine.add_proposal("claim_1", "Alternative hypothesis", 0.6, "agent_beta")
        await bp_engine.add_proposal("claim_1", "Primary hypothesis", 0.75, "agent_gamma")
        
        # Add validations
        await bp_engine.add_validation("claim_1", "logic_validator", {'valid': True, 'confidence': 0.7})
        await bp_engine.add_validation("claim_1", "semantic_validator", {'valid': True, 'confidence': 0.8})
        await bp_engine.add_validation("claim_1", "consistency_validator", {'valid': True, 'confidence': 0.6})
    
    def _assess_overall_performance(self, *test_results) -> Dict[str, Any]:
        """Assess overall BP performance"""
        successes = [result['success'] for result in test_results]
        overall_success = all(successes)
        success_rate = sum(successes) / len(successes)
        
        return {
            'overall_success': overall_success,
            'success_rate': success_rate,
            'individual_test_results': [result['success'] for result in test_results],
            'ready_for_production': overall_success and success_rate >= 0.8,
            'recommendations': self._generate_recommendations(test_results)
        }
    
    def _generate_recommendations(self, test_results) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        basic_result = test_results[0]
        if basic_result['convergence_rate'] < 0.95:
            recommendations.append("Increase damping factor or adjust convergence threshold")
        
        if basic_result['average_iterations'] > 10:
            recommendations.append("Optimize convergence speed - consider better initialization")
        
        oscillation_result = test_results[1]
        if not oscillation_result['success']:
            recommendations.append("Improve oscillation detection sensitivity")
        
        noise_result = test_results[2]
        if not noise_result['success']:
            recommendations.append("Add better noise filtering or robustness mechanisms")
        
        scalability_result = test_results[3]
        if not scalability_result['success']:
            recommendations.append("Optimize for better scalability - consider algorithmic improvements")
        
        edge_result = test_results[4]
        if not edge_result['success']:
            recommendations.append("Improve edge case handling and error recovery")
        
        if not recommendations:
            recommendations.append("BP system is performing well - ready for production testing")
        
        return recommendations
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 BP CONVERGENCE TEST SUMMARY")
        print("=" * 60)
        
        overall = results['overall_assessment']
        
        print(f"Overall Success: {'✅' if overall['overall_success'] else '❌'}")
        print(f"Success Rate: {overall['success_rate']:.1%}")
        print(f"Ready for Production: {'✅' if overall['ready_for_production'] else '❌'}")
        
        print(f"\nIndividual Test Results:")
        test_names = ['Basic Convergence', 'Oscillation Detection', 'Noise Stability', 'Scalability', 'Edge Cases']
        for i, (name, success) in enumerate(zip(test_names, overall['individual_test_results'])):
            print(f"  {name}: {'✅' if success else '❌'}")
        
        print(f"\nRecommendations:")
        for rec in overall['recommendations']:
            print(f"  • {rec}")
        
        if overall['ready_for_production']:
            print(f"\n🚀 BP SYSTEM READY FOR PRODUCTION BENCHMARKING!")
        else:
            print(f"\n⚠️  BP SYSTEM NEEDS IMPROVEMENT BEFORE BENCHMARKING")

async def main():
    """Run the BP convergence test suite"""
    
    import argparse
    parser = argparse.ArgumentParser(description='BP Convergence Test Suite')
    parser.add_argument('--n_runs', type=int, default=100, help='Number of convergence test runs')
    parser.add_argument('--quick', action='store_true', help='Run quick test with fewer runs')
    
    args = parser.parse_args()
    
    if args.quick:
        n_runs = 20
    else:
        n_runs = args.n_runs
    
    test_suite = BPConvergenceTestSuite()
    results = await test_suite.run_comprehensive_tests(n_runs)
    
    # Exit with appropriate code
    if results['overall_assessment']['ready_for_production']:
        print(f"\n✅ ALL TESTS PASSED - BP SYSTEM IS STABLE")
        return 0
    else:
        print(f"\n❌ SOME TESTS FAILED - BP SYSTEM NEEDS WORK")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())