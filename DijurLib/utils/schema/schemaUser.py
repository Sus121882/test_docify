from typing import TypedDict, List, Optional

class UserData(TypedDict):
    """
    Representa a seção 'data' da resposta da API.
    """
    chave: str
    acessos: str
    listaPerfis: List[str]
    codDependencia: str
    codigoUnidadeOrganizacional: str
    nome: str
    listaEscritorios: List[str]

class ResponseAPI(TypedDict):
    """
    Representa a resposta da API.
    """
    messages: List[str]
    data: UserData
    status: str
    statusCode: Optional[int]