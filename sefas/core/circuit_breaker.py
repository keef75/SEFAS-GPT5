"""Circuit breaker pattern implementation for fault tolerance."""

import time
import logging
from typing import Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests due to failures
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 3
    reset_timeout: float = 60.0  # seconds
    half_open_max_calls: int = 3
    success_threshold: int = 2  # successes needed to close from half-open

@dataclass
class CircuitBreakerState:
    """Internal state of a circuit breaker"""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0

class CircuitBreaker:
    """Circuit breaker for individual components"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState()
        
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        current_time = time.time()
        
        if self.state.state == CircuitState.CLOSED:
            return True
        elif self.state.state == CircuitState.OPEN:
            if current_time - self.state.last_failure_time >= self.config.reset_timeout:
                logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
                self.state.state = CircuitState.HALF_OPEN
                self.state.half_open_calls = 0
                self.state.success_count = 0
                return True
            return False
        elif self.state.state == CircuitState.HALF_OPEN:
            return self.state.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    def record_success(self):
        """Record a successful execution"""
        if self.state.state == CircuitState.HALF_OPEN:
            self.state.success_count += 1
            if self.state.success_count >= self.config.success_threshold:
                logger.info(f"Circuit breaker {self.name} transitioning to CLOSED")
                self.state.state = CircuitState.CLOSED
                self.state.failure_count = 0
                self.state.success_count = 0
                self.state.half_open_calls = 0
        elif self.state.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.state.failure_count = 0
    
    def record_failure(self):
        """Record a failed execution"""
        current_time = time.time()
        self.state.failure_count += 1
        self.state.last_failure_time = current_time
        
        if self.state.state == CircuitState.CLOSED:
            if self.state.failure_count >= self.config.failure_threshold:
                logger.warning(f"Circuit breaker {self.name} transitioning to OPEN after {self.state.failure_count} failures")
                self.state.state = CircuitState.OPEN
        elif self.state.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit breaker {self.name} transitioning back to OPEN after failure in HALF_OPEN")
            self.state.state = CircuitState.OPEN
            self.state.half_open_calls = 0
            self.state.success_count = 0
    
    def record_call(self):
        """Record that a call was made (for half-open state)"""
        if self.state.state == CircuitState.HALF_OPEN:
            self.state.half_open_calls += 1
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            "name": self.name,
            "state": self.state.state.value,
            "failure_count": self.state.failure_count,
            "success_count": self.state.success_count,
            "half_open_calls": self.state.half_open_calls,
            "last_failure_time": self.state.last_failure_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "reset_timeout": self.config.reset_timeout,
                "half_open_max_calls": self.config.half_open_max_calls,
                "success_threshold": self.config.success_threshold
            }
        }

class CircuitBreakerManager:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.global_config = CircuitBreakerConfig()
    
    def get_breaker(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(name, config or self.global_config)
        return self.breakers[name]
    
    def execute_with_breaker(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        breaker = self.get_breaker(name)
        
        if not breaker.can_execute():
            raise CircuitBreakerOpenError(f"Circuit breaker {name} is OPEN")
        
        breaker.record_call()
        
        try:
            result = func(*args, **kwargs)
            breaker.record_success()
            return result
        except Exception as e:
            breaker.record_failure()
            raise CircuitBreakerExecutionError(f"Circuit breaker {name} recorded failure: {str(e)}") from e
    
    async def execute_with_breaker_async(self, name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection"""
        breaker = self.get_breaker(name)
        
        if not breaker.can_execute():
            raise CircuitBreakerOpenError(f"Circuit breaker {name} is OPEN")
        
        breaker.record_call()
        
        try:
            result = await func(*args, **kwargs)
            breaker.record_success()
            return result
        except Exception as e:
            breaker.record_failure()
            raise CircuitBreakerExecutionError(f"Circuit breaker {name} recorded failure: {str(e)}") from e
    
    def get_all_states(self) -> Dict[str, Dict[str, Any]]:
        """Get state information for all circuit breakers"""
        return {name: breaker.get_state_info() for name, breaker in self.breakers.items()}
    
    def reset_breaker(self, name: str):
        """Manually reset a circuit breaker"""
        if name in self.breakers:
            breaker = self.breakers[name]
            breaker.state = CircuitBreakerState()
            logger.info(f"Circuit breaker {name} manually reset")
    
    def reset_all_breakers(self):
        """Reset all circuit breakers"""
        for name in self.breakers:
            self.reset_breaker(name)

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass

class CircuitBreakerExecutionError(Exception):
    """Raised when execution fails and circuit breaker records failure"""
    pass

# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()

def with_circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """Decorator for circuit breaker protection"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            return circuit_breaker_manager.execute_with_breaker(name, func, *args, **kwargs)
        return wrapper
    return decorator

async def with_circuit_breaker_async(name: str, func: Callable, *args, **kwargs):
    """Async function wrapper for circuit breaker protection"""
    return await circuit_breaker_manager.execute_with_breaker_async(name, func, *args, **kwargs)