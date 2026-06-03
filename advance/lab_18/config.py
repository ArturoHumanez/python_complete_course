from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite:///orders.db"
    debug: bool = False
    api_title: str = "Orders API"
    access_token_expire_minutes: int = 30

    model_config = {"env_file": ".env", "env_prefix": "APP_"}


settings = Settings()
