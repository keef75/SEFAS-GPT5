"""Enhanced execution reporting for SEFAS system."""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from config.settings import settings
from sefas.monitoring.metrics import performance_tracker


class ExecutionReporter:
    """Enhanced execution reporting with detailed analysis."""
    
    def __init__(self):
        self.console = Console()
        self.reports_dir = Path(settings.data_dir) / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_execution_report(self, execution_result: Dict[str, Any], 
                                save_to_file: bool = True) -> Dict[str, Any]:
        """Generate comprehensive execution report."""
        
        report_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "task_id": execution_result.get('task_id'),
                "system_version": "0.1.0",
                "report_type": "execution_analysis"
            },
            "execution_summary": self._analyze_execution_summary(execution_result),
            "agent_performance": self._analyze_agent_performance(execution_result),
            "token_analysis": self._analyze_token_usage(execution_result),
            "confidence_analysis": self._analyze_confidence_scores(execution_result),
            "timing_analysis": self._analyze_timing_performance(execution_result),
            "consensus_analysis": self._analyze_consensus(execution_result),
            "recommendations": self._generate_recommendations(execution_result)
        }
        
        if save_to_file:
            self._save_report(report_data)
        
        return report_data
    
    def display_execution_report(self, execution_result: Dict[str, Any]):
        """Display comprehensive execution report in terminal."""
        
        self.console.print("\n" + "="*80)
        self.console.print("[bold blue]🔍 SEFAS Execution Analysis Report[/bold blue]", justify="center")
        self.console.print("="*80)
        
        # Execution Summary
        self._display_execution_summary(execution_result)
        
        # Agent Performance Details
        self._display_agent_performance(execution_result)
        
        # API Call Details
        self._display_api_call_details(execution_result)
        
        # Confidence & Consensus Analysis
        self._display_confidence_analysis(execution_result)
        
        # Performance Metrics
        self._display_performance_metrics(execution_result)
        
        # System Recommendations
        self._display_recommendations(execution_result)
    
    def _analyze_execution_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall execution summary."""
        return {
            "task_id": result.get('task_id'),
            "status": "success" if result.get('consensus', False) else "failed",
            "total_hops": result.get('current_hop', 0),
            "execution_time": result.get('execution_time', 0),
            "total_tokens": result.get('tokens_used', 0),
            "final_confidence": result.get('confidence_scores', {}).get('mean_belief', 0.0),
            "consensus_reached": result.get('consensus', False),
            "error": result.get('error'),
            "error_type": result.get('error_type')
        }
    
    def _analyze_agent_performance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual agent performance."""
        proposals = result.get('proposals', [])
        verifications = result.get('verifications', [])
        
        agent_stats = {}
        
        # Analyze proposer performance
        for proposal in proposals:
            agent_id = proposal.get('agent_id', 'unknown')
            agent_stats[agent_id] = {
                "role": "proposer",
                "execution_time": proposal.get('execution_time', 0),
                "tokens_used": proposal.get('tokens_used', 0),
                "confidence": proposal.get('confidence', 0),
                "success": proposal.get('success', False),
                "content_length": len(str(proposal.get('response', ''))),
                "hop_number": proposal.get('hop_number', 0)
            }
        
        # Analyze checker performance
        for verification in verifications:
            agent_id = verification.get('agent_id', 'unknown')
            agent_stats[agent_id] = {
                "role": "checker",
                "execution_time": verification.get('execution_time', 0),
                "tokens_used": verification.get('tokens_used', 0),
                "confidence": verification.get('confidence', 0),
                "success": verification.get('success', False),
                "validation_result": verification.get('verification_result', 'unknown'),
                "hop_number": verification.get('hop_number', 0)
            }
        
        return agent_stats
    
    def _analyze_token_usage(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze token usage patterns."""
        proposals = result.get('proposals', [])
        verifications = result.get('verifications', [])
        
        total_tokens = result.get('tokens_used', 0)
        proposal_tokens = sum(p.get('tokens_used', 0) for p in proposals)
        verification_tokens = sum(v.get('tokens_used', 0) for v in verifications)
        
        return {
            "total_tokens": total_tokens,
            "proposal_tokens": proposal_tokens,
            "verification_tokens": verification_tokens,
            "average_tokens_per_agent": total_tokens / max(len(proposals) + len(verifications), 1),
            "token_efficiency": total_tokens / max(result.get('execution_time', 1), 0.1),  # tokens per second
            "cost_estimate_usd": self._estimate_cost(total_tokens)
        }
    
    def _analyze_confidence_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze confidence score patterns."""
        confidence_scores = result.get('confidence_scores', {})
        consensus_summary = result.get('consensus_summary', {})
        
        return {
            "confidence_scores": confidence_scores,
            "mean_confidence": consensus_summary.get('mean_belief', 0.0),
            "confidence_variance": consensus_summary.get('variance', 0.0),
            "consensus_status": consensus_summary.get('status', 'no_consensus'),
            "confidence_threshold": settings.confidence_threshold,
            "threshold_met": consensus_summary.get('mean_belief', 0.0) >= settings.confidence_threshold
        }
    
    def _analyze_timing_performance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze timing performance."""
        execution_time = result.get('execution_time', 0)
        proposals = result.get('proposals', [])
        verifications = result.get('verifications', [])
        
        proposal_times = [p.get('execution_time', 0) for p in proposals]
        verification_times = [v.get('execution_time', 0) for v in verifications]
        
        return {
            "total_execution_time": execution_time,
            "average_proposal_time": sum(proposal_times) / max(len(proposal_times), 1),
            "average_verification_time": sum(verification_times) / max(len(verification_times), 1),
            "longest_operation": max(proposal_times + verification_times) if (proposal_times + verification_times) else 0,
            "performance_rating": self._calculate_performance_rating(execution_time, len(proposals) + len(verifications))
        }
    
    def _analyze_consensus(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consensus achievement."""
        consensus_summary = result.get('consensus_summary', {})
        
        return {
            "consensus_achieved": result.get('consensus', False),
            "consensus_strength": consensus_summary.get('status', 'no_consensus'),
            "agreement_level": consensus_summary.get('mean_belief', 0.0),
            "agent_agreement": self._calculate_agent_agreement(result),
            "convergence_analysis": self._analyze_convergence(result)
        }
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Performance recommendations
        execution_time = result.get('execution_time', 0)
        if execution_time > 60:  # More than 1 minute
            recommendations.append("⚡ Consider optimizing agent response times - execution took over 1 minute")
        
        # Token usage recommendations
        total_tokens = result.get('tokens_used', 0)
        if total_tokens > 10000:
            recommendations.append("💰 High token usage detected - consider implementing response length limits")
        
        # Confidence recommendations
        consensus_summary = result.get('consensus_summary', {})
        mean_confidence = consensus_summary.get('mean_belief', 0.0)
        if mean_confidence < settings.confidence_threshold:
            recommendations.append(f"🎯 Low confidence ({mean_confidence:.2%}) - consider adding more checker agents or improving prompts")
        
        # Error handling recommendations
        if result.get('error'):
            recommendations.append("🔧 System error detected - check logs for debugging information")
        
        # Success recommendations
        if result.get('consensus', False) and mean_confidence > 0.8:
            recommendations.append("✨ Excellent performance! System achieved high confidence consensus")
        
        return recommendations
    
    def _display_execution_summary(self, result: Dict[str, Any]):
        """Display execution summary table."""
        table = Table(title="📊 Execution Summary", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # Status
        status = "✅ Success" if result.get('consensus', False) else "❌ Failed"
        if result.get('error'):
            status = f"🚨 Error: {result.get('error_type', 'Unknown')}"
        
        table.add_row("Task ID", str(result.get('task_id', 'Unknown'))[:36], "")
        table.add_row("Status", status, "")
        table.add_row("Execution Time", f"{result.get('execution_time', 0):.2f}s", "")
        table.add_row("Total Tokens", str(result.get('tokens_used', 0)), "")
        table.add_row("API Calls", str(len(result.get('proposals', [])) + len(result.get('verifications', []))), "")
        table.add_row("Final Confidence", f"{result.get('confidence_scores', {}).get('mean_belief', 0.0):.1%}", "")
        table.add_row("Consensus", "✅" if result.get('consensus', False) else "❌", "")
        
        self.console.print(table)
    
    def _display_agent_performance(self, result: Dict[str, Any]):
        """Display detailed agent performance."""
        proposals = result.get('proposals', [])
        verifications = result.get('verifications', [])
        
        if not proposals and not verifications:
            return
        
        table = Table(title="🤖 Agent Performance Details", show_header=True, header_style="bold magenta")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Role", style="blue")
        table.add_column("Time (s)", style="green")
        table.add_column("Tokens", style="yellow")
        table.add_column("Confidence", style="red")
        table.add_column("Status", style="white")
        
        # Add proposer data
        for proposal in proposals:
            agent_id = proposal.get('agent_id', 'unknown')
            execution_time = proposal.get('execution_time', 0)
            tokens = proposal.get('tokens_used', 0)
            confidence = proposal.get('confidence', 0)
            success = "✅" if proposal.get('success', False) else "❌"
            
            table.add_row(
                agent_id,
                "Proposer",
                f"{execution_time:.2f}",
                str(tokens),
                f"{confidence:.1%}",
                success
            )
        
        # Add verification data
        for verification in verifications:
            agent_id = verification.get('agent_id', 'unknown')
            execution_time = verification.get('execution_time', 0)
            tokens = verification.get('tokens_used', 0)
            confidence = verification.get('confidence', 0)
            success = "✅" if verification.get('success', False) else "❌"
            
            table.add_row(
                agent_id,
                "Checker",
                f"{execution_time:.2f}",
                str(tokens),
                f"{confidence:.1%}",
                success
            )
        
        self.console.print(table)
    
    def _display_api_call_details(self, result: Dict[str, Any]):
        """Display API call timeline and details."""
        proposals = result.get('proposals', [])
        verifications = result.get('verifications', [])
        
        if not proposals and not verifications:
            return
        
        tree = Tree("🌐 API Call Timeline")
        
        # Group by hop number
        all_calls = []
        for proposal in proposals:
            all_calls.append(('proposal', proposal))
        for verification in verifications:
            all_calls.append(('verification', verification))
        
        # Sort by execution order (hop number, then timestamp)
        all_calls.sort(key=lambda x: (x[1].get('hop_number', 0), x[1].get('execution_time', 0)))
        
        current_hop = None
        hop_branch = None
        
        for call_type, call_data in all_calls:
            hop_number = call_data.get('hop_number', 0)
            
            if hop_number != current_hop:
                current_hop = hop_number
                hop_branch = tree.add(f"Hop {hop_number}")
            
            agent_id = call_data.get('agent_id', 'unknown')
            execution_time = call_data.get('execution_time', 0)
            tokens = call_data.get('tokens_used', 0)
            success = "✅" if call_data.get('success', False) else "❌"
            
            call_info = f"{success} {agent_id} ({call_type}) - {execution_time:.2f}s, {tokens} tokens"
            if hop_branch:
                hop_branch.add(call_info)
        
        self.console.print(tree)
    
    def _display_confidence_analysis(self, result: Dict[str, Any]):
        """Display confidence and consensus analysis."""
        confidence_scores = result.get('confidence_scores', {})
        consensus_summary = result.get('consensus_summary', {})
        
        panel_content = []
        
        # Confidence scores
        if confidence_scores:
            panel_content.append("[bold]Confidence Scores:[/bold]")
            for claim, confidence in confidence_scores.items():
                panel_content.append(f"  • {claim}: {confidence:.1%}")
        
        # Consensus summary
        mean_confidence = consensus_summary.get('mean_belief', 0.0)
        consensus_status = consensus_summary.get('status', 'no_consensus')
        threshold_met = mean_confidence >= settings.confidence_threshold
        
        panel_content.append(f"\n[bold]Consensus Analysis:[/bold]")
        panel_content.append(f"  • Mean Confidence: {mean_confidence:.1%}")
        panel_content.append(f"  • Status: {consensus_status}")
        panel_content.append(f"  • Threshold ({settings.confidence_threshold:.0%}): {'✅ Met' if threshold_met else '❌ Not Met'}")
        
        panel = Panel(
            "\n".join(panel_content),
            title="🎯 Confidence & Consensus Analysis",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _display_performance_metrics(self, result: Dict[str, Any]):
        """Display performance metrics."""
        execution_time = result.get('execution_time', 0)
        total_tokens = result.get('tokens_used', 0)
        api_calls = len(result.get('proposals', [])) + len(result.get('verifications', []))
        
        metrics_content = [
            f"[bold]Performance Metrics:[/bold]",
            f"  • Total Execution Time: {execution_time:.2f}s",
            f"  • Total API Calls: {api_calls}",
            f"  • Average Time per Call: {execution_time/max(api_calls, 1):.2f}s",
            f"  • Total Tokens Used: {total_tokens:,}",
            f"  • Tokens per Second: {total_tokens/max(execution_time, 0.1):.0f}",
            f"  • Estimated Cost: ${self._estimate_cost(total_tokens):.4f}"
        ]
        
        panel = Panel(
            "\n".join(metrics_content),
            title="⚡ Performance Metrics",
            border_style="green"
        )
        self.console.print(panel)
    
    def _display_recommendations(self, result: Dict[str, Any]):
        """Display system recommendations."""
        recommendations = self._generate_recommendations(result)
        
        if recommendations:
            recs_content = "\n".join(f"  {rec}" for rec in recommendations)
            panel = Panel(
                recs_content,
                title="💡 System Recommendations",
                border_style="yellow"
            )
            self.console.print(panel)
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate API cost based on tokens."""
        # GPT-4o-mini pricing (approximate)
        input_cost_per_1k = 0.00015  # $0.15 per 1K input tokens
        output_cost_per_1k = 0.00060  # $0.60 per 1K output tokens
        
        # Assume 70% input, 30% output
        input_tokens = tokens * 0.7
        output_tokens = tokens * 0.3
        
        cost = (input_tokens / 1000 * input_cost_per_1k) + (output_tokens / 1000 * output_cost_per_1k)
        return cost
    
    def _calculate_performance_rating(self, execution_time: float, agent_count: int) -> str:
        """Calculate performance rating."""
        expected_time = agent_count * 2  # 2 seconds per agent
        
        if execution_time <= expected_time * 0.5:
            return "Excellent"
        elif execution_time <= expected_time:
            return "Good"
        elif execution_time <= expected_time * 1.5:
            return "Average"
        else:
            return "Needs Improvement"
    
    def _calculate_agent_agreement(self, result: Dict[str, Any]) -> float:
        """Calculate level of agreement between agents."""
        confidence_scores = result.get('confidence_scores', {})
        if not confidence_scores:
            return 0.0
        
        values = list(confidence_scores.values())
        if len(values) <= 1:
            return 1.0
        
        # Calculate coefficient of variation (lower = more agreement)
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        cv = (variance ** 0.5) / mean_val if mean_val > 0 else 1.0
        
        # Convert to agreement score (1 = perfect agreement, 0 = no agreement)
        return max(0.0, 1.0 - cv)
    
    def _analyze_convergence(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the system converged to consensus."""
        confidence_scores = result.get('confidence_scores', {})
        consensus_summary = result.get('consensus_summary', {})
        
        return {
            "convergence_quality": self._calculate_agent_agreement(result),
            "consensus_strength": consensus_summary.get('status', 'no_consensus'),
            "belief_variance": consensus_summary.get('variance', 0.0),
            "stability": "stable" if consensus_summary.get('variance', 1.0) < 0.1 else "unstable"
        }
    
    def _save_report(self, report_data: Dict[str, Any]):
        """Save report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = report_data['metadata']['task_id']
        filename = f"execution_report_{task_id}_{timestamp}.json"
        
        filepath = self.reports_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.console.print(f"\n📄 Report saved: {filepath}")


# Global reporter instance
execution_reporter = ExecutionReporter()