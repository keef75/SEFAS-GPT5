"""
Run manifest system for deterministic reproducibility.
Enables perfect replay and deterministic benchmarking.
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RunManifest:
    """Creates and manages run manifests for reproducible experiments"""
    
    @staticmethod
    def create(task_id: str, config: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Create reproducible run manifest"""
        
        # Get git commit hash for exact version tracking
        try:
            git_sha = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=Path(__file__).parent.parent.parent,  # Go to repo root
                stderr=subprocess.DEVNULL
            ).decode('ascii').strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            git_sha = 'unknown'
        
        # Get git status to check for uncommitted changes
        try:
            git_status = subprocess.check_output(
                ['git', 'status', '--porcelain'],
                cwd=Path(__file__).parent.parent.parent,
                stderr=subprocess.DEVNULL
            ).decode('ascii').strip()
            has_uncommitted = bool(git_status)
        except (subprocess.CalledProcessError, FileNotFoundError):
            has_uncommitted = True
        
        # Create configuration hash for integrity checking
        config_hash = hashlib.sha256(
            json.dumps(config, sort_keys=True, default=str).encode()
        ).hexdigest()
        
        manifest = {
            'manifest_version': '1.0',
            'task_id': task_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'git_commit': git_sha,
            'has_uncommitted_changes': has_uncommitted,
            'config_hash': config_hash,
            
            # BP-specific parameters for convergence analysis
            'belief_propagation': {
                'damping_factor': config.get('damping_factor', 0.8),
                'max_iterations': config.get('max_iterations', 50),
                'convergence_threshold': config.get('convergence_threshold', 1e-4),
                'use_log_domain': config.get('use_log_domain', True),
                'converged': results.get('converged', False),
                'actual_iterations': results.get('iterations', 0),
                'oscillation_detected': results.get('oscillation_detected', False),
                'final_damping': results.get('final_damping', 0.8)
            },
            
            # Model configurations for each agent
            'models': RunManifest._extract_model_configs(config),
            
            # Performance metrics
            'performance': {
                'success': results.get('success', False),
                'consensus_reached': results.get('consensus_reached', False),
                'mean_confidence': results.get('mean_confidence', 0.0),
                'system_confidence': results.get('system_confidence', 0.0),
                'total_tokens': results.get('total_tokens', 0),
                'estimated_cost_usd': results.get('estimated_cost_usd', 0.0),
                'total_latency_seconds': results.get('total_latency_seconds', 0.0),
                'validation_pass_rate': results.get('validation_pass_rate', 0.0)
            },
            
            # Circuit breaker states for fault tolerance analysis
            'circuit_breakers': results.get('circuit_breaker_states', {}),
            
            # Agent performance insights
            'agent_insights': results.get('agent_insights', {}),
            
            # Environment snapshot
            'environment': {
                'python_version': RunManifest._get_python_version(),
                'platform': RunManifest._get_platform_info(),
                'key_dependencies': RunManifest._get_key_dependencies()
            },
            
            # Full configuration backup
            'full_config': config,
            
            # Results summary
            'results_summary': results
        }
        
        # Create manifest directory if it doesn't exist
        manifest_dir = Path('data/manifests')
        manifest_dir.mkdir(parents=True, exist_ok=True)
        
        # Save manifest with timestamp
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = manifest_dir / f"{task_id}_{timestamp_str}.json"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Run manifest saved: {filepath}")
            
            # Also save a 'latest' symlink for easy access
            latest_path = manifest_dir / f"{task_id}_latest.json"
            try:
                if latest_path.exists():
                    latest_path.unlink()
                # Create relative symlink
                latest_path.symlink_to(filepath.name)
            except (OSError, NotImplementedError):
                # Fallback: copy file if symlinks not supported
                with open(latest_path, 'w', encoding='utf-8') as f:
                    json.dump(manifest, f, indent=2, default=str, ensure_ascii=False)
            
        except (IOError, OSError) as e:
            logger.error(f"Failed to save manifest: {e}")
        
        return manifest
    
    @staticmethod
    def load(filepath: str) -> Optional[Dict[str, Any]]:
        """Load a manifest from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load manifest from {filepath}: {e}")
            return None
    
    @staticmethod
    def validate_reproducibility(manifest1: Dict[str, Any], manifest2: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that two manifests are compatible for reproducibility"""
        issues = []
        
        # Check git commit
        if manifest1.get('git_commit') != manifest2.get('git_commit'):
            issues.append(f"Git commit mismatch: {manifest1.get('git_commit')} vs {manifest2.get('git_commit')}")
        
        # Check configuration hash
        if manifest1.get('config_hash') != manifest2.get('config_hash'):
            issues.append("Configuration hash mismatch - configs are different")
        
        # Check model configurations
        models1 = manifest1.get('models', {})
        models2 = manifest2.get('models', {})
        
        for agent_id in set(models1.keys()) | set(models2.keys()):
            if agent_id not in models1:
                issues.append(f"Agent {agent_id} missing in first manifest")
            elif agent_id not in models2:
                issues.append(f"Agent {agent_id} missing in second manifest")
            else:
                model1 = models1[agent_id]
                model2 = models2[agent_id]
                
                if model1.get('model') != model2.get('model'):
                    issues.append(f"Model mismatch for {agent_id}: {model1.get('model')} vs {model2.get('model')}")
                
                if model1.get('temperature') != model2.get('temperature'):
                    issues.append(f"Temperature mismatch for {agent_id}: {model1.get('temperature')} vs {model2.get('temperature')}")
        
        return {
            'compatible': len(issues) == 0,
            'issues': issues,
            'reproducibility_score': max(0.0, 1.0 - len(issues) / 10.0)  # Rough score
        }
    
    @staticmethod
    def _extract_model_configs(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract model configurations from system config"""
        models = {}
        
        # Try to extract from agent configs
        agents = config.get('agents', {})
        if isinstance(agents, dict):
            for agent_id, agent_config in agents.items():
                if isinstance(agent_config, dict):
                    models[agent_id] = {
                        'provider': agent_config.get('provider', 'openai'),
                        'model': agent_config.get('model', 'gpt-4o-mini'),
                        'temperature': agent_config.get('temperature', 0.7),
                        'max_tokens': agent_config.get('max_tokens', 2000),
                        'seed': agent_config.get('seed'),
                        'role': agent_config.get('role', 'unknown')
                    }
        
        return models
    
    @staticmethod
    def _get_python_version() -> str:
        """Get Python version string"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    @staticmethod
    def _get_platform_info() -> str:
        """Get platform information"""
        import platform
        return f"{platform.system()} {platform.release()}"
    
    @staticmethod
    def _get_key_dependencies() -> Dict[str, str]:
        """Get versions of key dependencies"""
        deps = {}
        
        try:
            import numpy
            deps['numpy'] = numpy.__version__
        except ImportError:
            pass
        
        try:
            import pydantic
            deps['pydantic'] = pydantic.__version__
        except ImportError:
            pass
        
        try:
            import langchain
            deps['langchain'] = langchain.__version__
        except ImportError:
            pass
        
        try:
            import openai
            deps['openai'] = openai.__version__
        except ImportError:
            pass
        
        return deps

class ReproducibilityValidator:
    """Validates experimental reproducibility"""
    
    @staticmethod
    def check_determinism(task_id: str, n_runs: int = 3) -> Dict[str, Any]:
        """Run the same task multiple times and check for determinism"""
        logger.info(f"Running determinism check for {task_id} with {n_runs} runs")
        
        # This would need to be integrated with the actual experiment runner
        # For now, return a placeholder
        return {
            'task_id': task_id,
            'n_runs': n_runs,
            'deterministic': False,  # To be implemented
            'variance_metrics': {},
            'recommendations': [
                "Set random seeds for all models",
                "Use deterministic sampling",
                "Verify environment reproducibility"
            ]
        }
    
    @staticmethod
    def replay_from_manifest(manifest_path: str) -> Dict[str, Any]:
        """Replay an experiment from a manifest"""
        manifest = RunManifest.load(manifest_path)
        if not manifest:
            return {'success': False, 'error': 'Failed to load manifest'}
        
        # This would need to be integrated with the actual experiment runner
        logger.info(f"Would replay experiment from {manifest_path}")
        
        return {
            'success': False,  # To be implemented
            'original_manifest': manifest,
            'replay_results': {},
            'differences': [],
            'reproducibility_score': 0.0
        }