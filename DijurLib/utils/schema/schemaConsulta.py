# schema/schemaConsulta.py

from typing import TypedDict, List, Optional

class Processo(TypedDict):
    """
    Representa um processo judicial.
    """
    numeroProcesso: int
    numeroProcessoPrincipalSaida: int
    numeroOrdemVariacaoSaida: int
    codigoPrefixoDependencia: int
    numeroContrarioPrincipal: int
    nomeContrarioPrincipal: str
    numeroAdvogadoProcesso: int
    nomeAdvogadoProcesso: str
    textoNumeroInventario: str
    codigoTipoEstadoProcesso: int
    textoEstadoProcesso: str
    codigoTipoProcesso: int
    codigoNaturezaProcesso: int
    textoNaturezaProcesso: str
    codigoTipoAcao: int
    codigoTipoRelacionamentoBancoProcesso: int
    indicadorProcessoConfidencial: str
    indicadorConsultarProcesso: str
    indicadorProcessoAtivo: str
    codigoTipoModeloCadastramento: int

class DataProcessos(TypedDict):
    """
    Representa a seção 'data' da resposta das APIs de processos.
    """
    quantidadeRegistro: Optional[int]
    quantidadeOcorrencia: Optional[int]
    indicadorContinuidade: str
    listaOcorrencia: List[Processo]

class ResponseProcessos(TypedDict):
    """
    Representa a resposta das APIs de processos.
    """
    messages: List[str]
    data: DataProcessos
    status: str
    statusCode: Optional[int]

class ProcessosResponse(TypedDict):
    """
    Representa o resultado final das funções de obtenção de processos.
    """
    quantidade: int
    indicadorContinuidade: str
    listaOcorrencia: List[Processo]
    

## SCHEMA CONSULTA NUMERO DO PROCESSO SIMPLES

from typing import TypedDict, List, Optional

class ProcessoRespostaSimples(TypedDict):
    """
    Representa um processo judicial na resposta.
    """
    numeroNPJ: str
    unidadeJuridica: int
    adverso: str
    numeroCNJ: str
    advogado: str
    situacao: str
    numeroProcesso: int
    numeroProcessoPrincipal: int
    numeroOrdemVariacao: int

class DataRespostaSimples(TypedDict):
    """
    Representa a seção 'data' da resposta das APIs de processos.
    """
    processos: List[ProcessoRespostaSimples]
    posicaoInicial: int
    posicaoFinal: int
    hasNext: bool
    hasPrevious: bool

class RespostaProcessosSimples(TypedDict):
    """
    Representa a resposta das APIs de processos.
    """
    messages: List[str]
    data: DataRespostaSimples
    status: str
