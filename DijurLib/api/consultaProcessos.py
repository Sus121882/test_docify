from typing import Optional
from urllib.parse import urlencode
import requests

from ..utils.schema.schemaPje import PJEResponse


def get_processo_pje(
    texto: Optional[str] = None,
    siglaTribunal: Optional[str] = None,
    dataDisponibilizacaoInicio: Optional[str] = None,
    dataDisponibilizacaoFim: Optional[str] = None,
    numeroProcesso: Optional[str] = None
    ) -> PJEResponse:
    """
    Obtém processos do PJe com base nos filtros fornecidos.

    :param texto: Texto para busca nos processos.
    :param siglaTribunal: Sigla do tribunal.
    :param dataDisponibilizacaoInicio: Data inicial de disponibilização no formato 'yyyy.mm.dd'.
    :param dataDisponibilizacaoFim: Data final de disponibilização no formato 'yyyy.mm.dd'.
    :return: Resposta estruturada contendo os processos encontrados.
    :raises Exception: Se ocorrer um erro ao acessar a API do PJE.
    """
    
    if not isinstance(dataDisponibilizacaoFim, str):
        try:
            dataDisponibilizacaoFim = dataDisponibilizacaoFim.strftime("%Y-%m-%d")
        except AttributeError:
            raise ValueError("dataDisponibilizacaoFim deve ser uma string ou um objeto datetime") from None
        
    if not isinstance(dataDisponibilizacaoInicio, str):
        try:
            dataDisponibilizacaoInicio = dataDisponibilizacaoInicio.strftime("%Y-%m-%d")
        except AttributeError:
            raise ValueError("dataDisponibilizacaoInicio deve ser uma string ou um objeto datetime") from None
    
    base_url = 'https://comunicaapi.pje.jus.br/api/v1/comunicacao'

    parametros = {
        'pagina': '1',
        'itensPorPagina': '5',
        'texto': texto,
        'siglaTribunal': siglaTribunal.upper(),
        'dataDisponibilizacaoInicio': dataDisponibilizacaoInicio,
        'dataDisponibilizacaoFim': dataDisponibilizacaoFim,
        'numeroProcesso': numeroProcesso
    }

    # Remove os parâmetros que são None
    parametros_filtrados = {k: v for k, v in parametros.items() if v is not None}

    # Constrói a URL com os parâmetros filtrados
    url_final = f"{base_url}?{urlencode(parametros_filtrados)}"
    tentativas = 0
    while True:
        try:
            response = requests.get(url_final).json()
            break
        except Exception as e:
            tentativas += 1
            if tentativas >= 3:
                raise Exception(f'Erro ao acessar a API do PJE: {e}') from e

    if response is None:
        return None

    data = response.get("items", [])

    # Extração dos campos desejados com valores padrão para evitar KeyError
    resultado: PJEResponse = {
        "count": response.get("count", 0),
        "items": [
            {
                "data_disponibilizacao": item.get("data_disponibilizacao"),
                "siglaTribunal": item.get("siglaTribunal"),
                "tipoComunicacao": item.get("tipoComunicacao"),
                "nomeOrgao": item.get("nomeOrgao"),
                "texto": item.get("texto"),
                "numero_processo": item.get("numero_processo"),
                "link": item.get("link"),
                "tipoDocumento": item.get("tipoDocumento"),
                "nomeClasse": item.get("nomeClasse"),
                "datadisponibilizacao": item.get("datadisponibilizacao"),
                "dataenvio": item.get("dataenvio"),
                "meiocompleto": item.get("meiocompleto"),
                "numeroprocessocommascara": item.get("numeroprocessocommascara"),
                "destinatarios": item.get("destinatarios", []),
                "destinatarioadvogados": item.get("destinatarioadvogados", [])
            } for item in data
        ]
    }

    return resultado