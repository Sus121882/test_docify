from DijurLib.utils.schema.schemaUser import UserData
from .base import get_api_navegador

def get_logged_user(driver):
    url = 'https://juridico.intranet.bb.com.br/paj/resources/app/portal/dadosusuario/get-current-user/'
    try:
        response = get_api_navegador(driver, url)
        if response['status'] == 'OK':
            return UserData(
                chave=response['data']['chave'],
                acessos=response['data']['acessos'],
                listaPerfis=response['data']['listaPerfis'],
                codDependencia=response['data']['codDependencia'],
                codigoUnidadeOrganizacional=response['data']['codigoUnidadeOrganizacional'],
                nome=response['data']['nome'],
                listaEscritorios=response['data']['listaEscritorios']
            )
        else:
            return {"error": "Status not OK"}
    except Exception as e:
        return {"error": str(e)}
