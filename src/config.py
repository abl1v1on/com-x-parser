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


class DownloaderSettings(BaseModel):
    full_chapter_id_url: str = (
        "/engine/ajax/controller.php?"
        "mod=api&action=chapters/download"
    )
    download_chapter_url: str = "https://rus.com-x.life/download"
    download_dir: Path = BASE_DIR / "downloads"

class Settings(BaseSettings):
    login: LoginSettings
    downloader: DownloaderSettings = DownloaderSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


settings = Settings() # type: ignore

