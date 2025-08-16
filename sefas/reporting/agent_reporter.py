"""
Agent Report Module

Individual agent report structure and formatting for SEFAS multi-agent system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class AgentReport:
    """Individual agent report structure"""
    agent_id: str
    agent_role: str
    timestamp: datetime
    task: str
    
    # Core content
    input_received: Dict[str, Any]
    reasoning_process: List[str]
    output_generated: Dict[str, Any]
    confidence_score: float
    
    # Metadata
    tokens_used: int
    execution_time: float
    memory_accessed: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    
    # Evolution tracking
    prompt_version: int = 1
    mutations_applied: List[str] = field(default_factory=list)
    fitness_score: float = 0.5
    
    # Verification results (for checkers)
    verification_results: Optional[Dict[str, Any]] = None
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Generate markdown report"""
        report = f"""
# Agent Report: {self.agent_id}
**Role**: {self.agent_role}  
**Timestamp**: {self.timestamp.isoformat()}  
**Task**: {self.task}

## 📥 Input Analysis
```json
{json.dumps(self.input_received, indent=2)}
```

## 🧠 Reasoning Process
{self._format_reasoning()}

## 📤 Output Generated
**Confidence Score**: {self.confidence_score:.2%}

```json
{json.dumps(self.output_generated, indent=2)}
```

## 📊 Performance Metrics
- **Tokens Used**: {self.tokens_used:,}
- **Execution Time**: {self.execution_time:.2f}s
- **Prompt Version**: v{self.prompt_version}
- **Fitness Score**: {self.fitness_score:.2%}

## 🔍 Verification Results
{self._format_verification()}

## 💡 Recommendations
{self._format_recommendations()}

## 🧬 Evolution Status
- **Mutations Applied**: {', '.join(self.mutations_applied) or 'None'}
- **Memory Accesses**: {len(self.memory_accessed)}
- **Tools Used**: {', '.join(self.tools_used) or 'None'}
"""
        return report
    
    def _format_reasoning(self) -> str:
        """Format reasoning steps"""
        if not self.reasoning_process:
            return "*No detailed reasoning recorded*"
        
        formatted = []
        for i, step in enumerate(self.reasoning_process, 1):
            formatted.append(f"{i}. {step}")
        return "\n".join(formatted)
    
    def _format_verification(self) -> str:
        """Format verification results for checker agents"""
        if not self.verification_results:
            return "*N/A - Not a verification agent*"
        
        results = []
        for check, result in self.verification_results.items():
            status = "✅" if result.get('passed', False) else "❌"
            results.append(f"- {status} **{check}**: {result.get('details', 'No details')}")
        
        if self.issues_found:
            results.append("\n**Issues Identified:**")
            for issue in self.issues_found:
                results.append(f"- ⚠️ {issue}")
        
        return "\n".join(results)
    
    def _format_recommendations(self) -> str:
        """Format recommendations"""
        if not self.recommendations:
            return "*No specific recommendations*"
        
        return "\n".join([f"- {rec}" for rec in self.recommendations])
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return {
            "agent_id": self.agent_id,
            "agent_role": self.agent_role,
            "timestamp": self.timestamp.isoformat(),
            "task": self.task,
            "input_received": self.input_received,
            "reasoning_process": self.reasoning_process,
            "output_generated": self.output_generated,
            "confidence_score": self.confidence_score,
            "tokens_used": self.tokens_used,
            "execution_time": self.execution_time,
            "memory_accessed": self.memory_accessed,
            "tools_used": self.tools_used,
            "prompt_version": self.prompt_version,
            "mutations_applied": self.mutations_applied,
            "fitness_score": self.fitness_score,
            "verification_results": self.verification_results,
            "issues_found": self.issues_found,
            "recommendations": self.recommendations
        }
    
    def save(self, output_dir: Path = Path("data/reports/agents")) -> Path:
        """Save individual agent report to file"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.agent_id}_{timestamp}.md"
        filepath = output_dir / filename
        
        filepath.write_text(self.to_markdown())
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """Get concise summary for aggregation"""
        return {
            "agent_id": self.agent_id,
            "agent_role": self.agent_role,
            "confidence": self.confidence_score,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "fitness_score": self.fitness_score,
            "issues_count": len(self.issues_found),
            "recommendations_count": len(self.recommendations),
            "memory_usage": len(self.memory_accessed),
            "tools_usage": len(self.tools_used),
            "prompt_version": self.prompt_version,
            "mutations_count": len(self.mutations_applied)
        }