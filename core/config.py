BASE_URL = "https://www.ozon.ru/product/"
WAIT_TIMEOUT = 50
RESULTS_DIR = "results"
FILENAME_TEMPLATE = "ozon_reviews_{}_{}.xlsx"
WAIT_TIMEOUT_GET_PRODUCT = 10

# Максимальное количество страниц отзывов, которые будет пытаться загрузить парсер
# (защита от бесконечного цикла, если что-то пойдёт не так с URL/пагинацией)
MAX_REVIEW_PAGES = 30
