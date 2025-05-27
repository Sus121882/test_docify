from typing import TypedDict, List

class Publicacao(TypedDict):
    """
    Representa uma publicação judicial com os campos filtrados.
    """
    codigoEstadoPublicacaoJudicial: str
    codigoExternoProcessoInteresse: str
    codigoIdentificadorJornalOficial: str
    codigoUnidadeOrganizacionalRecebedor: int
    dataDivulgacao: str
    dataPublicacao: str
    dataRecebimento: str
    nomeEmpresaResponsavel: str
    numeroProcesso: int
    numeroProcessoCompleto: str
    numeroProcessoPrincipal: int
    numeroPublicacaoJudicial: int
    numeroVariacao: int
    textoPublicacaoJudicial: str

class PublicacoesResponse(TypedDict):
    """
    Representa a resposta da função listar_publicacoes.
    """
    quantidadeRegistro: int
    listaPublicacao: List[Publicacao]
