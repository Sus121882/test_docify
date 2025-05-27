from typing import TypedDict, List

class Parte(TypedDict):
    """
    Representa uma parte (ativa, passiva ou neutra) envolvida no processo judicial.
    """
    nomeRazaoSocialClientePessoa: str
    codigoMercadoInternoPessoa: int
    numeroCpfCadastroNacPessoasJuridicasPessoa: int
    codigoTipoRelacionamentoPessoaBanco: int

class AdvogadoDetalhe(TypedDict):
    """
    Representa os detalhes do advogado associado ao processo.
    """
    nomeRazaoSocialAdvogado: str
    codigoPrefixoTributarioAdvogado: int
    nomeDependenciaTributarioAdvogado: str
    numeroCpfCadastroNacPessoasJuridicas: int
    siglaUnidadeFederacaoUnidadeOrganizacional: str

class PartesResponse(TypedDict):
    """
    Representa a resposta completa da função npj_pessoas_processo.
    """
    ativos: List[Parte]
    passivos: List[Parte]
    neutros: List[Parte]
    advogado: AdvogadoDetalhe
