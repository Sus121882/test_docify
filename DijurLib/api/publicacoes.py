from .base import post_api_navegador
from .consulta import get_processos_npj
from datetime import datetime, timedelta
from selenium.webdriver.remote.webdriver import WebDriver

from typing import List, Optional
import json
import time

from ..utils.schema.schemaPublicacoes import PublicacoesResponse

def listar_publicacoes(driver: WebDriver, tipo: str, tribunal: str) -> PublicacoesResponse:
    """
    Lista as publicações judiciais de um determinado tipo e tribunal nos últimos 5 dias.
    Faz paginação para coletar todas as publicações disponíveis.
    
    :param driver: Instância do WebDriver do Selenium.
    :param tipo: Tipo de publicação (ex: 'todas', 'tratadas', 'pendente', 'emtratamento').
    :param tribunal: Tribunal de origem (ex: 'stf', 'stj', 'tst').
    :return: Dicionário com a lista de publicações filtradas, conforme o schema PublicacoesResponse.
    """
    dict_tipo = {
        'todas': '0',
        'tratada': '2',
        'pendente': '3',
        'emtratamento': '12',
        'complementada': '4',
        'descartada': '13',
        'descartadabbnaoparte': '6',
        'enviadaparacadastramento': '11',
        'env.paracadastroincidental': '14',
        'cadastroempresaexterna': '16',
        'cadastroempresaexternaincidental': '15',
        'npjnaocadastrado': '17',
    }
    
    dict_tribunal = {
        'stf': 22,
        'stj': 23,
        'tst': 24,
    }
    
    # Dicionários invertidos para mapear código para string
    dict_tipo_reversed = {int(v): k for k, v in dict_tipo.items()}
    dict_tribunal_reversed = {v: k for k, v in dict_tribunal.items()}
    
    tipo_codigo = dict_tipo.get(tipo.lower().strip())
    if tipo_codigo is None:
        raise ValueError(f"Tipo inválido: {tipo}")
    
    tribunal_codigo = dict_tribunal.get(tribunal.lower().strip())
    if tribunal_codigo is None:
        raise ValueError(f"Tribunal inválido: {tribunal}")
    
    data_atual = datetime.now()
    data_5_dias_atras = data_atual - timedelta(days=5)
    
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/listar/unidadeJuridicaEJornalOficial"
    
    lista_publicacao_processada: List[dict] = []
    posicao_inicial = 1  # primeiro registro
    total_publicacoes = None  # será definido na primeira chamada
    
    while True:
        payload = {
            "codigoUnidadeOrganizacionalRecebedor": 18908,
            "dataFimDivulgacao": data_atual.strftime('%d.%m.%Y'),
            "dataFimPublicacao": "",
            "dataInicioDivulgacao": data_5_dias_atras.strftime('%d.%m.%Y'),
            "dataInicioPublicacao": "",
            "numeroOrdem": 8,
            "codigoEstadoPublicacaoJudicial": tipo_codigo,
            "tipo": 6,
            "codigoIdentificadorJornalOficial": tribunal_codigo,
            "numeroPosicaoLista": posicao_inicial
        }
    
        response = post_api_navegador(driver, url, payload)
    
        if response["statusCode"] != 200:
            raise Exception(f"Erro ao listar publicações: {response.get('status', 'Erro desconhecido')}")
    
        data = response.get("data", {})
        if total_publicacoes is None:
            total_publicacoes = data.get("totalDePublicacoes", 0)
        
        lista_publicacao_raw = data.get("listaPublicacao", [])
    
        for pub in lista_publicacao_raw:
            try:
                publicacao = {
                    "codigoEstadoPublicacaoJudicial": dict_tipo_reversed.get(pub.get("codigoEstadoPublicacaoJudicial"), "Desconhecido"),
                    "codigoExternoProcessoInteresse": pub.get("codigoExternoProcessoInteresse", ""),
                    "codigoIdentificadorJornalOficial": dict_tribunal_reversed.get(pub.get("codigoIdentificadorJornalOficial"), "Desconhecido"),
                    "codigoUnidadeOrganizacionalRecebedor": pub.get("codigoUnidadeOrganizacionalRecebedor", 0),
                    "dataDivulgacao": pub.get("dataDivulgacao", ""),
                    "dataPublicacao": pub.get("dataPublicacao", ""),
                    "dataRecebimento": pub.get("dataRecebimento", ""),
                    "nomeEmpresaResponsavel": pub.get("nomeEmpresaResponsavel", ""),
                    "numeroProcesso": pub.get("numeroProcesso", 0),
                    "numeroProcessoCompleto": pub.get("numeroProcessoCompleto", ""),
                    "numeroProcessoPrincipal": pub.get("numeroProcessoPrincipal", 0),
                    "numeroPublicacaoJudicial": pub.get("numeroPublicacaoJudicial", 0),
                    "numeroVariacao": pub.get("numeroVariacao", 0),
                    "textoPublicacaoJudicial": pub.get("textoPublicacaoJudicial", ""),
                }
                lista_publicacao_processada.append(publicacao)
            except Exception as e:
                # Logar o erro e continuar com as demais publicações
                print(f"Erro ao processar publicação: {e}")
                continue
        
        # Se já pegamos todas as publicações, sai do loop
        if posicao_inicial + 50 > total_publicacoes:
            break
        
        posicao_inicial += 50
    
    resultado: PublicacoesResponse = {
        "quantidadeRegistro": len(lista_publicacao_processada),
        "listaPublicacao": lista_publicacao_processada
    }
    
    return resultado


def listar_publicacoes_por_numero(driver: WebDriver, tipo: str, numero: str) -> PublicacoesResponse:
    """
    Lista as publicações judiciais de um determinado tipo e tribunal nos últimos 5 dias.

    :param driver: Instância do WebDriver do Selenium.
    :param tipo: Tipo de publicação a ser consultada (ex: 'todas', 'tratadas', 'pendente', 'emtratamento').
    :param tribunal: Tribunal de origem da publicação (ex: 'stf', 'stj', 'tst').
    :return: Dicionário com a lista de publicações filtradas, conforme o schema PublicacoesResponse.
    """

    dict_tipo = {
        'todas': '0',
        'tratada': '2',
        'pendente': '3',
        'emtratamento': '12',
        'complementada': '4',
        'descartada': '13',
        'descartadabbnaoparte': '6',
        'enviadaparacadastramento': '11',
        'env.paracadastroincidental': '14',
        'cadastroempresaexterna': '16',
        'cadastroempresaexternaincidental': '15',
        'npjnaocadastrado': '17',
    }

    dict_tribunal = {
        'stf': 22,
        'stj': 23,
        'tst': 24,
    }

    # Dicionários invertidos para mapear código para string
    dict_tipo_reversed = {int(v): k for k, v in dict_tipo.items()}
    dict_tribunal_reversed = {v: k for k, v in dict_tribunal.items()}

    tipo_codigo = dict_tipo.get(tipo.lower().strip())
    if tipo_codigo is None:
        raise ValueError(f"Tipo inválido: {tipo}")

    if not isinstance(numero, str):
        try:
            numero = str(numero)
        except ValueError:
            raise ValueError("numero deve ser uma string.")

    data_atual = datetime.now()
    data_5_dias_atras = data_atual - timedelta(days=5)

    payload = {
        "codigoUnidadeOrganizacionalRecebedor": 1,
        "dataFimDivulgacao": data_atual.strftime('%d.%m.%Y'),
        "dataFimPublicacao": "",
        "dataInicioDivulgacao": data_5_dias_atras.strftime('%d.%m.%Y'),
        "dataInicioPublicacao": "",
        "numeroOrdem": 8,
        "codigoEstadoPublicacaoJudicial": tipo_codigo,
        "tipo": 5,
        "numeroCNJ": numero
    }

    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/listar/numeroCNJ"
    response = post_api_navegador(driver, url, payload)

    if response["statusCode"] != 200:
        raise Exception(f"Erro ao listar publicações: {response.get('status', 'Erro desconhecido')}")

    lista_publicacao_raw = response.get("data", {}).get("listaPublicacao", [])

    lista_publicacao_processada: List[dict] = []

    for pub in lista_publicacao_raw:
        try:
            publicacao = {
                "codigoEstadoPublicacaoJudicial": dict_tipo_reversed.get(pub.get("codigoEstadoPublicacaoJudicial"), "Desconhecido"),
                "codigoExternoProcessoInteresse": pub.get("codigoExternoProcessoInteresse", ""),
                "codigoIdentificadorJornalOficial": dict_tribunal_reversed.get(pub.get("codigoIdentificadorJornalOficial"), "Desconhecido"),
                "codigoUnidadeOrganizacionalRecebedor": pub.get("codigoUnidadeOrganizacionalRecebedor", 0),
                "dataDivulgacao": pub.get("dataDivulgacao", ""),
                "dataPublicacao": pub.get("dataPublicacao", ""),
                "dataRecebimento": pub.get("dataRecebimento", ""),
                "nomeEmpresaResponsavel": pub.get("nomeEmpresaResponsavel", ""),
                "numeroProcesso": pub.get("numeroProcesso", 0),
                "numeroProcessoCompleto": pub.get("numeroProcessoCompleto", ""),
                "numeroProcessoPrincipal": pub.get("numeroProcessoPrincipal", 0),
                "numeroPublicacaoJudicial": pub.get("numeroPublicacaoJudicial", 0),
                "numeroVariacao": pub.get("numeroVariacao", 0),
                "textoPublicacaoJudicial": pub.get("textoPublicacaoJudicial", ""),
            }
            lista_publicacao_processada.append(publicacao)
        except Exception as e:
            # Logar o erro e continuar com as demais publicações
            print(f"Erro ao processar publicação: {e}")
            continue

    resultado: PublicacoesResponse = {
        "quantidadeRegistro": len(lista_publicacao_processada),
        "listaPublicacao": lista_publicacao_processada
    }

    return resultado

def listar_publicacoes_historico(driver: WebDriver, tipo: str, numero: str) -> PublicacoesResponse:
    """
    Lista as publicações judiciais de um determinado tipo e tribunal nos últimos 5 dias.

    :param driver: Instância do WebDriver do Selenium.
    :param tipo: Tipo de publicação a ser consultada (ex: 'todas', 'tratadas', 'pendente', 'emtratamento').
    :param tribunal: Tribunal de origem da publicação (ex: 'stf', 'stj', 'tst').
    :return: Dicionário com a lista de publicações filtradas, conforme o schema PublicacoesResponse.
    """

    dict_tipo = {
        'todas': '0',
        'tratada': '2',
        'pendente': '3',
        'emtratamento': '12',
        'complementada': '4',
        'descartada': '13',
        'descartadabbnaoparte': '6',
        'enviadaparacadastramento': '11',
        'env.paracadastroincidental': '14',
        'cadastroempresaexterna': '16',
        'cadastroempresaexternaincidental': '15',
        'npjnaocadastrado': '17',
    }

    dict_tribunal = {
        'stf': 22,
        'stj': 23,
        'tst': 24,
    }

    # Dicionários invertidos para mapear código para string
    dict_tipo_reversed = {int(v): k for k, v in dict_tipo.items()}
    dict_tribunal_reversed = {v: k for k, v in dict_tribunal.items()}

    tipo_codigo = dict_tipo.get(tipo.lower().strip())
    if tipo_codigo is None:
        raise ValueError(f"Tipo inválido: {tipo}")

    if not isinstance(numero, str):
        try:
            numero = str(numero)
        except ValueError:
            raise ValueError("numero deve ser uma string.")

    data_atual = datetime.now()
    data_11_meses_atras = data_atual - timedelta(days=330)

    payload = {
        "codigoUnidadeOrganizacionalRecebedor": 1,
        "dataFimDivulgacao": data_atual.strftime('%d.%m.%Y'),
        "dataFimPublicacao": "",
        "dataInicioDivulgacao": data_11_meses_atras.strftime('%d.%m.%Y'),
        "dataInicioPublicacao": "",
        "numeroOrdem": 8,
        "codigoEstadoPublicacaoJudicial": tipo_codigo,
        "tipo": 5,
        "numeroCNJ": numero
    }

    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/listar/numeroCNJ"
    response = post_api_navegador(driver, url, payload)

    if response["statusCode"] != 200:
        raise Exception(f"Erro ao listar publicações: {response.get('status', 'Erro desconhecido')}")

    lista_publicacao_raw = response.get("data", {}).get("listaPublicacao", [])

    lista_publicacao_processada: List[dict] = []

    for pub in lista_publicacao_raw:
        try:
            publicacao = {
                "codigoEstadoPublicacaoJudicial": dict_tipo_reversed.get(pub.get("codigoEstadoPublicacaoJudicial"), "Desconhecido"),
                "codigoExternoProcessoInteresse": pub.get("codigoExternoProcessoInteresse", ""),
                "codigoIdentificadorJornalOficial": dict_tribunal_reversed.get(pub.get("codigoIdentificadorJornalOficial"), "Desconhecido"),
                "codigoUnidadeOrganizacionalRecebedor": pub.get("codigoUnidadeOrganizacionalRecebedor", 0),
                "dataDivulgacao": pub.get("dataDivulgacao", ""),
                "dataPublicacao": pub.get("dataPublicacao", ""),
                "dataRecebimento": pub.get("dataRecebimento", ""),
                "nomeEmpresaResponsavel": pub.get("nomeEmpresaResponsavel", ""),
                "numeroProcesso": pub.get("numeroProcesso", 0),
                "numeroProcessoCompleto": pub.get("numeroProcessoCompleto", ""),
                "numeroProcessoPrincipal": pub.get("numeroProcessoPrincipal", 0),
                "numeroPublicacaoJudicial": pub.get("numeroPublicacaoJudicial", 0),
                "numeroVariacao": pub.get("numeroVariacao", 0),
                "textoPublicacaoJudicial": pub.get("textoPublicacaoJudicial", ""),
            }
            lista_publicacao_processada.append(publicacao)
        except Exception as e:
            # Logar o erro e continuar com as demais publicações
            print(f"Erro ao processar publicação: {e}")
            continue

    resultado: PublicacoesResponse = {
        "quantidadeRegistro": len(lista_publicacao_processada),
        "listaPublicacao": lista_publicacao_processada
    }

    return resultado

def detalhar_publicacao(driver: WebDriver, id_publicacao: int):
    """
    Detalha uma publicação a partir do seu ID.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser detalhada.
    """
    
    if not isinstance(id_publicacao, int):
        try:
            id_publicacao = int(id_publicacao)
        except ValueError:
            raise ValueError("id_publicacao deve ser um inteiro.")
    
    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
    }
    
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/detalhar"
    return post_api_navegador(driver, url, payload)

def emtratamento_publicacao(driver: WebDriver, id_publicacao: int):
    """
    Marca uma publicação como 'Em Tratamento' a partir do seu ID.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser marcada como 'Em Tratamento'.
    """
    
    if not isinstance(id_publicacao, int):
        try:
            id_publicacao = int(id_publicacao)
        except ValueError:
            raise ValueError("id_publicacao deve ser um inteiro.")
    
    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
    }
    
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/tratamento/emTratamento"
    return post_api_navegador(driver, url, payload)

def descartar_publicacao(driver: WebDriver, id_publicacao: int, mensagem: str):
    """
    Descarta uma publicação a partir do seu ID.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser descartada.
    :param mensagem: Mensagem a ser incluída no descarte.
    """
    
    if not isinstance(id_publicacao, int):
        try:
            id_publicacao = int(id_publicacao)
        except ValueError:
            raise ValueError("id_publicacao deve ser um inteiro.")
    
    emtratamento_publicacao(driver, id_publicacao)
    time.sleep(1)

    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
        "textoJustificativaDescarte": mensagem,
    }
    
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/tratamento/descartar"
    return post_api_navegador(driver, url, payload)

def descartar_publicacao_bbnaoparte(driver: WebDriver, id_publicacao: int):
    """
    Descarta uma publicação como 'BB não parte' a partir do seu ID.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser descartada.
    """
    
    if not isinstance(id_publicacao, int):
        try:
            id_publicacao = int(id_publicacao)
        except ValueError:
            raise ValueError("id_publicacao deve ser um inteiro.")
        
    emtratamento_publicacao(driver, id_publicacao)
    time.sleep(1)
    
    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
    }
    
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/tratamento/descartar/banco/nao/parte"
    return post_api_navegador(driver, url, payload)

def indicar_publicacao(driver: WebDriver, id_publicacao: int, id_npj: Optional[int] = None, npj: Optional[str] = None):
    """
    Indica um processo a partir do seu ID para uma publicação.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_publicacao: ID da publicação a ser indicada.
    :param id_npj: ID do processo a ser indicado, opcional caso npj seja fornecido.
    :param npj: NPJ do processo a ser indicado, opcional caso id_npj seja fornecido.
    """
    
    print("Começando a indicar publicação")
    
    if not id_npj and not npj:
        raise ValueError("Deve ser fornecido o ID ou o NPJ do processo.")
    
    if id_npj and npj:
        raise ValueError("Deve ser fornecido apenas o ID ou o NPJ do processo.")
    
    if id_npj:
        if not isinstance(id_npj, int):
            try:
                id_npj = int(id_npj)
            except ValueError:
                raise ValueError("id_npj deve ser um inteiro.")
            
    elif npj:
        if not isinstance(npj, str):
            try:
                npj = str(npj)
            except ValueError:
                raise ValueError("npj deve ser uma string.")
            
        npj = npj.replace("/", "").replace("-", "")
        
        if len(npj) != 14:
            raise ValueError("npj deve ter 14 caracteres, contendo ano, numero e variação.")
        
        processos = get_processos_npj(driver, npj)
        
        id_npj = processos['listaOcorrencia'][0]['numeroProcesso']
    
    payload = {
        "numeroPublicacaoJudicial": id_publicacao,
        "numeroProcesso": id_npj,
    }
    
    print("Colocando publicação em tratamento")
    emtratamento_publicacao(driver, id_publicacao)
    time.sleep(1)
    
    print("Indicando publicação")
    url = "https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/tratamento/identificar"
    return post_api_navegador(driver, url, payload)

def consultar_tratamento_publicacoes(driver, data_inicial, data_final):
    """
    Consulta o tratamento de publicações de um dia específico.
    
    :param driver: webdriver
    :param data: str
    
    :return: dict
    """
    data_inicial = data_inicial.replace('/', '.')
    data_final = data_final.replace('/', '.')

    url = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/totalizadores/listarTotalizadores'
    
    payload = {
        "codigoUnidadeOrganizacionalRecebedor": 18908,
        "dataFimDivulgacao": data_final,
        "dataInicioDivulgacao": data_inicial,
    }
    
    response = post_api_navegador(driver, url, payload)
    
    data = response['data']
    
    payload_result = {
        "Tratada": data[0]['quantidadePublicacao'],
        "Pendente": data[1]['quantidadePublicacao'],
        "Complementada": data[2]['quantidadePublicacao'],
        "Descartada banco não parte": data[3]['quantidadePublicacao'],
        "Descartada": data[4]['quantidadePublicacao'],
        "Em tratamento": data[5]['quantidadePublicacao'],
    }
    
    return payload_result