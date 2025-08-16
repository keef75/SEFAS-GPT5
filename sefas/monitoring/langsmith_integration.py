"""LangSmith integration for SEFAS monitoring and tracing."""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from dataclasses import dataclass

try:
    from langsmith import Client, traceable
    LANGSMITH_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency path
    LANGSMITH_AVAILABLE = False
    def traceable(func):
        return func  # No-op decorator if LangSmith not available

from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class AgentTrace:
    """Represents a trace for an individual agent interaction."""
    agent_id: str
    agent_role: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    tokens_used: int
    hop_number: int
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class FederatedTrace:
    """Represents a complete federated system execution trace."""
    task_id: str
    original_input: str
    final_output: str
    total_hops: int
    total_execution_time: float
    total_tokens_used: int
    agent_traces: List[AgentTrace]
    success: bool
    confidence_score: float
    metadata: Dict[str, Any] = None

class LangSmithMonitor:
    """Monitors SEFAS execution using LangSmith tracing."""
    
    def __init__(self):
        self.client = None
        self.enabled = False
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize LangSmith client if available and configured."""
        if not LANGSMITH_AVAILABLE:
            logger.warning("LangSmith not available. Install with: pip install langsmith")
            return
        
        if not settings.langsmith_tracing or not settings.langsmith_api_key:
            logger.info("LangSmith tracing disabled or not configured")
            return
        
        try:
            # Configure LangSmith environment
            settings.configure_langsmith()
            
            # Initialize client
            self.client = Client(
                api_url=settings.langsmith_endpoint,
                api_key=settings.langsmith_api_key
            )
            self.enabled = True
            logger.info(f"LangSmith monitoring initialized for project: {settings.langsmith_project}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangSmith client: {e}")
            self.enabled = False
    
    @traceable(name="agent_execution")
    def trace_agent_execution(self, agent_trace: AgentTrace) -> None:
        """Trace individual agent execution."""
        if not self.enabled:
            return
        
        try:
            # Create trace data for agent execution
            trace_data = {
                "agent_id": agent_trace.agent_id,
                "agent_role": agent_trace.agent_role,
                "hop_number": agent_trace.hop_number,
                "execution_time": agent_trace.execution_time,
                "tokens_used": agent_trace.tokens_used,
                "success": agent_trace.success,
                "input": agent_trace.input_data,
                "output": agent_trace.output_data,
                "metadata": agent_trace.metadata or {}
            }
            
            if agent_trace.error_message:
                trace_data["error"] = agent_trace.error_message
            
            logger.debug(f"Traced agent {agent_trace.agent_id} execution")
            
        except Exception as e:
            logger.error(f"Failed to trace agent execution: {e}")
    
    @traceable(name="federated_system_execution")
    def trace_federated_execution(self, federated_trace: FederatedTrace) -> None:
        """Trace complete federated system execution."""
        if not self.enabled:
            return
        
        try:
            # Create comprehensive trace for federated execution
            trace_data = {
                "task_id": federated_trace.task_id,
                "total_hops": federated_trace.total_hops,
                "total_execution_time": federated_trace.total_execution_time,
                "total_tokens_used": federated_trace.total_tokens_used,
                "confidence_score": federated_trace.confidence_score,
                "success": federated_trace.success,
                "agent_count": len(federated_trace.agent_traces),
                "input": federated_trace.original_input,
                "output": federated_trace.final_output,
                "metadata": federated_trace.metadata or {}
            }
            
            # Add agent performance summary
            agent_summary = {}
            for agent_trace in federated_trace.agent_traces:
                role = agent_trace.agent_role
                if role not in agent_summary:
                    agent_summary[role] = {
                        "executions": 0,
                        "total_time": 0,
                        "total_tokens": 0,
                        "success_rate": 0
                    }
                
                agent_summary[role]["executions"] += 1
                agent_summary[role]["total_time"] += agent_trace.execution_time
                agent_summary[role]["total_tokens"] += agent_trace.tokens_used
                if agent_trace.success:
                    agent_summary[role]["success_rate"] += 1
            
            # Calculate success rates
            for role_data in agent_summary.values():
                role_data["success_rate"] = role_data["success_rate"] / role_data["executions"]
                role_data["avg_time"] = role_data["total_time"] / role_data["executions"]
                role_data["avg_tokens"] = role_data["total_tokens"] / role_data["executions"]
            
            trace_data["agent_performance"] = agent_summary
            
            logger.info(f"Traced federated execution {federated_trace.task_id}")
            
        except Exception as e:
            logger.error(f"Failed to trace federated execution: {e}")
    
    def trace_evolution_event(self, agent_id: str, evolution_data: Dict[str, Any]) -> None:
        """Trace agent evolution events."""
        if not self.enabled:
            return
        
        try:
            @traceable(name="agent_evolution")
            def _trace_evolution():
                return {
                    "agent_id": agent_id,
                    "timestamp": datetime.now().isoformat(),
                    "evolution_data": evolution_data
                }
            
            _trace_evolution()
            logger.debug(f"Traced evolution event for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to trace evolution event: {e}")
    
    def trace_topology_change(self, topology_data: Dict[str, Any]) -> None:
        """Trace network topology changes."""
        if not self.enabled:
            return
        
        try:
            @traceable(name="topology_evolution")
            def _trace_topology():
                return {
                    "timestamp": datetime.now().isoformat(),
                    "topology_data": topology_data
                }
            
            _trace_topology()
            logger.debug("Traced topology change")
            
        except Exception as e:
            logger.error(f"Failed to trace topology change: {e}")
    
    def create_dataset(self, name: str, examples: List[Dict[str, Any]]) -> None:
        """Create a dataset in LangSmith for evaluation."""
        if not self.enabled:
            return
        
        try:
            dataset = self.client.create_dataset(
                dataset_name=name,
                description=f"SEFAS evaluation dataset: {name}"
            )
            
            for example in examples:
                self.client.create_example(
                    dataset_id=dataset.id,
                    inputs=example.get("inputs", {}),
                    outputs=example.get("outputs", {}),
                    metadata=example.get("metadata", {})
                )
            
            logger.info(f"Created dataset '{name}' with {len(examples)} examples")
            
        except Exception as e:
            logger.error(f"Failed to create dataset: {e}")
    
    def get_performance_metrics(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve performance metrics from LangSmith."""
        if not self.enabled:
            return {}
        
        try:
            project = project_name or settings.langsmith_project
            if not project:
                logger.warning("No project specified for metrics retrieval")
                return {}
            
            # Get runs for the project
            runs = list(self.client.list_runs(project_name=project, limit=100))
            
            if not runs:
                return {"message": "No runs found"}
            
            # Calculate aggregate metrics
            total_runs = len(runs)
            successful_runs = sum(1 for run in runs if not run.error)
            total_execution_time = sum(
                (run.end_time - run.start_time).total_seconds() 
                for run in runs if run.end_time and run.start_time
            )
            
            metrics = {
                "total_runs": total_runs,
                "success_rate": successful_runs / total_runs,
                "avg_execution_time": total_execution_time / total_runs if total_runs > 0 else 0,
                "project_name": project,
                "last_updated": datetime.now().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to retrieve performance metrics: {e}")
            return {"error": str(e)}

# Global monitor instance
langsmith_monitor = LangSmithMonitor()