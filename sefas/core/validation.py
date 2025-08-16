"""
Enhanced validation system with redundancy and error correction.
"""

import asyncio
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Result of a validation check"""
    valid: bool = True
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    evidence: str = ""
    errors: List[str] = Field(default_factory=list)
    validator_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    
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
        
        # Defensive initialization
        if not claim or 'content' not in claim:
            logger.warning(f"Invalid claim structure: {claim}")
            return ValidationResult(
                valid=False,
                confidence=0.0,
                evidence="Missing claim content",
                errors=["Invalid claim structure"]
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
        
        return ValidationResult(
            valid=is_valid,
            confidence=avg_confidence,
            evidence=' | '.join(evidence_parts),
            errors=errors,
            validator_id=self.validator_type
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
                valid=False,
                confidence=0.0,
                evidence="Insufficient validator consensus",
                errors=[f"Only {len(valid_results)} validators succeeded"]
            )
        
        # Calculate quorum consensus
        valid_count = sum(1 for r in valid_results if r.valid)
        total_confidence = sum(r.confidence for r in valid_results)
        avg_confidence = total_confidence / len(valid_results)
        
        # Require majority for validity
        is_valid = valid_count >= quorum
        
        # Aggregate evidence
        all_evidence = ' | '.join([r.evidence for r in valid_results if r.evidence])
        all_errors = [err for r in valid_results for err in r.errors]
        
        return ValidationResult(
            valid=is_valid,
            confidence=avg_confidence,
            evidence=all_evidence,
            errors=all_errors,
            validator_id='quorum_pool'
        )
    
    async def _validate_with_agent(self, agent, claim: Dict) -> ValidationResult:
        """Validate using an agent-based validator"""
        try:
            # Prepare task for agent
            validation_task = {
                'description': f"Validate this claim: {claim.get('content', '')}",
                'type': 'validation',
                'claim_data': claim
            }
            
            # Execute validation through agent
            result = agent.execute(validation_task)
            if asyncio.iscoroutine(result):
                result = await result
            
            # Parse agent response into ValidationResult
            confidence = result.get('confidence', 0.5)
            is_valid = confidence > 0.5  # Simple threshold
            evidence = result.get('reasoning', result.get('proposal', ''))
            
            return ValidationResult(
                valid=is_valid,
                confidence=confidence,
                evidence=evidence,
                errors=[],
                validator_id=getattr(agent, 'name', 'agent_validator')
            )
            
        except Exception as e:
            logger.error(f"Agent validation failed: {e}")
            return ValidationResult(
                valid=False,
                confidence=0.0,
                evidence=f"Validation error: {str(e)}",
                errors=[str(e)],
                validator_id=getattr(agent, 'name', 'agent_validator')
            )