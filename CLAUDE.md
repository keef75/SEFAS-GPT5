# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SEFAS (Self-Evolving Federated Agent System) is a multi-agent AI system implementing autonomous evolution through federated intelligence. The system features 15 specialized agent roles that collaborate in a dynamic topology using m→m+1 hop execution patterns.

## Core Architecture

### Federated Agent System
- **Agent Roles**: 15 specialized agents organized in 3 layers:
  - Layer 1: Orchestrator, Task Decomposer, Strategy Evolver
  - Layer 2: Proposer Alpha/Beta/Gamma (creative/practical/alternative)
  - Layer 3: Checker Logic/Semantic/Consistency
- **Evolution State**: Each agent maintains `EvolutionState` with fitness tracking, performance history, and strategy genome
- **Federated State**: Global system state coordinating multi-agent execution with hop tracking

### Key Data Flows
- **M→M+1 Hop Pattern**: Tasks flow through hops (0=decomposition, 1=proposition, 2=validation, M=refinement)
- **Evolution Cycle**: Performance → Fitness → Mutation → Validation → Deployment
- **Confidence Threshold**: System reaches consensus when confidence >= 0.7 (configurable)

### Configuration System
- **YAML-based Agent Definitions**: `config/agents.yaml` defines roles, prompts, temperatures, strategies
- **Pydantic Settings**: `config/settings.py` with environment variable support
- **Evolution Budget**: 20% of compute allocated to evolution (configurable)

## Development Commands

### Setup
```bash
# Install dependencies
make install

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI and LangSmith API keys
```

### Running the System
```bash
# Basic task execution
make run

# Custom task with CLI
python scripts/run_experiment.py run "Your task here" --max-hops 15 --verbose

# Batch experiments
python scripts/run_experiment.py batch tasks.json --output-dir results/
```

### Development Workflow
```bash
# Run tests
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests only
pytest tests/unit/test_agents/test_orchestrator.py  # Single test file

# Comprehensive testing
python test_agents.py       # Full system test suite with 5 challenge types

# Code quality
make lint                   # ruff + mypy
make format                 # ruff format + black

# Cleanup
make clean                  # Remove cache files
```

### Troubleshooting Commands
```bash
# Test with verbose output and enhanced reporting
python scripts/run_experiment.py "Your task" --verbose

# Environment variable debugging (common API key issues)
unset OPENAI_API_KEY && python scripts/run_experiment.py "test task"

# Check logs
tail -f logs/sefas.log      # Real-time system logs
tail -f logs/agents.log     # Agent execution logs  
tail -f logs/evolution.log  # Evolution events

# View detailed execution reports
ls data/reports/            # Saved execution reports (JSON format)
```

## Key Implementation Patterns

### Agent State Management
- All agents inherit from base patterns with `EvolutionState` tracking
- Performance metrics feed into fitness calculations for evolution decisions
- State persistence through `FederatedState` TypedDict with serialization support

### LangSmith Integration
- **Tracing**: All LangChain operations automatically traced when `LANGSMITH_TRACING=true`
- **Agent Traces**: Individual agent executions with hop numbers, execution time, token usage
- **Federated Traces**: Complete system execution with agent performance summaries
- **Evolution Tracking**: Strategy mutations and topology changes traced
- Configure via `settings.configure_langsmith()` before LLM initialization

### Monitoring Architecture
- **Performance Tracker**: Global `performance_tracker` instance with task completion metrics
- **Fitness Metrics**: Per-agent tracking with trend analysis (improving/declining/stable)
- **Structured Logging**: JSON formatting with agent_id, task_id, hop_number context
- **LangSmith Monitor**: `langsmith_monitor` for distributed tracing and analytics
- **Execution Reporting**: Enhanced reporting via `sefas.monitoring.execution_reporter` with:
  - Rich terminal displays (tables, trees, panels)
  - Agent performance analysis and API call timelines
  - Token usage and cost estimation
  - Confidence analysis and system recommendations
  - Structured JSON reports saved to `data/reports/`

### Configuration Patterns
- **Environment Variables**: All sensitive config via `.env` with Pydantic validation
- **Agent Config Loading**: `Settings.load_agent_config()` from YAML with topology definitions
- **Graceful Fallbacks**: Missing evolution config returns safe defaults
- **Path Configuration**: Data/logs/checkpoints configurable via settings

## Working with Agents

### Adding New Agents
1. Define role in `AgentRole` enum in `sefas/core/state.py`
2. Add configuration in `config/agents.yaml` with role, prompt, temperature
3. Update topology connections in agents.yaml
4. Implement agent class following existing patterns
5. Register in system workflows

### Evolution Implementation
- Evolution triggered when fitness drops or performance stagnates
- Mutations can modify prompts, parameters, or topology connections
- Evolution budget prevents excessive computation overhead
- All evolution events logged and traced for analysis

### Integration Points
- **LangChain/LangGraph**: Core orchestration framework
- **FAISS**: Vector storage for agent memory and knowledge
- **Rich/Typer**: CLI interface with enhanced visual reporting
- **Pydantic**: Configuration validation and serialization

### Enhanced Execution Reporting
- **Automatic Report Generation**: All experiment runs now generate comprehensive execution reports
- **Visual Terminal Output**: Rich tables, trees, and panels showing execution flow, agent performance, and API call details
- **Structured Data Export**: JSON reports saved to `data/reports/` with timestamp and task ID
- **Performance Analytics**: Token usage tracking, cost estimation, and execution time analysis
- **Debugging Support**: Detailed error context, partial execution state preservation, and system recommendations
- **Integration**: Seamlessly integrated into `scripts/run_experiment.py` with enhanced --verbose mode

## File Organization Principles

### Module Structure
- `sefas/core/`: State management and fundamental data structures
- `sefas/agents/`: Individual agent implementations (when fully implemented)
- `sefas/evolution/`: Evolutionary algorithms and strategies (when implemented) 
- `sefas/monitoring/`: Performance tracking, logging, LangSmith integration
- `sefas/workflows/`: LangGraph orchestration and execution flows

### Current Implementation Status
- **Core State**: Fully implemented with EvolutionState and FederatedState
- **Configuration**: Complete with environment/YAML loading and robust error handling
- **Monitoring**: Full LangSmith integration, performance tracking, and enhanced execution reporting
- **CLI**: Functional with multi-hop execution and comprehensive visual reporting
- **Agent Implementations**: Working federated execution with defensive error handling
- **Evolution Module**: Architecture defined, implementation pending
- **Error Handling**: Comprehensive exception handling with partial state preservation

### Configuration Dependencies
- Requires `OPENAI_API_KEY` for LLM operations
- Optional `LANGSMITH_*` variables for tracing and monitoring
- Agent configurations loaded from `config/agents.yaml`
- System parameters configurable via environment variables or defaults

## Critical Configuration Issues

### API Key Loading Order
**CRITICAL**: Environment variables must be configured BEFORE agent initialization. The system calls `settings.configure_langsmith()` in `FederatedSystemRunner.__init__()` to set `os.environ["OPENAI_API_KEY"]` before any `ChatOpenAI` instances are created. If agents are initialized first, they will fail with 401 Unauthorized errors.

### GPT-5 Compatibility
- System is configured for GPT-5 but supports fallback to GPT-4
- GPT-5 uses different parameter names (`max_completion_tokens` vs `max_tokens`)
- LangChain automatically handles parameter translation for GPT-5

### Environment Variable Priority
1. `.env` file loaded by Pydantic Settings
2. `settings.configure_langsmith()` sets OS environment variables  
3. LangChain clients read from OS environment variables
4. Missing step 2 causes 401 errors even with valid API keys

## Error Handling Patterns
- **Defensive Variable Initialization**: All execution variables initialized with safe defaults before try blocks to prevent KeyError in exception handlers
- **Enhanced Exception Handling**: System errors capture partial execution state and metrics for debugging
- **LangSmith Integration**: Gracefully degrades when unavailable (403 Forbidden errors logged but don't halt execution)
- **Configuration Loading**: Safe defaults for missing files and environment variables
- **Agent Execution**: Individual agent failures don't stop system execution; partial results preserved
- **Belief Propagation**: Safe dictionary access prevents KeyError exceptions
- **CLI Handling**: Empty confidence scores and missing data handled gracefully
- **Environment Variable Conflicts**: Shell environment variables override .env files; use `unset OPENAI_API_KEY` for troubleshooting