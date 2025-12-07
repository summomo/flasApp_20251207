# tests/test_e2e.py
# Tests end-to-end avec Selenium.
# Nécessite :
# - que l'app soit lancée (python app.py)
# - que le WebDriver (ChromeDriver ou GeckoDriver) soit installé et dans le PATH.

import os
import time

import pytest
from selenium import webdriver

IS_CI = os.environ.get("CI") == "true"


BASE_URL = "http://localhost:5000"

@pytest.mark.skipif(IS_CI, reason="Skip E2E Selenium test in CI (no Chrome available)")
def test_login_flow_e2e():
    """
    Exemple très simple :
    - Va sur la page de login
    - Vérifie que la page s'affiche
    (Tu peux ensuite l'étendre avec login réel, création de compte, etc.)
    """
    # Démarre le navigateur (ici Chrome, tu peux utiliser Firefox si tu préfères)
    driver = webdriver.Chrome()  # ou webdriver.Firefox()

    try:
        driver.get(f"{BASE_URL}/login")
        time.sleep(1)

        # Vérifie que le titre de la page contient "Login" (ou un texte spécifique)
        assert "Login" in driver.page_source or "username" in driver.page_source

        # Ici, tu peux ajouter les étapes :
        # - remplir username/password
        # - cliquer sur le bouton "Login"
        # - vérifier la redirection vers "/"
    finally:
        driver.quit()
