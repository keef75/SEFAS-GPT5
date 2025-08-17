#!/usr/bin/env python
"""
Main CLI for running SEFAS experiments
"""

import sys
from pathlib import Path
from sefas.core.belief_propagation import BeliefPropagationEngine
from sefas.core.validation import ValidatorPool
from sefas.core.redundancy import RedundancyOrchestrator


# Ensure repository root is on sys.path for absolute imports like `config.*`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer
import asyncio
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional

from sefas.workflows.executor import FederatedSystemRunner
from sefas.monitoring.execution_reporter import execution_reporter
from sefas.reporting.report_synthesizer import ReportSynthesizer

# Allow calling as: `python scripts/run_experiment.py "task..."` (insert default command)
KNOWN_COMMANDS = {"run", "batch", "analyze", "--help", "-h"}
if len(sys.argv) >= 2 and sys.argv[1] not in KNOWN_COMMANDS:
    sys.argv.insert(1, "run")

app = typer.Typer()
console = Console()

@app.command()
def run(
    task: str = typer.Argument("Demo task: summarize the benefits of renewable energy.", help="Task to execute"),
    max_hops: int = typer.Option(10, help="Maximum hops allowed"),
    experiment_name: Optional[str] = typer.Option(None, help="Experiment name for tracking"),
    verbose: bool = typer.Option(False, help="Verbose output")
):
    """Run a single task through the SEFAS system"""
    
    console.print(f"[bold green]Starting SEFAS experiment[/bold green]")
    console.print(f"Task: {task}")
    
    # Initialize runner
    runner = FederatedSystemRunner(max_hops=max_hops)
    
    # Run task
    result = asyncio.run(runner.run(task))
    
    # Display comprehensive synthesis report
    if 'synthesis' in result and result['synthesis']:
        synthesis = result['synthesis']
        console.print("\n[bold blue]📊 SEFAS Comprehensive Analysis Report[/bold blue]")
        console.print("=" * 60)
        
        # Executive Summary
        console.print("\n[bold]📋 Executive Summary:[/bold]")
        exec_summary = synthesis.get('executive_summary', 'No summary available')
        console.print(f"[italic]{exec_summary}[/italic]")
        
        # Key Metrics
        console.print("\n[bold]🎯 Key Performance Metrics:[/bold]")
        metrics_table = Table(title="System Performance")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="magenta")
        
        performance = synthesis.get('performance', {})
        consensus = synthesis.get('consensus', {})
        proposals = synthesis.get('proposals', {})
        verification = synthesis.get('verification', {})
        evolution = synthesis.get('evolution', {})
        
        metrics_table.add_row("Task ID", result['task_id'])
        metrics_table.add_row("Consensus Reached", "✅ Yes" if consensus.get('consensus_reached', False) else "❌ No")
        metrics_table.add_row("Mean Confidence", f"{consensus.get('mean_confidence', 0.0):.2%}")
        metrics_table.add_row("Total Proposals", str(proposals.get('total_proposals', 0)))
        metrics_table.add_row("Agents Evolved", str(len(evolution.get('evolved_agents', []))))
        metrics_table.add_row("Execution Time", f"{performance.get('total_execution_time', 0.0):.2f}s")
        metrics_table.add_row("Total Tokens", f"{performance.get('total_tokens_used', 0):,}")
        metrics_table.add_row("Estimated Cost", f"${performance.get('estimated_cost_usd', 0.0):.4f}")
        
        console.print(metrics_table)
        
        # Direct User-Friendly Answer Display - Using Available Synthesis Data
        from rich.panel import Panel
        
        # Get data that's already available in synthesis
        executive_summary = synthesis.get('executive_summary', 'Analysis completed successfully.')
        recommendations = synthesis.get('recommendations', [])
        mean_confidence = consensus.get('mean_confidence', 0.0)
        consensus_reached = consensus.get('consensus_reached', False)
        
        # Style the confidence level
        if mean_confidence > 0.8:
            confidence_style = "bold green"
            confidence_emoji = "✨"
        elif mean_confidence > 0.6:
            confidence_style = "bold yellow"
            confidence_emoji = "⚡"
        else:
            confidence_style = "bold red"
            confidence_emoji = "⚠️"
        
        # Format top recommendations
        top_recommendations = []
        for i, rec in enumerate(recommendations[:3], 1):
            rec_text = rec.get('recommendation', 'No recommendation text')
            top_recommendations.append(f"  {i}. {rec_text}")
        
        recommendations_text = "\n".join(top_recommendations) if top_recommendations else "  • No specific recommendations available"
        
        # Create the answer content using available data
        answer_content = f"""🎯 **ANSWER TO YOUR QUESTION**

❓ **Question:** {task}

💡 **Analysis Summary:**
{executive_summary}

📊 **System Confidence:** {mean_confidence:.1%}

💫 **Key Recommendations:**
{recommendations_text}

✅ **Consensus Status:** {'Reached - High agreement among agents' if consensus_reached else 'Partial - Agents still analyzing'}

🤖 **Agent Network:** {len(synthesis.get('agent_contributions', {}))} specialized agents analyzed this request"""
        
        # Create prominent answer panel
        answer_panel = Panel(
            answer_content,
            title=f"[bold blue]🎯 DIRECT ANSWER TO YOUR QUESTION[/bold blue]",
            subtitle=f"[{confidence_style}]{confidence_emoji} {mean_confidence:.1%} Confidence[/{confidence_style}]",
            border_style="blue",
            padding=(1, 2),
            expand=False
        )
        
        console.print("\n")
        console.print(answer_panel)
        console.print("\n")
        
        # Agent Contributions
        agent_contributions = synthesis.get('agent_contributions', {})
        if agent_contributions:
            console.print("\n[bold]🤖 Agent Contributions:[/bold]")
            agent_table = Table(title="Individual Agent Performance")
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Role", style="yellow")
            agent_table.add_column("Confidence", style="green")
            agent_table.add_column("Time (s)", style="blue")
            agent_table.add_column("Tokens", style="magenta")
            agent_table.add_column("Fitness", style="red")
            
            for agent_id, contrib in list(agent_contributions.items())[:8]:  # Limit to 8 agents for display
                agent_table.add_row(
                    agent_id[:15] + "..." if len(agent_id) > 15 else agent_id,
                    contrib['role'][:12] + "..." if len(contrib['role']) > 12 else contrib['role'],
                    f"{contrib['confidence']:.1%}",
                    f"{contrib['execution_time']:.2f}",
                    str(contrib['tokens_used']),
                    f"{contrib['fitness_score']:.1%}"
                )
            
            console.print(agent_table)
        
        # Top Recommendations
        recommendations = synthesis.get('recommendations', [])
        if recommendations:
            console.print("\n[bold]💡 Top Recommendations:[/bold]")
            for i, rec in enumerate(recommendations[:5], 1):
                source = rec.get('source', 'Unknown')
                confidence = rec.get('confidence', 0.0)
                recommendation = rec.get('recommendation', '')
                console.print(f"  {i}. [bold]{source}[/bold] ({confidence:.1%}): {recommendation}")
        
        # Critical Issues
        critical_issues = verification.get('critical_issues', [])
        if critical_issues:
            console.print("\n[bold red]⚠️ Critical Issues Identified:[/bold red]")
            for issue in critical_issues[:3]:  # Show top 3 critical issues
                checker = issue.get('checker', 'Unknown')
                issue_text = issue.get('issue', '')
                console.print(f"  • [bold]{checker}[/bold]: {issue_text}")
        
        # Report Files
        if 'reports' in result and result['reports']:
            console.print("\n[bold]📄 Generated Reports:[/bold]")
            for format_type, filepath in result['reports'].items():
                console.print(f"  • {format_type.upper()}: {filepath}")
            
            # Generate GPT-5 executive synthesis (independent of core system)
            try:
                console.print("\n[bold]🧠 Generating GPT-5 Executive Synthesis...[/bold]")
                
                # Import and run independent GPT-5 synthesis agent
                import subprocess
                import sys
                
                # Get the actual task ID from current run (not from filename)
                task_id = result.get('task_id')
                if task_id:
                        # Run independent GPT-5 synthesis agent
                        synthesis_cmd = [
                            sys.executable, 
                            "scripts/gpt5_synthesis_agent.py", 
                            "--auto", 
                            task_id
                        ]
                        
                        # Execute synthesis in subprocess to avoid module conflicts
                        result_synthesis = subprocess.run(
                            synthesis_cmd, 
                            capture_output=True, 
                            text=True, 
                            cwd=str(Path.cwd())  # Convert Path to string
                        )
                        
                        if result_synthesis.returncode == 0:
                            console.print("✅ [green]GPT-5 Executive Synthesis completed successfully[/green]")
                            console.print(f"📋 [cyan]Analyzed current experiment: {task_id}[/cyan]")
                            
                            # Also display the GPT-5 analysis in Rich UI
                            try:
                                # Subprocess.run() is synchronous, so GPT-5 has completed, but give filesystem a moment to flush
                                import time
                                
                                reports_dir = Path("data/reports")
                                start_time = time.time()
                                recent_gpt5_files = []
                                
                                # Poll for the file for up to 5 seconds (should be immediate, but be safe)
                                for attempt in range(10):  # 10 attempts over 5 seconds
                                    current_time = time.time()
                                    
                                    # Find GPT-5 files created in the last 60 seconds (should be from this run)
                                    recent_gpt5_files = [
                                        f for f in reports_dir.glob("gpt5_executive_report_*.txt")
                                        if (current_time - f.stat().st_mtime) < 60  # Extended to 60 seconds for safety
                                    ]
                                    
                                    if recent_gpt5_files:
                                        break
                                    
                                    time.sleep(0.5)  # Wait 0.5 seconds between attempts
                                
                                if recent_gpt5_files:
                                    # Get the most recent one from this run
                                    latest_file = max(recent_gpt5_files, key=lambda f: f.stat().st_mtime)
                                    console.print(f"📄 [green]Found current run report: {latest_file.name}[/green]")
                                    
                                    # Read and display the GPT-5 analysis
                                    gpt5_content = latest_file.read_text(encoding='utf-8')
                                    
                                    # Create Rich Panel with GPT-5 content
                                    from rich.panel import Panel
                                    from rich.markdown import Markdown
                                    
                                    gpt5_panel = Panel(
                                        Markdown(gpt5_content),
                                        title="[bold green]🧠 GPT-5 EXECUTIVE ANALYSIS[/bold green]",
                                        subtitle="[bold cyan]Independent Executive Assessment[/bold cyan]",
                                        border_style="green",
                                        padding=(1, 2),
                                        expand=True
                                    )
                                    
                                    console.print("\n")
                                    console.print(gpt5_panel)
                                    console.print("\n")
                                else:
                                    # Check if any GPT-5 files exist at all
                                    all_gpt5_files = list(reports_dir.glob("gpt5_executive_report_*.txt"))
                                    if all_gpt5_files:
                                        latest_any = max(all_gpt5_files, key=lambda f: f.stat().st_mtime)
                                        age_seconds = current_time - latest_any.stat().st_mtime
                                        console.print(f"⚠️ [yellow]No recent GPT-5 report found after polling for 5 seconds[/yellow]")
                                        console.print(f"📝 [dim]Latest report is {age_seconds:.1f} seconds old: {latest_any.name}[/dim]")
                                        console.print(f"🔍 [dim]Checked {len(all_gpt5_files)} existing files[/dim]")
                                    else:
                                        console.print("⚠️ [yellow]No GPT-5 reports found in reports directory[/yellow]")
                            except Exception as e:
                                console.print(f"⚠️ [yellow]Could not display GPT-5 analysis: {e}[/yellow]")
                        else:
                            console.print(f"⚠️ [yellow]GPT-5 synthesis failed: {result_synthesis.stderr[:200]}[/yellow]")
                            if result_synthesis.stdout:
                                console.print(f"📝 Output: {result_synthesis.stdout[:300]}")
                else:
                    console.print("⚠️ [yellow]No task ID available for synthesis[/yellow]")
                    
            except Exception as e:
                console.print(f"\n⚠️ [yellow]Could not generate GPT-5 synthesis: {str(e)}[/yellow]")
            
            # Auto-open HTML report in browser if available
            if 'html' in result['reports'] and not verbose:
                html_path = result['reports']['html']
                try:
                    webbrowser.open(f"file://{Path(html_path).absolute()}")
                    console.print(f"\n🌐 [bold green]HTML report opened in browser![/bold green]")
                except Exception:
                    console.print(f"\n💻 [yellow]Manual open: file://{Path(html_path).absolute()}[/yellow]")
    
    # Fallback to original execution reporter if synthesis not available
    else:
        console.print("\n[bold yellow]📊 Generating Enhanced Execution Report...[/bold yellow]")
        
        # Display comprehensive report
        execution_reporter.display_execution_report(result)
        
        # Generate structured report data
        report_data = execution_reporter.generate_execution_report(result, save_to_file=True)
        
        # Show basic summary table for quick reference
        table = Table(title="📋 Quick Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Task ID", result['task_id'])
        table.add_row("Hops Taken", str(result['current_hop']))
        # Handle empty confidence scores gracefully
        confidence_scores = result.get('confidence_scores', {})
        if confidence_scores:
            max_confidence = max(confidence_scores.values())
        else:
            max_confidence = 0.0
        
        table.add_row("Final Confidence", f"{max_confidence:.2%}")
        table.add_row("Consensus Reached", "✅" if result['consensus'] else "❌")
        table.add_row("Total API Calls", str(len(result.get('proposals', [])) + len(result.get('verifications', []))))
        table.add_row("Execution Time", f"{result.get('execution_time', 0):.2f}s")
        table.add_row("Total Tokens", str(result.get('tokens_used', 0)))
        
        console.print(table)
    
    if verbose:
        console.print("\n[bold]🧬 Evolution Report:[/bold]")
        console.print(runner.get_evolution_report())
        
        # Show additional detailed analysis
        console.print("\n[bold]📈 System Performance Summary:[/bold]")
        from sefas.monitoring.metrics import performance_tracker
        summary = performance_tracker.get_system_summary()
        for key, value in summary.items():
            if isinstance(value, float):
                console.print(f"  {key}: {value:.3f}")
            else:
                console.print(f"  {key}: {value}")

@app.command()
def batch(
    tasks_file: Path = typer.Argument(..., help="JSON file with tasks"),
    output_dir: Path = typer.Option(Path("results"), help="Output directory")
):
    """Run batch experiments from a file"""
    # Implementation for batch processing
    pass

@app.command()
def analyze(
    experiment_dir: Path = typer.Argument(..., help="Directory with experiment results")
):
    """Analyze experiment results"""
    # Implementation for analysis
    pass

if __name__ == "__main__":
    app()