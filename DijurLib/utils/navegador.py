from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

# Inicializar o navegador Edge usando webdriver-manager
def iniciar_navegador(headless: bool = False, wait_time: int = 30):
    """
    Inicializa o navegador Edge com as opções especificadas.
    Define o tempo máximo de espera.
    Defalt: headless=False, wait_time=30.
    
    :param headless: Se True, o navegador será iniciado em modo headless.
    :param wait_time: Tempo máximo de espera para localizar elementos na página
    :return: Instância do WebDriver do Selenium e wait
    """
    options = webdriver.EdgeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('prefs', {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})
    
    driver = webdriver.Edge(options=options)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, wait_time)
    return driver, wait