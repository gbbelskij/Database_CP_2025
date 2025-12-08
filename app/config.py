from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str  # postgresql://smart_user:smart_password@db:5432/smart_home
    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "smart_home"
    DATABASE_USER: str = "smart_user"
    DATABASE_PASSWORD: str = "smart_password"
    
    JWT_SECRET_KEY: str = "supersecretjwtkeychangeme"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
