# 📚 SEFAS Documentation Index

**Self-Evolving Federated Agent System (SEFAS) - Complete Documentation Directory**

---

## 🎯 Quick Navigation

| Section | Description | Files |
|---------|-------------|-------|
| **[🚀 Getting Started](#-getting-started)** | Installation, setup, and first run | README.md, CLAUDE.md |
| **[🏗️ Architecture](#️-architecture)** | System design and components | STRUCTURE.md, API.md |
| **[🤖 Agent System](#-agent-system)** | 17-agent network and capabilities | agents.yaml, Agent docs |
| **[⚡ Core Components](#-core-components)** | Reliability, validation, belief propagation | Core modules |
| **[🔧 Development](#-development)** | Building, testing, and contributing | Scripts, tests, tools |
| **[📊 Monitoring](#-monitoring)** | Performance, reporting, and observability | Monitoring modules |
| **[🛠️ Configuration](#️-configuration)** | Settings, agents, and customization | Config files |
| **[📋 Reference](#-reference)** | API docs, CLI commands, and examples | API.md, examples |

---

## 🚀 Getting Started

### Essential Reading
- **[README.md](../README.md)** - Project overview, quick start, and key features
- **[CLAUDE.md](../CLAUDE.md)** - Development guide and implementation details
- **[setup.py](../setup.py)** - Package installation and dependencies

### Quick Start Commands
```bash
# Basic setup
make install && cp .env.example .env
# Edit .env with your OpenAI API key

# Run your first experiment
python scripts/run_experiment.py "Analyze renewable energy benefits" --verbose

# System testing
python test_agents.py
```

---

## 🏗️ Architecture

### System Design Documentation
- **[STRUCTURE.md](STRUCTURE.md)** - Complete project structure and organization
- **[API.md](API.md)** - Core classes, interfaces, and usage patterns

### Core Architecture Components

#### 📦 Module Structure
```
sefas/
├── 🎯 core/           # State management, belief propagation, reliability
├── 🤖 agents/         # 17-agent federated intelligence network
├── ⚡ workflows/      # LangGraph orchestration and execution
├── 📊 monitoring/     # Performance tracking and observability
├── 🧠 memory/         # Episodic memory and knowledge management
├── 📈 reporting/      # Multi-format report generation
└── 🔄 evolution/     # Adaptive strategy evolution (planned)
```

#### 🏛️ Three-Layer Intelligence Stack
1. **Layer 1: Strategic Command** (3 agents)
   - `orchestrator` - Central coordination and task decomposition
   - `task_decomposer` - Advanced problem breakdown
   - `strategy_evolver` - Adaptive optimization

2. **Layer 2: Creative & Analytical Generation** (7 agents)
   - `proposer_alpha/beta/gamma` - Multi-strategy solution generation
   - `domain_expert` - Specialized knowledge
   - `technical_architect` - System design
   - `innovation_catalyst` - Breakthrough thinking
   - `strategic_planner` - Execution roadmaps

3. **Layer 3: Quality Assurance & Validation** (5 agents)
   - `checker_logic/semantic/consistency` - Multi-dimensional validation
   - `quality_assurer` - Standards enforcement
   - `performance_optimizer` - Efficiency analysis
   - `risk_assessor` - Risk analysis
   - `compliance_officer` - Ethics and compliance

---

## 🤖 Agent System

### Agent Configuration & Management
- **[config/agents.yaml](../config/agents.yaml)** - Complete 17-agent configuration with prompts, models, and topology
- **[scripts/manage_agents.py](../scripts/manage_agents.py)** - CLI for agent configuration and management
- **[sefas/agents/factory.py](../sefas/agents/factory.py)** - Dynamic agent creation and instantiation

### Agent Types & Capabilities

#### 🎯 Strategic Command Agents
| Agent | Role | Specialty | Temperature | Model |
|-------|------|-----------|-------------|-------|
| **orchestrator** | Central coordination | Task decomposition | 0.1 | gpt-4o-mini |
| **task_decomposer** | Problem breakdown | Systematic analysis | 0.2 | gpt-4o-mini |
| **strategy_evolver** | System optimization | Adaptive improvement | 0.4 | gpt-4o-mini |

#### 💡 Creative & Analytical Agents
| Agent | Role | Specialty | Temperature | Model |
|-------|------|-----------|-------------|-------|
| **proposer_alpha** | Creative solutions | Innovation & ideation | 0.8 | gpt-4o |
| **proposer_beta** | Analytical solutions | Systematic analysis | 0.3 | gpt-4o |
| **proposer_gamma** | Research synthesis | Knowledge integration | 0.5 | gpt-4o |
| **domain_expert** | Specialized knowledge | Domain expertise | 0.4 | gpt-4o |
| **technical_architect** | System design | Technical blueprints | 0.3 | gpt-4o |
| **innovation_catalyst** | Breakthrough thinking | Paradigm shifts | 0.7 | gpt-4o |
| **strategic_planner** | Execution planning | Roadmap development | 0.4 | gpt-4o-mini |

#### ✅ Quality Assurance Agents
| Agent | Role | Specialty | Temperature | Model |
|-------|------|-----------|-------------|-------|
| **checker_logic** | Logic validation | Reasoning consistency | 0.1 | gpt-4o |
| **checker_semantic** | Meaning validation | Semantic accuracy | 0.2 | gpt-4o |
| **checker_consistency** | Coherence validation | Cross-claim harmony | 0.1 | gpt-4o |
| **quality_assurer** | Standards enforcement | Quality metrics | 0.3 | gpt-4o-mini |
| **performance_optimizer** | Efficiency analysis | Resource optimization | 0.4 | gpt-4o-mini |
| **risk_assessor** | Risk analysis | Threat assessment | 0.3 | gpt-4o-mini |
| **compliance_officer** | Ethics & compliance | Regulatory adherence | 0.2 | gpt-4o-mini |

### Agent Network Topology
```yaml
# Hierarchical connection structure
Layer 1 → Layer 2 → Layer 3 → Quality Feedback Loop
orchestrator → proposers → checkers → quality_assurance
```

---

## ⚡ Core Components

### 🔄 Reliability & Redundancy
- **[sefas/core/redundancy.py](../sefas/core/redundancy.py)** - Industrial-grade redundancy with N-version programming
  - Circuit breakers and fault tolerance
  - Hedged requests for tail latency reduction
  - Automatic recovery mechanisms

### ✅ Enhanced Validation System
- **[sefas/core/validation.py](../sefas/core/validation.py)** - Quorum-based consensus validation
  - Multi-validator pools with fallback mechanisms
  - Comprehensive error handling and partial state preservation
  - Quality gates and validation pipelines

### 🧠 Belief Propagation Engine
- **[sefas/core/belief_propagation.py](../sefas/core/belief_propagation.py)** - Advanced consensus calculation
  - Convergence detection and confidence weighting
  - Iterative belief updating with network effects
  - Opinion aggregation and uncertainty quantification

### 📊 State Management
- **[sefas/core/state.py](../sefas/core/state.py)** - Core state definitions and management
  - `AgentRole` enum with 17 specialized roles
  - `EvolutionState` for individual agent tracking
  - `FederatedState` for system-wide coordination

---

## 🔧 Development

### 🛠️ Build System
- **[Makefile](../Makefile)** - Standardized build, test, and development commands
```bash
make install    # Install dependencies
make test       # Run comprehensive test suite
make lint       # Code quality checks (ruff + mypy)
make format     # Code formatting (ruff + black)
make run        # Execute system with default task
make clean      # Remove cache and artifacts
```

### 🧪 Testing Infrastructure
- **[test_agents.py](../test_agents.py)** - Comprehensive agent system testing
- **[test_improvements.py](../test_improvements.py)** - Enhanced reliability and validation testing
- **[tests/](../tests/)** - Unit and integration test suites (when fully implemented)

### 📜 Scripts & Tools
- **[scripts/run_experiment.py](../scripts/run_experiment.py)** - Main execution engine with enhanced reporting
- **[scripts/manage_agents.py](../scripts/manage_agents.py)** - Agent configuration management CLI
- **[scripts/run_with_comprehensive_reports.py](../scripts/run_with_comprehensive_reports.py)** - Enhanced execution with full reporting

### 🔧 Development Workflow
```bash
# Setup development environment
python -m venv venv && source venv/bin/activate
make install

# Run with debugging
python scripts/run_experiment.py "test task" --verbose

# Monitor system health
tail -f logs/sefas.log      # System events
tail -f logs/agents.log     # Agent execution
tail -f logs/evolution.log  # Evolution events

# View execution reports
ls data/reports/            # Generated reports (HTML/JSON/MD)
```

---

## 📊 Monitoring

### 📈 Performance Tracking
- **[sefas/monitoring/metrics.py](../sefas/monitoring/metrics.py)** - Performance metrics collection and analysis
- **[sefas/monitoring/execution_reporter.py](../sefas/monitoring/execution_reporter.py)** - Rich terminal displays and structured reporting

### 📝 Logging System
- **[sefas/monitoring/logging.py](../sefas/monitoring/logging.py)** - Structured logging with agent context
- **[sefas/monitoring/langsmith_integration.py](../sefas/monitoring/langsmith_integration.py)** - Professional monitoring and tracing

### 📊 Report Generation
- **[sefas/reporting/final_report.py](../sefas/reporting/final_report.py)** - Multi-format report generation (HTML/JSON/Markdown)
- **[sefas/reporting/report_synthesizer.py](../sefas/reporting/report_synthesizer.py)** - Comprehensive synthesis reporting
- **[sefas/reporting/agent_reporter.py](../sefas/reporting/agent_reporter.py)** - Individual agent performance reporting

### 🔍 LangSmith Integration
```bash
# Enable professional monitoring
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=SEFAS-MultiAgent-System
```

---

## 🛠️ Configuration

### ⚙️ System Configuration
- **[config/settings.py](../config/settings.py)** - Pydantic-based settings with environment variable support
- **[.env.example](../.env.example)** - Environment variable template

### 🤖 Agent Configuration
- **[config/agents.yaml](../config/agents.yaml)** - Complete agent definitions with:
  - Individual LLM parameters (model, temperature, max_tokens, rate_limit_ms)
  - Custom prompts and strategies
  - Network topology and connections
  - Evolution and execution strategies

### 🔧 Customization Options
```yaml
# Model Selection
gpt-4o-mini    # Fast, efficient for routine tasks
gpt-4o         # Powerful for complex reasoning
gpt-5          # Cutting-edge capabilities (when available)

# Temperature Settings
0.1-0.2        # Focused (logic, consistency)
0.3-0.5        # Balanced (analysis, research)  
0.6-0.8        # Creative (innovation, ideation)

# Execution Strategies
layered_parallel    # Default: layers sequential, agents parallel
full_parallel      # All agents simultaneous
sequential         # One agent at a time
adaptive           # Dynamic based on complexity
```

---

## 📋 Reference

### 📖 API Documentation
- **[API.md](API.md)** - Complete API reference with classes, methods, and usage examples
- **[sefas/__init__.py](../sefas/__init__.py)** - Package exports and public interface

### 💾 Memory & Knowledge
- **[sefas/memory/episodic.py](../sefas/memory/episodic.py)** - Episodic memory system with:
  - Vector-based similarity search
  - Memory consolidation and pattern extraction
  - Deduplication and relevance scoring

### 🔄 Workflow Orchestration
- **[sefas/workflows/executor.py](../sefas/workflows/executor.py)** - Main federated system runner
  - Agent coordination and hop execution
  - Error handling and recovery
  - Performance monitoring integration

### 📊 Data Structures
```python
# Core state management
AgentRole          # 17 specialized agent roles
EvolutionState     # Individual agent evolution tracking  
FederatedState     # System-wide state coordination

# Execution tracking
AgentReport        # Individual agent performance
ExecutionMetrics   # System performance analytics
BeliefState        # Consensus and confidence scores
```

---

## 🎨 Examples & Use Cases

### 💡 Basic Usage Examples
```python
# Simple task execution
python scripts/run_experiment.py "Analyze climate change solutions"

# Complex problem solving
python scripts/run_experiment.py "Design sustainable transportation system" --max-hops 15 --verbose

# Batch processing
python scripts/run_experiment.py batch tasks.json --output-dir results/

# Agent management
python scripts/manage_agents.py list
python scripts/manage_agents.py show orchestrator
python scripts/manage_agents.py topology
```

### 🔬 Research & Experimentation
- **[examples/langsmith_integration_example.py](../examples/langsmith_integration_example.py)** - LangSmith monitoring integration
- **[data/reports/](../data/reports/)** - Example execution reports in multiple formats

### 📈 Performance Benchmarks
```bash
# System validation
python test_agents.py       # 5 challenge types with performance metrics
python test_improvements.py # Enhanced reliability testing

# Performance profiling
python scripts/run_experiment.py "benchmark task" --verbose | grep "Performance Summary"
```

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 🔑 API Key Configuration
```bash
# Issue: 401 Unauthorized errors
# Solution: Ensure proper environment variable setup
export OPENAI_API_KEY="your-key-here"
# or edit .env file

# Debug: Check environment loading
unset OPENAI_API_KEY && python scripts/run_experiment.py "test"
```

#### 🤖 Agent Initialization
```bash
# Issue: Agent configuration loading failures
# Solution: Validate YAML syntax and required fields
python -c "import yaml; print(yaml.safe_load(open('config/agents.yaml')))"

# Fallback: Use built-in minimal configuration
# System automatically falls back if config/agents.yaml is invalid
```

#### 📊 Performance Issues
```bash
# Issue: Slow execution or high token usage
# Solution: Optimize model selection and temperature settings
# - Use gpt-4o-mini for routine tasks
# - Reduce temperature for focused agents
# - Enable rate limiting in agent configuration

# Monitor: Check real-time performance
tail -f logs/performance.log
```

#### 🔧 Development Environment
```bash
# Issue: Import or dependency errors
# Solution: Ensure proper virtual environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Validation: Run system tests
make test
```

---

## 🔄 Evolution & Roadmap

### Current Implementation Status ✅
- **Enhanced Agent System**: 17-agent network with dynamic configuration
- **Reliability Stack**: N-version programming, quorum validation, circuit breakers  
- **Belief Propagation**: Advanced consensus with convergence detection
- **Agent Management**: Full CLI for configuration and monitoring
- **Report Generation**: Multi-format outputs with rich terminal displays
- **Error Handling**: Comprehensive exception handling with graceful fallbacks

### Planned Enhancements 🚧
- **Evolution System**: Full adaptive strategy evolution (partially implemented)
- **Advanced Memory**: Vector storage and knowledge base integration
- **Deployment Tools**: Docker containerization and orchestration
- **Performance Optimization**: Caching and parallel execution improvements
- **UI Dashboard**: Web interface for system monitoring and control

### Contributing 🤝
1. **Fork & Clone**: Standard GitHub workflow
2. **Environment Setup**: Follow development setup instructions
3. **Testing**: Ensure all tests pass with `make test`
4. **Documentation**: Update relevant documentation
5. **Pull Request**: Submit with clear description and test coverage

---

## 📚 Additional Resources

### 🔗 External Dependencies
- **[LangChain](https://langchain.com/)** - LLM orchestration framework
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - Graph-based workflows
- **[LangSmith](https://smith.langchain.com/)** - Professional monitoring and tracing
- **[OpenAI API](https://platform.openai.com/)** - LLM services
- **[Pydantic](https://pydantic.dev/)** - Data validation and settings

### 📖 Related Documentation
- **[GitHub Repository](https://github.com/keef75/SEFAS)** - Source code and issue tracking
- **[Python 3.9+ Documentation](https://docs.python.org/3/)** - Language reference
- **[YAML Configuration Guide](https://yaml.org/)** - Configuration file syntax

### 🏷️ Version Information
- **SEFAS Version**: Latest development
- **Python**: 3.9+ required
- **LangChain**: 0.1.0+
- **OpenAI**: Compatible with GPT-4, GPT-4o, and GPT-5 (when available)

---

## 📧 Support & Contact

- **🐛 Issues**: [GitHub Issues](https://github.com/keef75/SEFAS/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/keef75/SEFAS/discussions)
- **📧 Contact**: Open an issue for questions or collaboration

---

<div align="center">

**⚡ SEFAS - Where AI Agents Evolve Together ⚡**

*Built with ❤️ by K3ith.AI and Cocoa AI research*

</div>