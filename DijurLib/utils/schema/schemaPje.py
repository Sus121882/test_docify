from typing import TypedDict, List, Optional

class Advogado(TypedDict):
    nome: str
    numero_oab: str
    uf_oab: str

class DestinatarioAdvogado(TypedDict):
    advogado: Advogado

class Destinatario(TypedDict):
    nome: str
    polo: str

class Item(TypedDict):
    data_disponibilizacao: Optional[str]
    siglaTribunal: str
    tipoComunicacao: str
    nomeOrgao: str
    texto: str
    numero_processo: str
    link: str
    tipoDocumento: str
    nomeClasse: str
    datadisponibilizacao: Optional[str]
    dataenvio: Optional[str]
    meiocompleto: str
    numeroprocessocommascara: str
    destinatarios: List[Destinatario]
    destinatarioadvogados: List[DestinatarioAdvogado]

class PJEResponse(TypedDict):
    count: int
    items: List[Item]