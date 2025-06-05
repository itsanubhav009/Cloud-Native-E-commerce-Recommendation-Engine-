from pydantic import BaseSettings, AnyHttpUrl, PostgresDsn, Field
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "E-commerce Recommendation Engine"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "https://dashboard.yourdomain.com"
    ]
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "recommendation_engine")
    DATABASE_URI: Optional[PostgresDsn] = Field(None)
    
    # Redis settings for caching
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # ML Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./app/ml/models")
    
    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: List[str] = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
    KAFKA_TOPIC_EVENTS: str = os.getenv("KAFKA_TOPIC_EVENTS", "user-events")
    KAFKA_TOPIC_RECOMMENDATIONS: str = os.getenv("KAFKA_TOPIC_RECOMMENDATIONS", "recommendations")
    
    class Config:
        case_sensitive = True
    
    def __init__(self, **data: Any):
        super().__init__(**data)
        
        # Construct PostgreSQL URI
        if not self.DATABASE_URI:
            self.DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()