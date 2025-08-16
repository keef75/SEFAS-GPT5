# 🤖 SEFAS - Self-Evolving Federated Agent System

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-integrated-green)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)](https://openai.com/)

**Next-generation multi-agent AI system with autonomous evolution and federated intelligence**

</div>

---

## 🌟 Overview

SEFAS is an advanced multi-agent AI system featuring **15 specialized agents** that collaborate through **federated intelligence** and **autonomous evolution**. Unlike traditional AI systems, SEFAS agents continuously evolve their strategies and optimize their collaborative networks.

---

### ✨ Key Features

- 🧬 **Self-Evolution** - Agents autonomously improve their strategies
- 🌐 **Federated Intelligence** - Distributed reasoning across specialized roles  
- 📊 **Real-time Monitoring** - Comprehensive performance tracking
- 🔄 **Dynamic Topology** - Self-organizing agent networks
- 💡 **Emergent Intelligence** - Complex problem-solving through collaboration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Virtual environment (recommended)

---

### Installation

```bash
# Clone the repository
git clone https://github.com/keef75/SEFAS.git
cd SEFAS

# Set up virtual environment  
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
make install

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Run your first experiment
python scripts/run_experiment.py "Analyze the benefits of renewable energy" --verbose
```

---

## 🏗️ Architecture

### Three-Layer Intelligence Stack

**🎯 Layer 1: Strategic Command**
- **Orchestrator** - Central coordination and task decomposition
- **Task Decomposer** - Breaks complex problems into atomic claims
- **Strategy Evolver** - Optimizes agent performance through evolution

**💡 Layer 2: Creative Generation**  
- **Proposer Alpha** - Creative, out-of-the-box solutions
- **Proposer Beta** - Practical, implementation-focused approaches
- **Proposer Gamma** - Alternative perspectives and analysis

**✅ Layer 3: Quality Assurance**
- **Checker Logic** - Mathematical and logical consistency
- **Checker Semantic** - Meaning and context accuracy  
- **Checker Consistency** - Cross-claim coherence analysis

---

## 💫 Usage Examples

### Basic Usage

```bash
# Simple analysis
python scripts/run_experiment.py "What are the implications of quantum computing?"

# Complex problem solving  
python scripts/run_experiment.py "Design a sustainable transportation system" --verbose

# Creative tasks
python scripts/run_experiment.py "How might we solve the global water crisis?" --max-hops 15
```

---

### Advanced Features

```bash
# With comprehensive monitoring
python scripts/run_experiment.py "Analyze ethical implications of AGI" --verbose

# Batch processing
python scripts/run_experiment.py batch tasks.json --output-dir results/

# System testing
python test_agents.py
```

---

## 📊 What You Get

- **🎯 Multi-perspective Analysis** - Each proposer brings unique viewpoints
- **✅ Rigorous Validation** - Triple-checked through logic, semantics, consistency
- **📈 Performance Metrics** - Token usage, timing, and cost analysis
- **🧬 Evolution Insights** - How agents improve over time
- **📄 Comprehensive Reports** - JSON exports for further analysis

---

## 🔍 LangSmith Integration

Professional monitoring and debugging:

```bash
# Update .env file:
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-langsmith-api-key
LANGSMITH_PROJECT=SEFAS-MultiAgent-System
```

**Capabilities:**
- 🔄 Agent interaction flows
- ⚡ Performance analytics  
- 🧬 Evolution tracking
- 🐛 Debug complex workflows
- 💰 Cost optimization

---

## 🛠️ Development

### Testing & Quality

```bash
make test                    # All tests
make test-unit              # Unit tests only
make test-integration       # Integration tests
python test_agents.py       # Full system validation
```

---

### Code Quality

```bash
make lint                   # ruff + mypy
make format                 # ruff format + black
make clean                  # Remove cache files
```

---

### Development Workflow

```bash
# Run with debugging
python scripts/run_experiment.py "test task" --verbose

# Check logs
tail -f logs/sefas.log      # System events
tail -f logs/agents.log     # Agent executions

# View reports  
ls data/reports/            # Saved analysis reports
```

---

## 🌟 Why SEFAS?

### Next-Generation AI Architecture

SEFAS represents the future of artificial intelligence by combining:

- 🧬 **Evolutionary adaptation** that makes agents smarter over time
- 🌐 **Federated intelligence** that mirrors human collaboration
- 📊 **Enterprise monitoring** for production deployments
- 🔧 **Extensible design** for custom development

---

### Perfect For

- 🔬 **Research Teams** - Exploring multi-agent AI and emergence
- 🏢 **Enterprises** - Complex problem-solving workflows  
- 🎓 **Educators** - Teaching advanced AI concepts
- 💻 **Developers** - Building sophisticated AI applications

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/keef75/SEFAS/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/keef75/SEFAS/discussions)  
- 📧 **Contact**: Open an issue for questions or collaboration

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**⚡ SEFAS - Where AI Agents Evolve Together ⚡**

*Built with ❤️ by the K3ith.AI and Cocoa AI research*

[![Star this repo](https://img.shields.io/github/stars/keef75/SEFAS?style=social)](https://github.com/keef75/SEFAS)

</div>
