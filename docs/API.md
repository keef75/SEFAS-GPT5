# SEFAS API Documentation

## Core Classes and Interfaces

### State Management

#### `EvolutionState`

Tracks evolution metrics per agent in the federated system.

```python
@dataclass
class EvolutionState:
    agent_id: str
    prompt_version: int = 1
    topology_connections: List[str] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    mutation_count: int = 0
    fitness_score: float = 0.5
    last_evolution: datetime = field(default_factory=datetime.now)
    strategy_genome: Dict[str, Any] = field(default_factory=dict)
```

**Methods:**

- `to_dict() -> Dict[str, Any]`: Serialize state to dictionary format

**Properties:**

- `agent_id`: Unique identifier for the agent
- `prompt_version`: Current iteration of agent's prompt
- `topology_connections`: List of connected agent IDs
- `performance_history`: Historical performance scores
- `mutation_count`: Number of evolutionary mutations
- `fitness_score`: Current fitness level (0.0-1.0)
- `last_evolution`: Timestamp of last evolutionary update
- `strategy_genome`: Evolved strategy parameters

#### `AgentRole`

Enumeration of 15 specialized agent roles in the system.

```python
class AgentRole(Enum):
    # Layer 1: Decomposition & Planning
    ORCHESTRATOR = "orchestrator"
    TASK_DECOMPOSER = "task_decomposer" 
    STRATEGY_EVOLVER = "strategy_evolver"
    
    # Layer 2: Proposition & Analysis
    PROPOSER_ALPHA = "proposer_alpha"
    PROPOSER_BETA = "proposer_beta"
    PROPOSER_GAMMA = "proposer_gamma"
    
    # Layer 3: Verification & Validation
    CHECKER_LOGIC = "checker_logic"
    CHECKER_SEMANTIC = "checker_semantic"
    CHECKER_CONSISTENCY = "checker_consistency"
    
    # Additional specialized roles...
```

#### `FederatedState`

Global state container for the entire federated system.

```python
class FederatedState(TypedDict):
    task_id: str
    original_input: str
    decomposed_tasks: List[Dict[str, Any]]
    current_hop: int
    agent_states: Dict[str, EvolutionState]
    # Additional state fields...
```

### Configuration Management

#### `Settings`

System-wide configuration using Pydantic BaseSettings.

```python
class Settings(BaseSettings):
    # API Configuration
    openai_api_key: str
    langsmith_api_key: Optional[str] = None
    
    # Model Parameters
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.2
    embedding_model: str = "text-embedding-3-small"
    
    # System Parameters
    max_hops: int = 10
    confidence_threshold: float = 0.7
    evolution_budget: float = 0.2
    
    # File Paths
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")
    checkpoint_dir: Path = Path("checkpoints")
```

**Class Methods:**

- `load_agent_config() -> Dict[str, Any]`: Load agent configuration from YAML
- `load_evolution_config() -> Dict[str, Any]`: Load evolution parameters

## Agent System Architecture

### Orchestrator Agent

Central coordination agent responsible for:
- Task decomposition into verifiable subclaims
- Agent assignment based on evolving capabilities
- m→m+1 hop execution pattern coordination
- System-wide performance monitoring

**Configuration:**
```yaml
orchestrator:
  role: "orchestrator"
  temperature: 0.1
  max_tokens: 2000
```

### Proposer Agents

#### Proposer Alpha
- **Strategy**: Creative solution generation
- **Temperature**: 0.7 (higher creativity)
- **Focus**: Innovative approaches and out-of-box thinking

#### Proposer Beta  
- **Strategy**: Practical implementation
- **Temperature**: 0.3 (more focused)
- **Focus**: Feasibility and implementation details

### Checker Agents

#### Checker Logic
- **Purpose**: Logical consistency verification
- **Validates**: Reasoning chains and logical flows

#### Checker Semantic
- **Purpose**: Semantic accuracy validation
- **Validates**: Meaning and contextual correctness

#### Checker Consistency
- **Purpose**: Cross-claim consistency
- **Validates**: Agreement between different propositions

## Workflow Patterns

### M→M+1 Hop Execution

The system uses a structured hop execution pattern:

1. **Hop 0**: Initial task reception and decomposition
2. **Hop 1**: Primary agent proposition generation
3. **Hop 2**: Verification and validation
4. **Hop M**: Iterative refinement
5. **Hop M+1**: Final synthesis and output

### Evolution Cycle

1. **Performance Monitoring**: Track agent performance metrics
2. **Fitness Evaluation**: Calculate fitness scores based on outcomes
3. **Mutation Decision**: Determine if evolution is needed
4. **Strategy Mutation**: Modify prompts, parameters, or connections
5. **Validation**: Test evolved strategies
6. **Deployment**: Apply successful mutations

## Memory and Knowledge Management

### Vector Storage

Agents maintain vector-based memory for:
- Previous task solutions
- Successful strategy patterns
- Performance benchmarks
- Domain knowledge accumulation

### Knowledge Sharing

- **Federated Learning**: Agents share learned patterns
- **Topology Evolution**: Connection weights adapt based on collaboration success
- **Strategy Propagation**: Successful strategies spread through the network

## Monitoring and Metrics

### Performance Tracking

```python
# Performance metrics tracked per agent
metrics = {
    "accuracy": float,
    "response_time": float,
    "token_efficiency": float,
    "collaboration_score": float,
    "evolution_frequency": int
}
```

### System Health

- **Agent Availability**: Monitor agent responsiveness
- **Network Topology**: Track connection health
- **Evolution Progress**: Monitor improvement trends
- **Resource Usage**: API calls, tokens, computation time

## Error Handling and Recovery

### Failure Modes

1. **Agent Timeout**: Individual agent becomes unresponsive
2. **Network Partition**: Subset of agents lose connectivity
3. **Evolution Failure**: Strategy mutation produces poor results
4. **Resource Exhaustion**: API rate limits or token limits

### Recovery Strategies

1. **Agent Failover**: Backup agents take over failed roles
2. **Network Healing**: Automatic topology reconstruction
3. **Evolution Rollback**: Revert to previous successful strategies
4. **Resource Management**: Intelligent request batching and throttling

## Extension Points

### Custom Agents

```python
class CustomAgent:
    def __init__(self, role: str, config: Dict[str, Any]):
        self.role = role
        self.config = config
    
    def process(self, input_data: Any) -> Any:
        # Custom processing logic
        pass
    
    def evolve(self, performance_feedback: float) -> None:
        # Custom evolution strategy
        pass
```

### Custom Evolution Strategies

```python
class CustomEvolutionStrategy:
    def mutate_prompt(self, current_prompt: str, fitness: float) -> str:
        # Custom prompt mutation logic
        pass
    
    def mutate_topology(self, connections: List[str]) -> List[str]:
        # Custom topology mutation logic
        pass
```

## Usage Examples

### Basic Task Execution

```python
from sefas import FederatedSystem
from sefas.config import settings

# Initialize system
system = FederatedSystem(settings)

# Execute task
result = await system.execute_task(
    task="Analyze market trends for renewable energy",
    max_hops=10,
    confidence_threshold=0.8
)

print(f"Result: {result.output}")
print(f"Confidence: {result.confidence}")
print(f"Hops used: {result.hops}")
```

### Agent Performance Monitoring

```python
# Get system metrics
metrics = system.get_performance_metrics()

for agent_id, state in metrics.agent_states.items():
    print(f"Agent {agent_id}:")
    print(f"  Fitness: {state.fitness_score}")
    print(f"  Mutations: {state.mutation_count}")
    print(f"  Connections: {len(state.topology_connections)}")
```

### Custom Configuration

```python
# Load custom agent configuration
custom_config = {
    "agents": {
        "custom_analyzer": {
            "role": "custom_analyzer",
            "initial_prompt": "You are a custom analysis agent...",
            "temperature": 0.4,
            "strategy": "analytical"
        }
    }
}

system = FederatedSystem(settings, custom_config)
```

## Best Practices

1. **Task Decomposition**: Break complex tasks into verifiable subclaims
2. **Performance Monitoring**: Regularly check agent fitness scores
3. **Evolution Budget**: Limit evolution frequency to prevent instability
4. **Confidence Thresholds**: Set appropriate confidence levels for task completion
5. **Resource Management**: Monitor API usage and implement rate limiting
6. **Error Handling**: Implement robust fallback strategies
7. **Testing**: Use comprehensive test suites for validation

## Troubleshooting

### Common Issues

1. **Low Confidence Scores**: Increase max_hops or adjust confidence_threshold
2. **Poor Agent Performance**: Check evolution_budget and allow more mutations
3. **Network Connectivity**: Verify topology connections and agent availability
4. **Resource Limits**: Monitor API usage and implement throttling
5. **Evolution Instability**: Reduce evolution_budget or increase validation criteria