# SEFAS Project Structure

## Directory Overview

```
SEFAS/
├── sefas/                  # Main package
│   ├── __init__.py
│   ├── agents/             # Agent implementations
│   ├── core/               # Core system components
│   │   └── state.py        # State management
│   ├── evolution/          # Evolution strategies
│   ├── memory/             # Memory and knowledge storage
│   ├── monitoring/         # Performance tracking
│   ├── tools/              # Agent tools and utilities
│   ├── utils/              # Helper functions
│   └── workflows/          # LangGraph orchestration
├── config/                 # Configuration files
│   ├── agents.yaml         # Agent definitions
│   └── settings.py         # System settings
├── scripts/                # Utility scripts
│   └── run_experiment.py   # Main execution script
├── tests/                  # Test suite
│   ├── fixtures/           # Test data
│   ├── integration/        # Integration tests
│   └── unit/               # Unit tests
├── experiments/            # Research and experiments
│   └── notebooks/          # Jupyter notebooks
├── docker/                 # Docker configuration
├── docs/                   # Documentation
│   ├── API.md              # API reference
│   └── STRUCTURE.md        # This file
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py                # Package setup
├── Makefile                # Build and test commands
└── README.md               # Project overview
```

## Core Package Structure

### `sefas/` - Main Package

The main Python package containing all system components.

#### `agents/` - Agent Implementations

Contains individual agent classes and their specialized implementations:

- **Orchestrator Agents**: Central coordination and task management
- **Proposer Agents**: Solution generation with different strategies
- **Checker Agents**: Verification and validation components
- **Specialized Agents**: Domain-specific reasoning agents

**Expected Files:**
```
agents/
├── __init__.py
├── base_agent.py           # Abstract base agent class
├── orchestrator.py         # Central orchestrator
├── proposers/              # Proposition agents
│   ├── alpha.py           # Creative proposer
│   ├── beta.py            # Practical proposer
│   └── gamma.py           # Alternative proposer
├── checkers/              # Verification agents
│   ├── logic.py           # Logic checker
│   ├── semantic.py        # Semantic checker
│   └── consistency.py     # Consistency checker
└── specialized/           # Domain specialists
    ├── analyzer.py        # Analysis specialist
    ├── synthesizer.py     # Synthesis specialist
    └── evaluator.py       # Evaluation specialist
```

#### `core/` - Core Components

System-wide state management and fundamental data structures.

**Current Files:**
- `state.py` - Evolution state and federated state classes

**Expected Files:**
```
core/
├── __init__.py
├── state.py               # State management (existing)
├── types.py               # Type definitions
├── exceptions.py          # Custom exceptions
├── events.py              # Event system
└── registry.py            # Agent registry
```

#### `evolution/` - Evolution Strategies

Evolutionary algorithms and adaptation mechanisms:

**Expected Files:**
```
evolution/
├── __init__.py
├── strategies.py          # Evolution strategies
├── mutations.py           # Mutation operators
├── fitness.py             # Fitness evaluation
├── selection.py           # Selection mechanisms
└── crossover.py           # Crossover operations
```

#### `memory/` - Memory and Knowledge

Vector storage, knowledge management, and learning systems:

**Expected Files:**
```
memory/
├── __init__.py
├── vector_store.py        # Vector database interface
├── knowledge_base.py      # Knowledge management
├── embeddings.py          # Embedding utilities
└── retrieval.py           # Information retrieval
```

#### `monitoring/` - Performance Tracking

Metrics collection, performance analysis, and system health monitoring:

**Expected Files:**
```
monitoring/
├── __init__.py
├── metrics.py             # Performance metrics
├── logging.py             # Structured logging
├── dashboard.py           # Performance dashboard
└── alerts.py              # Alert system
```

#### `tools/` - Agent Tools

Reusable tools and capabilities for agents:

**Expected Files:**
```
tools/
├── __init__.py
├── base_tool.py           # Abstract tool interface
├── reasoning.py           # Reasoning tools
├── analysis.py            # Analysis utilities
├── validation.py          # Validation tools
└── communication.py       # Inter-agent communication
```

#### `utils/` - Utilities

Helper functions and common utilities:

**Expected Files:**
```
utils/
├── __init__.py
├── decorators.py          # Common decorators
├── formatting.py          # Text formatting
├── async_utils.py         # Async utilities
└── config_utils.py        # Configuration helpers
```

#### `workflows/` - LangGraph Orchestration

LangGraph workflow definitions and orchestration logic:

**Expected Files:**
```
workflows/
├── __init__.py
├── base_workflow.py       # Base workflow class
├── federated_flow.py      # Main federated workflow
├── evolution_flow.py      # Evolution workflow
└── validation_flow.py     # Validation workflow
```

## Configuration Structure

### `config/` - Configuration Files

System configuration and agent definitions.

#### `agents.yaml` - Agent Configuration

Defines agent roles, prompts, and parameters:

```yaml
agents:
  orchestrator:
    role: "orchestrator"
    initial_prompt: "System orchestration prompt..."
    temperature: 0.1
    max_tokens: 2000
    
topology:
  initial_connections:
    orchestrator: ["proposer_alpha", "proposer_beta"]
```

#### `settings.py` - System Settings

Python-based configuration using Pydantic:

```python
class Settings(BaseSettings):
    openai_api_key: str
    llm_model: str = "gpt-4"
    max_hops: int = 10
    confidence_threshold: float = 0.7
```

**Expected Additional Config Files:**
```
config/
├── agents.yaml            # Agent definitions (existing)
├── settings.py            # System settings (existing)
├── evolution.yaml         # Evolution parameters
├── topology.yaml          # Network topology
└── environments/          # Environment-specific configs
    ├── development.yaml
    ├── staging.yaml
    └── production.yaml
```

## Testing Structure

### `tests/` - Test Suite

Comprehensive test coverage for all components.

#### `unit/` - Unit Tests
```
unit/
├── test_agents/           # Agent unit tests
├── test_core/             # Core component tests
├── test_evolution/        # Evolution strategy tests
├── test_memory/           # Memory system tests
├── test_monitoring/       # Monitoring tests
├── test_tools/            # Tool tests
├── test_utils/            # Utility tests
└── test_workflows/        # Workflow tests
```

#### `integration/` - Integration Tests
```
integration/
├── test_federated_system.py  # End-to-end system tests
├── test_agent_coordination.py # Agent interaction tests
├── test_evolution_cycles.py   # Evolution integration
└── test_performance.py        # Performance benchmarks
```

#### `fixtures/` - Test Data
```
fixtures/
├── sample_tasks.json      # Test task definitions
├── agent_configs.yaml    # Test agent configurations
├── mock_responses.json   # Mock API responses
└── performance_data.json # Performance test data
```

## Scripts and Utilities

### `scripts/` - Execution Scripts

Utility scripts for running and managing the system.

#### `run_experiment.py` - Main Execution Script

Primary entry point for running SEFAS experiments and tasks.

**Expected Additional Scripts:**
```
scripts/
├── run_experiment.py      # Main execution (existing)
├── setup_environment.py   # Environment setup
├── migrate_data.py        # Data migration
├── benchmark.py           # Performance benchmarking
└── deploy.py              # Deployment script
```

## Development Structure

### `experiments/` - Research and Development

Research notebooks and experimental code.

#### `notebooks/` - Jupyter Notebooks
```
notebooks/
├── evolution_analysis.ipynb    # Evolution strategy analysis
├── performance_profiling.ipynb # Performance profiling
├── topology_visualization.ipynb # Network visualization
└── task_decomposition.ipynb    # Task analysis
```

## Documentation Structure

### `docs/` - Documentation

Comprehensive project documentation.

```
docs/
├── README.md              # Quick start guide
├── API.md                 # API reference
├── STRUCTURE.md           # This file
├── ARCHITECTURE.md        # System architecture
├── EVOLUTION.md           # Evolution strategies
├── DEPLOYMENT.md          # Deployment guide
└── TROUBLESHOOTING.md     # Common issues
```

## Build and Deployment

### `Makefile` - Build Commands

Standardized build, test, and deployment commands:

- `make install` - Install dependencies
- `make test` - Run test suite
- `make lint` - Code quality checks
- `make format` - Code formatting
- `make run` - Execute system
- `make clean` - Cleanup artifacts

### `docker/` - Containerization

Docker configuration for deployment:

**Expected Files:**
```
docker/
├── Dockerfile             # Main application image
├── docker-compose.yml     # Multi-service orchestration
├── requirements.txt       # Container dependencies
└── entrypoint.sh          # Container startup script
```

## Dependencies

### `requirements.txt` - Production Dependencies

Core runtime dependencies for the system:

- `langchain>=0.1.0` - LLM orchestration framework
- `langgraph>=0.0.30` - Graph-based workflows
- `langchain-openai>=0.0.5` - OpenAI integration
- `faiss-cpu>=1.7.4` - Vector similarity search
- `pydantic>=2.0.0` - Data validation
- `pyyaml>=6.0` - Configuration parsing

### `requirements-dev.txt` - Development Dependencies

Additional tools for development and testing:

- `pytest>=7.4.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `ruff` - Code linting
- `black` - Code formatting
- `mypy` - Type checking

## Key Design Patterns

### 1. Agent Pattern
Each agent is a self-contained unit with:
- Role-specific prompts and parameters
- Evolution state tracking
- Performance monitoring
- Inter-agent communication

### 2. State Management Pattern
Centralized state management using:
- `EvolutionState` for individual agents
- `FederatedState` for system-wide state
- Immutable state transitions
- Event-driven updates

### 3. Evolution Pattern
Evolutionary adaptation through:
- Fitness-based selection
- Strategy mutation
- Topology evolution
- Performance-driven adaptation

### 4. Configuration Pattern
Hierarchical configuration using:
- YAML for agent definitions
- Python classes for system settings
- Environment-specific overrides
- Runtime parameter injection

### 5. Testing Pattern
Comprehensive testing strategy:
- Unit tests for individual components
- Integration tests for workflows
- Performance benchmarks
- Mock external dependencies

## Extension Points

### Adding New Agents

1. Create agent class in `sefas/agents/`
2. Define configuration in `config/agents.yaml`
3. Register agent in system registry
4. Add unit tests in `tests/unit/test_agents/`
5. Update topology connections if needed

### Adding New Tools

1. Implement tool interface in `sefas/tools/`
2. Register tool with agent system
3. Add tool tests in `tests/unit/test_tools/`
4. Document tool capabilities

### Adding New Evolution Strategies

1. Implement strategy in `sefas/evolution/`
2. Register strategy with evolution system
3. Add strategy tests
4. Update configuration options

## File Naming Conventions

- **Python files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Configuration files**: `lowercase.yaml`
- **Documentation**: `UPPERCASE.md`

## Import Conventions

- Absolute imports from package root
- Relative imports within modules
- Type imports in TYPE_CHECKING blocks
- Lazy imports for optional dependencies