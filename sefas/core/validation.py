"""
Enhanced validation system with redundancy and error correction.
"""

import asyncio
import hashlib
import json
import logging
from math import log
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime

from sefas.core.circuit_breaker import (
    circuit_breaker_manager, 
    CircuitBreakerOpenError, 
    CircuitBreakerExecutionError,
    CircuitBreakerConfig
)

logger = logging.getLogger(__name__)

def verdict_to_llr(verdict: str, confidence: float) -> float:
    """Convert verdict to log-likelihood ratio for BP"""
    # CRITICAL FIX: Clamp confidence to avoid log(0)
    conf = min(max(confidence, 1e-6), 1 - 1e-6)
    llr = log(conf / (1 - conf))
    
    if verdict == "support":
        return +llr  # Positive evidence
    elif verdict == "reject":
        return -llr  # Negative evidence
    else:  # abstain
        return 0.0   # Neutral evidence

class ValidationResult(BaseModel):
    """Result of a validation check with signed verdicts"""
    # CRITICAL FIX: Validators must take a stance - support/reject/abstain
    verdict: Literal["support", "reject", "abstain"] = "abstain"
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    validator_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: float = 0.0
    llr: float = 0.0  # Computed from verdict + confidence
    
    # Legacy compatibility
    valid: bool = True  # Derived from verdict != "reject"
    
    @validator('llr', always=True)
    def compute_llr(cls, v, values):
        """Compute log-likelihood ratio from verdict and confidence"""
        verdict = values.get('verdict', 'abstain')
        confidence = values.get('confidence', 0.5)
        return verdict_to_llr(verdict, confidence)
    
    @validator('valid', always=True)
    def compute_valid(cls, v, values):
        """Compute legacy valid field from verdict"""
        verdict = values.get('verdict', 'abstain')
        return verdict != "reject"
    
class EnhancedValidator:
    """
    Enhanced validator with multiple validation strategies and redundancy.
    """
    
    def __init__(self, validator_type: str = "general"):
        self.validator_type = validator_type
        self.validation_history = []
        
    async def validate_claim(
        self,
        claim: Dict,
        validators: List[Any] = None
    ) -> ValidationResult:
        """
        Validate a claim using multiple strategies.
        """
        import time
        start_time = time.time()
        
        # Defensive initialization
        if not claim or 'content' not in claim:
            logger.warning(f"Invalid claim structure: {claim}")
            return ValidationResult(
                valid=False,
                confidence=0.0,
                evidence="Missing claim content",
                errors=["Invalid claim structure"],
                execution_time=time.time() - start_time
            )
        
        content = claim.get('content', '')
        claim_id = claim.get('claim_id', 'unknown')
        
        # Run multiple validation checks in parallel
        validation_tasks = [
            self._validate_logic(content),
            self._validate_semantic(content),
            self._validate_consistency(content, self.validation_history),
            self._validate_evidence(claim.get('evidence', [])),
            self._validate_structure(claim)
        ]
        
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Aggregate results with error handling
        total_confidence = 0.0
        valid_count = 0
        errors = []
        evidence_parts = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Validation {i} failed: {result}")
                errors.append(str(result))
                continue
            
            if result.get('valid', False):
                valid_count += 1
            
            conf = result.get('confidence', 0.5)
            total_confidence += conf
            
            if result.get('evidence'):
                evidence_parts.append(result['evidence'])
        
        # Calculate aggregate confidence
        num_checks = len([r for r in results if not isinstance(r, Exception)])
        avg_confidence = total_confidence / num_checks if num_checks > 0 else 0.5
        
        # Require majority of checks to pass
        is_valid = valid_count > (num_checks / 2)
        
        # Store in history for consistency checks
        self.validation_history.append({
            'claim_id': claim_id,
            'content': content,
            'valid': is_valid,
            'confidence': avg_confidence,
            'timestamp': datetime.now()
        })
        
        # CRITICAL FIX: Convert to signed verdict
        if is_valid and avg_confidence > 0.7:
            verdict = "support"
        elif not is_valid or avg_confidence < 0.3:
            verdict = "reject"
        else:
            verdict = "abstain"  # Uncertain cases
        
        return ValidationResult(
            verdict=verdict,
            confidence=avg_confidence,
            evidence=evidence_parts,
            errors=errors,
            validator_id=self.validator_type,
            execution_time=time.time() - start_time
        )
    
    async def _validate_logic(self, content: str) -> Dict:
        """Check logical consistency"""
        try:
            # Check for logical contradictions
            contradictions = [
                ('all', 'none'),
                ('always', 'never'),
                ('must', 'cannot'),
                ('increase', 'decrease')
            ]
            
            content_lower = content.lower()
            has_contradiction = any(
                word1 in content_lower and word2 in content_lower
                for word1, word2 in contradictions
            )
            
            confidence = 0.2 if has_contradiction else 0.8
            
            return {
                'valid': not has_contradiction,
                'confidence': confidence,
                'evidence': 'No logical contradictions' if not has_contradiction else 'Potential contradiction detected'
            }
        except Exception as e:
            logger.error(f"Logic validation error: {e}")
            return {'valid': True, 'confidence': 0.5, 'evidence': 'Logic check inconclusive'}
    
    async def _validate_semantic(self, content: str) -> Dict:
        """Check semantic coherence"""
        try:
            # Simple semantic checks
            word_count = len(content.split())
            
            # Check if content is too short or too long
            if word_count < 3:
                return {'valid': False, 'confidence': 0.2, 'evidence': 'Content too short'}
            elif word_count > 1000:
                return {'valid': False, 'confidence': 0.3, 'evidence': 'Content too long'}
            
            # Check for meaningful content (not just repeated words)
            unique_words = len(set(content.lower().split()))
            diversity_ratio = unique_words / word_count
            
            if diversity_ratio < 0.3:
                return {'valid': False, 'confidence': 0.4, 'evidence': 'Low semantic diversity'}
            
            return {
                'valid': True,
                'confidence': min(0.9, 0.5 + diversity_ratio),
                'evidence': f'Semantic diversity: {diversity_ratio:.2f}'
            }
        except Exception as e:
            logger.error(f"Semantic validation error: {e}")
            return {'valid': True, 'confidence': 0.5, 'evidence': 'Semantic check inconclusive'}
    
    async def _validate_consistency(self, content: str, history: List[Dict]) -> Dict:
        """Check consistency with previous validations"""
        try:
            if not history:
                return {'valid': True, 'confidence': 0.7, 'evidence': 'First validation'}
            
            # Check for repeated content (potential loop)
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            recent_hashes = [
                hashlib.md5(h['content'].encode()).hexdigest()
                for h in history[-5:]  # Last 5 validations
            ]
            
            if content_hash in recent_hashes:
                return {'valid': False, 'confidence': 0.3, 'evidence': 'Duplicate content detected'}
            
            # Check confidence trend
            recent_confidences = [h['confidence'] for h in history[-3:]]
            if recent_confidences:
                avg_recent = sum(recent_confidences) / len(recent_confidences)
                confidence = min(0.9, avg_recent + 0.1)  # Slight boost for consistency
            else:
                confidence = 0.7
            
            return {
                'valid': True,
                'confidence': confidence,
                'evidence': f'Consistent with history (trend: {confidence:.2f})'
            }
        except Exception as e:
            logger.error(f"Consistency validation error: {e}")
            return {'valid': True, 'confidence': 0.5, 'evidence': 'Consistency check inconclusive'}
    
    async def _validate_evidence(self, evidence: List[str]) -> Dict:
        """Validate supporting evidence"""
        try:
            if not evidence:
                return {'valid': True, 'confidence': 0.4, 'evidence': 'No evidence provided'}
            
            # Check evidence quality
            valid_evidence = [e for e in evidence if e and len(e) > 10]
            evidence_ratio = len(valid_evidence) / len(evidence) if evidence else 0
            
            confidence = min(0.9, 0.4 + (evidence_ratio * 0.5))
            
            return {
                'valid': evidence_ratio > 0.5,
                'confidence': confidence,
                'evidence': f'{len(valid_evidence)} valid evidence items'
            }
        except Exception as e:
            logger.error(f"Evidence validation error: {e}")
            return {'valid': True, 'confidence': 0.5, 'evidence': 'Evidence check inconclusive'}
    
    async def _validate_structure(self, claim: Dict) -> Dict:
        """Validate claim structure and completeness"""
        try:
            required_fields = ['claim_id', 'content']
            optional_fields = ['confidence', 'evidence', 'agent_id']
            
            # Check required fields
            missing = [f for f in required_fields if f not in claim]
            if missing:
                return {
                    'valid': False,
                    'confidence': 0.2,
                    'evidence': f'Missing required fields: {missing}'
                }
            
            # Check optional fields for bonus confidence
            present_optional = [f for f in optional_fields if f in claim]
            completeness = (len(required_fields) + len(present_optional)) / (len(required_fields) + len(optional_fields))
            
            confidence = min(0.9, 0.5 + (completeness * 0.4))
            
            return {
                'valid': True,
                'confidence': confidence,
                'evidence': f'Structure completeness: {completeness:.2f}'
            }
        except Exception as e:
            logger.error(f"Structure validation error: {e}")
            return {'valid': True, 'confidence': 0.5, 'evidence': 'Structure check inconclusive'}

class ValidatorPool:
    """
    Pool of validators with different specializations.
    """
    
    def __init__(self):
        self.validators = {
            'logic': EnhancedValidator('logic'),
            'semantic': EnhancedValidator('semantic'),
            'consistency': EnhancedValidator('consistency'),
            'evidence': EnhancedValidator('evidence'),
            'structure': EnhancedValidator('structure')
        }
    
    def register_validator(self, name: str, validator: Any):
        """Register a new validator (agent-based)"""
        # Create wrapper for agent-based validators
        self.validators[name] = validator
    
    async def validate_with_quorum(
        self,
        claim: Dict,
        quorum: int = 3
    ) -> ValidationResult:
        """
        Validate using multiple validators and require quorum agreement.
        """
        
        # Run all validators in parallel
        validation_tasks = []
        for validator in self.validators.values():
            if hasattr(validator, 'validate_claim'):
                # Enhanced validator
                validation_tasks.append(validator.validate_claim(claim))
            elif hasattr(validator, 'execute'):
                # Agent-based validator
                validation_tasks.append(self._validate_with_agent(validator, claim))
            else:
                logger.warning(f"Unknown validator type: {type(validator)}")
        
        if not validation_tasks:
            logger.error("No valid validators available")
            return ValidationResult(
                valid=False,
                confidence=0.0,
                evidence="No validators available",
                errors=["No validators configured"]
            )
        
        results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, ValidationResult)]
        
        if len(valid_results) < quorum:
            logger.warning(f"Insufficient validators: {len(valid_results)} < {quorum}")
            return ValidationResult(
                verdict="abstain",
                confidence=0.0,
                evidence=["Insufficient validator consensus"],
                errors=[f"Only {len(valid_results)} validators succeeded"]
            )
        
        # CRITICAL FIX: Calculate verdict-based consensus using LLR
        support_count = sum(1 for r in valid_results if r.verdict == "support")
        reject_count = sum(1 for r in valid_results if r.verdict == "reject")
        abstain_count = sum(1 for r in valid_results if r.verdict == "abstain")
        
        total_llr = sum(r.llr for r in valid_results)
        avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
        
        # CRITICAL FIX: Use majority voting instead of absolute quorum thresholds
        total_validators = len(valid_results)
        majority_threshold = total_validators // 2 + 1  # More than half
        
        logger.info(f"🗳️ QUORUM VOTING: {total_validators} validators - support:{support_count}, reject:{reject_count}, abstain:{abstain_count}")
        logger.info(f"🗳️ MAJORITY THRESHOLD: {majority_threshold}, total_llr:{total_llr:.3f}, avg_conf:{avg_confidence:.3f}")
        
        # Determine verdict using majority voting with confidence backup
        if support_count >= majority_threshold:
            verdict = "support"
            logger.info(f"🗳️ VERDICT: support (majority {support_count}/{total_validators})")
        elif reject_count >= majority_threshold:
            verdict = "reject"
            logger.info(f"🗳️ VERDICT: reject (majority {reject_count}/{total_validators})")
        elif support_count > reject_count:
            # Plurality support (most votes but not majority)
            verdict = "support" if avg_confidence > 0.6 else "abstain"
            logger.info(f"🗳️ VERDICT: {verdict} (plurality support {support_count} > {reject_count}, conf={avg_confidence:.3f})")
        elif reject_count > support_count:
            # Plurality reject (most votes but not majority)
            verdict = "reject" if avg_confidence < 0.4 else "abstain"
            logger.info(f"🗳️ VERDICT: {verdict} (plurality reject {reject_count} > {support_count}, conf={avg_confidence:.3f})")
        else:
            # Tie or all abstain - use confidence as tiebreaker
            if avg_confidence > 0.7:
                verdict = "support"
                logger.info(f"🗳️ VERDICT: support (tie-breaker, high confidence {avg_confidence:.3f})")
            elif avg_confidence < 0.3:
                verdict = "reject"
                logger.info(f"🗳️ VERDICT: reject (tie-breaker, low confidence {avg_confidence:.3f})")
            else:
                verdict = "abstain"
                logger.info(f"🗳️ VERDICT: abstain (tie-breaker, moderate confidence {avg_confidence:.3f})")
        
        # Aggregate evidence
        all_evidence = []
        for r in valid_results:
            if isinstance(r.evidence, list):
                all_evidence.extend(r.evidence)
            elif r.evidence:
                all_evidence.append(str(r.evidence))
        
        all_errors = [err for r in valid_results for err in r.errors]
        
        return ValidationResult(
            verdict=verdict,
            confidence=avg_confidence,
            evidence=all_evidence,
            errors=all_errors,
            validator_id='quorum_pool'
        )
    
    async def _validate_with_agent(self, agent, claim: Dict) -> ValidationResult:
        """Validate using an agent-based validator with circuit breaker protection"""
        agent_name = getattr(agent, 'name', getattr(agent, 'role', 'agent_validator'))
        breaker_name = f"validator_{agent_name}"
        
        # Configure circuit breaker for this validator
        config = CircuitBreakerConfig(
            failure_threshold=2,  # Lower threshold for validators
            reset_timeout=30.0,   # Shorter reset time
            half_open_max_calls=2,
            success_threshold=1
        )
        
        try:
            # Execute with circuit breaker protection
            async def execute_validation():
                # Import the input preparation function
                from sefas.core.contracts import prepare_validation_input, create_validation_task
                
                # THE CRITICAL FIX - Use proper input preparation
                prepared_content = prepare_validation_input(claim)
                
                # Create proper validation task structure
                validation_task = {
                    'description': f"Validate this claim: {prepared_content[:100]}...",
                    'type': 'verification',  # CheckerAgent expects 'verification' type
                    'proposal': claim,  # Pass original claim for context
                    'claim_data': {
                        'content': prepared_content,  # This is now a STRING!
                        'claim_id': claim.get('claim_id', 'unknown'),
                        'confidence': claim.get('confidence', 0.5)
                    }
                }
                
                # Execute validation through agent (async)
                result = agent.execute(validation_task)
                if asyncio.iscoroutine(result):
                    result = await result
                
                # Check for validation errors
                if 'error' in result or result.get('confidence', 0) == 0.0:
                    raise ValueError(f"Validation failed: {result.get('error', 'Low confidence')}")
                
                return result
            
            result = await circuit_breaker_manager.execute_with_breaker_async(
                breaker_name, execute_validation
            )
            
            # Parse agent response into ValidationResult with signed verdict
            confidence = result.get('confidence', 0.5)
            
            # Handle verification result properly
            verification = result.get('verification', {})
            if verification:
                is_valid = verification.get('passed', confidence > 0.5)
                overall_score = verification.get('overall_score', confidence)
                evidence = verification.get('details', result.get('summary', ''))
            else:
                is_valid = confidence > 0.5  # Simple threshold
                overall_score = confidence
                evidence = result.get('reasoning', result.get('summary', result.get('proposal', '')))
            
            # CRITICAL FIX: Convert to signed verdict based on confidence and validity
            if is_valid and overall_score > 0.7:
                verdict = "support"
            elif not is_valid or overall_score < 0.3:
                verdict = "reject"
            else:
                verdict = "abstain"  # Uncertain/middle ground
            
            logger.info(f"🔍 INDIVIDUAL VALIDATOR: {agent_name} → verdict={verdict}, conf={overall_score:.3f}, valid={is_valid}")
            
            # Extract any issues found
            issues = result.get('issues', [])
            if isinstance(issues, str):
                issues = [issues]
            
            # Ensure evidence is a list
            evidence_list = [evidence] if isinstance(evidence, str) else evidence
            if not evidence_list:
                evidence_list = []
            
            return ValidationResult(
                verdict=verdict,
                confidence=overall_score,
                evidence=evidence_list,
                errors=issues,
                validator_id=agent_name
            )
            
        except CircuitBreakerOpenError:
            logger.warning(f"Circuit breaker is OPEN for validator {agent_name}")
            return ValidationResult(
                verdict="abstain",
                confidence=0.0,
                evidence=[f"Validator {agent_name} unavailable (circuit breaker OPEN)"],
                errors=["Circuit breaker protection active"],
                validator_id=agent_name
            )
            
        except CircuitBreakerExecutionError as e:
            logger.error(f"Circuit breaker recorded failure for validator {agent_name}: {e}")
            return ValidationResult(
                verdict="abstain",
                confidence=0.0,
                evidence=[f"Validation failed: {str(e)}"],
                errors=[str(e)],
                validator_id=agent_name
            )
            
        except Exception as e:
            logger.error(f"Agent validation failed: {e}")
            return ValidationResult(
                verdict="abstain",
                confidence=0.0,
                evidence=[f"Validation error: {str(e)}"],
                errors=[str(e)],
                validator_id=agent_name
            )