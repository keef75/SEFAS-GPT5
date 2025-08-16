#!/usr/bin/env python
"""
Comprehensive test script for SEFAS system validation and improvement.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sefas.workflows.executor import FederatedSystemRunner
from sefas.monitoring.metrics import performance_tracker
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

console = Console()

class SEFASTestSuite:
    """Comprehensive test suite for SEFAS system"""
    
    def __init__(self):
        self.test_tasks = [
            {
                "name": "World Hunger Challenge",
                "task": "Solve world hunger",
                "complexity": "very_high",
                "expected_min_confidence": 0.5,
                "description": "Complex global challenge requiring multi-faceted solutions"
            },
            {
                "name": "Simple Problem",
                "task": "How to make a peanut butter sandwich",
                "complexity": "low",
                "expected_min_confidence": 0.8,
                "description": "Simple procedural task"
            },
            {
                "name": "Technical Challenge",
                "task": "Design a sustainable energy system for a small city",
                "complexity": "high",
                "expected_min_confidence": 0.6,
                "description": "Technical problem with environmental constraints"
            },
            {
                "name": "Creative Challenge",
                "task": "Create an innovative solution for reducing plastic waste",
                "complexity": "medium",
                "expected_min_confidence": 0.65,
                "description": "Requires creative and practical thinking"
            },
            {
                "name": "Analytical Challenge",
                "task": "Analyze the economic impact of remote work trends",
                "complexity": "medium",
                "expected_min_confidence": 0.7,
                "description": "Requires systematic analysis of data and trends"
            }
        ]
        
        self.results = []
        
    async def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        
        console.print(Panel.fit(
            "[bold blue]SEFAS Comprehensive Test Suite[/bold blue]\n"
            "Testing system performance across multiple task types",
            title="🧪 Testing Suite"
        ))
        
        runner = FederatedSystemRunner()
        
        # Test each task
        for i, test_case in enumerate(self.test_tasks, 1):
            await self._run_single_test(runner, test_case, i)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate comprehensive report
        self._generate_report(runner)
        
    async def _run_single_test(self, runner: FederatedSystemRunner, test_case: dict, test_num: int):
        """Run a single test case"""
        
        console.print(f"\n[bold cyan]Test {test_num}/{len(self.test_tasks)}: {test_case['name']}[/bold cyan]")
        console.print(f"Task: {test_case['task']}")
        console.print(f"Complexity: {test_case['complexity']}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running test...", total=None)
            
            start_time = time.time()
            
            try:
                result = await runner.run(test_case['task'])
                execution_time = time.time() - start_time
                
                # Analyze results
                test_result = self._analyze_test_result(test_case, result, execution_time)
                self.results.append(test_result)
                
                # Display immediate results
                self._display_test_result(test_result)
                
            except Exception as e:
                console.print(f"[red]Test failed with error: {e}[/red]")
                self.results.append({
                    'test_name': test_case['name'],
                    'status': 'error',
                    'error': str(e),
                    'execution_time': time.time() - start_time
                })
    
    def _analyze_test_result(self, test_case: dict, result: dict, execution_time: float) -> dict:
        """Analyze test result and determine success/failure"""
        
        consensus_summary = result.get('consensus_summary', {})
        confidence = consensus_summary.get('mean_belief', 0.0)
        consensus_reached = result.get('consensus', False)
        
        # Determine test status
        expected_confidence = test_case['expected_min_confidence']
        
        if 'error' in result:
            status = 'error'
        elif confidence >= expected_confidence and consensus_reached:
            status = 'success'
        elif confidence >= expected_confidence * 0.8:  # Within 80% of expected
            status = 'partial_success'
        else:
            status = 'failure'
        
        return {
            'test_name': test_case['name'],
            'task': test_case['task'],
            'complexity': test_case['complexity'],
            'status': status,
            'confidence': confidence,
            'expected_confidence': expected_confidence,
            'consensus_reached': consensus_reached,
            'execution_time': execution_time,
            'proposals_count': len(result.get('proposals', [])),
            'verifications_count': len(result.get('verifications', [])),
            'consensus_summary': consensus_summary,
            'evolution_results': result.get('evolution_results', {}),
            'tokens_used': result.get('tokens_used', 0),
            'error': result.get('error')
        }
    
    def _display_test_result(self, test_result: dict):
        """Display individual test result"""
        
        status = test_result['status']
        status_colors = {
            'success': 'green',
            'partial_success': 'yellow',
            'failure': 'red',
            'error': 'red'
        }
        
        status_symbols = {
            'success': '✅',
            'partial_success': '⚠️',
            'failure': '❌',
            'error': '💥'
        }
        
        color = status_colors.get(status, 'white')
        symbol = status_symbols.get(status, '?')
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style=color)
        
        table.add_row("Status", f"{symbol} {status.upper()}")
        table.add_row("Confidence", f"{test_result['confidence']:.1%}")
        table.add_row("Expected", f"{test_result['expected_confidence']:.1%}")
        table.add_row("Consensus", "✅" if test_result['consensus_reached'] else "❌")
        table.add_row("Time", f"{test_result['execution_time']:.2f}s")
        table.add_row("Proposals", str(test_result['proposals_count']))
        table.add_row("Verifications", str(test_result['verifications_count']))
        
        if test_result.get('error'):
            table.add_row("Error", test_result['error'][:50] + "...")
        
        console.print(table)
    
    def _generate_report(self, runner: FederatedSystemRunner):
        """Generate comprehensive test report"""
        
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "[bold green]SEFAS Test Suite Report[/bold green]",
            title="📊 Final Report"
        ))
        
        # Summary statistics
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r['status'] == 'success'])
        partial_success_tests = len([r for r in self.results if r['status'] == 'partial_success'])
        failed_tests = len([r for r in self.results if r['status'] in ['failure', 'error']])
        
        # Performance metrics
        avg_confidence = sum(r.get('confidence', 0) for r in self.results) / total_tests if total_tests > 0 else 0
        avg_execution_time = sum(r.get('execution_time', 0) for r in self.results) / total_tests if total_tests > 0 else 0
        total_tokens = sum(r.get('tokens_used', 0) for r in self.results)
        
        # Create summary table
        summary_table = Table(title="Test Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        
        summary_table.add_row("Total Tests", str(total_tests))
        summary_table.add_row("Successful", f"{successful_tests} ({successful_tests/total_tests:.1%})")
        summary_table.add_row("Partial Success", f"{partial_success_tests} ({partial_success_tests/total_tests:.1%})")
        summary_table.add_row("Failed", f"{failed_tests} ({failed_tests/total_tests:.1%})")
        summary_table.add_row("Avg Confidence", f"{avg_confidence:.1%}")
        summary_table.add_row("Avg Execution Time", f"{avg_execution_time:.2f}s")
        summary_table.add_row("Total Tokens Used", f"{total_tokens:,}")
        
        console.print(summary_table)
        
        # Individual test results
        console.print("\n[bold cyan]Individual Test Results:[/bold cyan]")
        results_table = Table()
        results_table.add_column("Test", style="cyan")
        results_table.add_column("Status", style="white")
        results_table.add_column("Confidence", style="green")
        results_table.add_column("Time (s)", style="blue")
        results_table.add_column("Complexity", style="yellow")
        
        for result in self.results:
            status_symbol = {
                'success': '✅',
                'partial_success': '⚠️',
                'failure': '❌',
                'error': '💥'
            }.get(result['status'], '?')
            
            results_table.add_row(
                result['test_name'][:20],
                f"{status_symbol} {result['status']}",
                f"{result.get('confidence', 0):.1%}",
                f"{result.get('execution_time', 0):.2f}",
                result['complexity']
            )
        
        console.print(results_table)
        
        # System performance analysis
        console.print(f"\n[bold cyan]System Performance Analysis:[/bold cyan]")
        system_summary = performance_tracker.get_system_summary()
        
        perf_table = Table()
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="magenta")
        
        for key, value in system_summary.items():
            if isinstance(value, float):
                perf_table.add_row(key.replace('_', ' ').title(), f"{value:.3f}")
            else:
                perf_table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(perf_table)
        
        # Evolution report
        evolution_report = runner.get_evolution_report()
        if evolution_report.get('evolution_enabled'):
            console.print(f"\n[bold cyan]Evolution Report:[/bold cyan]")
            
            evo_table = Table()
            evo_table.add_column("Metric", style="cyan")
            evo_table.add_column("Value", style="green")
            
            for key, value in evolution_report.items():
                if key != 'current_agent_fitness':
                    if isinstance(value, float):
                        evo_table.add_row(key.replace('_', ' ').title(), f"{value:.3f}")
                    else:
                        evo_table.add_row(key.replace('_', ' ').title(), str(value))
            
            console.print(evo_table)
            
            # Agent fitness
            if 'current_agent_fitness' in evolution_report:
                console.print(f"\n[bold cyan]Agent Fitness Scores:[/bold cyan]")
                fitness_table = Table()
                fitness_table.add_column("Agent", style="cyan")
                fitness_table.add_column("Fitness", style="green")
                
                for agent, fitness in evolution_report['current_agent_fitness'].items():
                    fitness_table.add_row(agent, f"{fitness:.3f}")
                
                console.print(fitness_table)
        
        # Recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate improvement recommendations based on test results"""
        
        console.print(f"\n[bold yellow]Recommendations for Improvement:[/bold yellow]")
        
        recommendations = []
        
        # Analyze failure patterns
        failed_results = [r for r in self.results if r['status'] in ['failure', 'error']]
        low_confidence_results = [r for r in self.results if r.get('confidence', 0) < 0.6]
        
        if failed_results:
            recommendations.append(
                "🔧 Consider improving agent prompts for failed test cases"
            )
        
        if low_confidence_results:
            recommendations.append(
                "📈 Enable evolution mode to improve agent performance over time"
            )
        
        # Analyze complexity patterns
        complex_tasks = [r for r in self.results if r['complexity'] in ['high', 'very_high']]
        complex_failures = [r for r in complex_tasks if r['status'] in ['failure', 'partial_success']]
        
        if len(complex_failures) > len(complex_tasks) * 0.5:
            recommendations.append(
                "🧠 Complex tasks struggling - consider adding more specialized agents or improving decomposition"
            )
        
        # Performance recommendations
        avg_time = sum(r.get('execution_time', 0) for r in self.results) / len(self.results)
        if avg_time > 30:
            recommendations.append(
                "⚡ Execution time is high - consider optimizing agent prompts or using faster models"
            )
        
        # General recommendations
        recommendations.extend([
            "📊 Enable LangSmith tracing to get detailed execution insights",
            "🔄 Run tests multiple times to identify consistency patterns",
            "🎯 Focus on improving the lowest-performing agent types",
            "📝 Add more diverse test cases to better evaluate system capabilities"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            console.print(f"{i}. {rec}")

async def main():
    """Main test function"""
    
    console.print("[bold green]Starting SEFAS Test Suite...[/bold green]\n")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        console.print("[yellow]Warning: .env file not found. Copy .env.example to .env and configure your API keys.[/yellow]\n")
    
    test_suite = SEFASTestSuite()
    await test_suite.run_comprehensive_test()
    
    console.print(f"\n[bold green]Test suite completed![/bold green]")
    console.print("Use this data to improve your SEFAS system! 🚀")

if __name__ == "__main__":
    asyncio.run(main())