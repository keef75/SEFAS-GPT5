# 🚀 SEFAS Quick Reference

**Rapid navigation and command reference for SEFAS development**

---

## ⚡ Essential Commands

### 🏃 Quick Start
```bash
# Setup (one-time)
make install && cp .env.example .env
# Edit .env with your OpenAI API key

# Run experiment
python scripts/run_experiment.py "Your task here" --verbose

# System test
python test_agents.py
```

### 🔧 Development
```bash
make test                    # All tests
make lint                    # Code quality
make format                  # Code formatting
make clean                   # Clean artifacts
```

### 🤖 Agent Management
```bash
python scripts/manage_agents.py list              # View all agents
python scripts/manage_agents.py show orchestrator # Agent details
python scripts/manage_agents.py edit proposer_alpha # Edit configuration
python scripts/manage_agents.py topology          # Network visualization
```

### 📊 Monitoring
```bash
tail -f logs/sefas.log      # System events
tail -f logs/agents.log     # Agent execution
tail -f logs/performance.log # Performance metrics
ls data/reports/            # Generated reports
```

---

## 📁 Key File Locations

### 📖 Documentation
| File | Purpose |
|------|---------|
| `docs/INDEX.md` | Complete documentation index |
| `README.md` | Project overview and quick start |
| `CLAUDE.md` | Development guide and implementation details |
| `docs/STRUCTURE.md` | Project structure and organization |
| `docs/API.md` | API reference and usage examples |

### ⚙️ Configuration
| File | Purpose |
|------|---------|
| `config/agents.yaml` | 17-agent configuration with prompts and models |
| `config/settings.py` | System settings and environment variables |
| `.env` | API keys and environment configuration |

### 🤖 Core System
| Directory | Contents |
|-----------|----------|
| `sefas/core/` | State management, belief propagation, validation |
| `sefas/agents/` | 17-agent implementations and factory |
| `sefas/workflows/` | LangGraph orchestration and execution |
| `sefas/monitoring/` | Performance tracking and reporting |

### 🛠️ Development
| Directory | Contents |
|-----------|----------|
| `scripts/` | Execution scripts and utilities |
| `tests/` | Test suites (when implemented) |
| `logs/` | System, agent, and performance logs |
| `data/reports/` | Generated execution reports |

---

## 🤖 17-Agent System Overview

### Layer 1: Strategic Command (3 agents)
- **orchestrator** - Central coordination and task decomposition
- **task_decomposer** - Advanced problem breakdown
- **strategy_evolver** - Adaptive system optimization

### Layer 2: Creative & Analytical (7 agents)
- **proposer_alpha** - Creative solutions (temp: 0.8)
- **proposer_beta** - Analytical solutions (temp: 0.3)
- **proposer_gamma** - Research synthesis (temp: 0.5)
- **domain_expert** - Specialized knowledge
- **technical_architect** - System design
- **innovation_catalyst** - Breakthrough thinking
- **strategic_planner** - Execution roadmaps

### Layer 3: Quality Assurance (5 agents)
- **checker_logic** - Logic validation (temp: 0.1)
- **checker_semantic** - Meaning validation (temp: 0.2)
- **checker_consistency** - Coherence validation (temp: 0.1)
- **quality_assurer** - Standards enforcement
- **performance_optimizer** - Efficiency analysis
- **risk_assessor** - Risk analysis
- **compliance_officer** - Ethics and compliance

---

## 🔧 Configuration Quick Reference

### Model Selection
```yaml
gpt-4o-mini    # Fast, efficient (strategic agents)
gpt-4o         # Powerful (creative/analytical agents)
gpt-5          # Cutting-edge (when available)
```

### Temperature Settings
```yaml
0.1-0.2        # Focused (logic, consistency)
0.3-0.5        # Balanced (analysis, research)
0.6-0.8        # Creative (innovation, ideation)
```

### Execution Strategies
```yaml
layered_parallel    # Default: sequential layers, parallel agents
full_parallel      # All agents simultaneous
sequential         # One agent at a time
adaptive           # Dynamic based on complexity
```

---

## 🚨 Troubleshooting

### Common Issues
| Issue | Quick Fix |
|-------|-----------|
| 401 API errors | Check `OPENAI_API_KEY` in `.env` |
| Agent config failure | Validate `config/agents.yaml` syntax |
| Import errors | Activate venv: `source venv/bin/activate` |
| Slow performance | Use `gpt-4o-mini` for routine agents |
| Missing reports | Check `data/reports/` directory permissions |

### Debug Commands
```bash
# Environment check
echo $OPENAI_API_KEY

# Config validation
python -c "import yaml; print(yaml.safe_load(open('config/agents.yaml')))"

# Test minimal system
python -c "from sefas.core.state import AgentRole; print(list(AgentRole))"

# Clear cache
make clean
```

---

## 📊 Performance Optimization

### Model Recommendations
| Agent Type | Recommended Model | Reason |
|------------|------------------|---------|
| Strategic (orchestrator, evolver) | gpt-4o-mini | Fast, consistent |
| Creative (alpha, catalyst) | gpt-4o | High creativity |
| Technical (architect, expert) | gpt-4o | Deep reasoning |
| Validation (checkers) | gpt-4o | Precision required |
| Quality (assurer, optimizer) | gpt-4o-mini | Efficient routine checks |

### Performance Tuning
```yaml
# Rate limiting (prevents API overload)
rate_limit_ms: 1000           # 1 second between calls

# Token optimization
max_tokens: 1500              # Reduce for faster responses
temperature: 0.3              # Lower for consistency

# Execution optimization
execution:
  default_strategy: "layered_parallel"
  max_parallel_per_layer: 4
```

---

## 🔍 Monitoring & Observability

### LangSmith Integration
```bash
# Enable in .env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key
LANGSMITH_PROJECT=SEFAS-MultiAgent-System
```

### Performance Metrics
- **Token Usage** - Track API consumption
- **Execution Time** - Monitor response times
- **Confidence Scores** - Validate output quality
- **Agent Fitness** - Track evolution performance
- **Error Rates** - System reliability metrics

### Report Types
- **HTML** - Rich visual reports with charts
- **JSON** - Structured data for analysis
- **Markdown** - Human-readable documentation
- **Terminal** - Real-time execution displays

---

## 📚 Learning Resources

### Next Steps
1. **Read**: `README.md` for project overview
2. **Explore**: `docs/INDEX.md` for complete documentation
3. **Configure**: `config/agents.yaml` for customization
4. **Experiment**: `scripts/run_experiment.py` for testing
5. **Monitor**: `data/reports/` for execution analysis

### Key Concepts
- **Federated Intelligence** - Distributed multi-agent reasoning
- **Belief Propagation** - Consensus calculation and convergence
- **N-Version Programming** - Redundant execution for reliability
- **Quorum Validation** - Multi-validator consensus requirements
- **Evolution Strategy** - Adaptive agent improvement (planned)

---

## 🎯 Common Use Cases

### Research & Analysis
```bash
python scripts/run_experiment.py "Analyze quantum computing implications" --max-hops 15
```

### Creative Problem Solving
```bash
python scripts/run_experiment.py "Design sustainable transportation system" --verbose
```

### Technical Architecture
```bash
python scripts/run_experiment.py "Create microservices architecture for e-commerce" --verbose
```

### Risk Assessment
```bash
python scripts/run_experiment.py "Evaluate cybersecurity risks for cloud migration" --verbose
```

---

<div align="center">

**⚡ Quick Reference - SEFAS Documentation ⚡**

*For complete documentation, see [docs/INDEX.md](INDEX.md)*

</div>