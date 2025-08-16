from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import yaml
import os

class Settings(BaseSettings):
    """System-wide configuration"""
    
    # API Keys
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    openai_project: Optional[str] = None
    langsmith_api_key: Optional[str] = None
    
    # LangSmith Configuration
    langsmith_tracing: bool = False
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_project: Optional[str] = None
    
    # Model Configuration
    llm_model: str = "gpt-5"
    llm_temperature: float = 0.2
    embedding_model: str = "text-embedding-3-small"
    
    # System Parameters
    max_hops: int = 10
    confidence_threshold: float = 0.7
    evolution_budget: float = 0.2
    evolution_enabled: bool = False
    evolution_threshold: float = 0.6
    offline_mode: bool = False
    rate_limit_ms: int = 1000
    llm_fallback_on_unauthorized: bool = False
    # GPT-5 Responses API options
    use_responses_api_for_gpt5: bool = False
    gpt5_reasoning_effort: str = "low"   # minimal|low|medium|high
    gpt5_text_verbosity: str = "low"     # low|medium|high
    
    # Paths
    data_dir: Path = Path("data")
    logs_dir: Path = Path("logs")
    checkpoint_dir: Path = Path("checkpoints")
    
    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def load_agent_config(cls) -> Dict[str, Any]:
        """Load agent configuration from YAML"""
        with open("config/agents.yaml", "r") as f:
            return yaml.safe_load(f)
    
    @classmethod
    def load_evolution_config(cls) -> Dict[str, Any]:
        """Load evolution parameters from YAML"""
        try:
            with open("config/evolution.yaml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Provide a safe default if evolution config is missing
            return {"evolution": {"enabled": False}}
    
    def configure_langsmith(self) -> None:
        """Configure LangSmith and OpenAI environment variables"""
        # Set OpenAI API key for LangChain (only if not offline)
        if self.openai_api_key and not self.offline_mode:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
            if self.openai_organization:
                # Set common variations for org env var to maximize compatibility
                os.environ["OPENAI_ORG"] = self.openai_organization
                os.environ["OPENAI_ORGANIZATION"] = self.openai_organization
            if self.openai_project:
                os.environ["OPENAI_PROJECT"] = self.openai_project
            print(f"🔑 OpenAI API Key configured: {self.openai_api_key[:8]}...{self.openai_api_key[-4:]}")
        else:
            print("ℹ️ Offline mode enabled or missing API key; skipping OpenAI configuration.")
        
        # Configure LangSmith tracing
        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_ENDPOINT"] = self.langsmith_endpoint
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            
            if self.langsmith_project:
                os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
            
            # Optional: Configure additional LangSmith settings
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
        else:
            # Disable tracing if not configured
            os.environ.pop("LANGSMITH_TRACING", None)
            os.environ.pop("LANGCHAIN_TRACING_V2", None)

settings = Settings()