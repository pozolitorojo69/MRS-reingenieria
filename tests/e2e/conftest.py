import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1280,800")

    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin

    if os.environ.get("CI"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver_path = ChromeDriverManager().install()
    if not driver_path.endswith("chromedriver.exe") and not driver_path.endswith("chromedriver"):
        driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe" if os.name == "nt" else "chromedriver")
    service = Service(driver_path)

    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()