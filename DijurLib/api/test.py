from .base import get_api_navegador, post_api_navegador
from selenium.webdriver.remote.webdriver import WebDriver
from ..utils.schema.schemaConsulta import DataProcessos
from .npj_andamentos import listar_andamentos, filtrar_andamentos
import time 

def extrair_quantidade(data: DataProcessos) -> int:
    """
    Extrai a quantidade de ocorrências ou registros de maneira unificada.

    :param data: Dicionário contendo os dados da API.
    :return: Quantidade de registros/ocorrências.
    """
    return data.get("quantidadeRegistro") or data.get("quantidadeOcorrencia") or 0

def get_api_navegador(driver: WebDriver, api_url: str, max_attempts: int = 3):
    """
    Faz uma requisição GET para uma API via navegador com retry em caso de erro.
    
    :param driver: Instância do WebDriver do Selenium.
    :param api_url: URL da API a ser acessada.
    :param max_attempts: Número máximo de tentativas (padrão: 3).
    :return: JSON obtido da API ou None se todas as tentativas falharem.
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            print(f"Iniciando requisição GET - tentativa {attempts + 1}...")
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
            
            if json_data and 'error' not in json_data:
                print("Requisição GET bem-sucedida!")
                return json_data
            else:
                print(f"Erro na requisição: {json_data.get('error') if json_data else 'Nenhuma resposta recebida'}")
        except Exception as e:
            print("Ocorreu um erro ao fazer a requisição GET via navegador:", e)
        
        attempts += 1
        if attempts < max_attempts:
            print("Tentando novamente em 1 segundo...")
            time.sleep(1)
    
    print("Número máximo de tentativas alcançado. Retornando None.")
    return None



def get_processos_npj(driver, npj):
    """
    Obtém os processos de um NPJ a partir da API.
    
    :param driver: Instância do Selenium WebDriver.
    :param npj: Número de Processo Judicial a ser consultado.
    :return: Dicionário com informações dos processos.
    :raises Exception: Se a requisição falhar.
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
    
    response = get_api_navegador(driver, api_url)
    if response is None:
        raise Exception("Falha ao obter resposta da API.")
    
    if response.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    data = response.get("data", {})
    quantidade = extrair_quantidade(data)
    indicador_continuidade = data.get("indicadorContinuidade", "")
    lista_ocorrencia = data.get("listaOcorrencia", [])
    
    resultado = {
        "quantidade": quantidade,
        "indicadorContinuidade": indicador_continuidade,
        "listaOcorrencia": lista_ocorrencia
    }
    
    return resultado

def incluir_andamentos(driver: WebDriver, cd_admt: int, cd_solicitante:str, dt_admt: str, ind_doc_dig:bool, idNpj:str, descricao:str, cd_tipo_doc: int, nome_arquivo: str, num_id_tipo_doc:int, rawbytes: str) -> dict:
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
    :param nome_arquivo: Nome do arquivo.
    :param num_id_tipo_doc: Número de identificação do tipo de documento. Geralmente é o número de documentos vinculados + 1.
    :param rawbytes: Bytes do arquivo
    """

    lista_documentos = []


    lista_documentos.append({
        "codigoGrupoDocumento": 2,
        "codigoNivelConfidencialidade": 2,
        "codigoTipoDocumento": cd_tipo_doc,
        "codigoTipoDocumentoDigitalizado": 2,
        "nomeArquivoOriginal": nome_arquivo,
        "numeroProcesso": idNpj,
        "rawBytes": rawbytes
    })

    def incluir_documento_andamento(payload_incluir_doc):
        """
        Inclui um documento vinculado a um andamento.
        :param cd_tipo_doc: Código do tipo de documento.
        :param nome_arquivo: Nome do arquivo.
        :param idNpj: ID do NPJ do processo.
        :param num_id_tipo_doc: Número de identificação do tipo de documento.
        :param rawbytes: Bytes do arquivo.
        """
        api_incluir_documento = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/incluirDocumentoAndamento'

        response = post_api_navegador(driver, api_url=api_incluir_documento, payload=payload_incluir_doc)

        if response.get("status") != "OK":
            raise Exception(f"Erro na resposta da API: {response.get('status')}")
        
        return response
    

    payload = {
        "codigoTipoAndamento": cd_admt,
        "codigoTipoConfidencialidade": 2,
        "codigoTipoSolicitanteAndamento": "B",
        "dataAndamento": dt_admt,
        "indicadorAndamentoCompleto": "S",
        "textoInformacao": descricao,
        "indicadorDocumentoDigitalizado": "S",
        "listaDocumentos": lista_documentos,
        "numeroProcesso": idNpj,
        "numeroTipoLancamento": 0,
        "valorLancamento": 0,
    }

    api_incluir_andamentos = 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/andamento/incluir'

    response = post_api_navegador(driver, api_url=api_incluir_andamentos, payload=payload)
    admts_criados = listar_andamentos(driver, idNpj)
    andamentos = filtrar_andamentos(admts_criados,'PETICAO INICIAL', chave)
    maior_id = 0
    for andamento in andamentos:
        num_id_tipo_doc = andamento["numeroAndamentoProcesso"]
        if num_id_tipo_doc > maior_id:
            maior_id = num_id_tipo_doc
    if maior_id == 0:
        raise Exception(f"Erro ao incluir andamento:")
            
    payload_incluir_doc = {
        "codigoGrupoDocumento": 2,
        "codigoNivelConfidencialidade": 2,
        "codigoTipoDocumento": cd_tipo_doc,
        "codigoTipoDocumentoDigitalizado": 2,
        "nomeArquivoOriginal": nome_arquivo,
        "numeroIdentificacaoTipoDocumento": maior_id,
        "numeroProcesso": idNpj,
        "rawBytes": rawbytes
    }

    if response.get("status") != "OK":
        raise Exception(f"Erro na resposta da API: {response.get('status')}")
    
    incluir_documento_andamento(payload_incluir_doc)
    
    return response


