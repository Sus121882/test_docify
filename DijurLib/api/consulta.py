from typing import List
from selenium.webdriver.remote.webdriver import WebDriver
from .base import get_api_navegador, post_api_navegador
from ..utils.schema.schemaConsulta import ResponseProcessos, ProcessosResponse, Processo, DataProcessos, DataRespostaSimples, ProcessoRespostaSimples, RespostaProcessosSimples

def extrair_quantidade(data: DataProcessos) -> int:
    """
    Extrai a quantidade de ocorrências ou registros de maneira unificada.

    :param data: Dicionário contendo os dados da API.
    :return: Quantidade de registros/ocorrências.
    """
    return data.get("quantidadeRegistro") or data.get("quantidadeOcorrencia") or 0

def get_processos_npj(driver: WebDriver, npj: str) -> ProcessosResponse:
    """
    Obtém os processos de um determinado Número de Processo Judicial (NPJ) a partir da API da Dijur.

    :param driver: Instância do WebDriver do Selenium.
    :param npj: Número de Processo Judicial a ser consultado.
    :return: Dicionário com informações dos processos.
    :raises ValueError: Se npj não for uma string válida.
    :raises Exception: Se houver erro ao acessar a API.
    """
    if not isinstance(npj, str):
        try:
            npj = str(npj)
        except ValueError:
            raise ValueError("npj deve ser uma string válida.")
        
    npj = npj.replace("/", "").replace("-", "")

    npj1, npj2 = npj[:11], npj[11:]

    if npj2 == "":
        npj2 = "-1"   

    api_url = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/{npj1}/{npj2}/0"
    
    # Obter dados da API via GET
    response: ResponseProcessos = get_api_navegador(driver, api_url)
    
    # Verificar status da resposta
    if response.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    data: DataProcessos = response.get("data", {})
    
    quantidade = extrair_quantidade(data)
    indicador_continuidade = data.get("indicadorContinuidade", "")
    lista_ocorrencia: List[Processo] = data.get("listaOcorrencia", [])
    
    resultado: ProcessosResponse = {
        "quantidade": quantidade,
        "indicadorContinuidade": indicador_continuidade,
        "listaOcorrencia": lista_ocorrencia
    }
    
    return resultado

def get_processo_numerodoprocesso(driver: WebDriver, numerodoprocesso: str) -> ProcessosResponse:
    """
    Obtém os dados de um processo a partir do seu Número do Processo.

    :param driver: Instância do WebDriver do Selenium.
    :param numerodoprocesso: Número do Processo a ser consultado.
    :return: Dicionário com informações dos processos.
    :raises ValueError: Se numerodoprocesso não for uma string válida.
    :raises Exception: Se houver erro ao acessar a API.
    """
    if not isinstance(numerodoprocesso, str):
        raise ValueError("numerodoprocesso deve ser uma string.")
    
    payload = {
        "numeroProcesso": numerodoprocesso,
        "unidadeJuridica": 0,
        "ajuizado": "S",
        "estadoNPJ": "A",
        "tipoVariacao": "T",
        "inicioPesquisa": 0
    }
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/consulta-numero-processo"
    
    # Obter dados da API via POST
    response: ResponseProcessos = post_api_navegador(driver, url, payload)
    
    # Verificar status da resposta
    if response.get("statusCode") != 200 and response.get("status") != "OK":
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    data: DataProcessos = response.get("data", {})
    
    quantidade = extrair_quantidade(data)
    indicador_continuidade = data.get("indicadorContinuidade", "")
    lista_ocorrencia: List[Processo] = data.get("listaOcorrencia", [])
    
    resultado: ProcessosResponse = {
        "quantidade": quantidade,
        "indicadorContinuidade": indicador_continuidade,
        "listaOcorrencia": lista_ocorrencia
    }
    
    return resultado

def get_processo_numerodoprocesso_simples(driver: WebDriver, numerodoprocesso: str) -> RespostaProcessosSimples:
    """
    Obtém os dados de um processo a partir do seu Número do Processo de maneira simplificada.

    :param driver: Instância do WebDriver do Selenium.
    :param numerodoprocesso: Número do Processo a ser consultado.
    :return: Dicionário com informações dos processos.
    :raises ValueError: Se numerodoprocesso não for uma string válida.
    :raises Exception: Se houver erro ao acessar a API.
    """
    if not isinstance(numerodoprocesso, str):
        raise ValueError("numerodoprocesso deve ser uma string.")
    
    # Obter dados da API via POST
    response: ResponseProcessos = get_api_navegador(driver, f'https://juridico.intranet.bb.com.br/paj/resources/app/portal/cadastro/processo/pesquisa-avancada/numero-processo/{numerodoprocesso}')
    
    # Verificar status da resposta
    if response.get("statusCode") != 200 and response.get("status") != "OK":
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    data: DataRespostaSimples = response.get("data", {})
    
    processos: List[ProcessoRespostaSimples] = data.get("processos", [])
    posicao_inicial = data.get("posicaoInicial", 0)
    posicao_final = data.get("posicaoFinal", 0)
    has_next = data.get("hasNext", False)
    has_previous = data.get("hasPrevious", False)
    
    resultado: RespostaProcessosSimples = {
        "processos": processos,
        "posicaoInicial": posicao_inicial,
        "posicaoFinal": posicao_final,
        "hasNext": has_next,
        "hasPrevious": has_previous
    }
    
    return resultado

def get_processo_id_npj(driver: WebDriver, id_npj: int) -> Processo:
    """
    Obtém os dados de um processo a partir do seu ID do NPJ.

    :param driver: Instância do WebDriver do Selenium.
    :param id_npj: ID do NPJ a ser consultado.
    :return: Dicionário com informações dos processos.
    :raises ValueError: Se id_npj não for um inteiro.
    :raises Exception: Se houver erro ao acessar a API.
    """
    if not isinstance(id_npj, int):
        raise ValueError("id_npj deve ser um inteiro.")
    
    api_url = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/{id_npj}"
    
    # Obter dados da API via GET
    response: ResponseProcessos = get_api_navegador(driver, api_url)
    
    # Verificar status da resposta
    if response.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    data: Processo = response.get("data", {})
    
    return data