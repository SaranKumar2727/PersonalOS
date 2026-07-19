from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./personal_os.db"
    jwt_secret: str = "development-only-secret"
    jwt_algorithm: str = "HS256"
    openai_api_key: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    github_client_id: str | None = None
    oauth_redirect_url: str = "http://localhost:8000/api/v1/auth/oauth/callback"
    frontend_url: str = "http://localhost:5173"


settings = Settings()
