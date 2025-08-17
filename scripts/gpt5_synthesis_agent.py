#!/usr/bin/env python3
"""
GPT-5 Independent Report Synthesis Agent for SEFAS

This standalone agent uses GPT-5's advanced reasoning capabilities to analyze 
SEFAS reports (HTML, JSON, MD) and generate executive-level synthesis reports.
Uses the new GPT-5 Responses API for maximum analytical power.
"""

import json
import sys
import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from openai import OpenAI as _OpenAI
    from config.settings import settings
    OPENAI_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing OpenAI or settings: {e}")
    print("🔧 Ensure SEFAS environment is active and dependencies installed")
    sys.exit(1)


class GPT5SynthesisAgent:
    """Advanced synthesis agent using GPT-5 Responses API for executive analysis"""
    
    def __init__(self):
        """Initialize GPT-5 client matching SEFAS architecture"""
        # Match SEFAS ResponsesShim pattern for GPT-5
        client_kwargs = {}
        if settings.openai_organization:
            client_kwargs["organization"] = settings.openai_organization
        if settings.openai_project:
            client_kwargs["project"] = settings.openai_project
            
        self.client = _OpenAI(**client_kwargs)
        self.model = "gpt-5"  # Use full GPT-5 for maximum capability
        
        # Use high reasoning and verbosity for executive analysis
        self.reasoning_effort = "high"    # Maximum reasoning for complex analysis
        self.text_verbosity = "high"      # Comprehensive detailed output
        
        print("✅ GPT-5 Synthesis Agent initialized with Responses API (matching SEFAS architecture)")
    
    def analyze_reports(self, report_paths: Dict[str, str]) -> str:
        """
        Analyze SEFAS reports using GPT-5's advanced reasoning
        
        Args:
            report_paths: Dict with 'json', 'html', 'md' keys pointing to report files
            
        Returns:
            Comprehensive executive synthesis report
        """
        print("🧠 Analyzing SEFAS reports with GPT-5...")
        
        # Extract comprehensive data from all available reports
        analysis_data = self._extract_comprehensive_data(report_paths)
        
        # Generate GPT-5 executive synthesis using high reasoning
        print("🎯 Generating GPT-5 executive synthesis with high reasoning...")
        synthesis = self._generate_gpt5_executive_analysis(analysis_data)
        
        # Format and save comprehensive report
        executive_report = self._format_executive_report(analysis_data, synthesis)
        self._save_executive_report(report_paths, executive_report, analysis_data)
        
        return executive_report
    
    def _extract_comprehensive_data(self, report_paths: Dict[str, str]) -> Dict[str, Any]:
        """Extract all available data from reports for comprehensive analysis"""
        comprehensive_data = {
            'extraction_timestamp': datetime.now().isoformat(),
            'available_formats': list(report_paths.keys()),
            'json_data': {},
            'markdown_content': '',
            'html_content': '',
            'metadata': {}
        }
        
        # 1. Extract structured JSON data (most detailed)
        if 'json' in report_paths and Path(report_paths['json']).exists():
            print(f"📊 Extracting JSON data: {report_paths['json']}")
            comprehensive_data['json_data'] = self._extract_json_data(report_paths['json'])
        
        # 2. Extract Markdown content (human-readable narrative)
        if 'md' in report_paths and Path(report_paths['md']).exists():
            print(f"📝 Extracting Markdown content: {report_paths['md']}")
            comprehensive_data['markdown_content'] = self._extract_markdown_content(report_paths['md'])
        
        # 3. Extract HTML content (rich formatted analysis)
        if 'html' in report_paths and Path(report_paths['html']).exists():
            print(f"🌐 Extracting HTML content: {report_paths['html']}")
            comprehensive_data['html_content'] = self._extract_html_content(report_paths['html'])
        
        return comprehensive_data
    
    def _extract_json_data(self, json_path: str) -> Dict[str, Any]:
        """Extract and structure JSON data for analysis"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract all key sections
            synthesis = data.get('synthesis', {})
            
            structured_data = {
                'task': synthesis.get('task', 'Unknown task'),
                'execution_id': synthesis.get('execution_id', 'unknown'),
                'timestamp': synthesis.get('timestamp', ''),
                
                # Core analysis results
                'consensus': synthesis.get('consensus', {}),
                'recommendations': synthesis.get('recommendations', []),
                'performance_metrics': synthesis.get('performance', {}),
                'agent_contributions': synthesis.get('agent_contributions', {}),
                
                # Detailed breakdowns
                'decomposition': synthesis.get('decomposition', {}),
                'proposals': synthesis.get('proposals', {}),
                'verification': synthesis.get('verification', {}),
                'evolution': synthesis.get('evolution', {}),
                
                # Executive summary from system
                'system_executive_summary': synthesis.get('executive_summary', ''),
                
                # Agent reports sample
                'agent_reports_count': len(data.get('agent_reports', [])),
                'agent_reports_sample': data.get('agent_reports', [])[:5],  # First 5 for context
                
                # Summary data
                'summary': data.get('summary', {}),
                'metadata': data.get('metadata', {})
            }
            
            return structured_data
            
        except Exception as e:
            print(f"⚠️ Error extracting JSON data: {e}")
            return {}
    
    def _extract_markdown_content(self, md_path: str) -> str:
        """Extract Markdown content for narrative context"""
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Return first 8000 chars to avoid token limits
            return content[:8000] + "..." if len(content) > 8000 else content
            
        except Exception as e:
            print(f"⚠️ Error extracting Markdown: {e}")
            return ""
    
    def _extract_html_content(self, html_path: str) -> str:
        """Extract HTML content for rich analysis context"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text content from HTML (simple approach)
            # Remove HTML tags for text analysis
            import re
            text_content = re.sub(r'<[^>]+>', '', content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Return first 6000 chars
            return text_content[:6000] + "..." if len(text_content) > 6000 else text_content
            
        except Exception as e:
            print(f"⚠️ Error extracting HTML: {e}")
            return ""
    
    def _generate_gpt5_executive_analysis(self, comprehensive_data: Dict[str, Any]) -> str:
        """Use GPT-5 Responses API with high reasoning for executive analysis"""
        
        # Prepare comprehensive context for GPT-5
        analysis_context = self._prepare_comprehensive_context(comprehensive_data)
        
        # Create detailed prompt for executive-level analysis
        executive_prompt = f"""
You are a senior management consultant and AI systems analyst. Your client has deployed a sophisticated SEFAS (Self-Evolving Federated Agent System) - a 17-agent federated intelligence network - to analyze a complex problem.

You have been provided with comprehensive execution data including JSON analytics, Markdown narratives, and HTML reports. Your task is to provide an executive-level analysis that transforms this technical execution data into strategic business intelligence.

ANALYSIS SCOPE:
Task Analyzed: {comprehensive_data.get('json_data', {}).get('task', 'Unknown')}
Execution ID: {comprehensive_data.get('json_data', {}).get('execution_id', 'Unknown')}
Agent Network: 17-agent federated system with specialized roles
Available Data: {', '.join(comprehensive_data.get('available_formats', []))}

SYSTEM PERFORMANCE OVERVIEW:
{self._format_performance_overview(comprehensive_data)}

COMPREHENSIVE CONTEXT:
{analysis_context}

DETAILED RECOMMENDATIONS FROM AGENTS:
{self._format_detailed_recommendations(comprehensive_data)}

AGENT NETWORK PERFORMANCE ANALYSIS:
{self._format_agent_network_analysis(comprehensive_data)}

Please provide a comprehensive executive analysis that includes:

1. **EXECUTIVE SUMMARY** (3-4 sentences): What was accomplished, how well, and what it means for the organization.

2. **STRATEGIC INSIGHTS** (5-7 key points): The most important findings that leadership should understand, focusing on actionable intelligence rather than technical details.

3. **SOLUTION QUALITY & CONFIDENCE ASSESSMENT**: 
   - Rate the overall solution quality (Exceptional/Strong/Adequate/Weak)
   - Assess confidence levels and what drives them
   - Identify any significant risks or limitations

4. **BUSINESS IMPACT ANALYSIS**:
   - Immediate implications of these findings
   - Potential opportunities identified
   - Risk mitigation recommendations

5. **AGENT SYSTEM PERFORMANCE EVALUATION**:
   - How effectively the 17-agent network collaborated
   - Quality of the federated intelligence approach
   - Recommendations for system optimization

6. **STRATEGIC RECOMMENDATIONS** (4-6 actionable items):
   - Immediate next steps (0-30 days)
   - Medium-term actions (1-3 months)
   - Long-term strategic considerations

7. **CONFIDENCE & RELIABILITY ASSESSMENT**:
   - How much confidence should leadership have in these results
   - What additional validation might be needed
   - When should this analysis be revisited

Format this as a professional consulting report suitable for C-level executives. Focus on business value, strategic implications, and actionable intelligence. Be direct and decisive while acknowledging uncertainties where they exist.
        """
        
        try:
            # Use GPT-5 Responses API matching SEFAS architecture
            response = self.client.responses.create(
                model=self.model,
                input=executive_prompt,
                reasoning={"effort": self.reasoning_effort},
                text={"verbosity": self.text_verbosity}
            )
            
            # Match SEFAS response handling pattern
            return getattr(response, 'output_text', str(response))
            
        except Exception as e:
            print(f"⚠️ GPT-5 executive analysis failed: {e}")
            return self._fallback_executive_analysis(comprehensive_data)
    
    def _prepare_comprehensive_context(self, comprehensive_data: Dict[str, Any]) -> str:
        """Prepare structured context for GPT-5 analysis"""
        context_sections = []
        
        json_data = comprehensive_data.get('json_data', {})
        
        # Consensus and confidence analysis
        consensus = json_data.get('consensus', {})
        if consensus:
            context_sections.append(
                f"CONSENSUS ANALYSIS: {consensus.get('mean_confidence', 0):.1%} average confidence, "
                f"{'Consensus achieved' if consensus.get('consensus_reached') else 'No consensus'}, "
                f"{consensus.get('high_confidence_count', 0)} high-confidence agents"
            )
        
        # Decomposition strategy
        decomposition = json_data.get('decomposition', {})
        if decomposition:
            context_sections.append(
                f"TASK DECOMPOSITION: {decomposition.get('num_subclaims', 0)} subclaims identified, "
                f"decomposition confidence: {decomposition.get('decomposition_confidence', 0):.1%}"
            )
        
        # Proposal generation
        proposals = json_data.get('proposals', {})
        if proposals:
            context_sections.append(
                f"PROPOSAL GENERATION: {proposals.get('total_proposals', 0)} proposals generated, "
                f"average confidence: {proposals.get('average_confidence', 0):.1%}"
            )
        
        # Verification results
        verification = json_data.get('verification', {})
        if verification:
            context_sections.append(
                f"VERIFICATION: {verification.get('pass_rate', 0):.1%} pass rate across "
                f"{verification.get('total_checks', 0)} validation checks"
            )
        
        # Performance metrics
        performance = json_data.get('performance_metrics', {})
        if performance:
            context_sections.append(
                f"EXECUTION PERFORMANCE: {performance.get('total_execution_time', 0):.1f}s total time, "
                f"{performance.get('total_tokens_used', 0):,} tokens, "
                f"${performance.get('estimated_cost_usd', 0):.4f} estimated cost"
            )
        
        # Markdown narrative summary
        markdown_content = comprehensive_data.get('markdown_content', '')
        if markdown_content:
            context_sections.append(f"NARRATIVE REPORT EXCERPT: {markdown_content[:1000]}...")
        
        return "\n\n".join(context_sections) if context_sections else "Limited context available"
    
    def _format_performance_overview(self, comprehensive_data: Dict[str, Any]) -> str:
        """Format high-level performance overview"""
        json_data = comprehensive_data.get('json_data', {})
        
        overview_parts = []
        
        # Agent count and roles
        agent_count = json_data.get('agent_reports_count', 0)
        overview_parts.append(f"• {agent_count} specialized agents deployed")
        
        # Consensus status
        consensus = json_data.get('consensus', {})
        if consensus:
            confidence = consensus.get('mean_confidence', 0) * 100
            overview_parts.append(f"• {confidence:.1f}% overall system confidence")
            overview_parts.append(f"• Consensus: {'✅ Achieved' if consensus.get('consensus_reached') else '❌ Not reached'}")
        
        # Execution efficiency
        performance = json_data.get('performance_metrics', {})
        if performance:
            exec_time = performance.get('total_execution_time', 0)
            overview_parts.append(f"• {exec_time:.1f} seconds total analysis time")
        
        # Recommendation count
        recommendations = json_data.get('recommendations', [])
        overview_parts.append(f"• {len(recommendations)} strategic recommendations generated")
        
        return "\n".join(overview_parts) if overview_parts else "Performance data not available"
    
    def _format_detailed_recommendations(self, comprehensive_data: Dict[str, Any]) -> str:
        """Format recommendations for GPT-5 analysis"""
        recommendations = comprehensive_data.get('json_data', {}).get('recommendations', [])
        
        if not recommendations:
            return "No recommendations available"
        
        formatted_recs = []
        for i, rec in enumerate(recommendations[:8], 1):  # Top 8 recommendations
            rec_text = rec.get('recommendation', 'No text available')
            confidence = rec.get('confidence', 0) * 100
            source = rec.get('source', 'Unknown agent')
            
            formatted_recs.append(
                f"{i}. {rec_text}\n"
                f"   Source: {source} | Confidence: {confidence:.1f}%"
            )
        
        return "\n\n".join(formatted_recs)
    
    def _format_agent_network_analysis(self, comprehensive_data: Dict[str, Any]) -> str:
        """Format agent network performance for analysis"""
        agent_contributions = comprehensive_data.get('json_data', {}).get('agent_contributions', {})
        
        if not agent_contributions:
            return "Agent network performance data not available"
        
        # Analyze top performing agents
        sorted_agents = sorted(
            agent_contributions.items(),
            key=lambda x: x[1].get('confidence', 0),
            reverse=True
        )
        
        network_analysis = []
        network_analysis.append("TOP PERFORMING AGENTS:")
        
        for agent_id, contrib in sorted_agents[:7]:  # Top 7 agents
            role = contrib.get('role', 'Unknown role')
            confidence = contrib.get('confidence', 0) * 100
            exec_time = contrib.get('execution_time', 0)
            recommendations = contrib.get('recommendations_made', 0)
            
            network_analysis.append(
                f"• {agent_id} ({role}): {confidence:.1f}% confidence, "
                f"{exec_time:.1f}s execution, {recommendations} recommendations"
            )
        
        # Overall network statistics
        total_agents = len(agent_contributions)
        avg_confidence = sum(contrib.get('confidence', 0) for contrib in agent_contributions.values()) / max(total_agents, 1) * 100
        total_exec_time = sum(contrib.get('execution_time', 0) for contrib in agent_contributions.values())
        
        network_analysis.append(f"\nNETWORK STATISTICS:")
        network_analysis.append(f"• {total_agents} agents active")
        network_analysis.append(f"• {avg_confidence:.1f}% average agent confidence")
        network_analysis.append(f"• {total_exec_time:.1f}s total network execution time")
        
        return "\n".join(network_analysis)
    
    def _fallback_executive_analysis(self, comprehensive_data: Dict[str, Any]) -> str:
        """Generate fallback analysis when GPT-5 fails"""
        json_data = comprehensive_data.get('json_data', {})
        task = json_data.get('task', 'Unknown task')
        confidence = json_data.get('consensus', {}).get('mean_confidence', 0) * 100
        agents = json_data.get('agent_reports_count', 0)
        
        return f"""
EXECUTIVE SUMMARY: The SEFAS 17-agent network analyzed "{task}" with {confidence:.1f}% overall confidence. System deployment successful with comprehensive multi-agent analysis completed.

STRATEGIC INSIGHTS:
• Multi-agent federated intelligence system operational and functional
• {agents} specialized agents contributed to analysis
• Consensus level: {'Strong' if confidence >= 70 else 'Moderate' if confidence >= 50 else 'Developing'}
• {len(json_data.get('recommendations', []))} strategic recommendations generated

SOLUTION QUALITY: {'Strong' if confidence >= 70 else 'Adequate'} - Based on system confidence metrics and agent consensus

BUSINESS IMPACT: Analysis provides strategic intelligence for decision-making. Recommend review of detailed recommendations for implementation planning.

STRATEGIC RECOMMENDATIONS:
1. Review detailed agent recommendations for actionable insights
2. Consider confidence levels when prioritizing implementation
3. Monitor system performance for continuous improvement
4. Validate findings through additional analysis if needed

CONFIDENCE ASSESSMENT: System demonstrates {confidence:.1f}% confidence in analysis. Recommend treating as strategic input for further planning and validation.
        """
    
    def _format_executive_report(self, comprehensive_data: Dict[str, Any], gpt5_synthesis: str) -> str:
        """Format the complete executive report"""
        json_data = comprehensive_data.get('json_data', {})
        task = json_data.get('task', 'Unknown task')
        execution_id = json_data.get('execution_id', 'Unknown')
        
        # Header with metadata
        report = "=" * 100 + "\n"
        report += "🎯 SEFAS EXECUTIVE INTELLIGENCE REPORT\n"
        report += "Generated by GPT-5 Advanced Analysis Engine\n"
        report += "=" * 100 + "\n\n"
        
        # Executive metadata
        report += f"📋 ANALYSIS SUBJECT: {task}\n"
        report += f"🆔 EXECUTION ID: {execution_id}\n"
        report += f"🤖 AGENT NETWORK: 17-agent federated intelligence system\n"
        report += f"📊 DATA SOURCES: {', '.join(comprehensive_data.get('available_formats', []))}\n"
        report += f"🗓️ REPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"⚙️ ANALYSIS ENGINE: GPT-5 with High Reasoning\n\n"
        
        # Performance dashboard
        consensus = json_data.get('consensus', {})
        performance = json_data.get('performance_metrics', {})
        
        report += "📊 EXECUTIVE DASHBOARD\n"
        report += "-" * 100 + "\n"
        
        if consensus:
            confidence = consensus.get('mean_confidence', 0) * 100
            conf_emoji = "🟢" if confidence >= 80 else "🟡" if confidence >= 60 else "🟠" if confidence >= 40 else "🔴"
            report += f"🎯 System Confidence: {confidence:.1f}% {conf_emoji}\n"
            report += f"✅ Consensus Status: {'Achieved' if consensus.get('consensus_reached') else 'Developing'}\n"
        
        if performance:
            report += f"⏱️ Analysis Time: {performance.get('total_execution_time', 0):.1f} seconds\n"
            report += f"🔢 Computational Cost: ${performance.get('estimated_cost_usd', 0):.4f}\n"
        
        agent_count = json_data.get('agent_reports_count', 0)
        rec_count = len(json_data.get('recommendations', []))
        report += f"👥 Agents Deployed: {agent_count}\n"
        report += f"💡 Recommendations: {rec_count}\n\n"
        
        # GPT-5 Executive Analysis
        report += "🧠 GPT-5 EXECUTIVE ANALYSIS\n"
        report += "=" * 100 + "\n\n"
        report += gpt5_synthesis + "\n\n"
        
        # Footer
        report += "=" * 100 + "\n"
        report += "🔬 Analysis Methodology: GPT-5 Responses API with High Reasoning Effort\n"
        report += "📈 Data Integration: JSON Analytics + Markdown Narrative + HTML Reports\n"
        report += "🎯 Target Audience: C-Level Executives and Strategic Decision Makers\n"
        report += "⚡ Generated by SEFAS GPT-5 Independent Synthesis Agent\n"
        report += "=" * 100 + "\n"
        
        return report
    
    def _save_executive_report(self, report_paths: Dict[str, str], executive_report: str, comprehensive_data: Dict[str, Any]) -> None:
        """Save executive report to file"""
        try:
            # Create filename from task
            task = comprehensive_data.get('json_data', {}).get('task', 'unknown_task')
            task_name = re.sub(r'[^\w\s-]', '', task)
            task_name = re.sub(r'\s+', '_', task_name).lower()[:50]
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gpt5_executive_report_{task_name}_{timestamp}.txt"
            
            # Save to reports directory
            json_path = report_paths.get('json', '')
            if json_path:
                reports_dir = Path(json_path).parent
            else:
                reports_dir = Path("data/reports")
            
            report_path = reports_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(executive_report)
            
            print(f"💾 GPT-5 Executive Report saved to: {report_path}")
            
        except Exception as e:
            print(f"⚠️ Could not save executive report: {e}")


def main():
    """Command line interface for GPT-5 synthesis agent"""
    parser = argparse.ArgumentParser(description="SEFAS GPT-5 Executive Synthesis Agent")
    parser.add_argument("--json", help="Path to JSON report")
    parser.add_argument("--html", help="Path to HTML report") 
    parser.add_argument("--md", help="Path to Markdown report")
    parser.add_argument("--auto", help="Auto-detect reports by task ID or filename pattern")
    
    args = parser.parse_args()
    
    if args.auto:
        # Auto-detect report files
        reports_dir = Path("data/reports")
        
        # Try to find matching files by task ID
        json_files = list(reports_dir.glob(f"*{args.auto}*.json"))
        
        if json_files:
            # If multiple matches, use the most recent one
            if len(json_files) > 1:
                print(f"📂 Found {len(json_files)} matching reports. Using most recent...")
                json_files = [max(json_files, key=lambda p: p.stat().st_mtime)]
            
            json_path = str(json_files[0])
            
            # Verify the report is recent (within last hour to ensure it's from current run)
            import time
            file_age = time.time() - Path(json_path).stat().st_mtime
            if file_age > 3600:  # More than 1 hour old
                print(f"⚠️ WARNING: Report is {file_age/60:.1f} minutes old - may not be from current run")
                print(f"🕐 File: {Path(json_path).name}")
            else:
                print(f"✅ Report is recent ({file_age:.0f} seconds old) - analyzing current run")
            
            html_path = json_path.replace('.json', '.html')
            md_path = json_path.replace('.json', '.md')
            
            report_paths = {}
            report_paths['json'] = json_path
            if Path(html_path).exists():
                report_paths['html'] = html_path
            if Path(md_path).exists():
                report_paths['md'] = md_path
                
            # Extract and display the actual task for verification
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                actual_task = report_data.get('synthesis', {}).get('task', 'Unknown task')
                print(f"📊 Analyzing reports for task ID {args.auto}: {list(report_paths.keys())}")
                print(f"🎯 Task being analyzed: '{actual_task}'")
            except Exception as e:
                print(f"⚠️ Could not verify task content: {e}")
                print(f"📊 Analyzing reports for task ID {args.auto}: {list(report_paths.keys())}")
        else:
            print(f"❌ No reports found for task ID: {args.auto}")
            print(f"🔍 Searched for pattern: *{args.auto}*.json in {reports_dir}")
            # List recent files for debugging
            recent_files = sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
            if recent_files:
                print(f"📋 Recent report files found:")
                for f in recent_files:
                    age_min = (time.time() - f.stat().st_mtime) / 60
                    print(f"   • {f.name} ({age_min:.1f} min ago)")
            else:
                print("📋 No report files found in directory")
            return
    else:
        # Manual file specification
        report_paths = {}
        if args.json and Path(args.json).exists():
            report_paths['json'] = args.json
        if args.html and Path(args.html).exists():
            report_paths['html'] = args.html
        if args.md and Path(args.md).exists():
            report_paths['md'] = args.md
        
        if not report_paths:
            print("❌ No valid report files specified or found")
            return
    
    # Initialize GPT-5 agent and generate executive analysis
    print("🚀 Initializing GPT-5 Executive Synthesis Agent...")
    agent = GPT5SynthesisAgent()
    
    print("🎯 Beginning comprehensive executive analysis...")
    executive_report = agent.analyze_reports(report_paths)
    
    print("\n" + executive_report)


if __name__ == "__main__":
    main()