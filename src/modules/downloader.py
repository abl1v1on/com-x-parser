import json
import asyncio

import aiofiles
from httpx import AsyncClient, Response

from . import get_client
from config import settings


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
        self._show_result(len(full_chapter_ids))

    async def download_single_chapter(
        self,
        client: AsyncClient,
        full_chapter_id: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        try:
            async with semaphore:
                async with client.stream(
                    "GET", f"/{full_chapter_id}",
                ) as response:
                    response.raise_for_status()
                    await self._write_content_to_file(response)
        except Exception as e:
            print(
                "Ошибка при запросе на загрузку "
                f"главы (ID {full_chapter_id}): {e}"
            )

    async def _write_content_to_file(
        self, 
        response: Response
    ) -> None:
        filename = self._get_filename(response)
        print(f"Downloading {filename}")

        try:
            async with aiofiles.open(
                settings.downloader.download_dir / filename, 
                mode="wb"
            ) as file:
                async for chunk in response.aiter_bytes():
                    await file.write(chunk)
        except Exception as e:
            print(
                f"Ошибка при сохранении файла {filename}: {e}"
            )

    @staticmethod
    async def _get_cookies() -> dict:
        async with aiofiles.open(
            settings.login.cookies_path, 
            mode="r",
        ) as file:
            return json.loads(await file.read())

    @staticmethod
    def _get_filename(response: Response) -> str:
        headers = response.headers
        disposition = headers["content-disposition"]
        return disposition.split("=")[-1].replace('"', "")

    @staticmethod
    def _show_result(total: int) -> None:
        files_count = len(
            [
                _ for _ in 
                settings.downloader.download_dir.iterdir()
            ]
        )
        print(f"Установлено {files_count} из {total} файлов!")
