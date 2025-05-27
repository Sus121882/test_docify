from selenium.webdriver.remote.webdriver import WebDriver

import time

from .base import get_api_navegador, put_api_navegador, post_api_navegador, comparar_str 
from .npj import npj_pessoas_processo

def cadastro_dados_iniciais(driver: WebDriver, npj: str, polo: str, autuacao: str):
    """
    Função que cadastra os dados iniciais do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param npj: ID do npj principal.
    :param polo: Polo do processo (A, P ou N).
    :param autuacao: Data de autuação do processo.
    :return: ID do processo criado.
    """
    
    if not isinstance(npj, str):
        raise Exception("npj deve ser uma string")
    elif not isinstance(polo, str):
        raise Exception("polo deve ser uma string")
    elif not isinstance(autuacao, str):
        raise Exception("autuacao deve ser uma string")
    
    # Confere se a autuação está no formato correto Ex: 05.02.2025 ou 05/02/2025
    if not autuacao[2] == '.' and not autuacao[2] == '/':
        raise Exception("Dados Iniciais: Data de autuação inválida")
    
    npj = npj.replace('/', '')
    autuacao = autuacao.replace('/', '.')
    
    dados = get_api_navegador(driver, f'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/consulta/{npj}')
    dados = dados['data']
    
    if polo.upper() == 'A' or polo.upper() == 'ATIVO':
        codigoTipoModeloCadastramento = '5'
    elif polo.upper() == 'P' or polo.upper() == 'PASSIVO':
        codigoTipoModeloCadastramento = '6'
    elif polo.upper() == 'N' or polo.upper() == 'NEUTRO':
        codigoTipoModeloCadastramento = '7'
    else:
        raise Exception("Dados Iniciais: Polo inválido")
    
    if dados['codigoNaturezaProcesso'] == 3:
        codigoNaturezaProcesso = 2
    else:
        codigoNaturezaProcesso = dados['codigoNaturezaProcesso']
    
    # Monta o payload da pagina 1 (Dados)
    payload_cadastro = {
        "valorCausa": 0,
        "codigoTipoModeloCadastramento": codigoTipoModeloCadastramento,
        "codigoPrefixoDependencia": 8553,
        "codigoTipoProcesso": dados['codigoTipoProcesso'],
        "codigoNaturezaProcesso": codigoNaturezaProcesso,
        "siglaUnidadeFederacao": "DF",
        "codigoGrupoMateriaProcesso": dados['codigoGrupoMateriaProcesso'],
        "indicadorConcessaoLiminar": dados['indicadorConcessaoLiminar'],
        "indicadorTransitoJudicialEspecial": dados['indicadorTransitoJudicialEspecial'],
        "dataAjuizamento": autuacao,
        "numeroProcessoPrincipal": dados['numeroProcesso'],
        "indicadorRegistroValidado": "S" 
    }
    
    cadastro_request = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/', payload_cadastro)
    
    if cadastro_request == None or cadastro_request['status'] != 'OK':
        raise Exception(f"Dados Iniciais: Erro ao cadastrar o processo")
    
    numeroProcessoCriado = cadastro_request['data']['numeroProcessoCriado']
    numeroProcessoPrincipalCriado = cadastro_request['data']['numeroProcessoPrincipalCriado']
    numeroProcessoPrincipalCriado = str(numeroProcessoPrincipalCriado)
    
    # Monta o payload da pagina 1 (Incidental)
    payload_incidental = {
        "numeroProcesso": numeroProcessoCriado,
        "numeroProcessoPrincipal": numeroProcessoPrincipalCriado,
        "poloBanco": polo
    }
    
    # Liga o incidental ao principal
    incidental = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/pessoas/incluirPessoa/inicial/incidental', payload_incidental)

    if incidental == None or incidental['status'] != 'OK':
        raise Exception(f"Dados Iniciais: Erro ao ligar o incidental ao principal")
    
    return numeroProcessoCriado

def cadastro_numeros(driver: WebDriver, numeroProcessoCriado: int, cnj: str, publicacao: str, outros: str = None):
    """
    Função que cadastra os números do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param cnj: Número do CNJ.
    :param publicacao: Número da publicação.
    :param outros: Outros números do processo.
    """
    
    if not isinstance(numeroProcessoCriado, int):
        raise Exception("numeroProcessoCriado deve ser um inteiro")
    elif not isinstance(cnj, str):
        raise Exception("cnj deve ser uma string")
    elif not isinstance(publicacao, str):
        raise Exception("publicacao deve ser uma string")
    elif outros != None and not isinstance(outros, str):
        raise Exception("outros deve ser uma string")
    
    cnj = cnj.replace('-', '').replace('.', '')
    publicacao = publicacao.replace('-', '').replace('/', '')
    
    # Monta o payload para ligar cnj a uf
    payload_uf = {
        "numeroConselhoNacionalJustica": cnj,
        "siglaUnidadeFederacao": "DF"
    }
    
    uf_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/numero/cnj', payload_uf)
    
    # monta o payload da pagina 2 (cnj)
    payload_cnj = {
        "numeroProcesso": numeroProcessoCriado,
        "textoNumeroInventario": cnj,
    }
    
    # Cadastra o CNJ
    cnj_api = put_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/numero/cnj', payload_cnj)
    
    if cnj_api == None or cnj_api['status'] != 'OK':
        raise Exception(f"Numeros: Erro ao cadastrar o CNJ")
    
    # Monta o payload da pagina 2 (publicacao)
    payload_publicacao = {
        "codigoTipoNumeracaoProcesso": 2,
        "numeroProcesso": numeroProcessoCriado,
        "textoNumeroExternoProcesso": publicacao,
    }
    
    # Cadastra o numero da publicacao
    publicacao_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/numero', payload_publicacao)
    
    if publicacao_api == None or publicacao_api['status'] != 'OK':
        raise Exception(f"Numeros: Erro ao cadastrar o numero da publicacao")
    
    if outros:
        # Monta o payload da pagina 2 (outros)
        payload_outros = {
            "numeroProcesso": numeroProcessoCriado,
            "codigoTipoNumeracaoProcesso": 3,
            "textoNumeroExternoProcesso": outros,
        }
        
        # Cadastra o outros
        outros_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/numero', payload_outros)
        
        if outros_api == None or outros_api['status'] != 'OK':
            raise Exception(f"Numeros: Erro ao cadastrar o outros")
    
    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 61,
        "codigoTipoSubFaseCadastramento": 2,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Números do Processo",
        "nomeTipoFaseCadastramento": "Dados Iniciais",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Numeros: Erro ao passar para a proxima pagina")

def cadastro_partes(driver: WebDriver, numeroProcessoCriado: int, polos: list):
    """
    Função que confere as partes do processo no cadastro.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param polos: Lista com os polos do processo (ativos, passivos e neutros) (Ex: polos = polos_ativos, polos_passivos, polos_neutros)
    
    :return True se as partes conferem, False caso contrário.
    """
    
    polos_ativos, polos_passivos, polos_neutros = polos
    
    polos_cadastrados = npj_pessoas_processo(driver, numeroProcessoCriado)
    
    ativos_cadastrados = polos_cadastrados['ativos']
    
    passivos_cadastrados = polos_cadastrados['passivos']
    
    neutros_cadastrados = polos_cadastrados['neutros']
    
    conferencia = True
    
    ativos = False
    for polo in ativos_cadastrados:
        for nome in polos_ativos:
            compara_ativos = comparar_str(polo['nomeRazaoSocialClientePessoa'], nome)
            if compara_ativos >= 0.85:
                ativos = True
                break
        if ativos:
            break
    
    if not ativos:
        conferencia = False

    passivos = False
    for polo in passivos_cadastrados:
        for nome in polos_passivos:
            compara_passivos = comparar_str(polo['nomeRazaoSocialClientePessoa'], nome)
            if compara_passivos >= 0.85:
                passivos = True
                break
        if passivos:
            break
        
    if not passivos:
        conferencia = False

    if len(polos_neutros) == 0:
        neutros = True
    
    else:
        neutros = False
        for polo in neutros_cadastrados:
            for nome in polos_neutros:
                compara_neutros = comparar_str(polo['nomeRazaoSocialClientePessoa'], nome)
                if compara_neutros >= 0.85:
                    neutros = True
                    break
            if neutros:
                break
    
    if not neutros:
        conferencia = False
        
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 61,
        "codigoTipoSubFaseCadastramento": 3,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Pessoas do Processo",
        "nomeTipoFaseCadastramento": "Dados Iniciais",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
        
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Partes: Erro ao passar para a proxima pagina")
    
    if not conferencia:
        return False
    
    return True

def cadastro_tramitacao(driver: WebDriver, numeroProcessoCriado: int, tramitacao: str, tribunal: str):
    """
    Função que cadastra a tramitação do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param tramitacao: Tramitação do processo.
    :param tribunal: Tribunal do processo (TST, STF, STJ).
    """
    
    if tribunal.upper() == 'STJ':
        # Dicionario tramitação stj("81"):
        dicionario_tramitacao = {
            "CORTE ESPECIAL": 1,
            "TRIBUNAL PLENO": 2,
            "01 SECAO": 3,
            "01 TURMA": 4,
            "02 SECAO": 5,
            "02 TURMA": 6,
            "03 SECAO": 7,
            "03 TURMA": 8,
            "04 TURMA": 9,
            "05 TURMA": 10,
            "06 TURMA": 11,
            "PRESIDENCIA": 12,
            "SUPERIOR TRIBUNAL DE JUSTICA": 14
        }
        
        codigoOrgaoTransito = "81"
    
    elif tribunal.upper() == 'TST':
        # Dicionario tramitação tst("122"):
        dicionario_tramitacao = {
            "CORREGEDORIA-GERAL DA JUSTICA DO TRABALHO": 1,
            "TRIBUNAL PLENO": 2,
            "SECAO ESPECIALIZADA EM DISSIDIOS COLETIVOS": 3,
            "SUBSECAO I ESPECIALIZ DISSIDIOS INDIVIDUAIS": 4,
            "SUBSECAO II ESPECIALI DISSIDIOS INDIVIDUAIS": 5,
            "01 TURMA": 6,
            "02 TURMA": 7,
            "03 TURMA": 8,
            "04 TURMA": 9,
            "05 TURMA": 10,
            "06 TURMA": 11,
            "07 TURMA": 12,
            "PRESIDENCIA": 13,
            "08 TURMA": 14,
            "ORGAO ESPECIAL": 15
        }
        
        codigoOrgaoTransito = "122"
    
    # Cria payload da tramitação
    payload_tramitacao = {
        "numeroProcesso": numeroProcessoCriado,
        "codigoOrgaoTransito": codigoOrgaoTransito,
        "codigoComplementoOrgaoTransito": dicionario_tramitacao[tramitacao.upper()],
    }
    
    # Cadastra a tramitação
    tramitacao_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/complementar/orgaotramitacao', payload_tramitacao)
    
    if tramitacao_api == None or tramitacao_api['status'] != 'OK':
        raise Exception(f"Tramitação: Erro ao cadastrar a tramitacao")
    
    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 61,
        "codigoTipoSubFaseCadastramento": 4,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Órgão de Tramitação",
        "nomeTipoFaseCadastramento": "Dados Iniciais",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Tramitação: Erro ao passar para a proxima pagina")
    
def cadastro_advogado(driver: WebDriver, numeroProcessoCriado: int, advogado: str):
    # Busca advogado
    advogado_payload = {
        'codigoTipoAdvogado': 2,
        'nome': advogado.upper()
    }
    
    advogado_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v0/advogado', advogado_payload)
    
    if advogado_api == None or advogado_api['status'] != 'OK':
        raise Exception(f"Advogado: Erro ao buscar o advogado")
    
    advogado_data = advogado_api['data'][0]
    
    materia_payload = numeroProcessoCriado
    
    materia_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/publicacao/validacao/materia/', materia_payload)
    
    if materia_api['status'] != 'OK':
        raise Exception(f"Advogado: Erro ao indicar a materia")
    
    indicar_payload = {
        "numeroProcesso": numeroProcessoCriado,
        "numeroAdvogado": advogado_data['numeroAdvogado'],
        "codigoTipoAdvogado": advogado_data['codigoTipoAdvogado'],
        "numeroCpfCnpjPessoaInteresseJuridico": advogado_data['cpfCnpj'],
        "chaveAdvogado": advogado_data['matricula']
    }
    
    indicar_adv_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v0/distribuicao/processo/funcionario', indicar_payload)
    
    if indicar_adv_api == None or indicar_adv_api['status'] != 'OK':
        raise Exception(f"Advogado: Erro ao indicar o advogado")
    
    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 62,
        "codigoTipoSubFaseCadastramento": 1,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Distribuição",
        "nomeTipoFaseCadastramento": "Distribuição",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Advogado: Erro ao passar para a proxima pagina")

def cadastro_dependencias(driver: WebDriver, numeroProcessoCriado: int):
    """
    Função que cadastra as dependências do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    """
    
    if not isinstance(numeroProcessoCriado, int):
        raise Exception("nDependencias: umeroProcessoCriado deve ser um inteiro")
    
    # Busca as dependências relacionadas
    dependenciasRelacionada = get_api_navegador(
        driver,
        f'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dados/processo/dependencia/listarDependenciasRelacionadaAoProcessoJuridico/{numeroProcessoCriado}/0'
    )
    if dependenciasRelacionada == None or dependenciasRelacionada['status'] != 'OK':
        raise Exception(f"Dependencias: Erro ao buscar as dependencias")
    
    dependenciasRelacionada = dependenciasRelacionada['data']['listaOcorrencia']

    # Busca as dependências contrárias
    dependenciContrarios = get_api_navegador(
        driver,
        f'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dados/processo/dependencia/listarDependenciaUnidadeOrganizacionalContrariosAoBanco/{numeroProcessoCriado}'
    )
    if dependenciContrarios == None or dependenciContrarios['status'] != 'OK':
        raise Exception(f"Dependencias: Erro ao buscar as dependencias contrarias")
    dependenciContrarios = dependenciContrarios['data']

    # Função para atualizar os campos de cada dependência
    def atualizar_dependencia(dep):
        dep['codigoTipoVinculoDependencia'] = "1"
        dep['textoTipoVinculoDependencia'] = "Interessada"
        return dep

    # Atualiza os objetos de cada lista
    dependenciasRelacionada = [atualizar_dependencia(dep) for dep in dependenciasRelacionada]
    dependenciContrarios = [atualizar_dependencia(dep) for dep in dependenciContrarios]

    # Objeto do 8553 conforme o padrão desejado
    prefixo8553 = {
        "numeroProcesso": numeroProcessoCriado,
        "codigoUnidadeOrganizacional": 18908,
        "codigoPrefixoDependencia": 8553,
        "textoNomeDependencia": "DIJUR-JURIDICA",
        "codigoTipoVinculoDependencia": "2",
        "textoMotivoVinculacao": None,
        "textoTipoVinculoDependencia": None,
        "subordinada": 0,
        "uf": "DF",
        "telefone": "34932312",
        "municipio": "BRASILIA"
    }

    # Monta a lista final com o objeto manual e os demais atualizados
    payload_dependencias = [prefixo8553] + dependenciasRelacionada + dependenciContrarios

    dependencias_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dados/processo/dependencia/salvar', payload_dependencias)
    
    if dependencias_api == None or dependencias_api['status'] != 'OK':
        raise Exception(f"Dependencias: Erro ao salvar as dependencias")

    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 63,
        "codigoTipoSubFaseCadastramento": 2,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Dependências",
        "nomeTipoFaseCadastramento": "Dados Complementares",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Dependencias: Erro ao passar para a proxima pagina")

def cadastro_sinopse(driver: WebDriver, numeroProcessoCriado: int, sinopse: str = None):
    """
    Função que cadastra a sinopse do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param sinopse: Sinopse do processo.
    """
    
    if not isinstance(numeroProcessoCriado, int):
        raise Exception("Sinopse: numeroProcessoCriado deve ser um inteiro")
    
    elif not isinstance(sinopse, str) and sinopse != None:
        raise Exception("Sinopse: sinopse deve ser uma string")

    payload_sinopse = {
        "numeroProcesso": numeroProcessoCriado,
        "textoObservacao": "",
        "valorTamanhoTextoObservacao": 0
    }
    
    sinopse_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/complementar/assunto/alterar', payload_sinopse)
    
    if sinopse_api == None or sinopse_api['status'] != 'OK':
        raise Exception(f"Sinopse: Erro ao cadastrar a sinopse")
    
    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 63,
        "codigoTipoSubFaseCadastramento": 3,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Assunto",
        "nomeTipoFaseCadastramento": "Dados Complementares",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Sinopse: Erro ao passar para a proxima pagina")
    
def cadastro_tipo_acao(driver: WebDriver, numeroProcessoCriado: int, tipo_acao: str, tribunal: str):
    """
    Função que cadastra o tipo de ação do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param tipo_acao: Tipo de ação do processo.
    :param tribunal: Tribunal do processo (STJ, TST, STF).
    """
    
    if tribunal.upper() == 'STJ':
        cod_processo_dict = {
            'RECURSO ESPECIAL': 20065,
            'AGRAVO EM RECURSO ESPECIAL': 226,
            'Conflito de competecia': 35,
            'CAUTELAR': 20078,
            'RECLAMAÇÃO': 245,
            'AGRAVO DE INSTRUMENTO': 1,
            # 'MANDADO DE SEGURANÇA': 96,
        }
    
    elif tribunal.upper() == 'TST':
        cod_processo_dict = {
            'AGRAVO DE INSTRUMENTO': 1,
            'RECURSO DE REVISTA': 132,
            'RECURSO EXTRAORDINARIO': 135,
            'RECURSO ORDINARIO': 136
        }
        
    else:
        raise Exception("Tipo Ação: Tribunal inválido")
    
    tipo_acao = cod_processo_dict[tipo_acao.upper()]
    
    payload_tipo_acao = {
        "numeroProcesso": numeroProcessoCriado,
        "codigoTipoAcao": tipo_acao
    }
    
    tipo_acao_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/tecnico/acao/alterar', payload_tipo_acao)
    
    if tipo_acao_api == None or tipo_acao_api['status'] != 'OK':
        raise Exception(f"Tipo Ação: Erro ao cadastrar o tipo de acao")
    
    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 63,
        "codigoTipoSubFaseCadastramento": 4,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Tipo de Ação",
        "nomeTipoFaseCadastramento": "Dados Complementares",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Tipo Ação: Erro ao passar para a proxima pagina")
    
def cadastro_classe_cnj(driver: WebDriver, numeroProcessoCriado: int, tipo_acao: str):
    """
    Função que cadastra a classe CNJ do processo.
    
    :param driver: Instância do Webdriver do Selenium.
    :param numeroProcessoCriado: Número do processo criado.
    :param tipo_acao: Tipo de ação do processo.
    """
    
    cod_processo_dict = {
        'RECURSO ESPECIAL': '1032',
        'AGRAVO EM RECURSO ESPECIAL': '1032',
        'Conflito de competecia': '1054',
        'CAUTELAR': '1057',
        'RECLAMAÇÃO': '1030',
        'AGRAVO DE INSTRUMENTO': '1044',
        'MANDADO DE SEGURANÇA': '1029',
        'AGRAVO DE INSTRUMENTO': '1002',
        'RECURSO DE REVISTA': '1008',
        'RECURSO ORDINARIO': '211',
        
    }

    codigo_classe = cod_processo_dict[tipo_acao.upper()]
    
    payload_classe_cnj = {
        "numeroProcesso": numeroProcessoCriado,
        "codigoClasse": codigo_classe,
        "codigoAssunto": 0
    }
    
    classe_cnj_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dados/processo/classeCNJ/incluir', payload_classe_cnj)
    
    if classe_cnj_api == None or classe_cnj_api['status'] != 'OK':
        raise Exception(f"Classe CNJ: Erro ao cadastrar a classe CNJ")

    confere_api = get_api_navegador(driver, f'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dados/processo/classeCNJ/listarClassesConselhoNacionalJusticaProcessoJuridico/{numeroProcessoCriado}/true')
    
    if confere_api == None or confere_api['status'] != 'OK':
        raise Exception(f"Classe CNJ: Erro ao buscar a classe CNJ")

    # Finaliza icidental
    payload_finalizar_incidental = {
        "numeroProcesso": numeroProcessoCriado
    }
    
    finalizar_incidental_api = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/incidental/fase/finalizar-incidental', payload_finalizar_incidental)
    
    if 'status=OK' not in finalizar_incidental_api['raw']:
        raise Exception(f"Classe CNJ: Erro ao finalizar a incidental")

    # Passa pra proxima pagina
    payload_proxima_pagina = {
        "codigoTipoCadastramento": 1,
        "codigoTipoFaseCadastramento": 63,
        "codigoTipoSubFaseCadastramento": 5,
        "codigoTipoModeloCadastramento": 4,
        "codigoEstadoSubFaseCadastramento": "A",
        "nomeTipoSubFaseCadastramento": "Classe CNJ",
        "nomeTipoFaseCadastramento": "Dados Complementares",
        "numeroProcesso": numeroProcessoCriado,
    }
    
    proxima_pagina = post_api_navegador(driver, 'https://juridico.intranet.bb.com.br/paj/resources/app/v1/processo/cadastro/fluxo/fase/proxima', payload_proxima_pagina)
    
    if proxima_pagina == None or proxima_pagina['data'] != True:
        raise Exception(f"Classe CNJ: Erro ao passar para a proxima pagina")

def cadastro(driver: WebDriver, npj: str, polo: str, autuacao: str, cnj: str, publicacao: str, polos: list, tramitacao: str, advogado: str, tipo_processo: str, tribunal: str, outros: str = None):
    """
    Função que cadastra uma incidental.
    
    :param driver: Instância do Webdriver do Selenium.
    :param npj: ID do npj principal.
    :param polo: Polo do processo (A, P ou N).
    :param autuacao: Data de autuação do processo.
    :param cnj: Número do CNJ.
    :param publicacao: Número da publicação.
    :param polos: Lista com os polos do processo (ativos, passivos e neutros) (Ex: polos = polos_ativos, polos_passivos, polos_neutros)
    :param tramitacao: Tramitação do processo.
    :param advogado: Nome do advogado.
    :param tipo_processo: Tipo de ação do processo.
    :param tribunal: Tribunal do processo (STJ, TST, STF).
    :param outros: Outros números do processo (opcional).
    """
                
    numeroProcessoCriado = cadastro_dados_iniciais(driver, npj, polo, autuacao)
    time.sleep(1)
    
    cadastro_numeros(driver, numeroProcessoCriado, cnj, publicacao, outros)        
    time.sleep(1)   
                
    
    confere_partes = cadastro_partes(driver, numeroProcessoCriado, polos)
    time.sleep(1)
    
    cadastro_tramitacao(driver, numeroProcessoCriado, tramitacao, tribunal)
    time.sleep(1)
    
    cadastro_advogado(driver, numeroProcessoCriado, advogado)
    time.sleep(1)
    
    cadastro_dependencias(driver, numeroProcessoCriado)
    time.sleep(1)
    
    cadastro_sinopse(driver, numeroProcessoCriado)
    time.sleep(1)
    
    cadastro_tipo_acao(driver, numeroProcessoCriado, tipo_processo, tribunal)
    time.sleep(1)
    
    cadastro_classe_cnj(driver, numeroProcessoCriado, tipo_processo)
    
    if not confere_partes:
        return numeroProcessoCriado, False
    
    return numeroProcessoCriado, True