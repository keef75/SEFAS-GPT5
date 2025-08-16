#!/usr/bin/env python
"""
Main CLI for running SEFAS experiments
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for absolute imports like `config.*`
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer
import asyncio
from rich.console import Console
from rich.table import Table
from typing import Optional

from sefas.workflows.executor import FederatedSystemRunner
from sefas.monitoring.execution_reporter import execution_reporter

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
    
    # Generate and display enhanced execution report
    console.print("\n[bold green]📊 Generating Enhanced Execution Report...[/bold green]")
    
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