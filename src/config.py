from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)


BASE_DIR = Path(__file__).parent.parent


class LoginSettings(BaseModel):
    name: str
    password: str
    cookies_path: Path = BASE_DIR / "cookies.json"


class Settings(BaseSettings):
    login: LoginSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


settings = Settings() # type: ignore

