"""Orchestrator agent for task decomposition and coordination."""

import json
import re
from typing import Dict, Any, List
from sefas.agents.base import SelfEvolvingAgent

class OrchestratorAgent(SelfEvolvingAgent):
    """Central orchestrator for task decomposition and agent coordination"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        super().__init__(agent_config)
        self.fitness_scores = {}  # Track other agents' fitness
    
    def execute(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute orchestration with fitness-aware agent assignment"""
        
        # Update context with current fitness scores
        if context is None:
            context = {}
        context['fitness_scores'] = self.fitness_scores
        
        return super().execute(task, context)
    
    def update_agent_fitness(self, agent_id: str, fitness_score: float) -> None:
        """Update fitness score for an agent"""
        self.fitness_scores[agent_id] = fitness_score
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse orchestrator response"""
        try:
            # Try to parse as JSON first
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
                parsed = json.loads(json_str)
                
                # Validate and enhance the parsed response
                return self._validate_decomposition(parsed, response)
            
            # Extract structured decomposition from text
            decomposition = self._extract_decomposition_from_text(response)
            return decomposition
            
        except Exception as e:
            # Fallback to basic parsing
            return self._create_fallback_decomposition(response, str(e))
    
    def _validate_decomposition(self, parsed: Dict[str, Any], full_response: str) -> Dict[str, Any]:
        """Validate and enhance parsed JSON decomposition"""
        
        result = {
            "decomposition_type": "structured",
            "confidence": self._extract_confidence(full_response),
            "subclaims": [],
            "coordination_strategy": "parallel",
            "estimated_complexity": "medium",
            "raw_response": full_response
        }
        
        # Process subclaims
        subclaims = parsed.get('subclaims', [])
        
        for i, subclaim in enumerate(subclaims):
            processed_subclaim = self._process_subclaim(subclaim, i)
            result["subclaims"].append(processed_subclaim)
        
        # Determine coordination strategy
        result["coordination_strategy"] = self._determine_coordination_strategy(result["subclaims"])
        
        # Estimate complexity
        result["estimated_complexity"] = self._estimate_complexity(result["subclaims"])
        
        return result
    
    def _extract_decomposition_from_text(self, response: str) -> Dict[str, Any]:
        """Extract decomposition structure from text response"""
        
        result = {
            "decomposition_type": "text_extracted",
            "confidence": self._extract_confidence(response),
            "subclaims": [],
            "coordination_strategy": "sequential",
            "estimated_complexity": "medium",
            "raw_response": response
        }
        
        # Extract subclaims from numbered lists or bullet points
        subclaims = self._extract_subclaims_from_text(response)
        
        for i, subclaim_text in enumerate(subclaims):
            subclaim = {
                "id": f"claim_{i+1}",
                "description": subclaim_text,
                "type": self._infer_subclaim_type(subclaim_text),
                "assigned_agents": self._assign_agents_by_type(self._infer_subclaim_type(subclaim_text)),
                "priority": "medium",
                "estimated_effort": "medium"
            }
            result["subclaims"].append(subclaim)
        
        # If no structured subclaims found, create basic decomposition
        if not result["subclaims"]:
            result["subclaims"] = self._create_basic_decomposition(response)
        
        return result
    
    def _extract_subclaims_from_text(self, text: str) -> List[str]:
        """Extract subclaims from text using various patterns"""
        subclaims = []
        
        # Look for numbered lists
        numbered_pattern = r'(\d+[\.\)]\s*)(.*?)(?=\d+[\.\)]|\Z)'
        numbered_matches = re.findall(numbered_pattern, text, re.DOTALL)
        
        if numbered_matches:
            for _, content in numbered_matches:
                clean_content = content.strip().replace('\n', ' ')
                if len(clean_content) > 20:
                    subclaims.append(clean_content)
        
        # Look for bullet points if no numbered list
        if not subclaims:
            bullet_pattern = r'[-*•]\s*(.*?)(?=[-*•]|\Z)'
            bullet_matches = re.findall(bullet_pattern, text, re.DOTALL)
            
            for content in bullet_matches:
                clean_content = content.strip().replace('\n', ' ')
                if len(clean_content) > 20:
                    subclaims.append(clean_content)
        
        # Look for task-oriented sentences
        if not subclaims:
            sentences = text.split('.')
            task_keywords = ['analyze', 'determine', 'evaluate', 'assess', 'identify', 'examine', 'investigate']
            
            for sentence in sentences:
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in task_keywords) and len(sentence) > 30:
                    subclaims.append(sentence)
        
        return subclaims[:5]  # Limit to 5 subclaims
    
    def _process_subclaim(self, subclaim: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Process and enhance a subclaim"""
        
        processed = {
            "id": subclaim.get('id', f"claim_{index+1}"),
            "description": subclaim.get('description', ''),
            "type": subclaim.get('type', 'general'),
            "assigned_agents": subclaim.get('assigned_agents', []),
            "priority": subclaim.get('priority', 'medium'),
            "estimated_effort": subclaim.get('estimated_effort', 'medium'),
            "dependencies": subclaim.get('dependencies', []),
            "success_criteria": subclaim.get('success_criteria', [])
        }
        
        # Auto-assign agents if not specified
        if not processed["assigned_agents"]:
            processed["assigned_agents"] = self._assign_agents_by_type(processed["type"])
        
        # Enhance with fitness-based agent selection
        processed["assigned_agents"] = self._optimize_agent_assignment(
            processed["assigned_agents"], 
            processed["type"]
        )
        
        return processed
    
    def _infer_subclaim_type(self, description: str) -> str:
        """Infer the type of a subclaim from its description"""
        
        description_lower = description.lower()
        
        type_indicators = {
            'factual': ['fact', 'data', 'evidence', 'research', 'study', 'information'],
            'logical': ['logic', 'reasoning', 'analysis', 'evaluate', 'assess', 'compare'],
            'creative': ['creative', 'innovative', 'brainstorm', 'generate', 'design', 'imagine'],
            'analytical': ['analyze', 'breakdown', 'systematic', 'methodical', 'process', 'framework']
        }
        
        type_scores = {}
        for claim_type, keywords in type_indicators.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            type_scores[claim_type] = score
        
        # Return type with highest score, default to 'general'
        if type_scores and max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)
        
        return 'general'
    
    def _assign_agents_by_type(self, claim_type: str) -> List[str]:
        """Assign appropriate agents based on claim type"""
        
        agent_assignments = {
            'factual': ['proposer_gamma'],  # Research proposer
            'logical': ['proposer_beta'],   # Analytical proposer
            'creative': ['proposer_alpha'], # Creative proposer
            'analytical': ['proposer_beta', 'proposer_gamma'],
            'general': ['proposer_alpha', 'proposer_beta']
        }
        
        return agent_assignments.get(claim_type, ['proposer_alpha', 'proposer_beta'])
    
    def _optimize_agent_assignment(self, assigned_agents: List[str], claim_type: str) -> List[str]:
        """Optimize agent assignment based on fitness scores"""
        
        if not self.fitness_scores:
            return assigned_agents
        
        # Sort assigned agents by fitness score
        optimized_agents = []
        
        for agent in assigned_agents:
            fitness = self.fitness_scores.get(agent, 0.5)
            optimized_agents.append((agent, fitness))
        
        # Sort by fitness (descending) and return agent names
        optimized_agents.sort(key=lambda x: x[1], reverse=True)
        
        return [agent for agent, _ in optimized_agents]
    
    def _determine_coordination_strategy(self, subclaims: List[Dict[str, Any]]) -> str:
        """Determine coordination strategy based on subclaims"""
        
        if len(subclaims) <= 2:
            return "sequential"
        
        # Check for dependencies
        has_dependencies = any(claim.get('dependencies') for claim in subclaims)
        
        if has_dependencies:
            return "dependency_aware"
        
        # Check complexity
        complex_claims = sum(1 for claim in subclaims if claim.get('estimated_effort') == 'high')
        
        if complex_claims > len(subclaims) / 2:
            return "staged_parallel"
        
        return "parallel"
    
    def _estimate_complexity(self, subclaims: List[Dict[str, Any]]) -> str:
        """Estimate overall task complexity"""
        
        if len(subclaims) <= 2:
            return "low"
        elif len(subclaims) <= 4:
            return "medium"
        else:
            return "high"
    
    def _create_basic_decomposition(self, response: str) -> List[Dict[str, Any]]:
        """Create basic decomposition when structured extraction fails"""
        
        # Split response into sentences and create subclaims
        sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 30]
        
        subclaims = []
        for i, sentence in enumerate(sentences[:3]):  # Limit to 3
            subclaim = {
                "id": f"claim_{i+1}",
                "description": sentence,
                "type": "general",
                "assigned_agents": ["proposer_alpha", "proposer_beta"],
                "priority": "medium",
                "estimated_effort": "medium"
            }
            subclaims.append(subclaim)
        
        # If still no subclaims, create one from the entire response
        if not subclaims:
            subclaims.append({
                "id": "claim_1", 
                "description": response[:200],
                "type": "general",
                "assigned_agents": ["proposer_alpha"],
                "priority": "high",
                "estimated_effort": "medium"
            })
        
        return subclaims
    
    def _create_fallback_decomposition(self, response: str, error: str) -> Dict[str, Any]:
        """Create fallback decomposition when parsing fails"""
        
        return {
            "decomposition_type": "fallback",
            "confidence": 0.3,
            "subclaims": [{
                "id": "claim_1",
                "description": response[:200] if len(response) > 200 else response,
                "type": "general",
                "assigned_agents": ["proposer_alpha"],
                "priority": "medium",
                "estimated_effort": "medium"
            }],
            "coordination_strategy": "sequential",
            "estimated_complexity": "unknown",
            "error": error,
            "raw_response": response
        }
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics"""
        
        return {
            "tracked_agents": len(self.fitness_scores),
            "avg_agent_fitness": sum(self.fitness_scores.values()) / len(self.fitness_scores) if self.fitness_scores else 0.0,
            "decompositions_performed": len(self.performance_history),
            "avg_decomposition_confidence": sum(self.performance_history[-10:]) / min(10, len(self.performance_history)) if self.performance_history else 0.0,
            "fitness_distribution": self.fitness_scores.copy()
        }