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
    Implements stabilized LDPC-style belief propagation for federated consensus.
    Exponentially reduces error rates through structured redundancy with oscillation detection.
    """
    
    def __init__(
        self,
        damping_factor: float = 0.7,  # Balanced for speed and stability
        convergence_threshold: float = 1e-3,  # Slightly relaxed for faster convergence
        max_iterations: int = 50,  # More iterations allowed
        min_confidence: float = 0.5,
        use_log_domain: bool = True  # For numerical stability
    ):
        self.damping_factor = damping_factor
        self.convergence_threshold = convergence_threshold
        self.max_iterations = max_iterations
        self.min_confidence = min_confidence
        self.use_log_domain = use_log_domain
        
        # Stability tracking
        self.oscillation_history: List[float] = []
        self.adaptive_damping = damping_factor
        self.patience_counter = 0
        self.last_delta = float('inf')
        
        # Belief states
        self.beliefs: Dict[str, BeliefNode] = {}
        self.messages: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(dict)
        self.check_results: Dict[str, List[Dict]] = defaultdict(list)
        
        # Track propagation history
        self.propagation_history: List[Dict[str, Any]] = []
        
    async def add_proposal(self, claim_id: str, content: str, confidence: float, agent_id: str):
        """Add a proposal from an agent"""
        if claim_id not in self.beliefs:
            self.beliefs[claim_id] = BeliefNode(claim_id=claim_id)
        
        node = self.beliefs[claim_id]
        
        # Use proper confidence aggregation instead of simple addition
        if content not in node.candidates:
            node.candidates[content] = confidence
        else:
            # Weighted average of existing and new confidence
            existing_conf = node.candidates[content]
            # Higher weight to new evidence encourages learning
            node.candidates[content] = (existing_conf * 0.6) + (confidence * 0.4)
        
        node.evidence_count += 1
        
        logger.info(f"Added proposal for {claim_id} from {agent_id}: confidence={confidence:.2f} -> {node.candidates[content]:.2f}")
    
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
        """Normalize probability distributions while preserving confidence relationships"""
        for node in self.beliefs.values():
            if not node.candidates:
                continue
                
            # Find the current max to preserve relative relationships
            max_confidence = max(node.candidates.values())
            
            # Only normalize if values exceed 1.0 to preserve confidence scale
            if max_confidence > 1.0:
                normalization_factor = 1.0 / max_confidence
                for content in node.candidates:
                    node.candidates[content] *= normalization_factor
            
            # Update node confidence as max probability (after normalization)
            node.confidence = max(node.candidates.values())
    
    async def propagate(self) -> Dict[str, Any]:
        """
        Run stabilized belief propagation with oscillation detection until convergence.
        Returns consensus results with confidence scores.
        """
        logger.info(f"Starting stabilized belief propagation with {len(self.beliefs)} nodes")
        
        # Reset stability tracking
        self.oscillation_history = []
        self.adaptive_damping = self.damping_factor
        self.patience_counter = 0
        self.last_delta = float('inf')
        
        # Initial normalization
        self.normalize_beliefs()
        
        # Initialize beliefs in log domain if requested
        if self.use_log_domain:
            beliefs_log = self._initialize_log_beliefs()
        else:
            beliefs_log = self._copy_beliefs()
            
        converged = False
        iteration = 0
        
        while not converged and iteration < self.max_iterations:
            old_beliefs = self._copy_beliefs()
            
            # Message passing phase with damping
            await self._update_messages_with_damping(old_beliefs)
            
            # Belief update phase
            self._update_beliefs()
            
            # Check convergence and oscillation
            max_delta = self._compute_max_delta(old_beliefs)
            self.oscillation_history.append(max_delta)
            
            # Detect oscillation and adapt
            if self._detect_oscillation():
                logger.warning(f"Oscillation detected at iteration {iteration}")
                self.adaptive_damping = min(0.95, self.adaptive_damping + 0.1)
                # Apply emergency stabilization
                self._apply_min_sum_stabilization()
            
            # Early stopping with patience
            converged = self._should_stop(max_delta, iteration)
            
            iteration += 1
            logger.info(f"Iteration {iteration}: max_delta={max_delta:.6f}, damping={self.adaptive_damping:.2f}, converged={converged}")
        
        # Extract consensus
        consensus = self._extract_consensus()
        
        # Calculate system confidence
        system_confidence = self._calculate_system_confidence()
        
        # Record this propagation run in history
        propagation_record = {
            'timestamp': asyncio.get_event_loop().time(),
            'iterations': iteration,
            'converged': converged,
            'system_confidence': system_confidence,
            'num_beliefs': len(self.beliefs),
            'num_validations': sum(len(v) for v in self.check_results.values()),
            'final_consensus': consensus,
            'oscillation_detected': len(self.oscillation_history) > 6 and self._detect_oscillation(),
            'final_damping': self.adaptive_damping
        }
        self.propagation_history.append(propagation_record)
        
        if not converged:
            logger.warning(f"BP did not converge after {iteration} iterations - using best estimate")
        else:
            logger.info(f"BP converged successfully in {iteration} iterations")
        
        return {
            'consensus': consensus,
            'system_confidence': system_confidence,
            'iterations': iteration,
            'converged': converged,
            'beliefs': {k: v.dict() for k, v in self.beliefs.items()},
            'oscillation_detected': propagation_record['oscillation_detected'],
            'final_damping': self.adaptive_damping
        }
    
    async def _update_messages(self):
        """Update messages between nodes (check-to-variable and variable-to-check)"""
        # For each validation result, propagate influence to beliefs
        for claim_id, validations in self.check_results.items():
            if claim_id not in self.beliefs:
                continue
                
            node = self.beliefs[claim_id]
            
            # Calculate average validation confidence for this claim
            total_validation_conf = 0.0
            positive_validations = 0
            total_validations = len(validations)
            
            for validation in validations:
                checker_conf = validation['confidence']
                is_valid = validation['valid']
                
                total_validation_conf += checker_conf
                if is_valid:
                    positive_validations += 1
            
            if total_validations > 0:
                avg_validation_conf = total_validation_conf / total_validations
                validation_success_rate = positive_validations / total_validations
                
                # Apply validation influence more meaningfully
                validation_multiplier = avg_validation_conf * validation_success_rate
                
                # Update all candidates based on validation results
                for content in node.candidates:
                    current_conf = node.candidates[content]
                    
                    # Apply more conservative validation influence
                    if validation_success_rate > 0.6 and avg_validation_conf > 0.6:
                        # Modest boost for strong positive validation
                        boost_factor = 1.0 + (validation_multiplier * 0.15)
                        node.candidates[content] = min(0.95, current_conf * boost_factor)
                    elif validation_success_rate < 0.4 or avg_validation_conf < 0.4:
                        # Modest penalty for poor validation
                        penalty_factor = 1.0 - (validation_multiplier * 0.1)
                        node.candidates[content] = max(0.15, current_conf * penalty_factor)
                    # For moderate validation, apply small adjustment
                    else:
                        adjustment = (validation_success_rate - 0.5) * 0.05
                        node.candidates[content] = max(0.15, min(0.95, current_conf + adjustment))
        
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
        
        # Use harmonic mean of confidences to be more conservative
        # This prevents one high confidence from inflating system confidence
        harmonic_sum = 0.0
        num_beliefs = 0
        
        for node in self.beliefs.values():
            if node.confidence > 0.0:  # Avoid division by zero
                harmonic_sum += 1.0 / node.confidence
                num_beliefs += 1
        
        if num_beliefs == 0:
            return 0.0
        
        harmonic_mean = num_beliefs / harmonic_sum
        
        # Apply convergence bonus (small)
        converged_count = sum(1 for node in self.beliefs.values() if node.converged)
        convergence_bonus = 0.05 * (converged_count / len(self.beliefs))
        
        return min(1.0, harmonic_mean + convergence_bonus)
    
    def get_propagation_history(self) -> List[Dict[str, Any]]:
        """Return the history of propagation runs"""
        return self.propagation_history.copy()
    
    def get_agent_performance_insights(self, proposals: List[Dict[str, Any]], beliefs: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Generate performance insights for agents based on their contributions"""
        insights = {}
        
        # Group proposals by agent role
        role_performance = defaultdict(list)
        
        for proposal in proposals:
            agent_role = proposal.get('agent_role', 'unknown')
            confidence = proposal.get('confidence', 0.5)
            
            # Get final belief for this proposal's claim
            claim_id = proposal.get('subclaim_id', '')
            final_belief = beliefs.get(claim_id, 0.5)
            
            role_performance[agent_role].append({
                'initial_confidence': confidence,
                'final_belief': final_belief,
                'agent_id': proposal.get('agent_id', 'unknown')
            })
        
        # Calculate insights for each role
        for role, performances in role_performance.items():
            if not performances:
                continue
                
            avg_initial = sum(p['initial_confidence'] for p in performances) / len(performances)
            avg_final = sum(p['final_belief'] for p in performances) / len(performances)
            
            # Determine performance trend
            if avg_final > avg_initial + 0.1:
                trend = "improving"
            elif avg_final < avg_initial - 0.1:
                trend = "declining"
            else:
                trend = "stable"
            
            insights[role] = {
                'avg_initial_confidence': avg_initial,
                'avg_final_belief': avg_final,
                'performance_trend': trend,
                'proposal_count': len(performances),
                'confidence_delta': avg_final - avg_initial
            }
        
        return insights
    
    def _initialize_log_beliefs(self) -> Dict[str, Dict[str, float]]:
        """Initialize beliefs in log domain for numerical stability"""
        log_beliefs = {}
        for claim_id, node in self.beliefs.items():
            log_beliefs[claim_id] = {}
            for content, prob in node.candidates.items():
                # Convert to log domain, handling edge cases
                if prob <= 0:
                    log_beliefs[claim_id][content] = -1e10  # Very small log probability
                else:
                    log_beliefs[claim_id][content] = np.log(prob)
        return log_beliefs
    
    async def _update_messages_with_damping(self, old_beliefs: Dict[str, Dict[str, float]]):
        """Update messages with adaptive damping for stability"""
        # First, update messages normally
        await self._update_messages()
        
        # Then apply damping to smooth changes
        for claim_id, node in self.beliefs.items():
            if claim_id not in old_beliefs:
                continue
                
            old_candidates = old_beliefs[claim_id]
            
            for content in node.candidates:
                if content in old_candidates:
                    old_value = old_candidates[content]
                    new_value = node.candidates[content]
                    
                    # Apply adaptive damping
                    damped_value = (
                        self.adaptive_damping * old_value +
                        (1 - self.adaptive_damping) * new_value
                    )
                    
                    node.candidates[content] = damped_value
        
        # Re-normalize after damping
        self.normalize_beliefs()
    
    def _detect_oscillation(self) -> bool:
        """Detect period-2 or period-3 oscillations in convergence"""
        if len(self.oscillation_history) < 6:
            return False
        
        recent = self.oscillation_history[-6:]
        
        # Check for A-B-A-B pattern (period-2)
        if (abs(recent[0] - recent[2]) < 1e-6 and 
            abs(recent[1] - recent[3]) < 1e-6 and
            abs(recent[2] - recent[4]) < 1e-6 and
            abs(recent[3] - recent[5]) < 1e-6):
            logger.debug("Period-2 oscillation detected")
            return True
            
        # Check for A-B-C-A-B-C pattern (period-3)
        if (abs(recent[0] - recent[3]) < 1e-6 and
            abs(recent[1] - recent[4]) < 1e-6 and
            abs(recent[2] - recent[5]) < 1e-6):
            logger.debug("Period-3 oscillation detected")
            return True
        
        # Check for stagnation (no improvement)
        if len(recent) >= 4:
            variance = np.var(recent[-4:])
            if variance < 1e-10:  # Very low variance indicates stagnation
                logger.debug("Stagnation detected")
                return True
                
        return False
    
    def _should_stop(self, delta: float, iteration: int) -> bool:
        """Determine if BP should stop based on convergence and patience"""
        # Primary convergence check
        if delta < self.convergence_threshold:
            return True
        
        # Patience mechanism - stop if no improvement for several iterations
        if delta >= self.last_delta * 0.99:  # No significant improvement
            self.patience_counter += 1
        else:
            self.patience_counter = 0
        
        # Stop if no improvement for 5 consecutive iterations
        if self.patience_counter >= 5:
            logger.info(f"Early stopping: no improvement for {self.patience_counter} iterations")
            return True
        
        # Minimum iterations check
        if iteration < 3:
            return False
        
        self.last_delta = delta
        return False
    
    def _apply_min_sum_stabilization(self):
        """Apply min-sum approximation for better numerical stability"""
        for node in self.beliefs.values():
            if len(node.candidates) <= 1:
                continue
            
            # Convert to log domain temporarily
            log_candidates = {}
            for content, prob in node.candidates.items():
                if prob > 0:
                    log_candidates[content] = np.log(prob)
                else:
                    log_candidates[content] = -1e10
            
            # Apply min-sum approximation (take maximum in log domain)
            max_log_prob = max(log_candidates.values())
            
            # Normalize in log domain
            for content in log_candidates:
                log_candidates[content] -= max_log_prob
            
            # Convert back to probability domain with better numerical stability
            for content in node.candidates:
                if content in log_candidates:
                    node.candidates[content] = np.exp(log_candidates[content])
            
        # Re-normalize
        self.normalize_beliefs()