import logging
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings, 
    SettingsConfigDict,
)

from utils import get_download_folder


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
    download_chapter_url: str = (
        "https://rus.com-x.life/download"
    )
    download_dir: Path = get_download_folder()


class DriverSettings(BaseModel):
    chrome_options: list[str] = [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--disable-blink-features=AutomationControlled",
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    ]
    chrome_experimental_options: list[tuple] = [
        ("excludeSwitches", ["enable-automation"]),
        ('useAutomationExtension', False),
    ]


class Settings(BaseSettings):
    login: LoginSettings
    driver: DriverSettings = DriverSettings()
    downloader: DownloaderSettings = DownloaderSettings()

    @property
    def metadata_path(self) -> Path:
        return self.downloader.download_dir / "metadata"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


settings = Settings() # type: ignore
