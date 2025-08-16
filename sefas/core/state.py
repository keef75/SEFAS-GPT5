from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AgentRole(Enum):
    """15 Specialized Agent Roles"""
    # Layer 1: Decomposition & Planning
    ORCHESTRATOR = "orchestrator"
    TASK_DECOMPOSER = "task_decomposer"
    STRATEGY_EVOLVER = "strategy_evolver"
    
    # [... rest of roles ...]

@dataclass
class EvolutionState:
    """Tracks evolution metrics per agent"""
    agent_id: str
    prompt_version: int = 1
    topology_connections: List[str] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    mutation_count: int = 0
    fitness_score: float = 0.5
    last_evolution: datetime = field(default_factory=datetime.now)
    strategy_genome: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "agent_id": self.agent_id,
            "prompt_version": self.prompt_version,
            "topology_connections": self.topology_connections,
            "performance_history": self.performance_history,
            "mutation_count": self.mutation_count,
            "fitness_score": self.fitness_score,
            "last_evolution": self.last_evolution.isoformat(),
            "strategy_genome": self.strategy_genome
        }

class FederatedState(TypedDict):
    """Global state for the federated system"""
    task_id: str
    original_input: str
    decomposed_tasks: List[Dict[str, Any]]
    current_hop: int
    agent_states: Dict[str, EvolutionState]
    # [... rest of state ...]