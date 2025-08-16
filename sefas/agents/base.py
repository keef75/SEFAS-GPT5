"""Base class for all self-evolving agents."""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import json

from langchain_openai import ChatOpenAI
from openai import OpenAI as _OpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage

from sefas.core.state import EvolutionState
from sefas.memory.episodic import EpisodicMemory
from config.settings import settings
import time

class SelfEvolvingAgent(ABC):
    """Base class for all self-evolving agents"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.role = agent_config['role']
        self.name = agent_config.get('name', self.role)
        self.temperature = agent_config.get('temperature', 0.3)
        
        # Initialize LLM or stub depending on offline_mode
        if getattr(settings, 'offline_mode', False) or not settings.openai_api_key:
            self.llm = _OfflineLLMStub()
        else:
            # Prefer Responses API for GPT-5 if enabled
            if settings.use_responses_api_for_gpt5 and str(settings.llm_model).startswith("gpt-5"):
                self.llm = _ResponsesShim(
                    model=settings.llm_model,
                    reasoning_effort=settings.gpt5_reasoning_effort,
                    text_verbosity=settings.gpt5_text_verbosity,
                    organization=settings.openai_organization,
                    project=settings.openai_project,
                )
            else:
                org_kw = {}
                if getattr(settings, 'openai_organization', None):
                    org_kw["organization"] = settings.openai_organization
                self.llm = ChatOpenAI(
                    model=settings.llm_model,
                    temperature=self.temperature,
                    max_tokens=agent_config.get('max_tokens', 1500),
                    **org_kw,
                )
        
        # Evolution state
        self.evolution_state = EvolutionState(agent_id=self.name)
        
        # Prompt management
        self.base_prompt = agent_config.get('initial_prompt', '')
        self.current_prompt = self.base_prompt
        
        # Memory
        self.memory = EpisodicMemory(capacity=100)
        
        # Performance tracking
        self.performance_history = []
        
    def execute(self, task: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute task with current configuration"""
        
        # Build prompt with context
        full_prompt = self._build_prompt(task, context)
        
        # Get response from LLM
        try:
            # Basic rate limiting to avoid rapid multi-agent bursts hitting the API
            if not getattr(settings, 'offline_mode', False):
                time.sleep(max(0, getattr(settings, 'rate_limit_ms', 200) / 1000.0))

            response = self.llm.invoke([
                SystemMessage(content=self.current_prompt),
                HumanMessage(content=full_prompt)
            ])
            
            # Parse and structure response
            result = self._parse_response(response.content)
            
            # Add to memory
            self.memory.add({
                'task': task,
                'response': result,
                'timestamp': datetime.now().isoformat(),
                'confidence': result.get('confidence', 0.5)
            })
            
            # Track performance
            self._update_performance(result)
            
            return result
            
        except Exception as e:
            # Enhanced error logging for 401 diagnosis
            if "401" in str(e) or "Unauthorized" in str(e):
                print(f"🚨 401 UNAUTHORIZED ERROR DETAILS:")
                print(f"   Agent: {self.name}")
                print(f"   Model: {getattr(settings, 'llm_model', 'unknown')}")
                print(f"   Error: {str(e)}")
                print(f"   Error Type: {type(e).__name__}")
                print(f"   API Key configured: {bool(getattr(settings, 'openai_api_key', None))}")
                print(f"   Organization: {getattr(settings, 'openai_organization', 'None')}")
                print(f"   Project: {getattr(settings, 'openai_project', 'None')}")
                import os
                print(f"   ENV OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
                
            # Handle LLM errors gracefully
            if (
                not getattr(settings, 'offline_mode', False)
                and getattr(settings, 'llm_fallback_on_unauthorized', True)
                and ("401" in str(e) or "Unauthorized" in str(e))
            ):
                print(f"   → Falling back to offline stub")
                # Switch to offline stub for this run to keep system responsive
                self.llm = _OfflineLLMStub()
                try:
                    response = self.llm.invoke([
                        SystemMessage(content=self.current_prompt),
                        HumanMessage(content=full_prompt)
                    ])
                    result = self._parse_response(response.content)
                    self._update_performance(result)
                    return result
                except Exception:
                    pass
            else:
                print(f"   → NO FALLBACK (llm_fallback_on_unauthorized={getattr(settings, 'llm_fallback_on_unauthorized', True)})")
                
            error_result = {
                'error': str(e),
                'confidence': 0.0,
                'proposal': f"Error executing task: {str(e)}",
                'reasoning': "Agent encountered an error during execution"
            }
            
            # Still add to memory for learning
            self.memory.add({
                'task': task,
                'response': error_result,
                'timestamp': datetime.now().isoformat(),
                'confidence': 0.0,
                'error': True
            })
            
            return error_result
    
    def evolve_prompt(self, feedback: Dict[str, Any]) -> bool:
        """Evolve prompt based on feedback"""
        
        if feedback.get('performance', 1.0) < settings.evolution_threshold:
            # Generate improved prompt
            evolution_prompt = f"""
            Current prompt: {self.current_prompt}
            
            Performance feedback: {feedback}
            
            Generate an improved version that addresses these issues:
            {feedback.get('issues', [])}
            
            Keep the same structure but improve clarity and effectiveness.
            Return only the improved prompt, no explanations.
            """
            
            try:
                response = self.llm.invoke([
                    SystemMessage(content="You are a prompt optimization expert."),
                    HumanMessage(content=evolution_prompt)
                ])
                
                self.current_prompt = response.content
                self.evolution_state.prompt_version += 1
                self.evolution_state.mutation_count += 1
                self.evolution_state.last_evolution = datetime.now()
                
                return True
                
            except Exception as e:
                # Evolution failed, keep current prompt
                return False
        
        return False
    
    def get_fitness_scores(self) -> Dict[str, float]:
        """Get current fitness metrics"""
        return {
            'current_fitness': self.evolution_state.fitness_score,
            'avg_confidence': sum(self.performance_history[-10:]) / min(10, len(self.performance_history)) if self.performance_history else 0.5,
            'memory_utilization': self.memory.size() / self.memory.capacity,
            'evolution_count': self.evolution_state.mutation_count
        }
    
    def consolidate_memory(self) -> Dict[str, Any]:
        """Consolidate episodic memories into patterns"""
        return self.memory.consolidate()
    
    def _build_prompt(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build full prompt with task and context"""
        
        # Get relevant memories
        relevant_memories = self.memory.get_relevant(
            query=str(task), 
            k=3
        )
        
        # Build context-aware prompt
        prompt_parts = []
        
        # Task description
        prompt_parts.append(f"Task: {task.get('description', '')}")
        if task.get('type'):
            prompt_parts.append(f"Type: {task.get('type')}")
        
        # Context information
        if context:
            prompt_parts.append(f"Context:\n{json.dumps(context, indent=2)}")
        
        # Relevant experiences
        if relevant_memories:
            memory_text = []
            for i, memory in enumerate(relevant_memories, 1):
                memory_summary = {
                    'task': memory.get('task', {}).get('description', 'Unknown'),
                    'outcome': memory.get('response', {}).get('proposal', 'Unknown')[:100],
                    'confidence': memory.get('confidence', 0.5)
                }
                memory_text.append(f"{i}. {json.dumps(memory_summary, indent=2)}")
            
            prompt_parts.append(f"Relevant past experiences:\n" + "\n".join(memory_text))
        
        # Performance expectations
        prompt_parts.append("Provide your response with confidence score (0-1).")
        
        return "\n\n".join(prompt_parts)
    
    @abstractmethod
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        pass
    
    def _update_performance(self, result: Dict[str, Any]):
        """Update performance metrics"""
        confidence = result.get('confidence', 0.5)
        self.performance_history.append(confidence)
        
        # Keep only recent history
        if len(self.performance_history) > 50:
            self.performance_history = self.performance_history[-50:]
        
        # Update fitness score (moving average with decay)
        if len(self.performance_history) > 0:
            recent_performance = self.performance_history[-10:]
            self.evolution_state.fitness_score = sum(recent_performance) / len(recent_performance)
            
        # Update evolution state performance history
        self.evolution_state.performance_history.append(confidence)
        if len(self.evolution_state.performance_history) > 100:
            self.evolution_state.performance_history = self.evolution_state.performance_history[-100:]
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence from text response"""
        import re
        
        # Look for confidence patterns
        patterns = [
            r'confidence[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*confidence',
            r'confident[:\s]+([0-9.]+)',
            r'certainty[:\s]+([0-9.]+)',
            r'score[:\s]+([0-9.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    value = float(match.group(1))
                    # Normalize to 0-1 range
                    if value > 1.0:
                        value = value / 100.0  # Assume percentage
                    return min(max(value, 0.0), 1.0)
                except:
                    pass
        
        return 0.5  # Default confidence


class _OfflineLLMStub:
    """Deterministic offline stub to avoid external API calls during tests/dev."""
    def invoke(self, messages: List[Any]) -> Any:
        # Produce a simple structured response with confidence calculated from prompt length
        full_text = "\n".join(getattr(m, 'content', str(m)) for m in messages)
        confidence = min(0.9, 0.4 + len(full_text) / 2000.0)

        class _Resp:
            def __init__(self, content: str) -> None:
                self.content = content

        import json as _json
        payload = {
            "proposal": "Offline stub response generated.",
            "reasoning": "No external API used.",
            "confidence": round(confidence, 2)
        }
        return _Resp(_json.dumps(payload))


class _ResponsesShim:
    """Minimal adapter to expose an .invoke([...]) API using OpenAI Responses."""
    def __init__(self, model: str, reasoning_effort: str = "low", text_verbosity: str = "low", organization: str | None = None, project: str | None = None) -> None:
        client_kwargs = {}
        if organization:
            client_kwargs["organization"] = organization
        if project:
            client_kwargs["project"] = project
        self._client = _OpenAI(**client_kwargs)
        self._model = model
        self._reasoning = reasoning_effort
        self._verbosity = text_verbosity

    def invoke(self, messages: List[Any]) -> Any:
        user_parts = []
        system_parts = []
        for m in messages:
            content = getattr(m, 'content', str(m))
            if getattr(m, 'type', None) == 'system' or m.__class__.__name__ == 'SystemMessage':
                system_parts.append(content)
            else:
                user_parts.append(content)
        input_text = "\n\n".join(filter(None, ["\n\n".join(system_parts), "\n\n".join(user_parts)]))
        resp = self._client.responses.create(
            model=self._model,
            input=input_text,
            reasoning={"effort": self._reasoning},
            text={"verbosity": self._verbosity},
        )

        class _Resp:
            def __init__(self, content: str) -> None:
                self.content = content

        return _Resp(getattr(resp, 'output_text', str(resp)))