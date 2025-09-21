"""
Configuration settings for the Data Analytics Engine.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Data Analytics Engine"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    
    # Database
    database_url: str = Field(
        default="postgresql://analytics_user:analytics_password@localhost:5432/data_analytics",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8080",
        "https://localhost:3000",
        "https://localhost:5000",
        "https://localhost:8080"
    ]
    
    # Trusted hosts (for production)
    allowed_hosts: List[str] = ["*"]
    
    # File Upload
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_dir: str = "data/uploads"
    temp_dir: str = "data/temp"
    
    # Machine Learning
    model_dir: str = "models"
    max_training_time: int = 3600  # 1 hour in seconds
    max_concurrent_jobs: int = 5
    
    # Data Processing
    chunk_size: int = 10000
    max_rows_in_memory: int = 1000000
    
    # Caching
    cache_ttl: int = 3600  # 1 hour
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = None
    
    # External Services
    c_sharp_api_url: str = Field(
        default="http://localhost:5000",
        env="CSHARP_API_URL"
    )
    
    # Feature Flags
    enable_ml_training: bool = True
    enable_auto_ml: bool = True
    enable_data_profiling: bool = True
    enable_real_time_processing: bool = True
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment variable."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from environment variable."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DatabaseSettings(BaseSettings):
    """Database-specific settings."""
    
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    database: str = Field(default="data_analytics", env="DB_NAME")
    username: str = Field(default="analytics_user", env="DB_USER")
    password: str = Field(default="analytics_password", env="DB_PASSWORD")
    
    # Connection pool settings
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    """Redis-specific settings."""
    
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    database: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Connection settings
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_timeout: int = 5
    
    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.database}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class MLSettings(BaseSettings):
    """Machine Learning specific settings."""
    
    # Model storage
    model_storage_backend: str = "local"  # local, s3, gcs
    model_registry_url: Optional[str] = None
    
    # Training settings
    default_test_size: float = 0.2
    default_random_state: int = 42
    default_cv_folds: int = 5
    
    # AutoML settings
    automl_time_limit: int = 300  # 5 minutes
    automl_metric: str = "accuracy"
    
    # Feature engineering
    max_features: int = 1000
    feature_selection_method: str = "mutual_info"
    
    # Model serving
    model_cache_size: int = 10
    prediction_batch_size: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    """Get cached database settings."""
    return DatabaseSettings()


@lru_cache()
def get_redis_settings() -> RedisSettings:
    """Get cached Redis settings."""
    return RedisSettings()


@lru_cache()
def get_ml_settings() -> MLSettings:
    """Get cached ML settings."""
    return MLSettings()
