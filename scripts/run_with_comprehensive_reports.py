#!/usr/bin/env python
"""
Enhanced SEFAS runner with comprehensive reporting demonstration
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import asyncio
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from sefas.workflows.executor import FederatedSystemRunner

console = Console()

async def run_with_comprehensive_reports(task: str = None):
    """Run SEFAS with comprehensive reporting demonstration"""
    
    # Use a compelling default task if none provided
    if not task:
        task = "Design a comprehensive solution for sustainable energy storage that addresses both environmental impact and economic viability for urban communities"
    
    console.print(Panel.fit(
        "[bold blue]🌐 SEFAS - Self-Evolving Federated Agent System[/bold blue]\n"
        "[italic]Comprehensive Multi-Agent Analysis with Full Reporting[/italic]",
        border_style="blue"
    ))
    
    console.print(f"\n[bold]📋 Task:[/bold] {task}")
    console.print("[dim]Initializing federated agent system...[/dim]")
    
    # Initialize runner
    runner = FederatedSystemRunner()
    
    # Run task with full reporting
    console.print("\n[bold green]🚀 Executing multi-agent analysis...[/bold green]")
    
    try:
        result = await runner.run(task)
        
        # Display comprehensive analysis
        if 'synthesis' in result and result['synthesis']:
            synthesis = result['synthesis']
            
            # Header
            console.print("\n" + "="*80)
            console.print("[bold blue]📊 COMPREHENSIVE SEFAS ANALYSIS COMPLETE[/bold blue]")
            console.print("="*80)
            
            # Executive Summary Panel
            exec_summary = synthesis.get('executive_summary', 'No summary available')
            console.print(Panel(
                exec_summary,
                title="📋 Executive Summary",
                border_style="green"
            ))
            
            # System Performance Overview
            performance = synthesis.get('performance', {})
            consensus = synthesis.get('consensus', {})
            
            overview_text = Text()
            overview_text.append("🎯 Consensus: ", style="bold")
            if consensus.get('consensus_reached', False):
                overview_text.append("✅ ACHIEVED", style="bold green")
            else:
                overview_text.append("🔄 PENDING", style="bold yellow")
            
            overview_text.append(f" ({consensus.get('mean_confidence', 0.0):.1%} confidence)\n", style="dim")
            overview_text.append("⚡ Performance: ", style="bold")
            overview_text.append(f"{performance.get('total_execution_time', 0.0):.1f}s", style="cyan")
            overview_text.append(" | ", style="dim")
            overview_text.append(f"{performance.get('total_tokens_used', 0):,} tokens", style="magenta")
            overview_text.append(" | ", style="dim")
            overview_text.append(f"${performance.get('estimated_cost_usd', 0.0):.4f}", style="green")
            
            console.print(Panel(overview_text, title="🎯 System Overview", border_style="cyan"))
            
            # Detailed Metrics Table
            console.print("\n[bold]📈 Detailed Performance Metrics[/bold]")
            
            metrics_table = Table(title="Multi-Agent System Analysis", show_header=True)
            metrics_table.add_column("Category", style="cyan", width=20)
            metrics_table.add_column("Metric", style="yellow", width=25)
            metrics_table.add_column("Value", style="magenta", width=15)
            metrics_table.add_column("Quality", style="green", width=10)
            
            proposals = synthesis.get('proposals', {})
            verification = synthesis.get('verification', {})
            evolution = synthesis.get('evolution', {})
            
            # Add metrics with quality indicators
            metrics_table.add_row(
                "Consensus", "Mean Confidence", 
                f"{consensus.get('mean_confidence', 0.0):.1%}",
                "🟢 High" if consensus.get('mean_confidence', 0.0) > 0.8 else "🟡 Med" if consensus.get('mean_confidence', 0.0) > 0.5 else "🔴 Low"
            )
            metrics_table.add_row(
                "Proposals", "Total Generated", 
                str(proposals.get('total_proposals', 0)),
                "🟢 Good" if proposals.get('total_proposals', 0) > 5 else "🟡 Fair" if proposals.get('total_proposals', 0) > 2 else "🔴 Limited"
            )
            metrics_table.add_row(
                "Evolution", "Agents Evolved", 
                str(len(evolution.get('evolved_agents', []))),
                "🟢 Active" if len(evolution.get('evolved_agents', [])) > 0 else "🟡 Stable"
            )
            metrics_table.add_row(
                "Performance", "Cost Efficiency", 
                f"${performance.get('estimated_cost_usd', 0.0):.4f}",
                "🟢 Efficient" if performance.get('estimated_cost_usd', 0.0) < 0.01 else "🟡 Moderate" if performance.get('estimated_cost_usd', 0.0) < 0.05 else "🔴 High"
            )
            
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
            
            # Agent Performance Analysis
            agent_contributions = synthesis.get('agent_contributions', {})
            if agent_contributions:
                console.print("\n[bold]🤖 Individual Agent Analysis[/bold]")
                
                agent_table = Table(title="Agent Performance Breakdown")
                agent_table.add_column("Agent ID", style="cyan")
                agent_table.add_column("Role", style="yellow")
                agent_table.add_column("Confidence", style="green")
                agent_table.add_column("Efficiency", style="blue")
                agent_table.add_column("Fitness", style="red")
                agent_table.add_column("Status", style="magenta")
                
                for agent_id, contrib in list(agent_contributions.items())[:10]:
                    # Calculate efficiency (tokens per second)
                    efficiency = contrib['tokens_used'] / max(contrib['execution_time'], 0.1)
                    
                    # Determine status
                    if contrib['confidence'] > 0.8 and contrib['fitness_score'] > 0.7:
                        status = "🌟 Excellent"
                    elif contrib['confidence'] > 0.6 and contrib['fitness_score'] > 0.5:
                        status = "✅ Good"
                    elif contrib['confidence'] > 0.4:
                        status = "🟡 Fair"
                    else:
                        status = "🔴 Needs Review"
                    
                    agent_table.add_row(
                        agent_id[:12] + "..." if len(agent_id) > 12 else agent_id,
                        contrib['role'][:15] + "..." if len(contrib['role']) > 15 else contrib['role'],
                        f"{contrib['confidence']:.1%}",
                        f"{efficiency:.0f}t/s",
                        f"{contrib['fitness_score']:.1%}",
                        status
                    )
                
                console.print(agent_table)
            
            # Strategic Recommendations
            recommendations = synthesis.get('recommendations', [])
            if recommendations:
                console.print("\n[bold]💡 Strategic Recommendations[/bold]")
                
                for i, rec in enumerate(recommendations[:5], 1):
                    source = rec.get('source', 'Unknown')
                    confidence = rec.get('confidence', 0.0)
                    recommendation = rec.get('recommendation', '')
                    
                    # Color code by confidence
                    if confidence > 0.8:
                        style = "green"
                    elif confidence > 0.6:
                        style = "yellow"
                    else:
                        style = "red"
                    
                    console.print(f"  {i}. [{style}]{source}[/{style}] ({confidence:.1%}): {recommendation}")
            
            # Critical Issues Alert
            critical_issues = verification.get('critical_issues', [])
            if critical_issues:
                console.print(Panel(
                    "\n".join([f"• {issue.get('checker', 'Unknown')}: {issue.get('issue', '')}" 
                             for issue in critical_issues[:3]]),
                    title="⚠️ Critical Issues Requiring Attention",
                    border_style="red"
                ))
            
            # Report Files Section
            if 'reports' in result and result['reports']:
                console.print("\n[bold]📄 Generated Comprehensive Reports[/bold]")
                
                report_table = Table(title="Available Report Formats")
                report_table.add_column("Format", style="cyan")
                report_table.add_column("File Path", style="yellow")
                report_table.add_column("Description", style="green")
                
                format_descriptions = {
                    'markdown': 'Detailed technical report with full analysis',
                    'html': 'Interactive web report with styling and navigation',
                    'json': 'Structured data for programmatic analysis'
                }
                
                for format_type, filepath in result['reports'].items():
                    description = format_descriptions.get(format_type, 'Comprehensive analysis report')
                    report_table.add_row(
                        format_type.upper(),
                        str(Path(filepath).name),
                        description
                    )
                
                console.print(report_table)
                
                # Auto-open HTML report
                if 'html' in result['reports']:
                    html_path = result['reports']['html']
                    try:
                        webbrowser.open(f"file://{Path(html_path).absolute()}")
                        console.print(Panel(
                            f"🌐 Interactive HTML report automatically opened in your browser!\n"
                            f"📁 Full file path: {html_path}",
                            title="Report Viewer",
                            border_style="green"
                        ))
                    except Exception:
                        console.print(Panel(
                            f"💻 Please manually open: file://{Path(html_path).absolute()}",
                            title="Manual Report Access",
                            border_style="yellow"
                        ))
            
            # Conclusion Summary
            console.print("\n" + "="*80)
            conclusion_text = Text()
            conclusion_text.append("🎉 Analysis Complete! ", style="bold green")
            conclusion_text.append(f"The federated agent system processed your task using ")
            conclusion_text.append(f"{len(agent_contributions)} specialized agents ", style="bold cyan")
            conclusion_text.append(f"and achieved ")
            if consensus.get('consensus_reached', False):
                conclusion_text.append("consensus ", style="bold green")
            else:
                conclusion_text.append("partial consensus ", style="bold yellow")
            conclusion_text.append(f"with {consensus.get('mean_confidence', 0.0):.1%} confidence.")
            
            console.print(conclusion_text)
            console.print("="*80)
            
        else:
            console.print("\n[bold red]❌ No comprehensive analysis available[/bold red]")
            console.print("The system may have encountered issues during execution.")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Execution failed: {str(e)}[/bold red]")
        return None
    
    return result

async def main():
    """Main entry point for comprehensive reporting demo"""
    
    # You can customize the task here or use the compelling default
    custom_task = input("\n🎯 Enter a custom task (or press Enter for default): ").strip()
    
    if custom_task:
        await run_with_comprehensive_reports(custom_task)
    else:
        await run_with_comprehensive_reports()

if __name__ == "__main__":
    asyncio.run(main())