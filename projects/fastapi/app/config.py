from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str

    class Config:
        env_file = ".env"

settings = Settings()