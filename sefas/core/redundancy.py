"""
Industrial-grade redundancy patterns for exponential reliability.
Based on Shannon's information theory and distributed systems best practices.
"""

import asyncio
import time
import random
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class CircuitBreakerState:
    """Circuit breaker state for fault tolerance"""
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    success_count: int = 0
    total_requests: int = 0

class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascade failures.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 30.0,
        half_open_requests: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.half_open_requests = half_open_requests
        self.states: Dict[str, CircuitBreakerState] = defaultdict(CircuitBreakerState)
    
    async def call(self, key: str, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        state = self.states[key]
        
        # Check if circuit is open
        if state.state == "OPEN":
            if state.last_failure_time:
                time_since_failure = (datetime.now() - state.last_failure_time).total_seconds()
                if time_since_failure > self.timeout:
                    # Try half-open
                    state.state = "HALF_OPEN"
                    state.success_count = 0
                    logger.info(f"Circuit breaker {key}: OPEN -> HALF_OPEN")
                else:
                    raise Exception(f"Circuit breaker {key} is OPEN")
            else:
                state.state = "HALF_OPEN"
        
        # Limit requests in half-open state
        if state.state == "HALF_OPEN" and state.total_requests % 10 > self.half_open_requests:
            raise Exception(f"Circuit breaker {key} is HALF_OPEN (limited requests)")
        
        try:
            # Execute the function
            state.total_requests += 1
            result = await func(*args, **kwargs)
            
            # Record success
            state.failure_count = 0
            state.success_count += 1
            
            # Check if we can close the circuit
            if state.state == "HALF_OPEN" and state.success_count >= self.success_threshold:
                state.state = "CLOSED"
                logger.info(f"Circuit breaker {key}: HALF_OPEN -> CLOSED")
            
            return result
            
        except Exception as e:
            # Record failure
            state.failure_count += 1
            state.last_failure_time = datetime.now()
            state.success_count = 0
            
            # Check if we should open the circuit
            if state.failure_count >= self.failure_threshold:
                state.state = "OPEN"
                logger.warning(f"Circuit breaker {key}: CLOSED/HALF_OPEN -> OPEN after {state.failure_count} failures")
            
            raise e

class HedgedRequestManager:
    """
    Implements hedged requests for tail latency reduction.
    """
    
    def __init__(self, hedge_delays: List[float] = None):
        self.hedge_delays = hedge_delays or [0.0, 0.15, 0.5]  # seconds
        self.latency_history = defaultdict(list)
        
    async def hedged_call(
        self,
        providers: List[Any],
        task: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Launch requests with increasing delays to avoid tail latency.
        Returns first successful result.
        """
        
        if not providers:
            raise ValueError("No providers available")
        
        tasks = []
        start_time = time.time()
        
        for i, provider in enumerate(providers[:len(self.hedge_delays)]):
            delay = self.hedge_delays[i] if i < len(self.hedge_delays) else self.hedge_delays[-1]
            
            async def delayed_call(p=provider, d=delay, idx=i):
                if d > 0:
                    await asyncio.sleep(d)
                
                call_start = time.time()
                try:
                    # Handle different provider types and method signatures
                    if hasattr(p, 'execute'):
                        # For SelfEvolvingAgent
                        if isinstance(task, str):
                            task_dict = {'description': task, 'type': 'hedged_execution'}
                        else:
                            task_dict = task
                        
                        # Try with kwargs first, fallback without if signature issues
                        try:
                            result = p.execute(task_dict, **kwargs)
                            if asyncio.iscoroutine(result):
                                result = await result
                        except TypeError:
                            # Method doesn't accept kwargs
                            result = p.execute(task_dict)
                            if asyncio.iscoroutine(result):
                                result = await result
                    else:
                        # Fallback for other provider types
                        result = await p(task)
                    
                    latency = time.time() - call_start
                    
                    return {
                        'result': result,
                        'provider': p.name if hasattr(p, 'name') else str(p),
                        'latency': latency,
                        'hedge_index': idx
                    }
                except Exception as e:
                    logger.error(f"Provider {idx} failed: {e}")
                    raise e
            
            tasks.append(asyncio.create_task(delayed_call()))
        
        # Wait for first successful result
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Get the result
        if done:
            winner = done.pop()
            result = await winner
            
            # Record latency for adaptive hedging
            total_latency = time.time() - start_time
            self.latency_history[result['provider']].append(total_latency)
            
            # Trim history
            if len(self.latency_history[result['provider']]) > 100:
                self.latency_history[result['provider']] = self.latency_history[result['provider']][-100:]
            
            logger.info(f"Hedged request won by {result['provider']} (hedge_index={result['hedge_index']}, latency={result['latency']:.2f}s)")
            
            return result['result']
        
        raise Exception("All hedged requests failed")
    
    def adapt_delays(self):
        """
        Adapt hedge delays based on latency history.
        """
        if not self.latency_history:
            return
        
        # Calculate p50, p95, p99 for each provider
        percentiles = {}
        for provider, latencies in self.latency_history.items():
            if len(latencies) >= 10:
                sorted_latencies = sorted(latencies)
                n = len(sorted_latencies)
                percentiles[provider] = {
                    'p50': sorted_latencies[int(n * 0.5)],
                    'p95': sorted_latencies[int(n * 0.95)],
                    'p99': sorted_latencies[int(n * 0.99)]
                }
        
        if percentiles:
            # Adapt delays based on percentiles
            avg_p50 = sum(p['p50'] for p in percentiles.values()) / len(percentiles)
            avg_p95 = sum(p['p95'] for p in percentiles.values()) / len(percentiles)
            
            # Set hedge delays at p50 and p95
            self.hedge_delays = [0.0, avg_p50, avg_p95]
            logger.info(f"Adapted hedge delays: {self.hedge_delays}")

class MajorityVoteAggregator:
    """
    Implements majority voting with confidence weighting.
    """
    
    @staticmethod
    async def aggregate(
        results: List[Dict],
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Aggregate results using weighted majority voting.
        """
        
        if not results:
            return {
                'consensus': None,
                'confidence': 0.0,
                'support': 0
            }
        
        # Filter by confidence threshold
        valid_results = [
            r for r in results
            if r.get('confidence', 0) >= confidence_threshold
        ]
        
        if not valid_results:
            # Fallback to all results if none meet threshold
            valid_results = results
        
        # Weight votes by confidence
        weighted_votes = defaultdict(float)
        for result in valid_results:
            content = result.get('content', '')
            confidence = result.get('confidence', 0.5)
            weighted_votes[content] += confidence
        
        # Find majority
        if weighted_votes:
            consensus = max(weighted_votes, key=weighted_votes.get)
            total_weight = sum(weighted_votes.values())
            consensus_weight = weighted_votes[consensus]
            
            return {
                'consensus': consensus,
                'confidence': consensus_weight / total_weight if total_weight > 0 else 0.0,
                'support': len([r for r in valid_results if r.get('content') == consensus]),
                'total_votes': len(valid_results),
                'alternatives': dict(weighted_votes)
            }
        
        return {
            'consensus': None,
            'confidence': 0.0,
            'support': 0
        }

class NVersionProgramming:
    """
    N-Version programming for diverse redundancy.
    """
    
    def __init__(self, min_versions: int = 3):
        self.min_versions = min_versions
        
    async def execute_n_versions(
        self,
        providers: List[Any],
        task: str,
        **kwargs
    ) -> List[Dict]:
        """
        Execute task with N different providers/configurations.
        """
        
        if len(providers) < self.min_versions:
            logger.warning(f"Only {len(providers)} providers available, need {self.min_versions}")
        
        # Diversify configurations
        tasks = []
        for i, provider in enumerate(providers):
            # Vary parameters for diversity
            diverse_kwargs = kwargs.copy()
            diverse_kwargs['temperature'] = min(1.0, 0.3 + (i * 0.2))
            diverse_kwargs['seed'] = 42 + i
            
            async def execute_version(p=provider, kw=diverse_kwargs):
                try:
                    # Handle different agent method signatures
                    if hasattr(p, 'execute'):
                        # For SelfEvolvingAgent - pass task as dict and handle kwargs gracefully
                        if isinstance(task, str):
                            task_dict = {'description': task, 'type': 'redundancy_execution'}
                        else:
                            task_dict = task
                        
                        # Try with kwargs first, fallback without if signature issues
                        try:
                            result = p.execute(task_dict, **kw)
                            if asyncio.iscoroutine(result):
                                result = await result
                        except TypeError as te:
                            # Method doesn't accept kwargs, call with minimal params
                            result = p.execute(task_dict)
                            if asyncio.iscoroutine(result):
                                result = await result
                    else:
                        # Fallback for other provider types
                        result = await p(task)
                    
                    return {
                        'content': result.get('proposal', result.get('content', str(result))),
                        'confidence': result.get('confidence', 0.5),
                        'provider': p.name if hasattr(p, 'name') else str(p),
                        'version': i
                    }
                except Exception as e:
                    logger.error(f"Version {i} failed: {e}")
                    return None
            
            tasks.append(execute_version())
        
        # Execute all versions in parallel
        results = await asyncio.gather(*tasks)
        
        # Filter out failures
        valid_results = [r for r in results if r is not None]
        
        if len(valid_results) < self.min_versions:
            logger.warning(f"Only {len(valid_results)} versions succeeded")
        
        return valid_results

class RedundancyOrchestrator:
    """
    Orchestrates all redundancy patterns for maximum reliability.
    """
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.hedge_manager = HedgedRequestManager()
        self.vote_aggregator = MajorityVoteAggregator()
        self.n_version = NVersionProgramming()
        
    async def execute_with_redundancy(
        self,
        providers: List[Any],
        task: str,
        strategy: str = "full",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute task with full redundancy stack.
        
        Strategies:
        - 'fast': Hedged requests only
        - 'reliable': N-version + majority vote
        - 'full': All patterns combined
        """
        
        if strategy == "fast":
            # Just hedged requests for speed
            result = await self.hedge_manager.hedged_call(providers, task, **kwargs)
            return {'result': result, 'strategy': 'fast'}
        
        elif strategy == "reliable":
            # N-version programming with voting
            versions = await self.n_version.execute_n_versions(providers, task, **kwargs)
            consensus = await self.vote_aggregator.aggregate(versions)
            return {'result': consensus, 'versions': versions, 'strategy': 'reliable'}
        
        elif strategy == "full":
            # Full redundancy stack
            
            # 1. N-version execution with circuit breakers
            protected_versions = []
            for i, provider in enumerate(providers[:5]):  # Limit to 5 for cost
                try:
                    result = await self.circuit_breaker.call(
                        f"provider_{i}",
                        self.n_version.execute_n_versions,
                        [provider],
                        task,
                        **kwargs
                    )
                    protected_versions.extend(result)
                except Exception as e:
                    logger.error(f"Provider {i} circuit opened: {e}")
            
            # 2. Aggregate with majority voting
            if protected_versions:
                consensus = await self.vote_aggregator.aggregate(protected_versions)
                
                # 3. If low confidence, try hedged requests for confirmation
                if consensus['confidence'] < 0.7:
                    try:
                        hedged_result = await self.hedge_manager.hedged_call(
                            providers[-3:],  # Use different providers
                            task,
                            **kwargs
                        )
                        
                        # Combine results
                        protected_versions.append({
                            'content': hedged_result.get('content', ''),
                            'confidence': hedged_result.get('confidence', 0.5) * 1.1,  # Boost for confirmation
                            'provider': 'hedged_confirmation'
                        })
                        
                        # Re-vote with hedged result
                        consensus = await self.vote_aggregator.aggregate(protected_versions)
                    except Exception as e:
                        logger.error(f"Hedged confirmation failed: {e}")
                
                return {
                    'result': consensus,
                    'versions': protected_versions,
                    'strategy': 'full',
                    'redundancy_level': len(protected_versions)
                }
            
        return {'error': 'No valid results', 'strategy': strategy}

# Utility function for idempotency
def generate_idempotency_key(task: str, params: Dict) -> str:
    """Generate deterministic key for request deduplication"""
    content = f"{task}:{json.dumps(params, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()