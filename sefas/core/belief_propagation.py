"""
LDPC-style belief propagation for agent consensus.
Based on Shannon's information theory and error-correcting codes.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class BeliefNode(BaseModel):
    """Represents a belief state for a claim"""
    claim_id: str
    candidates: Dict[str, float] = Field(default_factory=dict)  # content -> probability
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence_count: int = 0
    converged: bool = False

class BeliefPropagationEngine:
    """
    Implements LDPC-style belief propagation for federated consensus.
    Exponentially reduces error rates through structured redundancy.
    """
    
    def __init__(
        self,
        damping_factor: float = 0.5,
        convergence_threshold: float = 0.01,
        max_iterations: int = 20,
        min_confidence: float = 0.7
    ):
        self.damping_factor = damping_factor
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
        self.min_confidence = min_confidence
        
        # Belief states
        self.beliefs: Dict[str, BeliefNode] = {}
        self.messages: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(dict)
        self.check_results: Dict[str, List[Dict]] = defaultdict(list)
        
    async def add_proposal(self, claim_id: str, content: str, confidence: float, agent_id: str):
        """Add a proposal from an agent"""
        if claim_id not in self.beliefs:
            self.beliefs[claim_id] = BeliefNode(claim_id=claim_id)
        
        node = self.beliefs[claim_id]
        
        # Accumulate evidence with agent confidence weighting
        if content not in node.candidates:
            node.candidates[content] = 0.0
        
        # Weight by confidence and add
        node.candidates[content] += confidence
        node.evidence_count += 1
        
        logger.info(f"Added proposal for {claim_id} from {agent_id}: confidence={confidence:.2f}")
    
    async def add_validation(self, claim_id: str, validator_id: str, result: Dict):
        """Add validation result from a checker"""
        self.check_results[claim_id].append({
            'validator': validator_id,
            'valid': result.get('valid', True),
            'confidence': result.get('confidence', 0.5),
            'evidence': result.get('evidence', '')
        })
        
        logger.info(f"Added validation for {claim_id} from {validator_id}: {result.get('confidence', 0.5):.2f}")
    
    def normalize_beliefs(self):
        """Normalize probability distributions"""
        for node in self.beliefs.values():
            total = sum(node.candidates.values())
            if total > 0:
                for content in node.candidates:
                    node.candidates[content] /= total
            
            # Update node confidence as max probability
            if node.candidates:
                node.confidence = max(node.candidates.values())
    
    async def propagate(self) -> Dict[str, Any]:
        """
        Run belief propagation until convergence.
        Returns consensus results with confidence scores.
        """
        logger.info(f"Starting belief propagation with {len(self.beliefs)} nodes")
        
        # Initial normalization
        self.normalize_beliefs()
        
        converged = False
        iteration = 0
        
        while not converged and iteration < self.max_iterations:
            old_beliefs = self._copy_beliefs()
            
            # Message passing phase
            await self._update_messages()
            
            # Belief update phase
            self._update_beliefs()
            
            # Check convergence
            max_delta = self._compute_max_delta(old_beliefs)
            converged = max_delta < self.convergence_threshold
            
            iteration += 1
            logger.info(f"Iteration {iteration}: max_delta={max_delta:.4f}, converged={converged}")
        
        # Extract consensus
        consensus = self._extract_consensus()
        
        # Calculate system confidence
        system_confidence = self._calculate_system_confidence()
        
        return {
            'consensus': consensus,
            'system_confidence': system_confidence,
            'iterations': iteration,
            'converged': converged,
            'beliefs': {k: v.dict() for k, v in self.beliefs.items()}
        }
    
    async def _update_messages(self):
        """Update messages between nodes (check-to-variable and variable-to-check)"""
        # For each validation result, propagate influence to beliefs
        for claim_id, validations in self.check_results.items():
            if claim_id not in self.beliefs:
                continue
                
            node = self.beliefs[claim_id]
            
            for validation in validations:
                # Checker confidence influences belief
                checker_conf = validation['confidence']
                is_valid = validation['valid']
                
                # Apply checker influence with damping
                for content in node.candidates:
                    # Positive validation increases probability
                    if is_valid:
                        boost = checker_conf * 0.1 * self.damping_factor
                        node.candidates[content] += boost
                    else:
                        # Negative validation decreases probability
                        penalty = (1 - checker_conf) * 0.1 * self.damping_factor
                        node.candidates[content] = max(0, node.candidates[content] - penalty)
        
        # Re-normalize after message passing
        self.normalize_beliefs()
    
    def _update_beliefs(self):
        """Update beliefs based on messages"""
        for node in self.beliefs.values():
            # Mark as converged if confidence exceeds threshold
            if node.confidence >= self.min_confidence:
                node.converged = True
    
    def _copy_beliefs(self) -> Dict[str, Dict[str, float]]:
        """Create a copy of current beliefs for convergence checking"""
        return {
            claim_id: dict(node.candidates)
            for claim_id, node in self.beliefs.items()
        }
    
    def _compute_max_delta(self, old_beliefs: Dict) -> float:
        """Compute maximum change in beliefs"""
        max_delta = 0.0
        
        for claim_id, node in self.beliefs.items():
            if claim_id not in old_beliefs:
                continue
                
            old_candidates = old_beliefs[claim_id]
            
            for content, prob in node.candidates.items():
                old_prob = old_candidates.get(content, 0.0)
                delta = abs(prob - old_prob)
                max_delta = max(max_delta, delta)
        
        return max_delta
    
    def _extract_consensus(self) -> Dict[str, Dict]:
        """Extract consensus from converged beliefs"""
        consensus = {}
        
        for claim_id, node in self.beliefs.items():
            if not node.candidates:
                consensus[claim_id] = {
                    'content': '',
                    'confidence': 0.0,
                    'converged': False
                }
                continue
            
            # Get highest probability candidate
            best_content = max(node.candidates, key=node.candidates.get)
            best_prob = node.candidates[best_content]
            
            consensus[claim_id] = {
                'content': best_content,
                'confidence': best_prob,
                'converged': node.converged,
                'alternatives': sorted(
                    [(c, p) for c, p in node.candidates.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]  # Top 3 alternatives
            }
        
        return consensus
    
    def _calculate_system_confidence(self) -> float:
        """Calculate overall system confidence"""
        if not self.beliefs:
            return 0.0
        
        confidences = [node.confidence for node in self.beliefs.values()]
        
        # Weighted average with penalty for non-converged nodes
        total_conf = 0.0
        total_weight = 0.0
        
        for node in self.beliefs.values():
            weight = 1.0 if node.converged else 0.5
            total_conf += node.confidence * weight
            total_weight += weight
        
        return total_conf / total_weight if total_weight > 0 else 0.0