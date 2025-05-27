from .base import get_api_navegador, post_api_navegador
from .consulta import get_processos_npj
from selenium.webdriver.remote.webdriver import WebDriver

# Schemas
from typing import List
from ..utils.schema.schemaNpjAndamentos import Documentos
from ..utils.schema.schemaNpjDados import CabecalhoResponse, DadosProcessoResponse
from ..utils.schema.schemaNpjPartes import PartesResponse

# Função auxiliar para chamadas com tratamento de erro
def get_api_data(driver: WebDriver, api_url: str) -> dict:
    try:
        response = get_api_navegador(driver, api_url)
    except Exception as e:
        raise Exception(f"Erro ao acessar a API {api_url}: {e}")

    if response.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API {api_url}: {response.get('status')}")
    return response.get("data", {})

def reativar_npj(driver, justificativa: str, npj: str, idNpj: int) -> dict:
    """
    Reativa um processo a partir do seu Número do id de um NPJ.
    
    :param driver: Instância do WebDriver do Selenium.
    :param npj: Npj do processo a ser reativado (20250019564002).
    :param justificativa: Justificativa para a reativação (Ex: "Agendar Publicação.").
    :param idNpj: ID do NPJ (Ex: "numeroProcesso": 20250019564) (Caso vazio ira fazer uma consulta para pegar o id baseado no npj).
    :return: Status
    """
    
    if not isinstance(npj, str):
        try:
            npj = str(npj)
        except ValueError:
            raise ValueError("npj deve ser uma string.")
        
    if len(npj) != 14:
        raise ValueError("npj deve ter 14 caracteres.")
        
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")
    
    # URL da API
    api_reativar = "https://juridico.intranet.bb.com.br/paj/resources/app/v0/processo/reativar"
    
    # Dados para a requisição
    data = {
        "idProcesso": idNpj,
        "npj": npj,
        "justificativa": justificativa
    }
    
    # Requisição POST
    try:
        response = post_api_navegador(driver, api_reativar, data)
    except Exception as e:
        raise Exception(f"Erro ao acessar a API de reativação: {e}")
    
    return response

def npj_cabecalho(driver: WebDriver, idNpj: int) -> CabecalhoResponse:
    """
    Obtém os dados de cabeçalho de um processo a partir do seu Número do Processo Judicial (NPJ).

    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do NPJ (Ex: "numeroProcesso": 20250019564).
    :return: Dicionário com informações do cabeçalho do processo.
    :raises ValueError: Se idNpj não for um inteiro válido.
    :raises Exception: Se houver erro ao acessar a API.
    """
    # Validação do idNpj
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")

    # URL da API
    api_cabecalho = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/portal/dados/processo/resumo/processo/consultar/{idNpj}"
    
    # Obtenção dos dados da API
    try:
        cabecalho = get_api_navegador(driver, api_cabecalho)
    except Exception as e:
        raise Exception(f"Erro ao acessar a API de cabeçalho: {e}")

    # Verificação do status da resposta
    if cabecalho.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API: {cabecalho.get('status')}")

    data = cabecalho.get("data", {})
    
    # Extração dos campos desejados com valores padrão para evitar KeyError
    resultado: CabecalhoResponse = {
        "npj": data.get("numeroProcessoJuridico", ""),
        "adverso": data.get("nomeContrarioPrincipal", ""),
        "advogado": data.get("nomeAdvogadoBancoBrasil", ""),
        "uja": data.get("codigoPrefixoUnidadeJuridico", ""),
        "polo": data.get("textoPoloBancoBrasil", ""),
        "processo": data.get("textoNumeroInventario", ""),
        "natureza": data.get("textoNaturezaProcesso", ""),
        "acao": data.get("textoTipoAcao", ""),
        "data_ajuizamento": data.get("dataProtocoloJuridico", ""),
        "situacao": data.get("textoEstadoProcesso", ""),
        "tramitacao": data.get("nomeOrgaoTransito", ""),
        "valor_causa": data.get("textoValorCausa", "")
    }
    
    return resultado

def npj_dados_resumo(driver: WebDriver, idNpj: int) -> dict:
    # URL da API de resumo
    api_resumo = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/portal/dados/processo/resumo/processo/consultar/{idNpj}"
    data_resumo = get_api_data(driver, api_resumo)
    
    # Extração dos dados do resumo
    tipo = data_resumo.get("textoTipoProcesso", "")
    natureza = data_resumo.get("textoNaturezaProcesso", "")
    acao = data_resumo.get("textoTipoAcao", "")
    data_ajuizamento = data_resumo.get("dataProtocoloJuridico", "")
    
    # Chamada à API de histórico para obter o 'cadastramento'
    api_historico = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/portal/processo/classificacao/listarClassificacoesProcesso/ativas/{idNpj}"
    data_historico = get_api_data(driver, api_historico)
    cadastramento = ""
    for item in data_historico:
        if item.get('nomeTipoClassificacaoProcesso') == 'CADASTRO':
            cadastramento = item.get('codigoUsuarioResponsavelAtualizacao', "")
            break

    return {
        "tipo": tipo,
        "natureza": natureza,
        "acao": acao,
        "data_ajuizamento": data_ajuizamento,
        "cadastramento": cadastramento
    }

def npj_dados_numeros(driver: WebDriver, idNpj: int) -> dict:
    api_numeros = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/numero/{idNpj}"
    data_numeros = get_api_data(driver, api_numeros)
    
    uf = data_numeros.get("siglaUnidadeFederacao", "")
    cnj = data_numeros.get("textoNumeroInventario", {})
    if cnj is not None:
        cnj = cnj.get("textoNumeroExternoProcesso", "")
    else:
        cnj = ""

    publicacao = data_numeros.get("textoNumeroPublicacao", {})
    if publicacao is not None:
        publicacao = publicacao.get("textoNumeroExternoProcesso", "")
    else:
        publicacao = ""

    lista_texto = data_numeros.get("listaTextoNumeroExternoProcesso", [])
    if lista_texto is not None:
        outros = [item.get("textoNumeroExternoProcesso", "") for item in lista_texto]
    else:
        outros = []
    
    return {
        "uf": uf,
        "cnj": cnj,
        "publicacao": publicacao,
        "outros": outros
    }

def npj_dados_processo(driver: WebDriver, idNpj: int, apis: List[str] = None) -> DadosProcessoResponse:
    """
    Obtém dados do processo a partir do NPJ. Por padrão, obtém os dados do resumo (incluindo histórico) e números.
    
    :param driver: Instância do WebDriver.
    :param idNpj: Número do processo (deve ser inteiro).
    :param apis: Lista com os nomes das APIs a serem consultadas (ex: ["resumo", "numeros"]).
                 Se não informado, serão chamadas as duas.
    :return: Dicionário conforme DadosProcessoResponse.
    """
    # Validação do idNpj
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")

    # Se não for especificado, chama as APIs de resumo e números
    if apis is None:
        apis = ["resumo", "numeros"]

    resultado = {}
    if "resumo" in apis:
        resultado.update(npj_dados_resumo(driver, idNpj))
    if "numeros" in apis:
        resultado.update(npj_dados_numeros(driver, idNpj))
    
    # Garantir que todas as chaves do schema estejam presentes
    schema_default: DadosProcessoResponse = {
        "tipo": "",
        "natureza": "",
        "acao": "",
        "data_ajuizamento": "",
        "uf": "",
        "cadastramento": "",
        "cnj": "",
        "publicacao": "",
        "outros": []
    }
    
    for key, valor in schema_default.items():
        if key not in resultado:
            resultado[key] = valor

    return resultado

def npj_pessoas_processo(driver: WebDriver, idNpj: int) -> PartesResponse:
    """
    Obtém os dados de um processo a partir do seu Número do Processo Judicial (NPJ).
    
    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do npj (Ex: "numeroProcesso": 20250019564).
    :return: Dicionário com informações detalhadas das partes e do advogado, conforme o schema definido.
    """
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")
    
    # URLs das APIs
    api_ativos = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/pessoas/listarPessoasProcesso/{idNpj}/1/0"
    api_passivos = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/pessoas/listarPessoasProcesso/{idNpj}/2/0"
    api_neutros = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/pessoas/listarPessoasProcesso/{idNpj}/3/0"
    api_advogado = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/distribuicao/{idNpj}"
    
    # Função auxiliar para obter dados da API
    def get_data(api_url):
        response = get_api_navegador(driver, api_url)
        if response["statusCode"] != 200:
            raise Exception(f"Erro ao acessar {api_url}: {response['status']}")
        return response["data"]
    
    # Coletando dados das partes
    ativos_data = get_data(api_ativos)
    passivos_data = get_data(api_passivos)
    neutros_data = get_data(api_neutros)
    
    # Coletando dados do advogado
    advogado_data = get_data(api_advogado)
    
    # Função para extrair os campos desejados das partes
    def extrair_campos_partes(lista_ocorrencia):
        relacionamento_pessoa_banco = {
            0: "Banco do Brasil",
            1: "Sindicato de Bancários",
            2: "Sindicato de Outras Categorias",
            3: "Clientes",
            5: "A cadastrar",
            6: "Empregado BB - Aposentado/Pensionista",
            7: "Empregado de Empresa Terceirizada - Demais",
            8: "Usuário",
            9: "Empresa Terceirizada",
            10: "Empregado BB - Dispensado/Demitido",
            14: "Ex-Empregado de Empresa Terceirizada",
            16: "Indeterminado",
            17: "Autonomo/Trabalhador Temporario",
            18: "Empregado BB - Ativa",
            19: "Empregado BB Cedido - Poder Executivo/Legislativo/Judiciário",
            20: "Empregado BB Cedido - PREVI / FBB / CASSI e Outros",
            21: "Empregado de Coligada/Patrocinada",
            22: "Empregado de Controlada/Subsidiária",
            23: "Empregado de Correspondente (ECT e demais)",
            24: "Empregado de Empresa Terceirizada - Apoio",
            25: "Empregado de Empresa Terceirizada - Vigilante e Segurança",
            26: "Entidade Coligada/Patrocinada",
            27: "Entidade Controlada/Subsidiária",
            28: "Estagiário/Menor Aprendiz",
            29: "Ex-Empregado de Correspondente (ECT e demais)",
            30: "Ex-Empregado de Banco Incorporado",
            32: "Órgão de Fiscalização do Trabalho",
            33: "Ex-Empregado de Coligada / Patrocinada",
            34: "Ex-Empregado de Controlada / Subsidiária",
            35: "Empregado do Banco Postal",
            36: "Ex-Empregado do Banco Postal",
            37: "Empregrado BB - Expatriado",
            38: "Ministério Público do Trabalho e Associações"
        }
        
        return [
            {
                "nomeRazaoSocialClientePessoa": item.get("nomeRazaoSocialClientePessoa"),
                "codigoMercadoInternoPessoa": item.get("codigoMercadoInternoPessoa"),
                "numeroCpfCadastroNacPessoasJuridicasPessoa": item.get("numeroCpfCadastroNacPessoasJuridicasPessoa"),
                "codigoTipoRelacionamentoPessoaBanco": relacionamento_pessoa_banco[item.get("codigoTipoRelacionamentoPessoaBanco")],
            }
            for item in lista_ocorrencia
        ]
    
    # Extraindo informações das partes
    ativos = extrair_campos_partes(ativos_data.get("listaOcorrencia", []))
    passivos = extrair_campos_partes(passivos_data.get("listaOcorrencia", []))
    neutros = extrair_campos_partes(neutros_data.get("listaOcorrencia", []))
    
    # Extraindo informações do advogado
    advogado = {
        "nomeRazaoSocialAdvogado": advogado_data.get("nomeRazaoSocialAdvogado"),
        "codigoPrefixoTributarioAdvogado": advogado_data.get("codigoPrefixoTributarioAdvogado"),
        "nomeDependenciaTributarioAdvogado": advogado_data.get("nomeDependenciaTributarioAdvogado"),
        "numeroCpfCadastroNacPessoasJuridicas": advogado_data.get("numeroCpfCadastroNacPessoasJuridicas"),
        "siglaUnidadeFederacaoUnidadeOrganizacional": advogado_data.get("siglaUnidadeFederacaoUnidadeOrganizacional"),
    }
    
    # Estruturando o JSON de resposta conforme o schema
    resultado: PartesResponse = {
        "ativos": ativos,
        "passivos": passivos,
        "neutros": neutros,
        "advogado": advogado
    }
    
    return resultado

def npj_tramitacao(driver: WebDriver, idNpj: int):
    """
    Obtém os dados de um processo a partir do seu Número do Processo Judicial (NPJ).
    
    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do npj (Ex: "numeroProcesso": 20250019564).
    """
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")
    
    api_tramitacao = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/portal/processo/tramitacao/listarTramitacoesProcesso/{idNpj}"
    tramitacao = get_api_navegador(driver, api_tramitacao)
    tramitacao_data = tramitacao["data"]
    
    lista_tramitacoes = tramitacao_data["listaTramitacao"]
    
    json = []
    
    for item in lista_tramitacoes:
        data = item["dataTramitacao"]
        orgao = item["nomeOrgaoTramitacao"]

def npj_documentos(driver: WebDriver, idNpj: int) -> List[Documentos]:
    """
    Lista todos os documentos de um processo a partir do seu ID NPJ.
    :param driver: Instância do WebDriver do Selenium.
    :param idNpj: ID do NPJ do processo a ser consultado.
    :return: Lista de documentos no formato da classe Documentos.
    """
    if not isinstance(idNpj, int):
        try:
            idNpj = int(idNpj)
        except ValueError:
            raise ValueError("idNpj deve ser um inteiro.")
        
    api_documentos = f"https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/documentoV2?codigoTipoDocumentoPesquisa=0&numeroPosicaoPesquisa=0&numeroProcesso={idNpj}&tipoDocumento=0"
    documentos = get_api_navegador(driver, api_documentos)
    if documentos.get("statusCode") != 200:
        raise Exception(f"Erro na resposta da API: {documentos.get('status')}")
    documentos_data = documentos["data"]

    lista_documentos = documentos_data["listaDocumento"]

    return lista_documentos


