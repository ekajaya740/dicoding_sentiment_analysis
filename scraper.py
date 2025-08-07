import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

wait = WebDriverWait(driver, 10)


url = "https://www.imdb.com/title/tt0068646/reviews/?spoilers=EXCLUDE"

print("Opening the page with Selenium...")
driver.get(url)

review_section_locator = (By.CSS_SELECTOR, "section.ipc-page-section")
pagination_locator = (By.CSS_SELECTOR, "div.pagination-container")
all_button_locator = (
    By.CSS_SELECTOR,
    "div.pagination-container > :nth-child(2) > button",
)
next_25_button_locator = (
    By.CSS_SELECTOR,
    "div.pagination-container > span > button",
)


review_section = wait.until(EC.presence_of_element_located(review_section_locator))
all_button = wait.until(EC.element_to_be_clickable(all_button_locator))

driver.execute_script("arguments[0].click();", all_button)

time.sleep(600)


review_articles = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.user-review-item"))
)

all_reviews_data = []

print(f"Found {len(review_articles)} reviews to process...")


for review in review_articles:
    try:
        star_rating = review.find_element(
            By.CSS_SELECTOR, "span.review-rating > span"
        ).text
        title = review.find_element(By.CSS_SELECTOR, "div.ipc-title").text
        description = review.find_element(By.CSS_SELECTOR, "div.ipc-overflowText").text

        all_reviews_data.append(
            {"rating": star_rating, "title": title, "description": description}
        )

    except Exception as e:

        print(f"Skipping a malformed review card. Error: {e}")
        continue

print(f"Successfully extracted data from {len(all_reviews_data)} reviews.")


csv_file_name = "reviews.csv"


csv_headers = ["rating", "title", "description"]

try:
    with open(csv_file_name, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=csv_headers)

        writer.writeheader()

        writer.writerows(all_reviews_data)

    print(f"\nSuccessfully saved data to {csv_file_name}")

except IOError:
    print("I/O error while writing to the CSV file.")
