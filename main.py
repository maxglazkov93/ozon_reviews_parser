from core.config import BASE_URL
from core.scraping.page_loader import PageLoader
from core.scraping.review_extractor import ReviewExtractor
from core.utils.excel_saver import ExcelSaver
from core.utils.webdriver import WebDriverManager

if __name__ == "__main__":
    product_ids = input("Введите артикулы товаров через запятую: ").split(",")
    product_ids = [pid.strip() for pid in product_ids if pid.strip()]

    all_reviews = []
    for pid in product_ids:
        driver = WebDriverManager.create_webdriver()
        page_loader = PageLoader(driver)

        # 1. Открываем карточку товара
        page_loader.load_page(f"{BASE_URL}{pid}/")
        page_loader.do_not_adress()
        page_loader.accept_cookies()

        # 2. Получаем название товара один раз
        product_name = ReviewExtractor.get_product_name(driver)

        # 3. Переходим в раздел отзывов и крутимся по страницам
        if page_loader.open_reviews_section():
            page_number = 1

            while True:
                # еще раз принимаем куки
                page_loader.accept_cookies()
                # Загружаем все отзывы на текущей странице (скролл до конца)
                page_loader.scroll_to_load_reviews()

                # Парсим отзывы с текущей страницы
                page_reviews = ReviewExtractor.extract_reviews(
                    driver, pid, product_name
                )

                # Если на странице отзывов не оказалось — заканчиваем цикл для этого товара
                if not page_reviews:
                    break

                all_reviews.extend(page_reviews)

                # Переходим на следующую страницу; если не получилось — завершаем цикл
                if not page_loader.go_to_next_reviews_page(page_number):
                    break

                page_number += 1

        driver.quit()

    ExcelSaver.save_to_excel(all_reviews, product_ids)
