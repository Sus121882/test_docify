from typing import TypedDict, List

class CabecalhoResponse(TypedDict):
    """
    Representa a resposta da função npj_cabecalho.
    """
    npj: str
    adverso: str
    advogado: str
    uja: str
    polo: str
    processo: str
    natureza: str
    acao: str
    data_ajuizamento: str
    situacao: str
    tramitacao: str
    valor_causa: str

class DadosProcessoResponse(TypedDict):
    """
    Representa a resposta da função npj_dados_processo.
    """
    tipo: str
    natureza: str
    acao: str
    data_ajuizamento: str
    uf: str
    cadastramento: str
    cnj: str
    publicacao: str
    outros: List[str]