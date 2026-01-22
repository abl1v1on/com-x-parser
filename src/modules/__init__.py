from typing import AsyncGenerator
from contextlib import asynccontextmanager

from httpx import AsyncClient, Timeout


@asynccontextmanager
async def get_client(
    base_url: str = "https://com-x.life"
) -> AsyncGenerator[AsyncClient, None]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
    }

    async with AsyncClient(
        base_url=base_url,
        timeout=Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=1.0
        ),
        headers=headers,
    ) as client:
        yield client
