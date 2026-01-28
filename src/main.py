import asyncio
import tkinter as tk

from utils import ask
from modules.parser import Parser
from modules.auth import AuthModule
from modules.downloader import Downloader
from config import settings, configure_logging


async def main() -> None:
    configure_logging()

    win = tk.Tk()
    win.withdraw()

    if (
        not settings.user_config.exists() 
        or ask("Save cookies again?")
    ):
        auth_module = AuthModule()
        await auth_module.save_auth_cookies()

    manga_url = str(input("Manga URL: "))
    parser = Parser(manga_url)
    chapter_ids = parser.collect_chapter_ids()

    downloader = Downloader()
    full_chapter_ids = await downloader.get_full_chapter_ids(
        parser.news_id, chapter_ids
    )
    await downloader.download_chapters(full_chapter_ids)


if __name__ == "__main__":
    asyncio.run(main())
