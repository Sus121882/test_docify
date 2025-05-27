from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

from ..utils.navegador import iniciar_navegador

# Função para verificar se um elemento está presente ou não na página.
def is_element_present(driver, how, what): 
    try: driver.find_element(by=how, value=what)
    except NoSuchElementException as e: return False
    return True

# Função de login fornecida
def login_com_chave(driver, wait, chave, senha):
    """
    Realiza o login no portal do BB usando a chave e a senha informadas.
    
    :param driver: Instância do WebDriver do Selenium.
    :param wait: Instância do WebDriverWait do Selenium.
    :param chave: Chave de acesso do usuário.
    :param senha: Senha de acesso do usuário.
    :return: None
    """
    driver.get('https://juridico.intranet.bb.com.br/paj/app/')
    try:
        # Aguarda até que o campo de usuário esteja presente
        username = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="idToken1"]')))
        username.send_keys(chave)
        
        # Preenche o campo de senha
        senha_input = driver.find_element(By.XPATH, '//*[@id="idToken3"]')
        senha_input.send_keys(senha)
        
        # Clica no botão de login
        login_button = driver.find_element(By.XPATH, '//*[@id="loginButton_0"]')
        login_button.click()
        
        # Aguarda até que um elemento específico pós-login esteja presente
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="j_id90"]/table/tbody/tr/td/table/tbody/tr[1]/td')))
        
        print("Login realizado com sucesso.")
    except Exception as e:
        print("Ocorreu um erro durante o login:", e)
        driver.quit()
        exit()
        
def login_manual(driver, headless=False):
    """
    Realiza o login manual no portal do BB, atenção navegador não pode estar headless.
    
    :param driver: Instância do WebDriver do Selenium.
    :param headless: Define se o navegador vai ficar em modo headless ou não (default: False, PS: Demora mais para iniciar o programa).
    :return: Caso headless seja True, retorna o driver e o wait para serem usados no programa, caso contrário, retorna None.
    """
    driver.get('https://juridico.intranet.bb.com.br/paj/app/')
    
    while not is_element_present(driver, By.XPATH, "//*[contains(text(), 'Portal Jurídico')]"):
        time.sleep(0.5)
        
    if headless:
        cookies = driver.get_cookies()
        
        driver.quit()
        
        driver, wait = iniciar_navegador(True)
        
        driver.get('https://juridico.intranet.bb.com.br/paj/app/')
        
        for cookie in cookies:
            if 'juridico' in cookie['domain']:
                driver.get('https://juridico.intranet.bb.com.br/paj/app/')
                while 'juridico.intranet.bb.com.br' not in driver.current_url:
                    time.sleep(0.1)
            driver.add_cookie(cookie)
            
        return driver, wait