"""
Report Synthesizer Module

Synthesizes individual agent reports into comprehensive system report for SEFAS.
"""

from typing import List, Dict, Any
from datetime import datetime
import json
import statistics
from pathlib import Path

from sefas.reporting.agent_reporter import AgentReport

try:
    from langchain_openai import ChatOpenAI
    from config.settings import settings
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

class ReportSynthesizer:
    """Synthesizes individual agent reports into comprehensive system report"""
    
    def __init__(self):
        if LLM_AVAILABLE:
            try:
                self.llm = ChatOpenAI(
                    model=getattr(settings, 'llm_model', 'gpt-4o-mini'),
                    temperature=0.1  # Low temperature for factual synthesis
                )
            except Exception:
                self.llm = None
        else:
            self.llm = None
    
    def synthesize(
        self, 
        agent_reports: List[AgentReport],
        task: str,
        execution_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive synthesis report"""
        
        if not agent_reports:
            return self._empty_synthesis(task, execution_metadata)
        
        # Categorize reports by role
        orchestrator_reports = [r for r in agent_reports if 'orchestrator' in r.agent_role.lower()]
        proposer_reports = [r for r in agent_reports if 'proposer' in r.agent_role.lower()]
        checker_reports = [r for r in agent_reports if 'checker' in r.agent_role.lower()]
        specialist_reports = [r for r in agent_reports 
                             if not any(role in r.agent_role.lower() 
                                      for role in ['orchestrator', 'proposer', 'checker'])]
        
        # Extract key insights
        synthesis = {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_metadata.get('task_id', 'unknown'),
            
            # Decomposition Analysis
            "decomposition": self._analyze_decomposition(orchestrator_reports),
            
            # Solution Proposals
            "proposals": self._analyze_proposals(proposer_reports),
            
            # Verification Results
            "verification": self._analyze_verification(checker_reports),
            
            # Consensus Analysis
            "consensus": self._analyze_consensus(agent_reports),
            
            # Evolution Tracking
            "evolution": self._analyze_evolution(agent_reports),
            
            # Performance Metrics
            "performance": self._calculate_performance(agent_reports, execution_metadata),
            
            # AI-Generated Executive Summary
            "executive_summary": self._generate_executive_summary(
                task, agent_reports, execution_metadata
            ),
            
            # Recommendations
            "recommendations": self._compile_recommendations(agent_reports),
            
            # Agent contributions
            "agent_contributions": self._analyze_agent_contributions(agent_reports),
            
            # Raw reports for reference
            "individual_reports": [r.to_json() for r in agent_reports]
        }
        
        return synthesis
    
    def _empty_synthesis(self, task: str, execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Return empty synthesis when no reports available"""
        return {
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution_metadata.get('task_id', 'unknown'),
            "status": "No agent reports available",
            "decomposition": {"status": "No decomposition performed"},
            "proposals": {"total_proposals": 0, "average_confidence": 0.0},
            "verification": {"total_checks": 0, "pass_rate": 0.0},
            "consensus": {"consensus_reached": False, "mean_confidence": 0.0},
            "evolution": {"total_mutations": 0, "evolved_agents": []},
            "performance": {"total_execution_time": 0.0, "total_tokens_used": 0},
            "executive_summary": "No execution data available to analyze.",
            "recommendations": [],
            "agent_contributions": {},
            "individual_reports": []
        }
    
    def _analyze_decomposition(self, orchestrator_reports: List[AgentReport]) -> Dict[str, Any]:
        """Analyze task decomposition strategy"""
        if not orchestrator_reports:
            return {"status": "No orchestrator reports available"}
        
        report = orchestrator_reports[0]  # Primary orchestrator
        
        subclaims = report.output_generated.get('subclaims', [])
        
        return {
            "num_subclaims": len(subclaims),
            "subclaims": subclaims,
            "decomposition_confidence": report.confidence_score,
            "strategy": report.reasoning_process[0] if report.reasoning_process else "Standard decomposition",
            "execution_time": report.execution_time,
            "tokens_used": report.tokens_used
        }
    
    def _analyze_proposals(self, proposer_reports: List[AgentReport]) -> Dict[str, Any]:
        """Analyze all proposals"""
        if not proposer_reports:
            return {
                "total_proposals": 0,
                "proposals_by_claim": {},
                "best_proposals": {},
                "average_confidence": 0.0
            }
        
        proposals_by_claim = {}
        
        for report in proposer_reports:
            claim_id = report.input_received.get('id', 'general_task')
            if claim_id not in proposals_by_claim:
                proposals_by_claim[claim_id] = []
            
            proposals_by_claim[claim_id].append({
                "agent": report.agent_id,
                "proposal": report.output_generated.get('proposal', ''),
                "confidence": report.confidence_score,
                "approach": report.agent_role,
                "key_points": self._extract_key_points(report.output_generated),
                "execution_time": report.execution_time,
                "tokens_used": report.tokens_used
            })
        
        # Find best proposals
        best_proposals = {}
        for claim_id, proposals in proposals_by_claim.items():
            if proposals:
                best = max(proposals, key=lambda x: x['confidence'])
                best_proposals[claim_id] = best
        
        return {
            "total_proposals": len(proposer_reports),
            "proposals_by_claim": proposals_by_claim,
            "best_proposals": best_proposals,
            "average_confidence": statistics.mean([r.confidence_score for r in proposer_reports]),
            "confidence_range": {
                "min": min([r.confidence_score for r in proposer_reports]),
                "max": max([r.confidence_score for r in proposer_reports])
            }
        }
    
    def _analyze_verification(self, checker_reports: List[AgentReport]) -> Dict[str, Any]:
        """Analyze verification results"""
        verification_summary = {
            "total_checks": len(checker_reports),
            "passed_checks": 0,
            "failed_checks": 0,
            "issues_by_type": {},
            "critical_issues": [],
            "pass_rate": 0.0
        }
        
        if not checker_reports:
            return verification_summary
        
        # Enhanced verification analysis that accounts for both explicit verification_results
        # and confidence-based validation (which is how our system actually works)
        explicit_checks = 0
        confidence_based_checks = 0
        
        for report in checker_reports:
            # Check for explicit verification results first
            if report.verification_results:
                for check, result in report.verification_results.items():
                    explicit_checks += 1
                    if result.get('passed', False):
                        verification_summary['passed_checks'] += 1
                    else:
                        verification_summary['failed_checks'] += 1
                        
                        # Track issue types
                        issue_type = check
                        if issue_type not in verification_summary['issues_by_type']:
                            verification_summary['issues_by_type'][issue_type] = []
                        verification_summary['issues_by_type'][issue_type].extend(
                            report.issues_found
                        )
            
            # ENHANCED: For validator agents without explicit verification_results,
            # use confidence score as validation indicator (our actual system behavior)
            elif 'validator' in report.agent_role.lower() or 'validation' in report.agent_id.lower():
                confidence_based_checks += 1
                # Consider validation passed if confidence > 0.6 and no critical issues
                has_critical_issues = any(
                    word in issue.lower() 
                    for issue in report.issues_found 
                    for word in ['critical', 'severe', 'major', 'error', 'fail']
                )
                
                if report.confidence_score > 0.6 and not has_critical_issues:
                    verification_summary['passed_checks'] += 1
                else:
                    verification_summary['failed_checks'] += 1
            
            # Collect critical issues
            for issue in report.issues_found:
                if any(word in issue.lower() for word in ['critical', 'severe', 'major']):
                    verification_summary['critical_issues'].append({
                        'checker': report.agent_id,
                        'issue': issue
                    })
        
        # Calculate pass rate based on all validation attempts (explicit + confidence-based)
        total_checks = verification_summary['passed_checks'] + verification_summary['failed_checks']
        verification_summary['pass_rate'] = (
            verification_summary['passed_checks'] / max(total_checks, 1)
        )
        
        # Update total_checks to reflect actual validation attempts
        verification_summary['total_checks'] = total_checks
        
        return verification_summary
    
    def _analyze_consensus(self, agent_reports: List[AgentReport]) -> Dict[str, Any]:
        """Analyze consensus across all agents"""
        if not agent_reports:
            return {
                "consensus_reached": False,
                "mean_confidence": 0.0,
                "std_confidence": 0.0,
                "confidence_distribution": {"high": [], "medium": [], "low": []}
            }
        
        confidence_scores = [r.confidence_score for r in agent_reports]
        
        # Group by similar confidence levels
        high_confidence = [c for c in confidence_scores if c >= 0.8]
        medium_confidence = [c for c in confidence_scores if 0.5 <= c < 0.8]
        low_confidence = [c for c in confidence_scores if c < 0.5]
        
        mean_conf = statistics.mean(confidence_scores)
        
        return {
            "mean_confidence": mean_conf,
            "std_confidence": statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0.0,
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores),
            "high_confidence_count": len(high_confidence),
            "medium_confidence_count": len(medium_confidence),
            "low_confidence_count": len(low_confidence),
            "consensus_reached": mean_conf >= 0.7,
            "confidence_distribution": {
                "high": high_confidence,
                "medium": medium_confidence,
                "low": low_confidence
            }
        }
    
    def _analyze_evolution(self, agent_reports: List[AgentReport]) -> Dict[str, Any]:
        """Track evolution metrics"""
        evolution_data = {
            "total_mutations": sum(len(r.mutations_applied) for r in agent_reports),
            "evolved_agents": [],
            "fitness_improvements": [],
            "prompt_versions": {}
        }
        
        for report in agent_reports:
            if report.mutations_applied:
                evolution_data['evolved_agents'].append({
                    "agent": report.agent_id,
                    "mutations": report.mutations_applied,
                    "fitness": report.fitness_score,
                    "prompt_version": report.prompt_version
                })
            
            evolution_data['prompt_versions'][report.agent_id] = report.prompt_version
        
        # Calculate fitness improvement (would need historical data)
        if agent_reports:
            evolution_data['average_fitness'] = statistics.mean([r.fitness_score for r in agent_reports])
        else:
            evolution_data['average_fitness'] = 0.5
        
        return evolution_data
    
    def _calculate_performance(
        self, 
        agent_reports: List[AgentReport],
        execution_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        if not agent_reports:
            return {
                "total_execution_time": execution_metadata.get('total_time', 0.0),
                "total_tokens_used": 0,
                "total_api_calls": 0,
                "estimated_cost_usd": 0.0
            }
        
        total_tokens = sum(r.tokens_used for r in agent_reports)
        total_time = sum(r.execution_time for r in agent_reports)
        
        # Estimate costs (rough approximation)
        cost_per_1k_tokens = 0.0003  # Adjust based on model
        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
        
        return {
            "total_execution_time": execution_metadata.get('total_time', total_time),
            "total_tokens_used": total_tokens,
            "total_api_calls": len(agent_reports),
            "average_time_per_agent": total_time / len(agent_reports),
            "average_tokens_per_agent": total_tokens / len(agent_reports),
            "tokens_per_second": total_tokens / max(total_time, 1),
            "estimated_cost_usd": round(estimated_cost, 4),
            "memory_utilization": sum(len(r.memory_accessed) for r in agent_reports),
            "tool_utilization": sum(len(r.tools_used) for r in agent_reports)
        }
    
    def _generate_executive_summary(
        self,
        task: str,
        agent_reports: List[AgentReport],
        execution_metadata: Dict[str, Any]
    ) -> str:
        """Generate executive summary"""
        
        if not agent_reports:
            return "No agent execution data available for analysis."
        
        # If LLM is available, use it for sophisticated summary
        if self.llm:
            return self._llm_generate_summary(task, agent_reports, execution_metadata)
        else:
            return self._template_generate_summary(task, agent_reports, execution_metadata)
    
    def _llm_generate_summary(
        self,
        task: str,
        agent_reports: List[AgentReport],
        execution_metadata: Dict[str, Any]
    ) -> str:
        """Use LLM to generate executive summary"""
        
        # Prepare context for LLM
        consensus = self._analyze_consensus(agent_reports)
        proposals = self._analyze_proposals([r for r in agent_reports if 'proposer' in r.agent_role.lower()])
        
        context = {
            "task": task,
            "num_agents": len(agent_reports),
            "consensus": consensus,
            "best_proposals": proposals.get('best_proposals', {}),
            "key_issues": [
                issue for r in agent_reports 
                for issue in r.issues_found[:2]  # Top 2 issues per agent
            ][:5]  # Limit to 5 total issues
        }
        
        prompt = f"""
        Generate an executive summary for the following multi-agent task execution:
        
        Task: {task}
        Number of Agents: {context['num_agents']}
        Mean Confidence: {context['consensus']['mean_confidence']:.2%}
        
        Best Proposals Summary:
        {json.dumps(context['best_proposals'], indent=2)[:500]}...
        
        Key Issues Identified:
        {json.dumps(context['key_issues'], indent=2)}
        
        Please provide:
        1. A 2-3 sentence overview of what was accomplished
        2. The main approach taken by the agents
        3. Key strengths of the proposed solutions
        4. Main challenges or limitations identified
        5. Overall assessment of solution quality
        
        Keep it concise and executive-level.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Executive summary generation failed: {str(e)}. Using template summary."
    
    def _template_generate_summary(
        self,
        task: str,
        agent_reports: List[AgentReport],
        execution_metadata: Dict[str, Any]
    ) -> str:
        """Generate template-based summary when LLM unavailable"""
        
        consensus = self._analyze_consensus(agent_reports)
        proposals = self._analyze_proposals([r for r in agent_reports if 'proposer' in r.agent_role.lower()])
        verification = self._analyze_verification([r for r in agent_reports if 'checker' in r.agent_role.lower()])
        
        summary = f"""
        The SEFAS multi-agent system executed the task "{task}" using {len(agent_reports)} specialized agents. 
        
        The system generated {proposals['total_proposals']} proposals with an average confidence of {proposals['average_confidence']:.1%}. 
        Verification processes achieved a {verification['pass_rate']:.1%} pass rate across {verification['total_checks']} checks.
        
        Overall consensus reached: {'Yes' if consensus['consensus_reached'] else 'No'} 
        (mean confidence: {consensus['mean_confidence']:.1%}).
        
        The agents identified {len([issue for r in agent_reports for issue in r.issues_found])} total issues and 
        provided {len([rec for r in agent_reports for rec in r.recommendations])} recommendations for improvement.
        """
        
        return summary.strip()
    
    def _compile_recommendations(self, agent_reports: List[AgentReport]) -> List[Dict[str, str]]:
        """Compile all recommendations from agents"""
        recommendations = []
        
        for report in agent_reports:
            for rec in report.recommendations:
                recommendations.append({
                    "source": report.agent_id,
                    "recommendation": rec,
                    "confidence": report.confidence_score
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _analyze_agent_contributions(self, agent_reports: List[AgentReport]) -> Dict[str, Any]:
        """Analyze individual agent contributions"""
        contributions = {}
        
        for report in agent_reports:
            contributions[report.agent_id] = {
                "role": report.agent_role,
                "confidence": report.confidence_score,
                "execution_time": report.execution_time,
                "tokens_used": report.tokens_used,
                "fitness_score": report.fitness_score,
                "issues_found": len(report.issues_found),
                "recommendations_made": len(report.recommendations),
                "memory_accesses": len(report.memory_accessed),
                "tools_used": len(report.tools_used),
                "prompt_version": report.prompt_version,
                "mutations_applied": len(report.mutations_applied)
            }
        
        return contributions
    
    def _extract_key_points(self, output: Dict[str, Any]) -> List[str]:
        """Extract key points from agent output"""
        key_points = []
        
        # Try to extract from various possible formats
        if isinstance(output.get('proposal'), dict):
            if 'key_points' in output['proposal']:
                key_points = output['proposal']['key_points']
            elif 'summary' in output['proposal']:
                key_points = [output['proposal']['summary']]
        elif isinstance(output.get('proposal'), str):
            # Extract first 100 chars as key point
            text = output['proposal'][:100] + "..." if len(output['proposal']) > 100 else output['proposal']
            key_points = [text]
        
        return key_points
    
    # ==========================================
    # NEW: Human-Readable Answer Synthesis
    # ==========================================
    
    def synthesize_answer(self, json_path: str) -> str:
        """Read JSON report and create human-readable answer
        
        Args:
            json_path: Path to the JSON report file
            
        Returns:
            Formatted answer string ready for display
        """
        try:
            # Load JSON report
            with open(json_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # Extract data from the nested structure
            synthesis = report_data.get('synthesis', {})
            summary = report_data.get('summary', {})
            
            # Extract key fields with safe defaults
            task = synthesis.get('task', 'Unknown task')
            
            # Get consensus data
            consensus = synthesis.get('consensus', {})
            mean_confidence = consensus.get('mean_confidence', 0.0)
            consensus_reached = consensus.get('consensus_reached', False)
            
            # Get recommendations
            recommendations = synthesis.get('recommendations', [])
            
            # Get performance data
            performance = synthesis.get('performance', {})
            execution_time = performance.get('total_execution_time', 0.0)
            
            # Get agent data
            agent_reports = report_data.get('agent_reports', [])
            total_agents = len(agent_reports) if agent_reports else summary.get('total_agents', 0)
            
            # Translate confidence to human terms
            confidence_emoji, confidence_text = self._translate_confidence(mean_confidence)
            
            # Filter high-confidence recommendations (>70%)
            high_conf_recommendations = [
                rec for rec in recommendations 
                if rec.get('confidence', 0) > 0.7
            ][:5]  # Limit to top 5
            
            # Build formatted answer
            answer = self._format_answer(
                task=task,
                confidence_percent=mean_confidence * 100,
                confidence_emoji=confidence_emoji,
                confidence_text=confidence_text,
                recommendations=high_conf_recommendations,
                total_agents=total_agents,
                consensus_reached=consensus_reached,
                execution_time=execution_time
            )
            
            return answer
            
        except FileNotFoundError:
            return self._format_error_message(f"Report file not found: {json_path}")
        except json.JSONDecodeError:
            return self._format_error_message(f"Invalid JSON in report file: {json_path}")
        except Exception as e:
            return self._format_error_message(f"Error reading report: {str(e)}")
    
    def _translate_confidence(self, confidence: float) -> tuple:
        """Translate numeric confidence to emoji and text
        
        Args:
            confidence: Float between 0 and 1
            
        Returns:
            Tuple of (emoji, text) for the confidence level
        """
        if confidence >= 0.8:
            return "✅", "High"
        elif confidence >= 0.6:
            return "🔵", "Moderate"
        elif confidence >= 0.4:
            return "⚠️", "Low"
        else:
            return "❌", "Very Low"
    
    def _format_answer(
        self,
        task: str,
        confidence_percent: float,
        confidence_emoji: str,
        confidence_text: str,
        recommendations: List[Dict[str, Any]],
        total_agents: int,
        consensus_reached: bool,
        execution_time: float
    ) -> str:
        """Format the complete answer string
        
        Args:
            task: The original user question/task
            confidence_percent: Confidence as percentage (0-100)
            confidence_emoji: Emoji representing confidence level
            confidence_text: Human-readable confidence level
            recommendations: List of recommendation dictionaries
            total_agents: Number of agents that analyzed the problem
            consensus_reached: Whether consensus was achieved
            execution_time: Time taken for analysis
            
        Returns:
            Formatted answer string
        """
        # Header
        answer = "=" * 60 + "\n"
        answer += "🎯 SEFAS ANSWER TO YOUR REQUEST\n"
        answer += "=" * 60 + "\n\n"
        
        # Task
        answer += f"📋 Task: {task}\n\n"
        
        # Confidence Level
        answer += f"🔍 Confidence Level: {confidence_percent:.1f}% {confidence_emoji} ({confidence_text} Confidence)\n\n"
        
        # Recommendations
        if recommendations:
            answer += "💡 Top Recommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                rec_text = rec.get('recommendation', 'No recommendation text')
                rec_confidence = rec.get('confidence', 0) * 100
                # Clean up recommendation text
                if rec_text.startswith('- '):
                    rec_text = rec_text[2:]
                answer += f"{i}. {rec_text}\n"
                answer += f"   Confidence: {rec_confidence:.1f}%\n\n"
        else:
            answer += "💡 Top Recommendations:\n"
            answer += "No high-confidence recommendations available (>70% threshold)\n\n"
        
        # Analysis Summary
        answer += "📊 Analysis Summary:\n"
        answer += f"• {total_agents} agents analyzed the problem\n"
        answer += f"• Consensus: {'Reached ✅' if consensus_reached else 'Not reached ❌'}\n"
        answer += f"• Processing time: {execution_time:.1f} seconds\n\n"
        
        # Footer
        answer += "=" * 60 + "\n"
        
        return answer
    
    def _format_error_message(self, error_msg: str) -> str:
        """Format an error message in the same style as answers"""
        error = "=" * 60 + "\n"
        error += "❌ SEFAS SYNTHESIS ERROR\n"
        error += "=" * 60 + "\n\n"
        error += f"🚨 Error: {error_msg}\n\n"
        error += "📋 Please check that:\n"
        error += "• The report file exists and is valid JSON\n"
        error += "• The report was generated by SEFAS\n"
        error += "• File permissions allow reading\n\n"
        error += "=" * 60 + "\n"
        return error
    
    def display_synthesis(self, report_paths: Dict[str, str]) -> None:
        """Display the synthesis and save to file
        
        Args:
            report_paths: Dictionary with report format as key and file path as value
                         Expected to contain 'json' key with JSON report path
        """
        # Get JSON report path
        json_path = report_paths.get('json')
        if not json_path:
            print("\n❌ No JSON report found for synthesis")
            return
        
        # Generate synthesis
        answer = self.synthesize_answer(json_path)
        
        # Display the answer
        print("\n" + answer)
        
        # Save to answer file
        self._save_answer_file(json_path, answer)
    
    def _save_answer_file(self, json_path: str, answer: str) -> None:
        """Save the answer to a text file for easy sharing
        
        Args:
            json_path: Path to the JSON report (used to determine answer file name)
            answer: The formatted answer string to save
        """
        try:
            # Create answer file path with human-readable task name
            json_file = Path(json_path)
            
            # Extract task from the answer to create meaningful filename
            task_name = "unknown_task"
            try:
                # Extract task from JSON file to create meaningful name
                with open(json_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                task = report_data.get('synthesis', {}).get('task', 'unknown_task')
                
                # Clean task for filename (remove special characters, limit length)
                import re
                task_name = re.sub(r'[^\w\s-]', '', task)  # Remove special chars
                task_name = re.sub(r'\s+', '_', task_name)  # Replace spaces with underscores
                task_name = task_name.lower()[:50]  # Lowercase and limit to 50 chars
                if not task_name:
                    task_name = "unknown_task"
            except Exception:
                pass  # Fall back to default if extraction fails
            
            # Create timestamp for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            answer_file = f"answer_{task_name}_{timestamp}.txt"
            answer_path = json_file.parent / answer_file
            
            # Save answer
            with open(answer_path, 'w', encoding='utf-8') as f:
                f.write(answer)
                f.write(f"\nGenerated by SEFAS Report Synthesizer\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Source Report: {json_file.name}\n")
            
            print(f"💾 Answer saved to: {answer_path}")
            
        except Exception as e:
            print(f"⚠️ Could not save answer file: {str(e)}")