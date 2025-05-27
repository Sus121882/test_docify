from typing import TypedDict, List, Optional

class Andamento(TypedDict):
    numeroProcesso: int
    numeroProcessoPrincipal: int
    numeroOrdemVariacao: int
    codigoTipoAndamento: int
    textoTipoAndamento: str
    codigoTipoCategoriaAndamento: int
    textoTipoCategoriaAndamento: str
    codigoGrupoTipoAndamento: int
    textoGrupoTipoAndamento: str
    codigoTipoSolicitanteAndamento: str
    textoTipoSolicitanteAndamento: str
    numeroAndamentoProcesso: int
    dataAndamento: str
    textoInformacao: str
    valorTotalCalculo: float
    codigoUsuarioResponsavelAtualizacao: str
    timestampAtualizacaoRegistro: str
    indicadorAndamentoCompleto: str
    indicadorRegistroAtivo: str
    indicadorDocumentoDigitalizado: str
    codigoUsuarioResponsavelAndamento: str
    codigoNucleoResponsavelAndamento: int
    codigoDependenciaResponsavelAndamento: int
    indicadorControleMensagemInterno: str
    codigoTipoConfidencialidade: int
    indicadorIncentivoJuridicoNegocial: str
    indicadorDocumentoDigitalizadoMigrado: str
    numeroFatura: int
    textoTag: str

class AndamentoItem(TypedDict):
    andamento: Andamento
    documentos: Optional[List[dict]]
    quantidadeTotalDocumentos: int
    haMaisDocumentos: bool
    andamentoAntigo: Optional[dict]

class Documentos(TypedDict):
    """
    Representa um documento vinculado a um andamento.
    """
    numeroSequencialInclusaoDocumento: int
    numeroIdentificacaoTipoDocumento: int
    dataDigitalizacaoDocumento: str
    codigoGrupoDocumento: int
    codigoGeralDocumento: int
    codigoFaseInclusaoDocumento: int
    codigoTipoDocumentoDigitalizado: int
    textoTipoDocumentoDigitalizado: str
    codigoUsuarioResponsavelAtualizacao: str
    timestampAtualizacaoRegistro: str
    codigoDocumentoJuridico: str
    numeroRastreamentoAno: int
    numeroRastreamentoSequencial: int
    nomeArquivoOriginal: str
    codigoTipoDocumento: int
    textoTipoDocumento: str
    codigoNivelConfidencialidade: int
    textoNivelConfidencialidade: str

class Data(TypedDict):
    """
    Representa os dados da resposta da função listar_documento_vinculado.
    """
    indicadorContinuacaoPesquisa: str
    quantidadeTotalOcorrencia: int
    quantidadeOcorrencia: int
    listaDocumento: List[Documentos]

class ResponseSchema(TypedDict):
    """
    Representa a resposta completa da função listar_documento_vinculado.
    """
    messages: List[str]
    data: Data
    status: str
    statusCode: int