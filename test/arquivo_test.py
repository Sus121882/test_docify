import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time
import json

from DijurLib.utils.navegador import iniciar_navegador
from DijurLib.portal.login import login_manual, login_com_chave
from DijurLib.api.consulta import get_processos_npj

# Carregar as credenciais do arquivo .env
CHAVE = ''
SENHA = ''

def main():
    driver, wait = iniciar_navegador(True)
    
    try:          
        login_com_chave(driver, wait, CHAVE, SENHA)
        
        processos = get_processos_npj(driver, '20150083163')
        
        id_processo = processos['listaOcorrencia'][0]['numeroProcesso']
        
        print(id_processo)

    finally:
        # Fecha o navegador
        driver.quit()

if __name__ == "__main__":
    main()