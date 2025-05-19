import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add ChromaDB settings
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

class Config:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Server settings
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Security
    AUTH_TOKEN = os.getenv("AUTH_TOKEN", "dev_token")
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    @classmethod
    def is_development(cls):
        return cls.ENVIRONMENT.lower() == "development"
    
    @classmethod
    def is_production(cls):
        return cls.ENVIRONMENT.lower() == "production"