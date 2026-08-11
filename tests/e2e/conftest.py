import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5000"


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--window-size=1280,800")

    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin

    is_ci = os.environ.get("CI")
    if is_ci:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # En CI dejamos que el Selenium Manager integrado (Selenium 4+)
        # detecte y descargue el chromedriver que coincide exactamente
        # con el Chrome que se instaló en el workflow, en vez de
        # webdriver-manager, que no encuentra bien esta ruta no estándar.
        drv = webdriver.Chrome(options=options)
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        if not driver_path.endswith("chromedriver.exe"):
            driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        service = Service(driver_path)
        drv = webdriver.Chrome(service=service, options=options)

    drv.implicitly_wait(2)
    yield drv
    drv.quit()