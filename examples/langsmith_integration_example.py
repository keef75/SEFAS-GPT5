"""Example demonstrating LangSmith integration with SEFAS."""

import asyncio
from datetime import datetime
from langchain_openai import ChatOpenAI

# SEFAS imports
from sefas.config.settings import settings
from sefas.monitoring.langsmith_integration import (
    langsmith_monitor, 
    AgentTrace, 
    FederatedTrace
)
from sefas.monitoring.metrics import performance_tracker
from sefas.monitoring.logging import configure_logging, log_agent_execution

async def example_agent_interaction():
    """Example of tracing individual agent interactions."""
    
    # Configure logging
    configure_logging(level="INFO")
    
    # Configure LangSmith tracing
    settings.configure_langsmith()
    print(f"LangSmith monitoring enabled: {langsmith_monitor.enabled}")
    
    # Initialize LLM with tracing
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature
    )
    
    # Simulate agent execution
    start_time = datetime.now()
    
    try:
        # This will be traced by LangSmith
        response = llm.invoke("Analyze the benefits of renewable energy")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        tokens_used = len(response.content.split()) * 1.3  # Rough estimation
        
        # Create agent trace
        agent_trace = AgentTrace(
            agent_id="proposer_alpha",
            agent_role="proposer_alpha",
            input_data={"query": "Analyze the benefits of renewable energy"},
            output_data={"response": response.content[:200] + "..."},
            execution_time=execution_time,
            tokens_used=int(tokens_used),
            hop_number=1,
            success=True,
            metadata={
                "model": settings.llm_model,
                "temperature": settings.llm_temperature
            }
        )
        
        # Trace the execution
        langsmith_monitor.trace_agent_execution(agent_trace)
        
        # Record in performance tracker
        performance_tracker.record_agent_execution(
            agent_id="proposer_alpha",
            execution_time=execution_time,
            tokens=int(tokens_used),
            success=True,
            fitness_score=0.85
        )
        
        # Log the execution
        log_agent_execution(
            agent_id="proposer_alpha",
            task_id="example_task_001",
            hop_number=1,
            execution_time=execution_time,
            tokens_used=int(tokens_used),
            success=True,
            message="Successfully analyzed renewable energy benefits"
        )
        
        print(f"✅ Agent execution completed in {execution_time:.2f}s")
        print(f"📊 Tokens used: {int(tokens_used)}")
        print(f"🔗 Response preview: {response.content[:100]}...")
        
        return agent_trace
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create failed trace
        agent_trace = AgentTrace(
            agent_id="proposer_alpha",
            agent_role="proposer_alpha",
            input_data={"query": "Analyze the benefits of renewable energy"},
            output_data={},
            execution_time=execution_time,
            tokens_used=0,
            hop_number=1,
            success=False,
            error_message=str(e)
        )
        
        langsmith_monitor.trace_agent_execution(agent_trace)
        print(f"❌ Agent execution failed: {e}")
        return agent_trace

async def example_federated_system():
    """Example of tracing a complete federated system execution."""
    
    # Simulate multiple agent interactions
    agent_traces = []
    
    # Orchestrator
    start_time = datetime.now()
    orchestrator_trace = AgentTrace(
        agent_id="orchestrator",
        agent_role="orchestrator", 
        input_data={"task": "Comprehensive renewable energy analysis"},
        output_data={"decomposed_tasks": ["benefits", "challenges", "implementation"]},
        execution_time=0.5,
        tokens_used=150,
        hop_number=0,
        success=True
    )
    agent_traces.append(orchestrator_trace)
    
    # Proposer agents
    for i, proposer in enumerate(["alpha", "beta", "gamma"]):
        proposer_trace = await example_agent_interaction()
        proposer_trace.agent_id = f"proposer_{proposer}"
        proposer_trace.hop_number = i + 1
        agent_traces.append(proposer_trace)
    
    # Checker agents
    for i, checker in enumerate(["logic", "semantic", "consistency"]):
        checker_trace = AgentTrace(
            agent_id=f"checker_{checker}",
            agent_role=f"checker_{checker}",
            input_data={"proposals": ["proposal_1", "proposal_2", "proposal_3"]},
            output_data={"validation": "passed", "confidence": 0.92},
            execution_time=0.3,
            tokens_used=75,
            hop_number=len(agent_traces),
            success=True
        )
        agent_traces.append(checker_trace)
    
    # Create federated trace
    total_time = sum(trace.execution_time for trace in agent_traces)
    total_tokens = sum(trace.tokens_used for trace in agent_traces)
    
    federated_trace = FederatedTrace(
        task_id="renewable_energy_analysis_001",
        original_input="Provide a comprehensive analysis of renewable energy",
        final_output="Comprehensive renewable energy analysis with benefits, challenges, and implementation strategies",
        total_hops=len(agent_traces),
        total_execution_time=total_time,
        total_tokens_used=total_tokens,
        agent_traces=agent_traces,
        success=True,
        confidence_score=0.89,
        metadata={
            "system_version": "0.1.0",
            "evolution_enabled": True
        }
    )
    
    # Trace the federated execution
    langsmith_monitor.trace_federated_execution(federated_trace)
    
    # Record in performance tracker
    performance_tracker.record_task_completion(
        task_id=federated_trace.task_id,
        success=federated_trace.success,
        execution_time=federated_trace.total_execution_time,
        tokens_used=federated_trace.total_tokens_used,
        hops_used=federated_trace.total_hops,
        confidence=federated_trace.confidence_score,
        agent_contributions={
            trace.agent_id: {
                "execution_time": trace.execution_time,
                "tokens": trace.tokens_used,
                "success": trace.success
            } for trace in agent_traces
        }
    )
    
    print(f"\n🎯 Federated execution completed:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Total tokens: {total_tokens}")
    print(f"   Total hops: {len(agent_traces)}")
    print(f"   Confidence: {federated_trace.confidence_score:.2%}")
    print(f"   Agents involved: {len(set(trace.agent_id for trace in agent_traces))}")
    
    return federated_trace

async def example_evolution_tracking():
    """Example of tracking agent evolution."""
    
    # Simulate evolution event
    evolution_data = {
        "mutation_type": "prompt_optimization",
        "old_prompt_version": 1,
        "new_prompt_version": 2,
        "fitness_improvement": 0.15,
        "strategy_changes": {
            "temperature": {"old": 0.7, "new": 0.6},
            "approach": {"old": "creative", "new": "balanced"}
        }
    }
    
    # Trace evolution
    langsmith_monitor.trace_evolution_event("proposer_alpha", evolution_data)
    
    # Record evolution in metrics
    performance_tracker.record_agent_evolution("proposer_alpha")
    
    print("🧬 Evolution event tracked for proposer_alpha")

async def example_performance_analysis():
    """Example of analyzing performance metrics."""
    
    # Get system summary
    summary = performance_tracker.get_system_summary()
    print(f"\n📈 System Performance Summary:")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get agent leaderboard
    leaderboard = performance_tracker.get_agent_leaderboard(limit=5)
    print(f"\n🏆 Top Performing Agents:")
    for i, agent in enumerate(leaderboard, 1):
        print(f"   {i}. {agent['agent_id']}: {agent['current_fitness']:.3f}")
    
    # Get LangSmith metrics if available
    langsmith_metrics = langsmith_monitor.get_performance_metrics()
    if langsmith_metrics:
        print(f"\n🔗 LangSmith Metrics:")
        for key, value in langsmith_metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")

async def main():
    """Main example function."""
    print("🚀 SEFAS LangSmith Integration Example")
    print("=" * 50)
    
    # Single agent execution
    print("\n1. Single Agent Execution:")
    await example_agent_interaction()
    
    # Federated system execution
    print("\n2. Federated System Execution:")
    await example_federated_system()
    
    # Evolution tracking
    print("\n3. Evolution Tracking:")
    await example_evolution_tracking()
    
    # Performance analysis
    print("\n4. Performance Analysis:")
    await example_performance_analysis()
    
    print(f"\n✅ Example completed! Check your LangSmith dashboard: {settings.langsmith_endpoint}")

if __name__ == "__main__":
    asyncio.run(main())