from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


class Parser:
    def __init__(self, url: str) -> None:
        self.driver = self._init_driver()
        self.driver.implicitly_wait(5)
        self.url = url
        self.news_id = url.split("/")[-1].split("-")[0]

    def collect_chapter_ids(self) -> list[str]:
        self.driver.get(self.url)
        self.to_chapters_btn.click()
        self.show_from_first_chapter_btn.click()

        chapter_ids = []

        while True:
            try:
                for chapter in self.chapters_on_page:
                    href = chapter.get_attribute("href")
                    chapter_id = href.split("/")[-1] # type: ignore
                    chapter_ids.append(chapter_id)
                
                self.to_next_page.click()
            except NoSuchElementException:
                break
        return chapter_ids

    @property
    def to_chapters_btn(self) -> WebElement:
        return self._find(
            By.CSS_SELECTOR, "[data-tab='chapters']"
        ) # type: ignore

    @property
    def show_from_first_chapter_btn(self) -> WebElement:
        return self._find(By.CSS_SELECTOR, ".cl__action") # type: ignore

    @property
    def chapters_on_page(self) -> list[WebElement]:
        return self._find(
            By.CSS_SELECTOR, 
            ".cl__item a", 
            many=True
        ) # type: ignore

    @property
    def to_next_page(self) -> WebElement:
        return self._find(By.XPATH, "//a[text()='Вперед']") # type: ignore

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
        driver = Chrome(service=service)
        return driver
