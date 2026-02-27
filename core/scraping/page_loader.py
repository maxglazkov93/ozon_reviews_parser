from urllib.parse import urlparse, parse_qs, urljoin

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import MAX_REVIEW_PAGES, WAIT_TIMEOUT


class PageLoader:
    """Класс для загрузки страниц и обработки навигации."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)

    def load_page(self, url):
        """Загружает указанную страницу."""
        self.driver.get(url)

    def do_not_adress(self):
        """Убирает предложение добавить адрес в избранное"""
        try:
            button = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "checkout_oa6"))
            )
            button[1].click()
        except Exception:
            pass

    def accept_cookies(self):
        """Принимает файлы cookie, если появляется запрос."""
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "uw_f2a"))
            )
            button.click()
        except Exception:
            pass

    def _find_reviews_button(self, driver):
        """Ищет кнопку для открытия раздела с отзывами."""
        elems = driver.find_elements(
            By.XPATH, "//a[contains(@class, 'ga5_3_11-a')]"
        )
        if elems:
            print("Нашел", elems[0].get_attribute("href"))
            return elems[0].get_attribute("href")
        driver.execute_script("window.scrollBy(0, 400);")
        return False

    def open_reviews_section(self) -> bool:
        """Открывает раздел с отзывами (первую страницу)."""
        try:
            button = self.wait.until(self._find_reviews_button)
            self.driver.get(button)
            print("Перехожу в раздел отзывов")
            return True
        except TimeoutException:
            return False

    def scroll_to_load_reviews(self):
        """Прокручивает страницу для загрузки всех отзывов на ТЕКУЩЕЙ странице."""
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            try:
                self.wait.until(
                    lambda d: d.execute_script(
                        "return document.body.scrollHeight"
                    )
                    > last_height
                )
                last_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
            except Exception:
                break

    def _find_next_reviews_page(self, next_page: int):
        """
        Ищет ссылку на следующую страницу отзывов.

        Логика: среди ссылок пагинации находим <a> с href, в котором закодирован
        номер страницы next_page, и возвращаем сам WebElement (его можно кликнуть).
        """

        def _predicate(driver):
            # Ограничиваемся ссылками пагинации, чтобы не перебирать весь DOM
            anchors = driver.find_elements(
                By.XPATH, "//a[contains(@class, 'kt0_28') and @href]"
            )

            current_url = driver.current_url

            for a in anchors:
                href = a.get_attribute("href")
                if not href:
                    continue

                # На всякий случай нормализуем относительные ссылки
                href_abs = urljoin(current_url, href)
                parsed = urlparse(href_abs)
                query = parse_qs(parsed.query)

                page_value = query.get("page", [None])[0]
                if (
                    isinstance(page_value, str)
                    and page_value.isdigit()
                    and int(page_value) == next_page
                ):
                    # Иногда элемент может быть не кликабельным из-за перекрытия,
                    # но wait.until вернёт его, а клик сделаем через JS.
                    return a

            # Если не нашли — чуть прокрутим, чтобы пагинатор проявился/подгрузился
            driver.execute_script("window.scrollBy(0, 400);")
            return False

        return _predicate

    def go_to_next_reviews_page(self, current_page: int) -> bool:
        """
        Переходит на следующую страницу отзывов, кликая по ссылке пагинации.

        current_page — номер текущей страницы (начиная с 1).
        Возвращает True, если переход выполнен, иначе False.
        """
        if current_page >= MAX_REVIEW_PAGES:
            # Достигли лимита страниц — выходим из пагинации
            return False

        next_page = current_page + 1
        previous_url = self.driver.current_url

        try:
            next_link = self.wait.until(self._find_next_reviews_page(next_page))
            self.driver.execute_script("arguments[0].click();", next_link)
            print(f"Перехожу на страницу отзывов {next_page}")

            # Ждём, пока URL сменится (или произойдёт навигация в рамках SPA)
            self.wait.until(lambda d: d.current_url != previous_url)
            return True
        except TimeoutException:
            return False
        except Exception:
            return False
