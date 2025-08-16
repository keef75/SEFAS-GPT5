"""
Final Report Generator Module

Generates final comprehensive reports in multiple formats for SEFAS multi-agent system.
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

class FinalReportGenerator:
    """Generates final comprehensive reports in multiple formats"""
    
    def __init__(self, output_dir: Path = Path("data/reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        synthesis: Dict[str, Any],
        agent_reports: List['AgentReport'],
        format: str = "all"  # "markdown", "html", "json", "all"
    ) -> Dict[str, Path]:
        """Generate final report in specified formats"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = synthesis.get('execution_id', 'unknown')
        base_filename = f"final_report_{task_id}_{timestamp}"
        
        generated_files = {}
        
        if format in ["markdown", "all"]:
            md_path = self._generate_markdown(synthesis, agent_reports, base_filename)
            generated_files['markdown'] = md_path
        
        if format in ["html", "all"]:
            html_path = self._generate_html(synthesis, agent_reports, base_filename)
            generated_files['html'] = html_path
        
        if format in ["json", "all"]:
            json_path = self._generate_json(synthesis, agent_reports, base_filename)
            generated_files['json'] = json_path
        
        return generated_files
    
    def _generate_markdown(
        self,
        synthesis: Dict[str, Any],
        agent_reports: List['AgentReport'],
        base_filename: str
    ) -> Path:
        """Generate comprehensive markdown report"""
        
        consensus_status = "✅ Consensus Reached" if synthesis['consensus']['consensus_reached'] else "🔄 Consensus Pending"
        
        report = f"""# 🌐 SEFAS Final Report: {synthesis['task']}

**Report Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Execution ID**: {synthesis['execution_id']}  
**Status**: {consensus_status}

---

## 📋 Executive Summary

{synthesis['executive_summary']}

---

## 🔍 Task Decomposition

The orchestrator decomposed the task into **{synthesis['decomposition'].get('num_subclaims', 0)} subclaims**:

"""
        
        # Add subclaims
        subclaims = synthesis['decomposition'].get('subclaims', [])
        if subclaims:
            for i, claim in enumerate(subclaims, 1):
                claim_id = claim.get('id', f'Claim {i}')
                description = claim.get('description', 'No description')
                report += f"{i}. **{claim_id}**: {description}\n"
        else:
            report += "*No subclaims generated - task handled as single unit*\n"
        
        decomp_confidence = synthesis['decomposition'].get('decomposition_confidence', 0.0)
        report += f"\n**Decomposition Confidence**: {decomp_confidence:.2%}\n"
        
        report += f"""

---

## 💡 Solution Proposals

### Best Proposals by Subclaim

"""
        
        # Add best proposals
        best_proposals = synthesis['proposals'].get('best_proposals', {})
        if best_proposals:
            for claim_id, proposal in best_proposals.items():
                proposal_text = proposal.get('proposal', 'No proposal text')
                if len(proposal_text) > 200:
                    proposal_text = proposal_text[:200] + "..."
                
                report += f"""
#### {claim_id}
- **Agent**: {proposal['agent']}
- **Confidence**: {proposal['confidence']:.2%}
- **Approach**: {proposal['approach']}
- **Execution Time**: {proposal.get('execution_time', 0.0):.2f}s
- **Proposal Summary**: {proposal_text}

"""
        else:
            report += "*No proposals generated*\n"
        
        total_proposals = synthesis['proposals'].get('total_proposals', 0)
        avg_confidence = synthesis['proposals'].get('average_confidence', 0.0)
        
        report += f"""

### Proposal Statistics
- **Total Proposals Generated**: {total_proposals}
- **Average Confidence**: {avg_confidence:.2%}

---

## ✅ Verification Results

### Verification Summary
- **Total Checks**: {synthesis['verification']['total_checks']}
- **Passed**: {synthesis['verification']['passed_checks']} ({synthesis['verification']['pass_rate']:.1%})
- **Failed**: {synthesis['verification']['failed_checks']}

"""
        
        # Add critical issues if any
        critical_issues = synthesis['verification'].get('critical_issues', [])
        if critical_issues:
            report += "### ⚠️ Critical Issues\n\n"
            for issue in critical_issues:
                report += f"- **{issue['checker']}**: {issue['issue']}\n"
        
        # Add issues by type
        issues_by_type = synthesis['verification'].get('issues_by_type', {})
        if issues_by_type:
            report += "\n### Issues by Type\n\n"
            for issue_type, issues in issues_by_type.items():
                if issues:
                    report += f"**{issue_type}**:\n"
                    for issue in issues[:3]:  # Limit to 3 per type
                        report += f"- {issue}\n"
                    if len(issues) > 3:
                        report += f"- ... and {len(issues) - 3} more\n"
                    report += "\n"
        
        report += f"""

---

## 🎯 Consensus Analysis

### Confidence Distribution
- **Mean Confidence**: {synthesis['consensus']['mean_confidence']:.2%}
- **Standard Deviation**: {synthesis['consensus']['std_confidence']:.2%}
- **Range**: {synthesis['consensus']['min_confidence']:.2%} - {synthesis['consensus']['max_confidence']:.2%}

### Agent Agreement
- **High Confidence (≥80%)**: {synthesis['consensus']['high_confidence_count']} agents
- **Medium Confidence (50-79%)**: {synthesis['consensus']['medium_confidence_count']} agents
- **Low Confidence (<50%)**: {synthesis['consensus']['low_confidence_count']} agents

**Consensus Status**: {'✅ Achieved' if synthesis['consensus']['consensus_reached'] else '❌ Not Achieved'}

---

## 🧬 Evolution Metrics

- **Total Mutations**: {synthesis['evolution']['total_mutations']}
- **Evolved Agents**: {len(synthesis['evolution']['evolved_agents'])}
- **Average Fitness**: {synthesis['evolution']['average_fitness']:.2%}

### Evolved Agents
"""
        
        evolved_agents = synthesis['evolution'].get('evolved_agents', [])
        if evolved_agents:
            for evolved in evolved_agents:
                mutations = ', '.join(evolved.get('mutations', [])) or 'None'
                report += f"- **{evolved['agent']}**: v{evolved['prompt_version']} (fitness: {evolved['fitness']:.2%}) - {mutations}\n"
        else:
            report += "*No agents evolved during this execution*\n"
        
        report += f"""

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Total Execution Time | {synthesis['performance']['total_execution_time']:.2f}s |
| Total Tokens Used | {synthesis['performance']['total_tokens_used']:,} |
| API Calls | {synthesis['performance']['total_api_calls']} |
| Avg Time per Agent | {synthesis['performance'].get('average_time_per_agent', 0.0):.2f}s |
| Avg Tokens per Agent | {synthesis['performance'].get('average_tokens_per_agent', 0.0):.0f} |
| Tokens/Second | {synthesis['performance'].get('tokens_per_second', 0.0):.0f} |
| Estimated Cost | ${synthesis['performance']['estimated_cost_usd']:.4f} |
| Memory Utilization | {synthesis['performance']['memory_utilization']} accesses |
| Tool Utilization | {synthesis['performance']['tool_utilization']} uses |

---

## 💡 Recommendations

### Top Recommendations from Agents

"""
        
        recommendations = synthesis.get('recommendations', [])
        if recommendations:
            for i, rec in enumerate(recommendations[:5], 1):
                report += f"{i}. **{rec['source']}** ({rec['confidence']:.2%} confidence): {rec['recommendation']}\n"
        else:
            report += "*No specific recommendations provided by agents*\n"
        
        report += f"""

---

## 🤖 Agent Contributions

### Individual Agent Performance

| Agent | Role | Confidence | Time (s) | Tokens | Fitness | Issues | Recommendations |
|-------|------|------------|----------|--------|---------|--------|----------------|
"""
        
        # Add agent contributions table
        agent_contributions = synthesis.get('agent_contributions', {})
        for agent_id, contrib in agent_contributions.items():
            report += f"| {agent_id} | {contrib['role']} | {contrib['confidence']:.1%} | {contrib['execution_time']:.2f} | {contrib['tokens_used']} | {contrib['fitness_score']:.1%} | {contrib['issues_found']} | {contrib['recommendations_made']} |\n"
        
        report += f"""

---

## 📎 Individual Agent Reports

<details>
<summary>Click to expand individual agent reports</summary>

"""
        
        # Add individual reports
        for agent_report in agent_reports:
            report += f"\n### {agent_report.agent_id}\n"
            report += agent_report.to_markdown()
            report += "\n---\n"
        
        num_agents = len(agent_reports)
        task_title = synthesis['task']
        confidence = synthesis['consensus']['mean_confidence']
        consensus_status_text = 'consensus' if synthesis['consensus']['consensus_reached'] else 'ongoing deliberation'
        
        report += f"""
</details>

---

## 🔚 Conclusion

This report represents the collective intelligence of **{num_agents} specialized agents** working together to solve: **{task_title}**

The system achieved a mean confidence of **{confidence:.2%}** with {consensus_status_text}.

### Next Steps
1. Review critical issues identified by checker agents
2. Consider implementing top recommendations
3. Monitor evolution metrics for continued improvement
4. Validate best proposals through external verification

### System Performance
- **Total Execution Time**: {synthesis['performance']['total_execution_time']:.2f} seconds
- **Computational Cost**: ${synthesis['performance']['estimated_cost_usd']:.4f}
- **Agent Efficiency**: {synthesis['performance'].get('tokens_per_second', 0.0):.0f} tokens/second

---

*Generated by SEFAS - Self-Evolving Federated Agent System*  
*Report Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Save to file
        filepath = self.output_dir / f"{base_filename}.md"
        filepath.write_text(report)
        
        return filepath
    
    def _generate_html(
        self,
        synthesis: Dict[str, Any],
        agent_reports: List['AgentReport'],
        base_filename: str
    ) -> Path:
        """Generate HTML report with styling"""
        
        # First generate markdown
        md_content = self._generate_markdown(synthesis, agent_reports, "temp").read_text()
        
        # Convert to HTML if markdown library is available
        if MARKDOWN_AVAILABLE:
            html_content = markdown.markdown(
                md_content,
                extensions=['tables', 'fenced_code', 'codehilite', 'toc']
            )
        else:
            # Fallback: simple HTML conversion
            html_content = self._simple_md_to_html(md_content)
        
        # Add styling
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SEFAS Report - {synthesis['task']}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            color: #764ba2;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            font-size: 2.5em;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.8em;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
            margin-bottom: 10px;
            font-size: 1.3em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            font-size: 0.9em;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #667eea;
        }}
        .metric {{
            display: inline-block;
            padding: 10px 20px;
            margin: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 25px;
            font-weight: bold;
        }}
        details {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }}
        summary {{
            cursor: pointer;
            font-weight: bold;
            color: #667eea;
            padding: 10px;
            margin: -15px -15px 15px -15px;
            background: #f0f0f0;
            border-radius: 5px 5px 0 0;
        }}
        summary:hover {{
            background: #e8e8e8;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status-success {{
            background: #28a745;
            color: white;
        }}
        .status-pending {{
            background: #ffc107;
            color: #212529;
        }}
        .status-error {{
            background: #dc3545;
            color: white;
        }}
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 30px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-style: italic;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            background: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 5px 5px 0;
        }}
        .execution-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .execution-summary h3 {{
            color: white;
            margin-top: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""
        
        # Save to file
        filepath = self.output_dir / f"{base_filename}.html"
        filepath.write_text(html_template)
        
        # Clean up temp file
        temp_file = self.output_dir / "temp.md"
        if temp_file.exists():
            temp_file.unlink()
        
        return filepath
    
    def _simple_md_to_html(self, md_content: str) -> str:
        """Simple markdown to HTML conversion when markdown library unavailable"""
        
        # Basic conversions
        html = md_content
        
        # Headers
        html = html.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        html = html.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        html = html.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        
        # Bold text
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # Code blocks
        html = html.replace('```', '<pre><code>').replace('```', '</code></pre>')
        
        # Inline code
        html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = f'<p>{html}</p>'
        
        # Lists (basic)
        html = re.sub(r'\n- (.*)', r'\n<li>\1</li>', html)
        html = html.replace('<li>', '<ul><li>').replace('</li>\n<li>', '</li><li>')
        html = html.replace('</li>\n', '</li></ul>\n')
        
        # Horizontal rules
        html = html.replace('---', '<hr>')
        
        return html
    
    def _generate_json(
        self,
        synthesis: Dict[str, Any],
        agent_reports: List['AgentReport'],
        base_filename: str
    ) -> Path:
        """Generate JSON report"""
        
        # Combine synthesis with raw agent reports
        full_report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "format_version": "1.0",
                "system": "SEFAS",
                "report_type": "comprehensive_execution_report"
            },
            "synthesis": synthesis,
            "agent_reports": [r.to_json() for r in agent_reports],
            "summary": {
                "total_agents": len(agent_reports),
                "consensus_reached": synthesis['consensus']['consensus_reached'],
                "mean_confidence": synthesis['consensus']['mean_confidence'],
                "total_execution_time": synthesis['performance']['total_execution_time'],
                "total_cost": synthesis['performance']['estimated_cost_usd'],
                "evolution_events": synthesis['evolution']['total_mutations']
            }
        }
        
        # Save to file
        filepath = self.output_dir / f"{base_filename}.json"
        with open(filepath, 'w') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_summary_report(
        self,
        synthesis: Dict[str, Any],
        filename: str = None
    ) -> Path:
        """Generate a concise summary report"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.json"
        
        summary = {
            "task": synthesis['task'],
            "execution_id": synthesis['execution_id'],
            "timestamp": synthesis['timestamp'],
            "consensus_reached": synthesis['consensus']['consensus_reached'],
            "mean_confidence": synthesis['consensus']['mean_confidence'],
            "total_agents": len(synthesis.get('individual_reports', [])),
            "total_proposals": synthesis['proposals']['total_proposals'],
            "verification_pass_rate": synthesis['verification']['pass_rate'],
            "evolution_events": synthesis['evolution']['total_mutations'],
            "execution_time": synthesis['performance']['total_execution_time'],
            "estimated_cost": synthesis['performance']['estimated_cost_usd'],
            "top_recommendations": synthesis['recommendations'][:3],
            "critical_issues": synthesis['verification'].get('critical_issues', [])
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filepath