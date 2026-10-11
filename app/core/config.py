from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", extra="ignore")

    mistral_api_key: SecretStr = SecretStr("")
    mistral_chat_model: str = "mistral-small-latest"
    mistral_direct_chat_model: str = "mistral-large-4"
    mistral_embed_model: str = "mistral-embed"
    vespa_url: str = "http://127.0.0.1:8085"
    log_level: str = "INFO"
    adzuna_app_id: str = ""
    adzuna_app_key: SecretStr = SecretStr("")
    adzuna_country: str = "fr"
    adzuna_results_per_page: int = 50
