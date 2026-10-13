

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    test_database_url: str
    secret_key: str
    GROQ_API_KEY: str
    AI_MODEL: str = "openai/gpt-oss-20b"
    model_config = SettingsConfigDict(env_file='.env')
    

settings = Settings()