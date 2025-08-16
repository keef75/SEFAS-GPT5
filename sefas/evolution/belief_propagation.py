"""Belief propagation engine for consensus and evidence aggregation."""

from typing import Dict, List, Any, Tuple
import numpy as np
from collections import defaultdict
import math

class BeliefPropagationEngine:
    """Belief propagation for multi-agent consensus"""
    
    def __init__(self, convergence_threshold: float = 0.01, max_iterations: int = 50):
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
        self.belief_history = []
        
    def propagate(self, proposals: List[Dict[str, Any]], verifications: List[Dict[str, Any]]) -> Dict[str, float]:
        """Run belief propagation on proposals and verifications"""
        
        if not proposals:
            return {}
        
        # Initialize belief network
        belief_network = self._build_belief_network(proposals, verifications)
        
        # Run iterative belief propagation
        final_beliefs = self._iterate_belief_propagation(belief_network)
        
        # Store history
        self.belief_history.append({
            'proposals': len(proposals),
            'verifications': len(verifications),
            'beliefs': final_beliefs.copy(),
            'consensus_strength': self._calculate_consensus_strength(final_beliefs)
        })
        
        return final_beliefs
    
    def _build_belief_network(self, proposals: List[Dict[str, Any]], verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build belief network from proposals and verifications"""
        
        network = {
            'nodes': {},
            'edges': [],
            'evidence': {}
        }
        
        # Add proposal nodes
        for i, proposal in enumerate(proposals):
            node_id = f"proposal_{i}"
            network['nodes'][node_id] = {
                'type': 'proposal',
                'confidence': proposal.get('confidence', 0.5),
                'agent_id': proposal.get('agent_role', 'unknown'),
                'content': proposal.get('proposal', ''),
                'belief': proposal.get('confidence', 0.5)
            }
        
        # Add verification nodes and connect to proposals
        for i, verification in enumerate(verifications):
            node_id = f"verification_{i}"
            network['nodes'][node_id] = {
                'type': 'verification',
                'confidence': verification.get('confidence', 0.5),
                'overall_score': verification.get('overall_score', 0.5),
                'validation_result': verification.get('validation_result', 'unknown'),
                'belief': verification.get('overall_score', 0.5)
            }
            
            # Connect verifications to related proposals
            # In a full implementation, this would use semantic similarity
            # For now, connect each verification to all proposals
            for j in range(len(proposals)):
                proposal_id = f"proposal_{j}"
                edge_weight = self._calculate_edge_weight(
                    network['nodes'][proposal_id], 
                    network['nodes'][node_id]
                )
                network['edges'].append({
                    'from': proposal_id,
                    'to': node_id,
                    'weight': edge_weight
                })
        
        return network
    
    def _calculate_edge_weight(self, proposal_node: Dict[str, Any], verification_node: Dict[str, Any]) -> float:
        """Calculate edge weight between proposal and verification"""
        
        # Base weight on verification result
        validation_result = verification_node.get('validation_result', 'unknown')
        base_weights = {
            'passed': 0.9,
            'passed_with_notes': 0.7,
            'needs_revision': 0.4,
            'failed': 0.1,
            'unknown': 0.5
        }
        
        base_weight = base_weights.get(validation_result, 0.5)
        
        # Adjust based on verification confidence
        verification_confidence = verification_node.get('confidence', 0.5)
        adjusted_weight = base_weight * verification_confidence
        
        return max(0.1, min(0.9, adjusted_weight))
    
    def _iterate_belief_propagation(self, network: Dict[str, Any]) -> Dict[str, float]:
        """Iterate belief propagation until convergence"""
        
        nodes = network['nodes']
        edges = network['edges']
        
        # Initialize beliefs
        beliefs = {node_id: node['belief'] for node_id, node in nodes.items()}
        
        for iteration in range(self.max_iterations):
            new_beliefs = beliefs.copy()
            
            # Update beliefs for each node
            for node_id, node in nodes.items():
                if node['type'] == 'proposal':
                    new_beliefs[node_id] = self._update_proposal_belief(
                        node_id, beliefs, edges, nodes
                    )
                elif node['type'] == 'verification':
                    new_beliefs[node_id] = self._update_verification_belief(
                        node_id, beliefs, edges, nodes
                    )
            
            # Check convergence
            max_change = max(abs(new_beliefs[node_id] - beliefs[node_id]) 
                           for node_id in beliefs.keys())
            
            beliefs = new_beliefs
            
            if max_change < self.convergence_threshold:
                break
        
        # Return only proposal beliefs for final result
        proposal_beliefs = {
            node_id: belief for node_id, belief in beliefs.items()
            if nodes[node_id]['type'] == 'proposal'
        }
        
        return proposal_beliefs
    
    def _update_proposal_belief(self, node_id: str, beliefs: Dict[str, float], 
                              edges: List[Dict[str, Any]], nodes: Dict[str, Any]) -> float:
        """Update belief for a proposal node"""
        
        # Get connected verification nodes
        connected_verifications = [
            edge for edge in edges 
            if edge['from'] == node_id
        ]
        
        if not connected_verifications:
            return nodes[node_id]['belief']  # No change if no verifications
        
        # Calculate weighted evidence
        total_weight = 0.0
        weighted_belief = 0.0
        
        for edge in connected_verifications:
            verification_id = edge['to']
            verification_belief = beliefs[verification_id]
            edge_weight = edge['weight']
            
            weighted_belief += verification_belief * edge_weight
            total_weight += edge_weight
        
        if total_weight > 0:
            evidence_belief = weighted_belief / total_weight
        else:
            evidence_belief = 0.5
        
        # Combine with prior belief (initial confidence)
        prior_belief = nodes[node_id]['confidence']
        alpha = 0.7  # Weight for evidence vs prior
        
        updated_belief = alpha * evidence_belief + (1 - alpha) * prior_belief
        
        return max(0.0, min(1.0, updated_belief))
    
    def _update_verification_belief(self, node_id: str, beliefs: Dict[str, float],
                                  edges: List[Dict[str, Any]], nodes: Dict[str, Any]) -> float:
        """Update belief for a verification node"""
        
        # Verification beliefs are more stable, but can be influenced by proposal consensus
        current_belief = nodes[node_id]['belief']
        
        # Get connected proposals
        connected_proposals = [
            edge for edge in edges 
            if edge['to'] == node_id
        ]
        
        if not connected_proposals:
            return current_belief
        
        # Calculate proposal consensus
        proposal_beliefs = [beliefs[edge['from']] for edge in connected_proposals]
        proposal_consensus = np.mean(proposal_beliefs)
        
        # Slightly adjust verification belief based on proposal consensus
        adjustment_factor = 0.1
        adjusted_belief = current_belief + adjustment_factor * (proposal_consensus - current_belief)
        
        return max(0.0, min(1.0, adjusted_belief))
    
    def _calculate_consensus_strength(self, beliefs: Dict[str, float]) -> float:
        """Calculate the strength of consensus among beliefs"""
        
        if not beliefs:
            return 0.0
        
        belief_values = list(beliefs.values())
        
        # Calculate variance (lower variance = higher consensus)
        mean_belief = np.mean(belief_values)
        variance = np.var(belief_values)
        
        # Convert variance to consensus strength (0-1)
        # Lower variance = higher consensus
        max_variance = 0.25  # Maximum expected variance for normalization
        consensus_strength = max(0.0, 1.0 - (variance / max_variance))
        
        return consensus_strength
    
    def get_consensus_summary(self, beliefs: Dict[str, float]) -> Dict[str, Any]:
        """Get summary of consensus state"""
        
        if not beliefs:
            return {
                'status': 'no_beliefs',
                'consensus_strength': 0.0,
                'agreement_level': 'none'
            }
        
        belief_values = list(beliefs.values())
        consensus_strength = self._calculate_consensus_strength(beliefs)
        
        summary = {
            'consensus_strength': consensus_strength,
            'mean_belief': np.mean(belief_values),
            'std_belief': np.std(belief_values),
            'min_belief': min(belief_values),
            'max_belief': max(belief_values),
            'belief_range': max(belief_values) - min(belief_values),
            'high_confidence_count': sum(1 for b in belief_values if b > 0.7),
            'low_confidence_count': sum(1 for b in belief_values if b < 0.3),
            'total_proposals': len(belief_values)
        }
        
        # Determine agreement level
        if consensus_strength > 0.8:
            summary['agreement_level'] = 'strong'
        elif consensus_strength > 0.6:
            summary['agreement_level'] = 'moderate'
        elif consensus_strength > 0.4:
            summary['agreement_level'] = 'weak'
        else:
            summary['agreement_level'] = 'poor'
        
        # Determine overall status
        if summary.get('mean_belief', 0.0) > 0.7 and consensus_strength > 0.6:
            summary['status'] = 'strong_consensus'
        elif summary.get('mean_belief', 0.0) > 0.5 and consensus_strength > 0.4:
            summary['status'] = 'moderate_consensus'
        elif consensus_strength > 0.6:
            summary['status'] = 'agreement_but_low_confidence'
        else:
            summary['status'] = 'no_consensus'
        
        return summary
    
    def get_agent_performance_insights(self, proposals: List[Dict[str, Any]], 
                                     beliefs: Dict[str, float]) -> Dict[str, Any]:
        """Analyze agent performance based on belief propagation results"""
        
        agent_performance = defaultdict(list)
        
        # Group proposals by agent
        for i, proposal in enumerate(proposals):
            agent_id = proposal.get('agent_role', 'unknown')
            proposal_id = f"proposal_{i}"
            belief = beliefs.get(proposal_id, 0.5)
            
            agent_performance[agent_id].append({
                'initial_confidence': proposal.get('confidence', 0.5),
                'final_belief': belief,
                'belief_improvement': belief - proposal.get('confidence', 0.5)
            })
        
        # Calculate agent summaries
        agent_summaries = {}
        for agent_id, performances in agent_performance.items():
            avg_initial = np.mean([p['initial_confidence'] for p in performances])
            avg_final = np.mean([p['final_belief'] for p in performances])
            avg_improvement = np.mean([p['belief_improvement'] for p in performances])
            
            agent_summaries[agent_id] = {
                'proposal_count': len(performances),
                'avg_initial_confidence': avg_initial,
                'avg_final_belief': avg_final,
                'avg_belief_improvement': avg_improvement,
                'consistency': 1.0 - np.std([p['final_belief'] for p in performances]),
                'performance_trend': 'improving' if avg_improvement > 0.1 else 'stable' if avg_improvement > -0.1 else 'declining'
            }
        
        return agent_summaries
    
    def get_propagation_history(self) -> List[Dict[str, Any]]:
        """Get history of belief propagation runs"""
        return self.belief_history.copy()
    
    def reset_history(self) -> None:
        """Reset belief propagation history"""
        self.belief_history.clear()