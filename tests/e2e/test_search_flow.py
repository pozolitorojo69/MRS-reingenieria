from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from .conftest import BASE_URL


def search_by_title(driver, title, genre="Action"):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "movieTitle").send_keys(title)
    Select(driver.find_element(By.ID, "genre")).select_by_visible_text(genre)
    driver.find_element(By.ID, "minRating").send_keys("0")
    driver.find_element(By.ID, "getRecommendations").click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".movie-card, .no-results-container"))
    )


def search_with_retries(driver, title, genre="Action", attempts=3):
    """TMDB (API externa) a veces responde lento o falla desde el runner de CI.
    Reintentamos la búsqueda un par de veces antes de dar la prueba por fallida,
    en vez de depender de que la red externa funcione a la primera."""
    for attempt in range(attempts):
        search_by_title(driver, title, genre)
        cards = driver.find_elements(By.CSS_SELECTOR, ".movie-card")
        if cards:
            return cards
    return []


def test_home_page_loads_with_form(driver):
    driver.get(BASE_URL)
    assert "CineMatch" in driver.title or "CineMatch" in driver.page_source
    assert driver.find_element(By.ID, "recommendationForm") is not None


def test_search_by_title_shows_movie_cards(driver):
    cards = search_with_retries(driver, "Inception")
    assert len(cards) > 0, "Se esperaban recomendaciones para 'Inception' tras varios intentos"


def test_search_with_no_results_shows_message(driver):
    search_by_title(driver, "asdkjqwoiexxxxnonexistentmovie123")
    no_results = driver.find_elements(By.CSS_SELECTOR, ".no-results-container")
    assert len(no_results) > 0


def test_more_info_opens_modal_with_movie_details(driver):
    cards = search_with_retries(driver, "Inception")
    assert len(cards) > 0, "No se pudo obtener ninguna tarjeta para probar el modal"

    driver.find_element(By.CSS_SELECTOR, ".more-info-btn").click()

    modal_title = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".movie-modal.fade-in .modal-content h2"))
    )
    title_text = modal_title.get_attribute("textContent").strip()
    assert title_text != ""