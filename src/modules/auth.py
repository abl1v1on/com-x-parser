import json
import logging
from getpass import getpass

import aiofiles

from . import get_client
from config import settings


logger = logging.getLogger(__name__)


class AuthModule:
    async def save_auth_cookies(self) -> None:
        if not settings.user_config.exists():
            username = input("Username: ").strip()
            password = getpass().strip()

            async with aiofiles.open(
                settings.user_config, 
                mode="w"
            ) as file:
                content = json.dumps(
                    {
                        "username": username,
                        "password": password,
                    }, 
                    indent=4, 
                    ensure_ascii=False
                )
                await file.write(content)

        async with get_client() as client:
            form_data = {
                "login_name": settings.username,
                "login_password": settings.password,
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
        if settings.user_config.exists():
            async with aiofiles.open(
                settings.user_config, 
                mode="r",
            ) as file:
                user_config_obj = json.loads(
                    await file.read(),
                )
        else:
            user_config_obj = dict()

        async with aiofiles.open(
            settings.user_config, 
            mode="w",
        ) as file:
            user_config_obj["cookies"] = cookies
            content = json.dumps(
                user_config_obj, 
                indent=4, 
                ensure_ascii=False
            )

            logger.info(
                "Write auth cookies to "
                f"{settings.user_config}"
            )
            await file.write(content)
