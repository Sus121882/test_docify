from selenium.webdriver.remote.webdriver import WebDriver
from typing import List
from DijurLib.utils.schema.schemaNpjAndamentos import Andamento, Documentos
from .base import post_api_navegador, get_api_navegador

def listar_andamentos(driver: WebDriver, id_npj: int) -> List:
    """
    Lista os andamentos de um processo a partir do seu ID NPJ.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_npj: ID do NPJ do processo a ser consultado.
    :return: Lista de andamentos no formato da classe Andamento.
    :raises Exception: Se houver erro na resposta da API.
    """
    url = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/listar'
    posicao_lista = 1
    lista_andamentos = []
    while True:

        payload = {
            "numeroProcesso": id_npj,
            "numeroPosicaoLista": posicao_lista,
            "flagFiltro": False,
            "indicadorAndamentoAtivo": "S",
            "indicadorProcessoVariacao": "N",
        }

        response = post_api_navegador(driver, api_url=url, payload=payload)

        if response.get("statusCode") != 200 and response.get("status") != "OK":
            raise Exception(f"Erro na resposta da API: {response.get('status')}")

        data = response.get("data", {})
        andamentos = data.get("andamentos", [])
        if andamentos == []:
            break
        # Extrair a lista de andamentos no formato da classe Andamento
        resultado: List = [item["andamento"] for item in andamentos]
        lista_andamentos.extend(resultado)

        if data.get("quantidadeRegistros") % 50 == 0:
            posicao_lista += 50
        else:
            break
    return lista_andamentos

def filtrar_andamentos(andamentos: List[Andamento], tipo: str, chave_adv_resp:str = None) -> List[Andamento]:
    """
    Filtra a lista de andamentos pelo tipo especificado e pela chave do advogado responsável, evitando pegar andamentos registrados pelo PAJ.

    :param andamentos: Lista de andamentos.
    :param tipo: Tipo de andamento a ser filtrado.
    :param chave_adv_resp: Matrícula do advogado responsável.
    :return: Lista de andamentos filtrados.
    """
    if chave_adv_resp is None:
        return [andamento for andamento in andamentos if andamento["textoTipoAndamento"] == tipo]
    else:
        return [andamento for andamento in andamentos if andamento["textoTipoAndamento"] == tipo and andamento["codigoUsuarioResponsavelAtualizacao"] == chave_adv_resp]

def listar_documentos(driver, idNpj):
    """
    Lista os documentos vinculados a um processo a partir do seu ID NPJ.

    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do NPJ do processo.
    :return: Lista de documentos vinculados ao processo.
    :raises Exception: Se houver erro na resposta da API.
    """

    lista_documentos = []
    posicao_lista = 1
    while True:
        url = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/documentoV2?codigoTipoDocumentoPesquisa=0&numeroPosicaoPesquisa={posicao_lista}&numeroProcesso={idNpj}&tipoDocumento=0"
        response = get_api_navegador(driver, api_url=url)

        if response.get("statusCode") != 200 and response.get("status") != "OK":
            raise Exception(f"Erro na resposta da API: {response.get('status')}")
        
        data = response.get("data", {})
        documentos = data.get("listaDocumento", [])
        
        if documentos == []:
            break

        lista_documentos.extend(documentos)
        
        if data.get("quantidadeOcorrencia") % 100 == 0:
            posicao_lista += 100
        else:
            break

    return lista_documentos

def listar_documento_vinculado(driver: WebDriver, idNpj: int, num_admt: int) -> List:
    """
    Lista os dados de todos os documentos vinculados a um andamento específico.

    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do NPJ do processo.
    :param num_admt: Número do andamento do processo.
    :return: Lista de documentos vinculados ao andamento.
    :raises Exception: Se houver erro na resposta da API.
    """
    url = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/documentos/{idNpj}/{num_admt}/0"

    response = get_api_navegador(driver, api_url=url)

    if response.get("statusCode") != 200 and response.get("status") != "OK":
        raise Exception(f"Erro na resposta da API: {response.get('status')}")

    documentos = response.get("data", {}).get("listaDocumento", [])

    return documentos

def incluir_andamentos(driver: WebDriver, cd_admt: int, cd_solicitante:str, dt_admt: str, ind_doc_dig:bool, idNpj:str, descricao:str, cd_tipo_doc: int, nome_arquivo: str, rawbytes: str) -> dict:
    """
    Realiza a inclusão de um andamento no processo.
    :param driver: Instância do WebDriver do Selenium.
    :param cd_admt: Código do tipo de andamento.
    :param cd_solicitante: Tipo de solicitante. 'B' para banco, 'A' para adverso.
    :param dt_admt: Data do andamento no formato 'dd.mm.yyyy'.
    :param ind_doc_dig: Indicador de documento digitalizado. True para digitalizado, False para não digitalizado.
    :param idNpj: ID do NPJ do processo.
    :param descricao: Descrição do andamento.
    :param cd_tipo_doc: Código do tipo de documento.
    """
    api_incluir_andamentos = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/incluir'

    def incluir_documento_andamento(cd_tipo_doc:int, nome_arquivo:str, idNpj:int, rawbytes:str):
        """
        Inclui um documento vinculado a um andamento.
        :param cd_tipo_doc: Código do tipo de documento.
        :param nome_arquivo: Nome do arquivo.
        :param idNpj: ID do NPJ do processo.
        :param rawbytes: Bytes do arquivo.
        """
        api_incluir_documento = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/incluirDocumentoAndamento'
        
        lista_documentos = []

        payload_incluir_doc = {
            "codigoGrupoDocumento": 2,
            "codigoNivelConfidencialidade": 2,
            "codigoTipoDocumento": cd_tipo_doc,
            "codigoTipoDocumentoDigitalizado": 2,
            "nomeArquivoOriginal": nome_arquivo,
            "numeroIdentificacaoTipoDocumento": 23,
            "numeroProcesso": idNpj,
            "rawBytes": rawbytes
        }

        response = post_api_navegador(driver, api_url=api_incluir_documento, payload=payload_incluir_doc)

        if response.get("statusCode") != 200 and response.get("status") != "OK":
            raise Exception(f"Erro na resposta da API: {response.get('status')}")
        
        lista_documentos.append(payload_incluir_doc)

        return response, lista_documentos
    
    _, lista_documentos = incluir_documento_andamento(cd_tipo_doc, nome_arquivo, idNpj, rawbytes)


    payload = {
        "codigoTipoAndamento": cd_admt,
        "codigoTipoConfidencialidade": 2,
        "codigoTipoSolicitanteAndamento": cd_solicitante,
        "dataAndamento": dt_admt,
        "indicadorAndamentoCompleto": "S",
        "indicadorDocumentoDigitalizado": ind_doc_dig,
        "listaDocumentos:": lista_documentos,
        "numeroProcesso": idNpj,
        "numeroTipoLancamento": 0,
        "textoInformacao": descricao,
        "valorLancamento": 0
    }

    
    response = post_api_navegador(driver, api_url=api_incluir_andamentos, payload=payload)

    if response.get("statusCode") != 200 and response.get("status") != "OK":
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    return response
