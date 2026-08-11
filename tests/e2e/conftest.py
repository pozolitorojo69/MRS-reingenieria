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
    # Para correr en modo visual (necesario para tu evidencia local),
    # deja estas líneas comentadas. Para CI, se activan (ver Fase 5).
    # options.add_argument("--headless=new")

    driver_path = ChromeDriverManager().install()
    if not driver_path.endswith("chromedriver.exe"):
        driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
    service = Service(driver_path)

    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(2)
    yield drv
    drv.quit()