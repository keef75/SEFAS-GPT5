from setuptools import setup, find_packages

setup(
    name="sefas",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langgraph>=0.0.30",
        "langchain-openai>=0.0.5",
        "langchain-experimental>=0.0.47",
        "langsmith>=0.0.87",  # for tracing and monitoring
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",  # for settings management
        "python-dotenv>=1.0.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",  # for pretty console output
        "typer>=0.9.0",   # for CLI
    ],
    python_requires=">=3.9",
)