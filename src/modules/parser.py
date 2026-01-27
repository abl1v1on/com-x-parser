import json
import logging

import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from config import settings
from utils import ask, get_user_agent


logger = logging.getLogger(__name__)


class Parser:
    def __init__(self, url: str) -> None:
        self.driver = self._init_driver()
        self.driver.implicitly_wait(5)
        self.url = url
        self.news_id = url.split("/")[-1].split("-")[0]

    def collect_chapter_ids(self) -> list[str]:
        self.driver.get(self.url)

        if ask("Collect metadata?"):
            self.collect_metadata()

        self.to_chapters_btn.click()
        self.show_from_first_chapter_btn.click()

        chapter_ids = []

        logger.info("Start chapter IDs collecting")
        while True:
            try:
                for chapter in self.chapters_on_page:
                    href = chapter.get_attribute("href")
                    chapter_id = href.split("/")[-1] # type: ignore
                    chapter_ids.append(chapter_id)
                
                self.to_next_page.click()
            except NoSuchElementException:
                self.driver.quit()
                break
        
        logger.info("Chapter IDs collected")
        return chapter_ids

    def collect_metadata(self) -> None:
        logger.info("Start metadata collecting")
        settings.metadata_path.mkdir(exist_ok=True)
        
        self._save_poster()

        with open(
            settings.metadata_path / "data.json", 
            mode="w",
            encoding="utf-8",
        ) as file:
            manga_name = self.manga_name.text
            clean_tags = [
                tag.text.capitalize() 
                for tag in self.tags
            ]

            content = json.dumps(
                {
                    "name": manga_name,
                    "description": self.description.text,
                    "tags": clean_tags,
                },
                indent=2,
                ensure_ascii=False,
            )

            logger.info(
                "Write manga info to "
                f"{settings.metadata_path / "data.json"}"
            )
            file.write(content)
        logger.info("Metadata collected")

    @property
    def to_chapters_btn(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR, 
            "[data-tab='chapters']",
        ) # type: ignore

    @property
    def show_from_first_chapter_btn(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR, 
            ".cl__action",
        ) # type: ignore

    @property
    def chapters_on_page(self) -> list[WebElement]:
        return self._find(
            By.CSS_SELECTOR, 
            ".cl__item a", 
            many=True
        ) # type: ignore

    @property
    def to_next_page(self) -> WebElement:
        return self._find(
            By.XPATH, 
            "//a[text()='Вперед']",
        ) # type: ignore

    @property
    def manga_name(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR, 
            ".page__header h1"
        ) # type: ignore

    @property
    def poster(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR, 
            ".page__poster img",
        ) # type: ignore

    @property
    def description(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR,
            ".page__text",
        ) # type: ignore

    @property
    def tags(self) -> list[WebElement]:
        return self._find(
            By.CSS_SELECTOR,
            ".page__tags a",
            many=True
        ) # type: ignore

    def _find(
        self, 
        by: str, 
        value: str, 
        many: bool = False,
    ) -> WebElement | list[WebElement]:
        if many:
            return self.driver.find_elements(by, value)
        return self.driver.find_element(by, value)

    @staticmethod
    def _init_driver() -> Chrome:
        service = Service(ChromeDriverManager().install())
        options = Options()
        
        for option in settings.driver.chrome_options:
            options.add_argument(option)

        for option in settings.driver.chrome_experimental_options:
            options.add_experimental_option(*option)

        driver = Chrome(service=service, options=options)
        return driver

    def _save_poster(self) -> None:
        poster_url = str(self.poster.get_attribute("src"))

        logger.info("Send response to get manga poster")
        response = requests.get(
            url=poster_url,
            headers={
                "User-Agent": get_user_agent(),
            },
        )

        with open(
            settings.metadata_path / "poster.jpg", 
            mode="wb",
        ) as file:
            logger.info(
                "Write poster to "
                f"{settings.metadata_path / "poster.jpg"}"
            )
            file.write(response.content)
