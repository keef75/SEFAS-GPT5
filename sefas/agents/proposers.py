"""Proposer agents for solution generation."""

import json
import re
from typing import Dict, Any
from sefas.agents.base import SelfEvolvingAgent

class ProposerAgent(SelfEvolvingAgent):
    """Agent that proposes solutions"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse proposer response"""
        try:
            # Try to parse as JSON first
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            
            # Try to extract structured information from text
            result = self._extract_structured_response(response)
            
            return result
            
        except Exception as e:
            # Fallback to text parsing
            return {
                "proposal": response,
                "confidence": self._extract_confidence(response),
                "reasoning": response,
                "type": "fallback_text",
                "approaches": [{"description": response, "confidence": self._extract_confidence(response)}]
            }
    
    def _extract_structured_response(self, response: str) -> Dict[str, Any]:
        """Extract structured data from text response"""
        
        # Extract confidence
        confidence = self._extract_confidence(response)
        
        # Extract approaches (look for numbered lists or bullet points)
        approaches = self._extract_approaches(response)
        
        # Extract reasoning sections
        reasoning = self._extract_reasoning(response)
        
        # Main proposal (first few sentences)
        lines = response.split('\n')
        proposal_lines = []
        for line in lines:
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('-'):
                proposal_lines.append(line.strip())
                if len(proposal_lines) >= 3:  # Take first 3 substantial lines
                    break
        
        proposal = ' '.join(proposal_lines) if proposal_lines else response[:200]
        
        return {
            "proposal": proposal,
            "confidence": confidence,
            "reasoning": reasoning,
            "approaches": approaches,
            "type": "structured",
            "agent_role": self.role,
            "strategy": getattr(self, 'strategy', 'general')
        }
    
    def _extract_approaches(self, text: str) -> list:
        """Extract multiple approaches from text"""
        approaches = []
        
        # Look for numbered lists
        numbered_pattern = r'(\d+[\.\)]\s*)(.*?)(?=\d+[\.\)]|\Z)'
        numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if numbered_matches:
            for i, (_, content) in enumerate(numbered_matches):
                approach_confidence = self._extract_confidence(content)
                approaches.append({
                    "id": f"approach_{i+1}",
                    "description": content.strip(),
                    "confidence": approach_confidence
                })
        
        # Look for bullet points if no numbered list
        if not approaches:
            bullet_pattern = r'[-*•]\s*(.*?)(?=[-*•]|\Z)'
            bullet_matches = re.findall(bullet_pattern, text, re.DOTALL)
            
            for i, content in enumerate(bullet_matches):
                if len(content.strip()) > 20:  # Only substantial content
                    approach_confidence = self._extract_confidence(content)
                    approaches.append({
                        "id": f"approach_{i+1}",
                        "description": content.strip(),
                        "confidence": approach_confidence
                    })
        
        # If no structured approaches found, create one from the whole response
        if not approaches:
            approaches.append({
                "id": "approach_1",
                "description": text.strip(),
                "confidence": self._extract_confidence(text)
            })
        
        return approaches[:3]  # Limit to 3 approaches
    
    def _extract_reasoning(self, text: str) -> str:
        """Extract reasoning section from text"""
        
        # Look for reasoning keywords
        reasoning_keywords = [
            'reasoning', 'rationale', 'because', 'justification', 
            'explanation', 'why', 'logic', 'approach'
        ]
        
        lines = text.split('\n')
        reasoning_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in reasoning_keywords):
                # Include this line and following context
                start_idx = lines.index(line)
                reasoning_lines = lines[start_idx:start_idx+3]
                break
        
        if reasoning_lines:
            return ' '.join(line.strip() for line in reasoning_lines if line.strip())
        
        # Fallback: use middle portion of response
        sentences = text.split('. ')
        if len(sentences) > 2:
            return '. '.join(sentences[1:min(4, len(sentences))])
        
        return text[:300]  # First 300 chars as reasoning

class CreativeProposer(ProposerAgent):
    """Creative proposer agent specializing in innovative solutions"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.strategy = "creative"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse creative proposer response with emphasis on innovation"""
        result = super()._parse_response(response)
        
        # Add creativity metrics
        creativity_score = self._assess_creativity(response)
        result['creativity_score'] = creativity_score
        result['innovation_level'] = 'high' if creativity_score > 0.7 else 'medium' if creativity_score > 0.4 else 'low'
        
        return result
    
    def _assess_creativity(self, text: str) -> float:
        """Assess creativity level of the response"""
        creative_indicators = [
            'innovative', 'novel', 'unique', 'creative', 'original',
            'breakthrough', 'revolutionary', 'unconventional', 'what if',
            'imagine', 'envision', 'reimagine', 'transform', 'disrupt'
        ]
        
        text_lower = text.lower()
        creativity_score = 0.0
        
        for indicator in creative_indicators:
            if indicator in text_lower:
                creativity_score += 0.1
        
        # Bonus for question words (creative exploration)
        question_words = ['what if', 'how might', 'could we', 'why not']
        for question in question_words:
            if question in text_lower:
                creativity_score += 0.15
        
        return min(creativity_score, 1.0)

class AnalyticalProposer(ProposerAgent):
    """Analytical proposer agent specializing in systematic solutions"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.strategy = "analytical"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse analytical proposer response with emphasis on structure"""
        result = super()._parse_response(response)
        
        # Add analytical metrics
        structure_score = self._assess_structure(response)
        result['structure_score'] = structure_score
        result['analysis_depth'] = 'deep' if structure_score > 0.7 else 'medium' if structure_score > 0.4 else 'shallow'
        
        # Extract implementation steps if present
        steps = self._extract_implementation_steps(response)
        if steps:
            result['implementation_steps'] = steps
        
        return result
    
    def _assess_structure(self, text: str) -> float:
        """Assess structural quality of the response"""
        structure_indicators = [
            'first', 'second', 'third', 'step', 'phase', 'stage',
            'analysis', 'data', 'evidence', 'systematic', 'methodical',
            'process', 'framework', 'approach', 'methodology'
        ]
        
        text_lower = text.lower()
        structure_score = 0.0
        
        for indicator in structure_indicators:
            if indicator in text_lower:
                structure_score += 0.1
        
        # Bonus for numbered lists
        numbered_items = len(re.findall(r'\d+[\.\)]', text))
        structure_score += min(numbered_items * 0.1, 0.3)
        
        return min(structure_score, 1.0)
    
    def _extract_implementation_steps(self, text: str) -> list:
        """Extract implementation steps from response"""
        steps = []
        
        # Look for step patterns
        step_pattern = r'(step\s+\d+|phase\s+\d+|\d+[\.\)]\s*)(.*?)(?=step\s+\d+|phase\s+\d+|\d+[\.\)]|\Z)'
        step_matches = re.findall(step_pattern, text.lower(), re.DOTALL)
        
        for i, (prefix, content) in enumerate(step_matches):
            if len(content.strip()) > 10:
                steps.append({
                    "step": i + 1,
                    "description": content.strip(),
                    "type": "implementation"
                })
        
        return steps

class ResearchProposer(ProposerAgent):
    """Research proposer agent specializing in evidence-based solutions"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.strategy = "research"
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse research proposer response with emphasis on evidence"""
        result = super()._parse_response(response)
        
        # Add research metrics
        evidence_score = self._assess_evidence(response)
        result['evidence_score'] = evidence_score
        result['research_depth'] = 'comprehensive' if evidence_score > 0.7 else 'moderate' if evidence_score > 0.4 else 'basic'
        
        # Extract references if present
        references = self._extract_references(response)
        if references:
            result['references'] = references
        
        return result
    
    def _assess_evidence(self, text: str) -> float:
        """Assess evidence quality of the response"""
        evidence_indicators = [
            'research', 'study', 'studies', 'evidence', 'data',
            'according to', 'research shows', 'proven', 'demonstrated',
            'case study', 'best practice', 'precedent', 'example',
            'benchmark', 'industry standard', 'methodology'
        ]
        
        text_lower = text.lower()
        evidence_score = 0.0
        
        for indicator in evidence_indicators:
            if indicator in text_lower:
                evidence_score += 0.1
        
        # Bonus for specific citations or examples
        citation_patterns = [r'\[\d+\]', r'\(\d{4}\)', r'et al\.']
        for pattern in citation_patterns:
            matches = len(re.findall(pattern, text))
            evidence_score += min(matches * 0.15, 0.3)
        
        return min(evidence_score, 1.0)
    
    def _extract_references(self, text: str) -> list:
        """Extract research references from response"""
        references = []
        
        # Look for citation patterns
        citation_patterns = [
            r'according to ([^,\n]+)',
            r'research by ([^,\n]+)',
            r'study by ([^,\n]+)',
            r'([A-Z][a-z]+ et al\. \(\d{4}\))'
        ]
        
        for pattern in citation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                references.append({
                    "source": match.strip(),
                    "type": "citation"
                })
        
        return references[:5]  # Limit to 5 references