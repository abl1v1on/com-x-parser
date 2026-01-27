import json
import logging

import aiofiles

from . import get_client
from config import settings


logger = logging.getLogger(__name__)


class AuthModule:
    async def save_auth_cookies(self) -> None:
        async with get_client() as client:
            form_data = {
                "login_name": settings.login.name,
                "login_password": settings.login.password,
                "login": "submit",
            }

            logger.info("Send response to get auth cookies")
            response = await client.post(
                "/home", 
                data=form_data
            )

            cookies = response.headers.get("set-cookie")
            clean_cookies = dict()

            for cookie in cookies.split(";"):
                if "=" in cookie:
                    parts = cookie.split(",")[-1].split("=")

                    if (
                        "PHPSESSID" in parts[0] 
                        or "dle" in parts[0]
                    ):
                        key, value = parts
                        clean_cookies[key.strip()] = value

            await self._write_cookies_to_file(clean_cookies)

    @staticmethod
    async def _write_cookies_to_file(cookies: dict) -> None:
        async with aiofiles.open(
            settings.login.cookies_path, 
            mode="w"
        ) as file:
            content = json.dumps(
                cookies, 
                indent=2, 
                ensure_ascii=False,
            )
            logger.info(
                "Write auth cookies to "
                f"{settings.login.cookies_path}"
            )
            await file.write(content)
