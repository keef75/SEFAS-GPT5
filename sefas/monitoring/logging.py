"""Logging configuration for SEFAS."""

import logging
import logging.config
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

def configure_logging(
    level: str = "INFO",
    log_dir: Path = Path("logs"),
    enable_file_logging: bool = True,
    enable_json_logging: bool = False
) -> None:
    """Configure structured logging for SEFAS."""
    
    # Create log directory if it doesn't exist
    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Base logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "sefas.monitoring.logging.JSONFormatter"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "sefas": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            "langchain": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "langsmith": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }
    
    # Add file handlers if enabled
    if enable_file_logging:
        # General application logs
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "detailed",
            "filename": str(log_dir / "sefas.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Agent-specific logs
        config["handlers"]["agent_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(log_dir / "agents.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Evolution logs
        config["handlers"]["evolution_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": str(log_dir / "evolution.log"),
            "maxBytes": 5242880,  # 5MB
            "backupCount": 3
        }
        
        # Performance logs
        config["handlers"]["performance_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json" if enable_json_logging else "detailed",
            "filename": str(log_dir / "performance.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        
        # Add file handlers to loggers
        config["loggers"]["sefas"]["handlers"].extend([
            "file", "agent_file", "evolution_file", "performance_file"
        ])
    
    # Configure logging
    logging.config.dictConfig(config)
    
    # Create specialized loggers
    logger = logging.getLogger("sefas")
    logger.info(f"Logging configured with level: {level}")

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage()
        }
        
        # Add extra fields if present
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id
        if hasattr(record, "task_id"):
            log_entry["task_id"] = record.task_id
        if hasattr(record, "hop_number"):
            log_entry["hop_number"] = record.hop_number
        if hasattr(record, "execution_time"):
            log_entry["execution_time"] = record.execution_time
        if hasattr(record, "tokens_used"):
            log_entry["tokens_used"] = record.tokens_used
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def get_agent_logger(agent_id: str) -> logging.Logger:
    """Get a logger for a specific agent."""
    logger = logging.getLogger(f"sefas.agents.{agent_id}")
    return logger

def get_evolution_logger() -> logging.Logger:
    """Get a logger for evolution events."""
    logger = logging.getLogger("sefas.evolution")
    return logger

def get_performance_logger() -> logging.Logger:
    """Get a logger for performance metrics."""
    logger = logging.getLogger("sefas.performance")
    return logger

def log_agent_execution(
    agent_id: str,
    task_id: str,
    hop_number: int,
    execution_time: float,
    tokens_used: int,
    success: bool,
    message: str = ""
) -> None:
    """Log agent execution with structured data."""
    logger = get_agent_logger(agent_id)
    
    extra_data = {
        "agent_id": agent_id,
        "task_id": task_id,
        "hop_number": hop_number,
        "execution_time": execution_time,
        "tokens_used": tokens_used,
        "success": success
    }
    
    level = logging.INFO if success else logging.WARNING
    logger.log(level, f"Agent execution: {message}", extra=extra_data)

def log_evolution_event(
    agent_id: str,
    evolution_type: str,
    old_fitness: float,
    new_fitness: float,
    details: Dict[str, Any] = None
) -> None:
    """Log evolution events with structured data."""
    logger = get_evolution_logger()
    
    extra_data = {
        "agent_id": agent_id,
        "evolution_type": evolution_type,
        "old_fitness": old_fitness,
        "new_fitness": new_fitness,
        "fitness_improvement": new_fitness - old_fitness
    }
    
    if details:
        extra_data.update(details)
    
    logger.info(
        f"Agent {agent_id} evolved: {evolution_type} "
        f"(fitness: {old_fitness:.3f} → {new_fitness:.3f})",
        extra=extra_data
    )

def log_performance_metrics(metrics: Dict[str, Any]) -> None:
    """Log performance metrics with structured data."""
    logger = get_performance_logger()
    logger.info("Performance metrics", extra=metrics)