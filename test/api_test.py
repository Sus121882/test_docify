import json
import inspect
import sys
from datetime import datetime, timedelta

# Função para imprimir "Hello, world!" na tela, usada para testar a biblioteca
def hello():
    """
    Imprime "Hello, world!" na tela.

    Exemplo de uso:
        >>> from apiDijur.test import hello
        >>> hello()
        Hello, world!
    """
    print("Hello, world")
    
# Função para fazer a requisição via navegador e obter o JSON, essa função sera usada para todas as funções de requisição GET
def get_api_navegador(driver, api_url):
    """
    Faz uma requisição GET para uma API via navegador e retorna o JSON obtido.
    
    :param driver: Instância do WebDriver do Selenium.
    :param api_url: URL da API a ser acessada.
    """
    try:
        print("Iniciando requisição...")
        
        # Executa um script assíncrono para fazer a requisição via fetch
        json_data = driver.execute_async_script("""
            const api_url = arguments[0];
            const callback = arguments[arguments.length - 1];
            fetch(api_url, {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => callback(data))
            .catch(error => callback({'error': error.toString()}));
        """, api_url)
        
        if 'error' in json_data:
            print(f"Erro na requisição: {json_data['error']}")

        else:
            print("Requisição bem-sucedida!")
            return json_data
    
    except Exception as e:
        print("Ocorreu um erro ao fazer a requisição via navegador:", e)

# Função para fazer a requisição via navegador e obter o JSON, essa função sera usada para todas as funções de requisição POST
def post_api_navegador(driver, api_url, payload):
    """
    Faz uma requisição POST para uma API via navegador e retorna o JSON obtido.
    
    :param driver: Instância do WebDriver do Selenium.
    :param api_url: URL da API a ser acessada.
    :param payload: Dicionário com os dados a serem enviados no corpo da requisição.
    """
    try:
        print("Iniciando requisição...")
        
        # Executa um script assíncrono para fazer a requisição via fetch
        json_data = driver.execute_async_script("""
            const api_url = arguments[0];
            const payload = arguments[1];
            const callback = arguments[arguments.length - 1];
            fetch(api_url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload),
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => callback(data))
            .catch(error => callback({'error': error.toString()}));
        """, api_url, payload)
        
        if 'error' in json_data:
            print(f"Erro na requisição: {json_data['error']}")

        else:
            print("Requisição bem-sucedida!")
            return json_data
    
    except Exception as e:
        print("Ocorreu um erro ao fazer a requisição via navegador:", e)

def get_processos_npj(driver, npj):
    """
    Obtém os processos de um determinado Número de Processo Judicial (NPJ) a partir da API da Dijur.
    
    :param driver: Instância do WebDriver do Selenium.
    :param npj: Número de Processo Judicial a ser consultado.
    """
    # URL da API de processos do Dijur
    api_url = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/{npj}/-1/0"
    
    # Faz a requisição GET via navegador
    return get_api_navegador(driver, api_url)

def get_processo_numerodoprocesso(driver, numerodoprocesso):
    """
    Obtém os dados de um processo a partir do seu Número do Processo.
    
    :param driver: Instância do WebDriver do Selenium.
    :param numerodoprocesso: Número do Processo a ser consultado.
    """
    
    # Defina o payload da requisição
    payload = {
        "numeroProcesso": numerodoprocesso,
        "unidadeJuridica": 0,
        "ajuizado": "S",
        "estadoNPJ": "A",
        "tipoVariacao": "T",
        "inicioPesquisa": 0
    }
    
    # URL da API de processos do Dijur
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/consulta-numero-processo"
    
    # Faz a requisição POST via navegador
    return post_api_navegador(driver, url, payload)

def listar_publicacoes(driver, tipo, tribunal):
    """
    Lista as publicações judiciais de um determinado tipo e tribunal nos últimos 5 dias.
    
    :param driver: Instância do WebDriver do Selenium.
    :param tipo: Tipo de publicação a ser consultada (ex: 'todas', 'tratadas', 'pendente', 'emtratamento').
    :param tribunal: Tribunal de origem da publicação (ex: 'stf', 'stj', 'tst').
    """
    
    # Dicionario tipo para transformar o texto no codigo
    dict_tipo = {
        'todas': '0',
        'tratadas': '2',
        'pendente': '3',
        'emtratamento': '12',
        'complementadas': '4',
        'descartada': '13',
        'descartadabbnaoparte': '6',
        'enviadaparacadastramento': '11',
        'env.paracadastroincidental': '14',
        'cadastroempresaexterna': '16',
        'cadastroempresaexternaincidental': '15',
        'npjnaocadastrado': '17',
    }
    
    # Dicionario tribunal para transformar o texto no codigo
    dict_tribunal = {
        'stf': 22,
        'stj': 23,
        'tst': 24,
    }
    
    tipo = tipo.lower().strip()
    tipo = dict_tipo[tipo]
    
    tribunal = tribunal.lower().strip()
    tribunal = dict_tribunal[tribunal]
    
    # Data atual
    data_atual = datetime.now()

    # Data 5 dias atrás
    data_5_dias_atras = data_atual - timedelta(days=5)

    # Formatando as datas no formato 'dd.mm.yyyy'
    data_atual = data_atual.strftime('%d.%m.%Y')
    data_5_dias_atras = data_5_dias_atras.strftime('%d.%m.%Y')

    payload = {
        "codigoUnidadeOrganizacionalRecebedor": 18908,
        "dataFimDivulgacao": data_atual,
        "dataFimPublicacao": "",
        "dataInicioDivulgacao": data_5_dias_atras,
        "dataInicioPublicacao": "",
        "numeroOrdem": 8,
        "codigoEstadoPublicacaoJudicial": tipo,
        "tipo": 6,
        "codigoIdentificadorJornalOficial": tribunal,
    }
    
    return post_api_navegador(driver, "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/listar/unidadeJuridicaEJornalOficial", payload)

def detalhar_publicacao(driver, id_publicacao):
    """
    Detalha uma publicação a partir do seu ID.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser detalhada.
    """
    
    if id_publicacao is not int:
        id_publicacao = int(id_publicacao)
    
    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
    }
    
    return post_api_navegador(driver, "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/detalhar", payload)

# Deve ser a última função definida no arquivo
def helpDijurApi():
    """
    Lista todas as funções definidas no DijurAPI.
    """

    # Obtém o módulo atual
    current_module = sys.modules[__name__]
    
    # Inspeciona todas as funções definidas no módulo atual
    functions_list = [
        name for name, obj in inspect.getmembers(current_module, inspect.isfunction)
        if obj.__module__ == current_module.__name__
    ]
    
    if functions_list:
        print("Funções definidas no módulo atual:")
        for func in functions_list:
            print(f"- {func}")
    else:
        print("Nenhuma função encontrada no módulo atual.")
    