"""Performance tracking and metrics collection for SEFAS."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import numpy as np
import json

@dataclass
class FitnessMetrics:
    """Agent fitness and performance metrics."""
    agent_id: str
    current_fitness: float
    fitness_history: List[float] = field(default_factory=list)
    execution_times: List[float] = field(default_factory=list)
    token_usage: List[int] = field(default_factory=list)
    success_rate: float = 0.0
    total_executions: int = 0
    successful_executions: int = 0
    evolution_count: int = 0
    last_evolution: Optional[datetime] = None
    
    def update_fitness(self, new_fitness: float) -> None:
        """Update fitness score and maintain history."""
        self.current_fitness = new_fitness
        self.fitness_history.append(new_fitness)
        
        # Keep only last 100 entries
        if len(self.fitness_history) > 100:
            self.fitness_history = self.fitness_history[-100:]
    
    def record_execution(self, execution_time: float, tokens: int, success: bool) -> None:
        """Record execution metrics."""
        self.execution_times.append(execution_time)
        self.token_usage.append(tokens)
        self.total_executions += 1
        
        if success:
            self.successful_executions += 1
        
        self.success_rate = self.successful_executions / self.total_executions
        
        # Keep only last 100 entries
        if len(self.execution_times) > 100:
            self.execution_times = self.execution_times[-100:]
        if len(self.token_usage) > 100:
            self.token_usage = self.token_usage[-100:]
    
    def record_evolution(self) -> None:
        """Record an evolution event."""
        self.evolution_count += 1
        self.last_evolution = datetime.now()
    
    def get_avg_execution_time(self) -> float:
        """Get average execution time."""
        return statistics.mean(self.execution_times) if self.execution_times else 0.0
    
    def get_avg_token_usage(self) -> float:
        """Get average token usage."""
        return statistics.mean(self.token_usage) if self.token_usage else 0.0
    
    def get_fitness_trend(self) -> str:
        """Get fitness trend (improving, declining, stable)."""
        if len(self.fitness_history) < 2:
            return "insufficient_data"
        
        recent = self.fitness_history[-5:]  # Last 5 measurements
        if len(recent) < 2:
            return "insufficient_data"
        
        # Compute linear trend using numpy to avoid Python version differences
        x = np.arange(len(recent))
        slope, intercept = np.polyfit(x, np.array(recent, dtype=float), 1)
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "current_fitness": self.current_fitness,
            "avg_execution_time": self.get_avg_execution_time(),
            "avg_token_usage": self.get_avg_token_usage(),
            "success_rate": self.success_rate,
            "total_executions": self.total_executions,
            "evolution_count": self.evolution_count,
            "fitness_trend": self.get_fitness_trend(),
            "last_evolution": self.last_evolution.isoformat() if self.last_evolution else None
        }

class PerformanceTracker:
    """Tracks system-wide performance metrics."""
    
    def __init__(self):
        self.agent_metrics: Dict[str, FitnessMetrics] = {}
        self.system_metrics: Dict[str, Any] = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "total_execution_time": 0.0,
            "total_tokens": 0,
            "total_hops": 0,
            "start_time": datetime.now()
        }
        self.task_history: List[Dict[str, Any]] = []
    
    def get_agent_metrics(self, agent_id: str) -> FitnessMetrics:
        """Get or create metrics for an agent."""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = FitnessMetrics(agent_id=agent_id)
        return self.agent_metrics[agent_id]
    
    def record_task_completion(
        self, 
        task_id: str, 
        success: bool, 
        execution_time: float, 
        tokens_used: int, 
        hops_used: int,
        confidence: float,
        agent_contributions: Dict[str, Any]
    ) -> None:
        """Record completion of a federated task."""
        self.system_metrics["total_tasks"] += 1
        if success:
            self.system_metrics["successful_tasks"] += 1
        
        self.system_metrics["total_execution_time"] += execution_time
        self.system_metrics["total_tokens"] += tokens_used
        self.system_metrics["total_hops"] += hops_used
        
        # Record task in history
        task_record = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "execution_time": execution_time,
            "tokens_used": tokens_used,
            "hops_used": hops_used,
            "confidence": confidence,
            "agent_contributions": agent_contributions
        }
        
        self.task_history.append(task_record)
        
        # Keep only last 1000 tasks
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
    
    def record_agent_execution(
        self, 
        agent_id: str, 
        execution_time: float, 
        tokens: int, 
        success: bool,
        fitness_score: Optional[float] = None
    ) -> None:
        """Record individual agent execution."""
        metrics = self.get_agent_metrics(agent_id)
        metrics.record_execution(execution_time, tokens, success)
        
        if fitness_score is not None:
            metrics.update_fitness(fitness_score)
    
    def record_agent_evolution(self, agent_id: str) -> None:
        """Record agent evolution event."""
        metrics = self.get_agent_metrics(agent_id)
        metrics.record_evolution()
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get system-wide performance summary."""
        uptime = datetime.now() - self.system_metrics["start_time"]
        
        summary = {
            "uptime_hours": uptime.total_seconds() / 3600,
            "total_tasks": self.system_metrics["total_tasks"],
            "success_rate": (
                self.system_metrics["successful_tasks"] / self.system_metrics["total_tasks"]
                if self.system_metrics["total_tasks"] > 0 else 0.0
            ),
            "avg_execution_time": (
                self.system_metrics["total_execution_time"] / self.system_metrics["total_tasks"]
                if self.system_metrics["total_tasks"] > 0 else 0.0
            ),
            "avg_tokens_per_task": (
                self.system_metrics["total_tokens"] / self.system_metrics["total_tasks"]
                if self.system_metrics["total_tasks"] > 0 else 0.0
            ),
            "avg_hops_per_task": (
                self.system_metrics["total_hops"] / self.system_metrics["total_tasks"]
                if self.system_metrics["total_tasks"] > 0 else 0.0
            ),
            "active_agents": len(self.agent_metrics),
            "total_evolutions": sum(m.evolution_count for m in self.agent_metrics.values())
        }
        
        return summary
    
    def get_agent_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents by fitness."""
        sorted_agents = sorted(
            self.agent_metrics.values(),
            key=lambda x: x.current_fitness,
            reverse=True
        )
        
        return [agent.to_dict() for agent in sorted_agents[:limit]]
    
    def get_recent_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for recent time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_tasks = [
            task for task in self.task_history
            if datetime.fromisoformat(task["timestamp"]) > cutoff
        ]
        
        if not recent_tasks:
            return {"message": f"No tasks in last {hours} hours"}
        
        total_tasks = len(recent_tasks)
        successful_tasks = sum(1 for task in recent_tasks if task["success"])
        total_time = sum(task["execution_time"] for task in recent_tasks)
        total_tokens = sum(task["tokens_used"] for task in recent_tasks)
        
        return {
            "time_period_hours": hours,
            "total_tasks": total_tasks,
            "success_rate": successful_tasks / total_tasks,
            "avg_execution_time": total_time / total_tasks,
            "avg_tokens": total_tokens / total_tasks,
            "throughput_tasks_per_hour": total_tasks / hours
        }
    
    def export_metrics(self, filepath: str) -> None:
        """Export all metrics to JSON file."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "system_summary": self.get_system_summary(),
            "agent_metrics": {
                agent_id: metrics.to_dict() 
                for agent_id, metrics in self.agent_metrics.items()
            },
            "recent_tasks": self.task_history[-100:]  # Last 100 tasks
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def get_evolution_insights(self) -> Dict[str, Any]:
        """Get insights about evolution effectiveness."""
        evolved_agents = [m for m in self.agent_metrics.values() if m.evolution_count > 0]
        non_evolved_agents = [m for m in self.agent_metrics.values() if m.evolution_count == 0]
        
        if not evolved_agents:
            return {"message": "No agents have evolved yet"}
        
        evolved_avg_fitness = statistics.mean(m.current_fitness for m in evolved_agents)
        non_evolved_avg_fitness = (
            statistics.mean(m.current_fitness for m in non_evolved_agents) 
            if non_evolved_agents else 0.0
        )
        
        return {
            "evolved_agents": len(evolved_agents),
            "non_evolved_agents": len(non_evolved_agents),
            "evolved_avg_fitness": evolved_avg_fitness,
            "non_evolved_avg_fitness": non_evolved_avg_fitness,
            "evolution_effectiveness": evolved_avg_fitness - non_evolved_avg_fitness,
            "total_evolutions": sum(m.evolution_count for m in evolved_agents),
            "most_evolved_agent": max(evolved_agents, key=lambda x: x.evolution_count).agent_id
        }

# Global performance tracker instance
performance_tracker = PerformanceTracker()