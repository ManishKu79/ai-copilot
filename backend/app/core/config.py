from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mongodb://localhost:27017/aicompilot"
    secret_key: str = "your-secret-key-here"
    ai_model_path: str = "./models"
    
    class Config:
        env_file = ".env"

settings = Settings()