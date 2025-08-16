#!/usr/bin/env python
"""
SEFAS Agent Management Interface

Easy interface for viewing and modifying all 15 agent configurations.
"""

import sys
from pathlib import Path

# Ensure repository root is on sys.path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from typing import Optional

from sefas.agents.factory import AgentFactory

app = typer.Typer()
console = Console()

@app.command()
def list_agents(
    detail: bool = typer.Option(False, "--detail", "-d", help="Show detailed information")
):
    """List all agents and their configurations"""
    
    factory = AgentFactory()
    agents_info = factory.list_agents()
    
    if not agents_info:
        console.print("❌ No agents found in configuration")
        return
    
    console.print(f"🤖 [bold blue]SEFAS Agent Network ({len(agents_info)} agents)[/bold blue]")
    
    if detail:
        # Detailed view with full configuration
        for agent_id, info in agents_info.items():
            panel_content = Text()
            panel_content.append(f"Role: ", style="cyan")
            panel_content.append(f"{info['role']}\\n", style="white")
            panel_content.append(f"Model: ", style="cyan")
            panel_content.append(f"{info['model']}\\n", style="yellow")
            panel_content.append(f"Temperature: ", style="cyan")
            panel_content.append(f"{info['temperature']}\\n", style="green")
            panel_content.append(f"Max Tokens: ", style="cyan")
            panel_content.append(f"{info['max_tokens']}\\n", style="magenta")
            panel_content.append(f"Strategy: ", style="cyan")
            panel_content.append(f"{info['strategy']}", style="blue")
            
            console.print(Panel(
                panel_content,
                title=f"[bold]{info['name']}[/bold] ({agent_id})",
                border_style="green"
            ))
    else:
        # Compact table view
        table = Table(title="Agent Network Overview", show_header=True)
        table.add_column("Agent ID", style="cyan", width=20)
        table.add_column("Name", style="yellow", width=25)
        table.add_column("Role", style="green", width=20)
        table.add_column("Model", style="blue", width=15)
        table.add_column("Temp", style="magenta", width=6)
        table.add_column("Tokens", style="red", width=8)
        
        for agent_id, info in agents_info.items():
            table.add_row(
                agent_id,
                info['name'][:24] + "..." if len(info['name']) > 24 else info['name'],
                info['role'],
                info['model'],
                f"{info['temperature']:.1f}",
                str(info['max_tokens'])
            )
        
        console.print(table)

@app.command()
def show(agent_id: str):
    """Show detailed configuration for a specific agent"""
    
    factory = AgentFactory()
    config = factory.get_agent_config(agent_id)
    
    if not config:
        console.print(f"❌ Agent '{agent_id}' not found")
        return
    
    console.print(f"\\n🤖 [bold blue]{config.get('name', agent_id)}[/bold blue] Configuration")
    console.print("=" * 60)
    
    # Display key configuration items
    key_items = [
        ("Role", config.get('role', 'unknown')),
        ("Model", config.get('model', 'default')),
        ("Temperature", config.get('temperature', 0.0)),
        ("Max Tokens", config.get('max_tokens', 1500)),
        ("Strategy", config.get('strategy', 'general')),
        ("Specialization", config.get('specialization', 'adaptive')),
        ("Rate Limit", f"{config.get('rate_limit_ms', 1000)}ms"),
    ]
    
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan", width=15)
    table.add_column("Value", style="yellow")
    
    for prop, value in key_items:
        table.add_row(prop, str(value))
    
    console.print(table)
    
    # Display prompt
    prompt = config.get('initial_prompt', 'No prompt configured')
    console.print(f"\\n[bold cyan]Initial Prompt:[/bold cyan]")
    console.print(Panel(prompt, border_style="blue"))

@app.command()
def edit(agent_id: str):
    """Interactively edit an agent's configuration"""
    
    factory = AgentFactory()
    config = factory.get_agent_config(agent_id)
    
    if not config:
        console.print(f"❌ Agent '{agent_id}' not found")
        return
    
    console.print(f"🛠️ [bold blue]Editing {config.get('name', agent_id)}[/bold blue]")
    console.print("Leave blank to keep current value, 'q' to quit")
    
    updates = {}
    
    # Edit key parameters
    edit_items = [
        ("name", "Agent Name", config.get('name', agent_id)),
        ("model", "LLM Model (gpt-4o-mini, gpt-4o, gpt-5)", config.get('model', 'gpt-4o-mini')),
        ("temperature", "Temperature (0.1-0.9)", config.get('temperature', 0.3)),
        ("max_tokens", "Max Tokens (500-3000)", config.get('max_tokens', 1500)),
        ("rate_limit_ms", "Rate Limit (ms)", config.get('rate_limit_ms', 1000)),
    ]
    
    for key, description, current_value in edit_items:
        new_value = Prompt.ask(
            f"[cyan]{description}[/cyan]",
            default=str(current_value),
            show_default=True
        )
        
        if new_value.lower() == 'q':
            console.print("❌ Edit cancelled")
            return
        
        if new_value and new_value != str(current_value):
            # Type conversion
            if key in ['temperature']:
                try:
                    updates[key] = float(new_value)
                except ValueError:
                    console.print(f"⚠️ Invalid float value for {key}, skipping")
            elif key in ['max_tokens', 'rate_limit_ms']:
                try:
                    updates[key] = int(new_value)
                except ValueError:
                    console.print(f"⚠️ Invalid integer value for {key}, skipping")
            else:
                updates[key] = new_value
    
    # Edit prompt
    if Confirm.ask("\\n[cyan]Edit the initial prompt?[/cyan]"):
        console.print("\\n[yellow]Current prompt:[/yellow]")
        console.print(Panel(config.get('initial_prompt', ''), border_style="dim"))
        
        console.print("\\n[cyan]Enter new prompt (press Ctrl+D when done):[/cyan]")
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            new_prompt = '\\n'.join(lines)
            if new_prompt.strip():
                updates['initial_prompt'] = new_prompt
        except KeyboardInterrupt:
            console.print("\\n❌ Prompt edit cancelled")
    
    # Apply updates
    if updates:
        console.print(f"\\n[yellow]Applying {len(updates)} updates...[/yellow]")
        for key, value in updates.items():
            console.print(f"  • {key}: {value}")
        
        if factory.update_agent_config(agent_id, updates):
            console.print("✅ [green]Configuration updated successfully![/green]")
        else:
            console.print("❌ [red]Failed to update configuration[/red]")
    else:
        console.print("ℹ️ No changes made")

@app.command()
def clone(
    source: str = typer.Argument(..., help="Source agent ID to clone"),
    target: str = typer.Argument(..., help="New agent ID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for the new agent")
):
    """Clone an existing agent with optional modifications"""
    
    factory = AgentFactory()
    
    modifications = {}
    if name:
        modifications['name'] = name
    
    if factory.clone_agent(source, target, modifications):
        console.print(f"✅ Successfully cloned {source} → {target}")
        if name:
            console.print(f"   New name: {name}")
    else:
        console.print(f"❌ Failed to clone agent")

@app.command()
def topology():
    """Show the agent network topology"""
    
    factory = AgentFactory()
    topology = factory.get_topology()
    
    if not topology:
        console.print("❌ No topology configuration found")
        return
    
    console.print("🕸️ [bold blue]Agent Network Topology[/bold blue]")
    console.print("=" * 50)
    
    table = Table(title="Agent Connections", show_header=True)
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Connections", style="yellow", width=40)
    table.add_column("Weight", style="green", width=8)
    table.add_column("Priority", style="magenta", width=10)
    
    for agent_id, config in topology.items():
        connections = config.get('connections', [])
        weight = config.get('weight', 0.0)
        priority = config.get('priority', 'medium')
        
        connections_str = ", ".join(connections) if connections else "Terminal"
        if len(connections_str) > 40:
            connections_str = connections_str[:37] + "..."
        
        table.add_row(agent_id, connections_str, f"{weight:.1f}", priority)
    
    console.print(table)

@app.command()
def models():
    """Show model distribution across agents"""
    
    factory = AgentFactory()
    agents_info = factory.list_agents()
    
    # Count models
    model_counts = {}
    temp_stats = {}
    
    for agent_id, info in agents_info.items():
        model = info['model']
        temp = info['temperature']
        
        model_counts[model] = model_counts.get(model, 0) + 1
        
        if model not in temp_stats:
            temp_stats[model] = []
        temp_stats[model].append(temp)
    
    console.print("🧠 [bold blue]Model Distribution[/bold blue]")
    
    table = Table(title="LLM Usage Across Agents", show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Agent Count", style="yellow")
    table.add_column("Avg Temperature", style="green")
    table.add_column("Temp Range", style="magenta")
    
    for model, count in sorted(model_counts.items()):
        temps = temp_stats[model]
        avg_temp = sum(temps) / len(temps)
        temp_range = f"{min(temps):.1f} - {max(temps):.1f}"
        
        table.add_row(model, str(count), f"{avg_temp:.2f}", temp_range)
    
    console.print(table)

@app.command()
def test(agent_id: Optional[str] = typer.Argument(None, help="Specific agent to test")):
    """Test agent creation and basic functionality"""
    
    if agent_id:
        # Test specific agent
        from sefas.agents.factory import quick_agent_test
        console.print(f"🧪 Testing agent: {agent_id}")
        success = quick_agent_test(agent_id)
        
        if success:
            console.print("✅ [green]Agent test passed![/green]")
        else:
            console.print("❌ [red]Agent test failed![/red]")
    else:
        # Test all agents
        factory = AgentFactory()
        console.print("🧪 Testing all agents...")
        
        agents = factory.create_all_agents()
        
        if len(agents) > 0:
            console.print(f"✅ [green]Successfully created {len(agents)} agents![/green]")
            
            # Show quick summary
            table = Table(title="Agent Test Results")
            table.add_column("Agent", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Type", style="yellow")
            
            for agent_id, agent in agents.items():
                table.add_row(
                    agent_id,
                    "✅ OK",
                    agent.__class__.__name__
                )
            
            console.print(table)
        else:
            console.print("❌ [red]No agents could be created![/red]")

@app.command()
def quick_config():
    """Quick configuration wizard for common agent modifications"""
    
    console.print("⚡ [bold blue]Quick Agent Configuration Wizard[/bold blue]")
    
    factory = AgentFactory()
    agents_info = factory.list_agents()
    
    # Show options
    console.print("\\nWhat would you like to do?")
    console.print("1. Switch all agents to gpt-4o (more powerful)")
    console.print("2. Switch all agents to gpt-4o-mini (faster, cheaper)")
    console.print("3. Increase creativity (higher temperatures)")
    console.print("4. Increase focus (lower temperatures)")
    console.print("5. Custom model assignment")
    
    choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4", "5"])
    
    updates_applied = 0
    
    if choice == "1":
        # Switch to gpt-4o
        for agent_id in agents_info.keys():
            if factory.update_agent_config(agent_id, {"model": "gpt-4o"}):
                updates_applied += 1
        console.print(f"✅ Switched {updates_applied} agents to gpt-4o")
        
    elif choice == "2":
        # Switch to gpt-4o-mini
        for agent_id in agents_info.keys():
            if factory.update_agent_config(agent_id, {"model": "gpt-4o-mini"}):
                updates_applied += 1
        console.print(f"✅ Switched {updates_applied} agents to gpt-4o-mini")
        
    elif choice == "3":
        # Increase creativity
        for agent_id, info in agents_info.items():
            current_temp = info['temperature']
            new_temp = min(0.8, current_temp + 0.2)
            if factory.update_agent_config(agent_id, {"temperature": new_temp}):
                updates_applied += 1
        console.print(f"✅ Increased creativity for {updates_applied} agents")
        
    elif choice == "4":
        # Increase focus
        for agent_id, info in agents_info.items():
            current_temp = info['temperature']
            new_temp = max(0.1, current_temp - 0.2)
            if factory.update_agent_config(agent_id, {"temperature": new_temp}):
                updates_applied += 1
        console.print(f"✅ Increased focus for {updates_applied} agents")
        
    elif choice == "5":
        # Custom assignment
        console.print("\\nCustom model assignment:")
        console.print("Enter model assignments in format: agent_id=model")
        console.print("Example: proposer_alpha=gpt-4o,orchestrator=gpt-4o-mini")
        console.print("Available models: gpt-4o-mini, gpt-4o, gpt-5")
        
        assignments = Prompt.ask("Enter assignments (comma-separated)")
        
        for assignment in assignments.split(','):
            if '=' not in assignment:
                continue
            agent_id, model = assignment.strip().split('=', 1)
            if agent_id in agents_info:
                if factory.update_agent_config(agent_id, {"model": model.strip()}):
                    updates_applied += 1
                    console.print(f"  ✅ {agent_id} → {model.strip()}")
                else:
                    console.print(f"  ❌ Failed to update {agent_id}")
            else:
                console.print(f"  ⚠️ Agent {agent_id} not found")
        
        console.print(f"\\n✅ Applied {updates_applied} custom assignments")

if __name__ == "__main__":
    app()