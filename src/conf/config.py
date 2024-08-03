"""Configuration file for the project."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@host:port/db'
    secret_key: str = 'secret_key'
    algorithm: str = 'algorithm'
    mail_username: str = 'mail@mail.com'
    mail_password: str = 'password'
    mail_from: str = mail_username
    mail_port: int = 465
    mail_server: str = 'mail.server.com'
    redis_host: str = 'host'
    redis_port: int = 6379
    ai_used: str = 'gemini | gpt | claude | llama'
    ai_api_key: str = 'api_key'
    ai_model: str = 'model'
    cloudinary_name: str = 'name'
    cloudinary_api_key: str = 'api_key'
    cloudinary_api_secret: str = 'api_secret'

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = 'ignore'


settings = Settings()
