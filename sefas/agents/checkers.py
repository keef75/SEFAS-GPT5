"""Checker agents for validation and verification."""

import json
import re
from typing import Dict, Any, List
from sefas.agents.base import SelfEvolvingAgent

class CheckerAgent(SelfEvolvingAgent):
    """Base agent for validation and checking"""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse checker response"""
        try:
            # Try to parse as JSON first
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
                return json.loads(json_str)
            
            # Extract validation results from text
            result = self._extract_validation_results(response)
            return result
            
        except Exception as e:
            # Fallback to basic parsing
            return {
                "validation_result": "error",
                "confidence": 0.0,
                "overall_score": 0.0,
                "issues": [f"Parsing error: {str(e)}"],
                "summary": response[:200],
                "raw_response": response
            }
    
    def _extract_validation_results(self, response: str) -> Dict[str, Any]:
        """Extract validation results from text response"""
        
        # Extract overall confidence/score
        confidence = self._extract_confidence(response)
        overall_score = self._extract_score(response)
        
        # Extract individual scores for validation aspects
        aspect_scores = self._extract_aspect_scores(response)
        
        # Extract issues and problems
        issues = self._extract_issues(response)
        
        # Extract recommendations
        recommendations = self._extract_recommendations(response)
        
        # Determine validation result
        validation_result = self._determine_validation_result(overall_score, issues)
        
        return {
            "validation_result": validation_result,
            "confidence": confidence,
            "overall_score": overall_score,
            "aspect_scores": aspect_scores,
            "issues": issues,
            "recommendations": recommendations,
            "summary": self._generate_summary(validation_result, overall_score, len(issues)),
            "checker_type": self.role
        }
    
    def _extract_score(self, text: str) -> float:
        """Extract numerical score from text"""
        # Look for score patterns
        score_patterns = [
            r'score[:\s]+([0-9.]+)',
            r'rating[:\s]+([0-9.]+)',
            r'overall[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*\/\s*[0-9.]+',
            r'([0-9.]+)\s*out\s*of'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    value = float(match.group(1))
                    # Normalize to 0-1 range
                    if value > 1.0:
                        value = value / 100.0 if value <= 100 else value / 10.0
                    return min(max(value, 0.0), 1.0)
                except:
                    pass
        
        # Fallback: use confidence score
        return self._extract_confidence(text)
    
    def _extract_aspect_scores(self, text: str) -> Dict[str, float]:
        """Extract scores for individual validation aspects"""
        aspects = {}
        
        # Common validation aspects
        aspect_keywords = {
            'logic': ['logic', 'logical', 'reasoning'],
            'consistency': ['consistency', 'consistent', 'coherent'],
            'clarity': ['clarity', 'clear', 'understandable'],
            'completeness': ['complete', 'completeness', 'comprehensive'],
            'accuracy': ['accurate', 'accuracy', 'correct'],
            'relevance': ['relevant', 'relevance', 'applicable']
        }
        
        for aspect, keywords in aspect_keywords.items():
            for keyword in keywords:
                # Look for scores associated with keywords
                pattern = f'{keyword}[:\\\\s]+([0-9.]+)'
                match = re.search(pattern, text.lower())
                if match:
                    try:
                        score = float(match.group(1))
                        if score > 1.0:
                            score = score / 100.0 if score <= 100 else score / 10.0
                        aspects[aspect] = min(max(score, 0.0), 1.0)
                        break
                    except:
                        pass
        
        return aspects
    
    def _extract_issues(self, text: str) -> List[str]:
        """Extract identified issues from text"""
        issues = []
        
        # Look for issue indicators
        issue_patterns = [
            r'issue[s]?[:\s]+(.*?)(?=\n|$)',
            r'problem[s]?[:\s]+(.*?)(?=\n|$)',
            r'error[s]?[:\s]+(.*?)(?=\n|$)',
            r'concern[s]?[:\s]+(.*?)(?=\n|$)',
            r'flaw[s]?[:\s]+(.*?)(?=\n|$)'
        ]
        
        for pattern in issue_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    issues.append(match.strip())
        
        # Look for bullet-pointed issues
        lines = text.split('\n')
        in_issues_section = False
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['issue', 'problem', 'error', 'concern']):
                in_issues_section = True
                continue
            
            if in_issues_section and line.startswith(('-', '*', '•')):
                issue = line[1:].strip()
                if len(issue) > 10:
                    issues.append(issue)
            elif in_issues_section and line and not line.startswith(('-', '*', '•')):
                in_issues_section = False
        
        return issues[:5]  # Limit to 5 issues
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text"""
        recommendations = []
        
        # Look for recommendation patterns
        rec_patterns = [
            r'recommend[s]?[:\s]+(.*?)(?=\n|$)',
            r'suggest[s]?[:\s]+(.*?)(?=\n|$)',
            r'should[:\s]+(.*?)(?=\n|$)',
            r'improvement[s]?[:\s]+(.*?)(?=\n|$)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:
                    recommendations.append(match.strip())
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def _determine_validation_result(self, score: float, issues: List[str]) -> str:
        """Determine overall validation result"""
        if score >= 0.8 and len(issues) == 0:
            return "passed"
        elif score >= 0.6 and len(issues) <= 1:
            return "passed_with_notes"
        elif score >= 0.4:
            return "needs_revision"
        else:
            return "failed"
    
    def _generate_summary(self, result: str, score: float, issue_count: int) -> str:
        """Generate validation summary"""
        result_descriptions = {
            "passed": "Validation successful",
            "passed_with_notes": "Validation passed with minor issues",
            "needs_revision": "Significant issues require revision",
            "failed": "Validation failed"
        }
        
        summary = result_descriptions.get(result, "Unknown result")
        return f"{summary} (Score: {score:.2f}, Issues: {issue_count})"

class LogicChecker(CheckerAgent):
    """Logic validation agent"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.validation_aspects = [
            'logical_consistency',
            'valid_reasoning',
            'complete_arguments',
            'sound_conclusions'
        ]
    
    def _extract_validation_results(self, response: str) -> Dict[str, Any]:
        """Extract logic-specific validation results"""
        result = super()._extract_validation_results(response)
        
        # Add logic-specific analysis
        logic_analysis = self._analyze_logical_structure(response)
        result['logic_analysis'] = logic_analysis
        
        return result
    
    def _analyze_logical_structure(self, text: str) -> Dict[str, Any]:
        """Analyze logical structure of the validation"""
        
        logical_indicators = {
            'premises': ['premise', 'assumption', 'given', 'if'],
            'conclusions': ['therefore', 'thus', 'hence', 'conclude'],
            'contradictions': ['contradict', 'inconsistent', 'conflict'],
            'fallacies': ['fallacy', 'invalid', 'non sequitur', 'circular']
        }
        
        analysis = {}
        text_lower = text.lower()
        
        for category, keywords in logical_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            analysis[category] = count
        
        # Calculate logical structure score
        structure_score = 0.0
        if analysis['premises'] > 0:
            structure_score += 0.3
        if analysis['conclusions'] > 0:
            structure_score += 0.3
        if analysis['contradictions'] == 0:
            structure_score += 0.2
        if analysis['fallacies'] == 0:
            structure_score += 0.2
        
        analysis['structure_score'] = structure_score
        return analysis

class SemanticChecker(CheckerAgent):
    """Semantic validation agent"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.validation_aspects = [
            'meaning_clarity',
            'conceptual_accuracy', 
            'contextual_relevance',
            'semantic_coherence'
        ]
    
    def _extract_validation_results(self, response: str) -> Dict[str, Any]:
        """Extract semantic-specific validation results"""
        result = super()._extract_validation_results(response)
        
        # Add semantic-specific analysis
        semantic_analysis = self._analyze_semantic_quality(response)
        result['semantic_analysis'] = semantic_analysis
        
        return result
    
    def _analyze_semantic_quality(self, text: str) -> Dict[str, Any]:
        """Analyze semantic quality of the validation"""
        
        semantic_indicators = {
            'clarity': ['clear', 'unclear', 'ambiguous', 'precise'],
            'terminology': ['term', 'concept', 'definition', 'meaning'],
            'context': ['context', 'relevant', 'applicable', 'appropriate'],
            'coherence': ['coherent', 'consistent', 'unified', 'logical']
        }
        
        analysis = {}
        text_lower = text.lower()
        
        for category, keywords in semantic_indicators.items():
            positive_keywords = [k for k in keywords if k not in ['unclear', 'ambiguous']]
            negative_keywords = [k for k in keywords if k in ['unclear', 'ambiguous']]
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            analysis[f'{category}_positive'] = positive_count
            analysis[f'{category}_negative'] = negative_count
        
        # Calculate semantic quality score
        total_positive = sum(v for k, v in analysis.items() if 'positive' in k)
        total_negative = sum(v for k, v in analysis.items() if 'negative' in k)
        
        if total_positive + total_negative > 0:
            quality_score = total_positive / (total_positive + total_negative)
        else:
            quality_score = 0.5
        
        analysis['quality_score'] = quality_score
        return analysis

class ConsistencyChecker(CheckerAgent):
    """Consistency validation agent"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.validation_aspects = [
            'internal_consistency',
            'external_consistency',
            'temporal_consistency',
            'cross_proposal_consistency'
        ]
    
    def _extract_validation_results(self, response: str) -> Dict[str, Any]:
        """Extract consistency-specific validation results"""
        result = super()._extract_validation_results(response)
        
        # Add consistency-specific analysis
        consistency_analysis = self._analyze_consistency_aspects(response)
        result['consistency_analysis'] = consistency_analysis
        
        return result
    
    def _analyze_consistency_aspects(self, text: str) -> Dict[str, Any]:
        """Analyze consistency aspects of the validation"""
        
        consistency_indicators = {
            'agreement': ['agree', 'consistent', 'align', 'match'],
            'disagreement': ['disagree', 'inconsistent', 'conflict', 'contradict'],
            'temporal': ['before', 'after', 'sequence', 'timeline'],
            'cross_reference': ['compare', 'other', 'alternative', 'versus']
        }
        
        analysis = {}
        text_lower = text.lower()
        
        for category, keywords in consistency_indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            analysis[f'{category}_mentions'] = count
        
        # Calculate consistency score
        agreement_mentions = analysis['agreement_mentions']
        disagreement_mentions = analysis['disagreement_mentions']
        
        if agreement_mentions + disagreement_mentions > 0:
            consistency_score = agreement_mentions / (agreement_mentions + disagreement_mentions)
        else:
            consistency_score = 0.5
        
        analysis['consistency_score'] = consistency_score
        return analysis