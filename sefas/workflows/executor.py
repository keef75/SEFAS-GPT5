"""Real federated system runner with agent coordination."""

from __future__ import annotations

import time
import uuid
import asyncio
from typing import Dict, Any, List
import yaml

from config.settings import settings
from sefas.monitoring.metrics import performance_tracker
from sefas.monitoring.logging import (
    configure_logging,
    log_agent_execution,
    log_performance_metrics,
    log_evolution_event
)
from sefas.agents.proposers import ProposerAgent, CreativeProposer, AnalyticalProposer, ResearchProposer
from sefas.agents.checkers import CheckerAgent, LogicChecker, SemanticChecker, ConsistencyChecker
from sefas.agents.orchestrator import OrchestratorAgent
from sefas.evolution.belief_propagation import BeliefPropagationEngine
from sefas.reporting.report_synthesizer import ReportSynthesizer
from sefas.reporting.final_report import FinalReportGenerator


class FederatedSystemRunner:
    """Real federated system with agent coordination"""

    def __init__(self, max_hops: int | None = None) -> None:
        configure_logging()
        self.max_hops = max_hops or settings.max_hops
        
        # Configure LangSmith and API keys BEFORE initializing agents
        if hasattr(settings, 'configure_langsmith'):
            settings.configure_langsmith()
        
        # Load agent configurations
        try:
            with open('config/agents.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Use minimal default config if file doesn't exist
            self.config = self._get_default_config()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Initialize belief propagation
        self.belief_engine = BeliefPropagationEngine()
        
        # Initialize reporting system
        self.report_synthesizer = ReportSynthesizer()
        self.report_generator = FinalReportGenerator()
        
        # Performance tracking
        self.execution_history = []

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if config file is missing"""
        return {
            'agents': {
                'orchestrator': {
                    'role': 'orchestrator',
                    'model': settings.llm_model,
                    'temperature': 0.1,
                    'initial_prompt': 'You are an orchestrator. Decompose tasks into subclaims.'
                },
                'proposer_alpha': {
                    'role': 'creative_proposer',
                    'model': settings.llm_model,
                    'temperature': 0.7,
                    'strategy': 'creative',
                    'initial_prompt': 'You are a creative proposer. Generate innovative solutions.'
                },
                'proposer_beta': {
                    'role': 'analytical_proposer',
                    'model': settings.llm_model,
                    'temperature': 0.3,
                    'strategy': 'analytical',
                    'initial_prompt': 'You are an analytical proposer. Generate systematic solutions.'
                },
                'checker_logic': {
                    'role': 'logic_validator',
                    'model': settings.llm_model,
                    'temperature': 0.1,
                    'initial_prompt': 'You are a logic checker. Validate logical consistency.'
                }
            }
        }
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents from config"""
        agents = {}
        
        for agent_name, agent_config in self.config['agents'].items():
            try:
                if agent_name == 'orchestrator':
                    agents[agent_name] = OrchestratorAgent(agent_config)
                elif 'proposer_alpha' in agent_name:
                    agents[agent_name] = CreativeProposer(agent_config)
                elif 'proposer_beta' in agent_name:
                    agents[agent_name] = AnalyticalProposer(agent_config)
                elif 'proposer_gamma' in agent_name:
                    agents[agent_name] = ResearchProposer(agent_config)
                elif 'checker_logic' in agent_name:
                    agents[agent_name] = LogicChecker(agent_config)
                elif 'checker_semantic' in agent_name:
                    agents[agent_name] = SemanticChecker(agent_config)
                elif 'checker_consistency' in agent_name:
                    agents[agent_name] = ConsistencyChecker(agent_config)
                else:
                    # Fallback to base classes
                    if 'proposer' in agent_name:
                        agents[agent_name] = ProposerAgent(agent_config)
                    elif 'checker' in agent_name:
                        agents[agent_name] = CheckerAgent(agent_config)
                        
            except Exception as e:
                print(f"Warning: Failed to initialize agent {agent_name}: {e}")
                # Continue with available agents
                
        return agents

    async def run(self, task: str) -> Dict[str, Any]:
        """Execute task through the real federated system"""
        start_time = time.perf_counter()
        task_id = str(uuid.uuid4())
        
        # Initialize variables with safe defaults to prevent KeyError in exception handler
        decomposition_result = {}
        proposals = []
        verifications = []
        beliefs = {}
        consensus_summary = {}
        evolution_results = {}
        
        try:
            # Step 1: Orchestrate - decompose task
            decomposition_result = await self._orchestrate_task(task_id, task)
            
            # Step 2: Propose - get solutions from proposers
            proposals = await self._generate_proposals(task_id, decomposition_result)
            
            # Step 3: Verify - check proposals
            verifications = await self._verify_proposals(task_id, proposals)
            
            # Step 4: Belief Propagation - calculate consensus
            beliefs = self.belief_engine.propagate(proposals, verifications)
            consensus_summary = self.belief_engine.get_consensus_summary(beliefs)
            
            # Step 5: Evolution (if enabled)
            evolution_results = {}
            if settings.evolution_enabled:
                evolution_results = await self._trigger_evolution(beliefs, proposals, verifications)
            
            # Calculate final metrics
            total_time = time.perf_counter() - start_time
            total_tokens = sum(p.get('tokens_used', 500) for p in proposals) + \
                          sum(v.get('tokens_used', 300) for v in verifications)
            
            # Record performance
            performance_tracker.record_task_completion(
                task_id=task_id,
                success=consensus_summary.get('status', 'no_consensus') in ['strong_consensus', 'moderate_consensus'],
                execution_time=total_time,
                tokens_used=total_tokens,
                hops_used=3,  # orchestrate, propose, verify
                confidence=consensus_summary.get('mean_belief', 0.0),
                agent_contributions=self._calculate_agent_contributions(proposals, verifications)
            )
            
            log_performance_metrics(performance_tracker.get_system_summary())
            
            # Collect all agent reports
            agent_reports = []
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'get_report'):
                    report = agent.get_report()
                    if report:
                        agent_reports.append(report)
            
            # Generate comprehensive synthesis
            execution_metadata = {
                'task_id': task_id,
                'total_time': total_time,
                'total_api_calls': len(agent_reports),
                'system_status': 'success'
            }
            
            synthesis = self.report_synthesizer.synthesize(
                agent_reports,
                task,
                execution_metadata
            )
            
            # Generate final reports in multiple formats
            try:
                report_files = self.report_generator.generate(
                    synthesis,
                    agent_reports,
                    format="all"
                )
                
                print(f"\n📄 Comprehensive reports generated:")
                for format_type, filepath in report_files.items():
                    print(f"  - {format_type.upper()}: {filepath}")
            except Exception as e:
                print(f"⚠️ Report generation failed: {e}")
                report_files = {}
            
            # Store execution history
            execution_record = {
                'task_id': task_id,
                'task': task,
                'decomposition': decomposition_result,
                'proposals': proposals,
                'verifications': verifications,
                'beliefs': beliefs,
                'consensus_summary': consensus_summary,
                'evolution_results': evolution_results,
                'execution_time': total_time,
                'tokens_used': total_tokens,
                'agent_reports': [r.to_json() for r in agent_reports],
                'synthesis': synthesis,
                'report_files': report_files
            }
            self.execution_history.append(execution_record)
            
            return {
                'task_id': task_id,
                'current_hop': 3,
                'confidence_scores': beliefs,
                'consensus': consensus_summary.get('status', 'no_consensus') in ['strong_consensus', 'moderate_consensus'],
                'consensus_summary': consensus_summary,
                'proposals': proposals,
                'verifications': verifications,
                'evolution_results': evolution_results,
                'execution_time': total_time,
                'tokens_used': total_tokens,
                'agent_reports': agent_reports,
                'synthesis': synthesis,
                'reports': report_files
            }
            
        except Exception as e:
            # Handle system-level errors gracefully
            error_time = time.perf_counter() - start_time
            
            # Calculate partial metrics safely
            partial_tokens = sum(p.get('tokens_used', 500) for p in proposals) + \
                           sum(v.get('tokens_used', 300) for v in verifications)
            
            log_agent_execution(
                agent_id="system",
                task_id=task_id,
                hop_number=0,
                execution_time=error_time,
                tokens_used=partial_tokens,
                success=False,
                message=f"System error: {str(e)}"
            )
            
            # Record failed execution in performance tracker
            performance_tracker.record_task_completion(
                task_id=task_id,
                success=False,
                execution_time=error_time,
                tokens_used=partial_tokens,
                hops_used=0,
                confidence=0.0,
                agent_contributions={}
            )
            
            # Collect partial agent reports for error analysis
            agent_reports = []
            for agent_name, agent in self.agents.items():
                if hasattr(agent, 'get_report'):
                    report = agent.get_report()
                    if report:
                        agent_reports.append(report)
            
            # Generate error synthesis
            execution_metadata = {
                'task_id': task_id,
                'total_time': error_time,
                'total_api_calls': len(agent_reports),
                'system_status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }
            
            try:
                synthesis = self.report_synthesizer.synthesize(
                    agent_reports,
                    task,
                    execution_metadata
                )
                
                # Generate error reports
                report_files = self.report_generator.generate(
                    synthesis,
                    agent_reports,
                    format="json"  # Only JSON for error reports to avoid HTML issues
                )
                
                print(f"\n⚠️ Error reports generated:")
                for format_type, filepath in report_files.items():
                    print(f"  - {format_type.upper()}: {filepath}")
            except Exception as report_error:
                print(f"⚠️ Error report generation also failed: {report_error}")
                synthesis = {}
                report_files = {}
            
            # Store partial execution history for debugging
            execution_record = {
                'task_id': task_id,
                'task': task,
                'decomposition': decomposition_result,
                'proposals': proposals,
                'verifications': verifications,
                'beliefs': beliefs,
                'consensus_summary': consensus_summary,
                'evolution_results': evolution_results,
                'execution_time': error_time,
                'tokens_used': partial_tokens,
                'error': str(e),
                'error_type': type(e).__name__,
                'agent_reports': [r.to_json() for r in agent_reports],
                'synthesis': synthesis,
                'report_files': report_files
            }
            self.execution_history.append(execution_record)
            
            return {
                'task_id': task_id,
                'current_hop': 0,
                'confidence_scores': beliefs,
                'consensus': False,
                'consensus_summary': consensus_summary,
                'proposals': proposals,
                'verifications': verifications,
                'evolution_results': evolution_results,
                'error': str(e),
                'error_type': type(e).__name__,
                'execution_time': error_time,
                'tokens_used': partial_tokens,
                'agent_reports': agent_reports,
                'synthesis': synthesis,
                'reports': report_files
            }

    async def _orchestrate_task(self, task_id: str, task: str) -> Dict[str, Any]:
        """Orchestrate task decomposition"""
        start_time = time.time()
        
        orchestrator = self.agents.get('orchestrator')
        if not orchestrator:
            return {
                'subclaims': [{
                    'id': 'claim_1',
                    'description': task,
                    'type': 'general',
                    'assigned_agents': ['proposer_alpha']
                }]
            }
        
        # Update orchestrator with current agent fitness scores
        fitness_scores = {name: agent.evolution_state.fitness_score 
                         for name, agent in self.agents.items() 
                         if hasattr(agent, 'evolution_state')}
        orchestrator.fitness_scores = fitness_scores
        
        result = orchestrator.execute({
            'description': task,
            'type': 'decomposition'
        })
        
        execution_time = time.time() - start_time
        log_agent_execution(
            agent_id="orchestrator",
            task_id=task_id,
            hop_number=0,
            execution_time=execution_time,
            tokens_used=500,  # Estimated
            success=True,
            message="Task decomposed successfully"
        )
        
        return result

    async def _generate_proposals(self, task_id: str, decomposition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate proposals from proposer agents"""
        proposals = []
        hop_number = 1
        
        subclaims = decomposition.get('subclaims', [])
        
        for subclaim in subclaims:
            assigned_agents = subclaim.get('assigned_agents', ['proposer_alpha'])
            
            for agent_name in assigned_agents:
                if agent_name in self.agents:
                    start_time = time.time()
                    agent = self.agents[agent_name]
                    
                    try:
                        proposal = agent.execute(subclaim)
                        execution_time = time.time() - start_time
                        
                        # Enhance proposal with metadata
                        proposal.update({
                            'subclaim_id': subclaim.get('id'),
                            'agent_id': agent_name,
                            'agent_role': agent.role,
                            'tokens_used': int(len(str(proposal)) * 1.3),  # Rough estimate
                            'execution_time': execution_time
                        })
                        
                        proposals.append(proposal)
                        
                        log_agent_execution(
                            agent_id=agent_name,
                            task_id=task_id,
                            hop_number=hop_number,
                            execution_time=execution_time,
                            tokens_used=proposal['tokens_used'],
                            success=True,
                            message=f"Generated proposal for {subclaim.get('id')}"
                        )
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        log_agent_execution(
                            agent_id=agent_name,
                            task_id=task_id,
                            hop_number=hop_number,
                            execution_time=execution_time,
                            tokens_used=0,
                            success=False,
                            message=f"Failed to generate proposal: {str(e)}"
                        )
        
        return proposals

    async def _verify_proposals(self, task_id: str, proposals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify proposals using checker agents"""
        verifications = []
        hop_number = 2
        
        checker_agents = [name for name in self.agents.keys() if 'checker' in name]
        
        for proposal in proposals:
            for checker_name in checker_agents:
                if checker_name in self.agents:
                    start_time = time.time()
                    checker = self.agents[checker_name]
                    
                    try:
                        verification = checker.execute({
                            'proposal': proposal,
                            'type': 'verification'
                        })
                        execution_time = time.time() - start_time
                        
                        # Enhance verification with metadata
                        verification.update({
                            'proposal_id': proposal.get('subclaim_id'),
                            'checker_id': checker_name,
                            'checker_role': checker.role,
                            'tokens_used': int(len(str(verification)) * 1.2),  # Rough estimate
                            'execution_time': execution_time
                        })
                        
                        verifications.append(verification)
                        
                        log_agent_execution(
                            agent_id=checker_name,
                            task_id=task_id,
                            hop_number=hop_number,
                            execution_time=execution_time,
                            tokens_used=verification['tokens_used'],
                            success=True,
                            message=f"Verified proposal {proposal.get('subclaim_id')}"
                        )
                        
                    except Exception as e:
                        execution_time = time.time() - start_time
                        log_agent_execution(
                            agent_id=checker_name,
                            task_id=task_id,
                            hop_number=hop_number,
                            execution_time=execution_time,
                            tokens_used=0,
                            success=False,
                            message=f"Failed to verify proposal: {str(e)}"
                        )
        
        return verifications

    async def _trigger_evolution(self, beliefs: Dict[str, float], 
                               proposals: List[Dict[str, Any]], 
                               verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Trigger agent evolution based on performance"""
        evolution_results = {
            'evolutions_triggered': 0,
            'agents_evolved': [],
            'fitness_improvements': {}
        }
        
        # Get agent performance insights
        agent_insights = self.belief_engine.get_agent_performance_insights(proposals, beliefs)
        
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'evolve_prompt'):
                performance_data = agent_insights.get(agent.role, {})
                
                # Check if evolution is needed
                avg_final_belief = performance_data.get('avg_final_belief', 0.5)
                if avg_final_belief < settings.evolution_threshold:
                    
                    # Prepare evolution feedback
                    feedback = {
                        'performance': avg_final_belief,
                        'issues': [
                            f'Low average belief score: {avg_final_belief:.3f}',
                            f'Performance trend: {performance_data.get("performance_trend", "unknown")}'
                        ],
                        'improvement_target': settings.evolution_threshold
                    }
                    
                    # Attempt evolution
                    old_fitness = agent.evolution_state.fitness_score
                    evolved = agent.evolve_prompt(feedback)
                    
                    if evolved:
                        new_fitness = agent.evolution_state.fitness_score
                        evolution_results['evolutions_triggered'] += 1
                        evolution_results['agents_evolved'].append(agent_name)
                        evolution_results['fitness_improvements'][agent_name] = {
                            'old_fitness': old_fitness,
                            'new_fitness': new_fitness,
                            'improvement': new_fitness - old_fitness
                        }
                        
                        log_evolution_event(
                            agent_id=agent_name,
                            evolution_type='prompt_optimization',
                            old_fitness=old_fitness,
                            new_fitness=new_fitness,
                            details={'feedback': feedback}
                        )
        
        return evolution_results

    def _calculate_agent_contributions(self, proposals: List[Dict[str, Any]], 
                                     verifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate agent contributions for performance tracking"""
        contributions = {}
        
        # Proposer contributions
        for proposal in proposals:
            agent_id = proposal.get('agent_id', 'unknown')
            if agent_id not in contributions:
                contributions[agent_id] = {
                    'proposals': 0,
                    'avg_confidence': 0.0,
                    'execution_time': 0.0,
                    'tokens_used': 0
                }
            
            contributions[agent_id]['proposals'] += 1
            contributions[agent_id]['avg_confidence'] = (
                contributions[agent_id]['avg_confidence'] + proposal.get('confidence', 0.5)
            ) / contributions[agent_id]['proposals']
            contributions[agent_id]['execution_time'] += proposal.get('execution_time', 0.0)
            contributions[agent_id]['tokens_used'] += proposal.get('tokens_used', 0)
        
        # Checker contributions
        for verification in verifications:
            checker_id = verification.get('checker_id', 'unknown')
            if checker_id not in contributions:
                contributions[checker_id] = {
                    'verifications': 0,
                    'avg_score': 0.0,
                    'execution_time': 0.0,
                    'tokens_used': 0
                }
            
            contributions[checker_id]['verifications'] += 1
            contributions[checker_id]['avg_score'] = (
                contributions[checker_id]['avg_score'] + verification.get('overall_score', 0.5)
            ) / contributions[checker_id]['verifications']
            contributions[checker_id]['execution_time'] += verification.get('execution_time', 0.0)
            contributions[checker_id]['tokens_used'] += verification.get('tokens_used', 0)
        
        return contributions

    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive evolution report"""
        if not self.execution_history:
            return {
                "evolution_enabled": settings.evolution_enabled,
                "executions": 0,
                "notes": "No executions completed yet."
            }
        
        # Aggregate evolution data
        total_evolutions = sum(
            ex.get('evolution_results', {}).get('evolutions_triggered', 0) 
            for ex in self.execution_history
        )
        
        evolved_agents = set()
        for ex in self.execution_history:
            evolved_agents.update(ex.get('evolution_results', {}).get('agents_evolved', []))
        
        # Agent fitness summary
        agent_fitness = {
            name: agent.evolution_state.fitness_score
            for name, agent in self.agents.items()
            if hasattr(agent, 'evolution_state')
        }
        
        return {
            "evolution_enabled": settings.evolution_enabled,
            "total_executions": len(self.execution_history),
            "total_evolutions": total_evolutions,
            "unique_agents_evolved": len(evolved_agents),
            "current_agent_fitness": agent_fitness,
            "avg_system_fitness": sum(agent_fitness.values()) / len(agent_fitness) if agent_fitness else 0.0,
            "belief_propagation_runs": len(self.belief_engine.get_propagation_history()),
            "evolution_rate": total_evolutions / len(self.execution_history) if self.execution_history else 0.0
        }


