import sys
import inspect
from .schema.schemaPje import PJEResponse

def hello():
    """
    Imprime "Hello, world!" na tela.
    
    Exemplo de uso:
        >>> from DijurLib.utils.helpers import hello
        >>> hello()
        Hello, world!
    """
    print("Hello, world!")

def helpDijurApi():
    """
    Lista todas as funções definidas no módulo atual.
    """
    current_module = sys.modules[__name__]
    functions_list = [
        name for name, obj in inspect.getmembers(current_module, inspect.isfunction)
        if obj.__module__ == current_module.__name__
    ]
    
    if functions_list:
        print("Funções definidas no módulo atual:")
        for func in functions_list:
            print(f"- {func}")
    else:
        print("Nenhuma função encontrada no módulo atual.")

def test():
    """
    Função de teste para verificar se o módulo está funcionando corretamente.
    """
    print("Test")

# Função que retorna os dados validados usando o schema
def pje_exemplo() -> PJEResponse:
    """
    Simula uma requisição para a API e retorna os dados validados no formato do schema.
    """
    # Simulando a resposta JSON de uma API
    simulated_response: PJEResponse = {
        "status": "success",
        "message": "Sucesso",
        "count": 1,
        "items": [
            {
                "id": 213120583,
                "data_disponibilizacao": "2025-01-16",
                "siglaTribunal": "TJCE",
                "tipoComunicacao": "Intimação",
                "nomeOrgao": "1ª Vara Cível da Comarca de Maranguape",
                "texto": "Texto longo aqui...",
                "numero_processo": "00013528520008060119",
                "meio": "D",
                "link": "https://exemplo.com",
                "tipoDocumento": "INTIMAÇÃO DA SENTENÇA",
                "nomeClasse": "PROCEDIMENTO COMUM CíVEL",
                "codigoClasse": "7",
                "numeroComunicacao": 9200,
                "ativo": True,
                "hash": "AOMEBVQ8YpbcdBBUmTWG1G76d9l2za",
                "status": "P",
                "motivo_cancelamento": None,
                "data_cancelamento": None,
                "datadisponibilizacao": "16/01/2025",
                "dataenvio": "15/01/2025",
                "meiocompleto": "Diário de Justiça Eletrônico Nacional",
                "numeroprocessocommascara": "0001352-85.2000.8.06.0119",
                "destinatarios": [
                    {
                        "nome": "JOAO LUCIO ROLA FERREIRA",
                        "polo": "P",
                        "comunicacao_id": 213120583
                    }
                ],
                "destinatarioadvogados": [
                    {
                        "id": 327988797,
                        "comunicacao_id": 213120583,
                        "advogado_id": 1503852,
                        "created_at": "2025-01-15 12:40:45",
                        "updated_at": "2025-01-15 12:40:45",
                        "advogado": {
                            "id": 1503852,
                            "nome": "JOAO LUCIO ROLA FERREIRA",
                            "numero_oab": "7538",
                            "uf_oab": "CE"
                        }
                    }
                ]
            }
        ]
    }

    return simulated_response