import json
import asyncio
import logging

import aiofiles
from httpx import AsyncClient, Response

from . import get_client
from config import settings


logger = logging.getLogger(__name__)


class Downloader:
    async def get_full_chapter_ids(
        self, 
        news_id: str, 
        chapter_ids: list[str]
    ) -> list[str]:
        async with get_client() as client:
            cookies = await self._get_cookies()
            full_chapter_ids = []
            semaphore = asyncio.Semaphore(10)
            tasks = []

            logger.info("Start full chapter IDs collecting")
            for chapter_id in chapter_ids:
                task = asyncio.create_task(
                    self.get_single_full_chapter_id(
                        client=client,
                        news_id=news_id,
                        cookies=cookies,
                        chapter_id=chapter_id,
                        semaphore=semaphore,
                    )
                )
                tasks.append(task)

            full_chapter_ids = await asyncio.gather(*tasks)
        
        logger.info("Chapter IDs collected")
        return full_chapter_ids

    @staticmethod
    async def get_single_full_chapter_id(
        client: AsyncClient,
        news_id: str,
        cookies: dict,
        chapter_id: str,
        semaphore: asyncio.Semaphore,
    ) -> str:
        async with semaphore:
            logger.info(
                "Send response to get "
                f"full id for {chapter_id}"
            )
            response = await client.post(
                settings.downloader.full_chapter_id_url,
                json={
                    "news_id": news_id, 
                    "chapter_id": chapter_id
                },
                cookies=cookies,
            )
            response.raise_for_status()

            data = response.json()
            full_id = data["data"].split("/")[-1]
            return full_id

    async def download_chapters(
        self, 
        full_chapter_ids: list[str],
    ) -> None:
        async with get_client(
            settings.downloader.download_chapter_url
        ) as client:
            tasks = []
            semaphore = asyncio.Semaphore(10)
            settings.downloader.download_dir.mkdir(
                exist_ok=True
            )

            logger.info("Start downloading chapters")
            for chapter_id in full_chapter_ids:
                task = asyncio.create_task(
                    self.download_single_chapter(
                        client=client,
                        full_chapter_id=chapter_id,
                        semaphore=semaphore,
                    )
                )
                tasks.append(task)
            await asyncio.gather(*tasks)
        
        logger.info("Chapters downloaded")
        self._show_result(len(full_chapter_ids))

    async def download_single_chapter(
        self,
        client: AsyncClient,
        full_chapter_id: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        try:
            async with semaphore:
                logger.info(
                    "Send response to download "
                    f"chapter with id {full_chapter_id}"
                )
                async with client.stream(
                    "GET", f"/{full_chapter_id}",
                ) as response:
                    response.raise_for_status()
                    await self._write_content_to_file(response)
        except Exception as e:
            logger.error(
                "Error when requesting to download "
                f"chapter {full_chapter_id}: {e}"
            )

    async def _write_content_to_file(
        self, 
        response: Response
    ) -> None:
        filename = self._get_filename(response)

        try:
            async with aiofiles.open(
                settings.downloader.download_dir / filename, 
                mode="wb"
            ) as file:
                logger.info(
                    f"Write {filename} to "
                    f"{settings.downloader.download_dir}"
                )
                async for chunk in response.aiter_bytes():
                    await file.write(chunk)
        except Exception as e:
            logger.error(f"Error when saving {filename}: {e}")

    @staticmethod
    async def _get_cookies() -> dict:
        async with aiofiles.open(
            settings.user_config, 
            mode="r",
        ) as file:
            return json.loads(await file.read())["cookies"]

    @staticmethod
    def _get_filename(response: Response) -> str:
        headers = response.headers
        disposition = headers["content-disposition"]
        return disposition.split("=")[-1].replace('"', "")

    @staticmethod
    def _show_result(total: int) -> None:
        files_count = len(
            [
                item for item in 
                settings.downloader.download_dir.iterdir()
                if item.is_file()
            ]
        )
        logging.info(
            f"\033[32m{files_count} out of "
            f"{total} files installed\033[0m"
        )
