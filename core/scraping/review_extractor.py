from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import WAIT_TIMEOUT_GET_PRODUCT


class ReviewExtractor:
    """Класс для извлечения отзывов из загруженной страницы."""

    @staticmethod
    def get_product_name(driver):
        """Извлекает название продукта с ожиданием появления элемента."""
        try:
            wait = WebDriverWait(driver, WAIT_TIMEOUT_GET_PRODUCT)
            element = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "pdp_ib6")
                )
            )
            print(element.text)
            return element.text.strip()
        except Exception:
            return "Не найдено"

    @staticmethod
    def extract_reviews(driver, product_id, product_name):
        """Извлекает отзывы о товаре."""
        soup = BeautifulSoup(driver.page_source, "html.parser")
        reviews_section = soup.find("div", class_="tl5_28")
        if not reviews_section:
            return []

        reviews = []
        for review in reviews_section.select("div.t6l_28"):
            reviewer = review.find("span", class_="k9r_28")
            reviewer = reviewer.get_text(strip=True) if reviewer else "Аноним"

            # Рейтинг на Ozon кодируется количеством "закрашенных" svg-звёзд
            # внутри контейнера div с классом a5d5_3_11-a.
            rating_element = review.find(
                "div",
                class_=lambda c: c and "a5d5_3_11-a" in c.split(),
            )
            rating = 0
            if rating_element:
                for star in rating_element.find_all("svg"):
                    style = (star.get("style") or "").replace(" ", "")
                    # Закрашенная звезда: color:var(--graphicRating);
                    if "color:var(--graphicRating)" in style:
                        rating += 1

            date_element = review.find("div", class_="ku7_28")
            review_date = (
                date_element.text.strip() if date_element else "Не найдено"
            )

            comment_element = review.find("span", class_="uk8_28")
            comment = (
                comment_element.get_text(strip=True)
                if comment_element is not None
                else ""
            )

            # purchase_state = review.find(
            #     "span", class_="feedback__state--text"
            # )
            # purchase_state = (
            #     purchase_state.get_text(strip=True) if purchase_state else ""
            # )

            reviews.append(
                {
                    "product_id": product_id,
                    "product_name": product_name,
                    "reviewer": reviewer,
                    "rating": rating,
                    "review_date": review_date,
                    # "advantages": advantages,
                    # "disadvantages": disadvantages,
                    "comment": comment,
                    # "purchase_state": purchase_state,
                }
            )

        return reviews
