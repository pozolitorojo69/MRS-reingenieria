from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from .conftest import BASE_URL


def test_home_page_loads_with_form(driver):
    driver.get(BASE_URL)
    assert "CineMatch" in driver.title or "CineMatch" in driver.page_source
    assert driver.find_element(By.ID, "recommendationForm") is not None


def test_search_by_title_shows_movie_cards(driver):
    driver.get(BASE_URL)

    driver.find_element(By.ID, "movieTitle").send_keys("Inception")
    Select(driver.find_element(By.ID, "genre")).select_by_visible_text("Action")
    driver.find_element(By.ID, "minRating").send_keys("0")
    driver.find_element(By.ID, "getRecommendations").click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".movie-card, .no-results-container"))
    )
    cards = driver.find_elements(By.CSS_SELECTOR, ".movie-card")
    assert len(cards) > 0, "Se esperaban recomendaciones para 'Inception'"


def test_search_with_no_results_shows_message(driver):
    driver.get(BASE_URL)

    driver.find_element(By.ID, "movieTitle").send_keys("asdkjqwoiexxxxnonexistentmovie123")
    Select(driver.find_element(By.ID, "genre")).select_by_visible_text("Action")
    driver.find_element(By.ID, "minRating").send_keys("0")
    driver.find_element(By.ID, "getRecommendations").click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".movie-card, .no-results-container"))
    )
    no_results = driver.find_elements(By.CSS_SELECTOR, ".no-results-container")
    assert len(no_results) > 0


def test_more_info_opens_modal_with_movie_details(driver):
    driver.get(BASE_URL)

    driver.find_element(By.ID, "movieTitle").send_keys("Inception")
    Select(driver.find_element(By.ID, "genre")).select_by_visible_text("Action")
    driver.find_element(By.ID, "minRating").send_keys("0")
    driver.find_element(By.ID, "getRecommendations").click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".movie-card"))
    )
    driver.find_element(By.CSS_SELECTOR, ".more-info-btn").click()

    modal_title = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".movie-modal.fade-in .modal-content h2"))
    )
    title_text = modal_title.get_attribute("textContent").strip()
    assert title_text != ""