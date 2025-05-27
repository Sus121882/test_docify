from selenium.webdriver.remote.webdriver import WebDriver
import difflib
import unicodedata
import re
import os
import base64
import time

def get_api_navegador(driver: WebDriver, api_url: str, max_attempts: int = 3):
    """
    Faz uma requisição GET para uma API via navegador com retry em caso de erro.
    
    :param driver: Instância do WebDriver do Selenium.
    :param api_url: URL da API a ser acessada.
    :param max_attempts: Número máximo de tentativas (padrão: 3).
    :return: JSON obtido da API ou None se todas as tentativas falharem.
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            print(f"Iniciando requisição GET - tentativa {attempts + 1}...")
            json_data = driver.execute_async_script("""
                const api_url = arguments[0];
                const callback = arguments[arguments.length - 1];
                fetch(api_url, {
                    method: 'GET',
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => callback(data))
                .catch(error => callback({'error': error.toString()}));
            """, api_url)
            
            if json_data and 'error' not in json_data:
                print("Requisição GET bem-sucedida!")
                return json_data
            else:
                print(f"Erro na requisição: {json_data.get('error') if json_data else 'Nenhuma resposta recebida'}")
        except Exception as e:
            print("Ocorreu um erro ao fazer a requisição GET via navegador:", e)
        
        attempts += 1
        if attempts < max_attempts:
            print("Tentando novamente em 1 segundo...")
            time.sleep(1)
    
    print("Número máximo de tentativas alcançado. Retornando None.")
    return None

def post_api_navegador(driver, api_url: str, payload: dict, max_attempts: int = 3):
    """
    Faz uma requisição POST para uma API via navegador e retorna um dicionário com o resultado.
    - Se o retorno for JSON válido, devolve o JSON parseado.
    - Se o retorno não for JSON, devolve um dicionário com a extração de dados (se possível) ou o texto cru.

    :param driver: Instância do WebDriver do Selenium.
    :param api_url: URL da API a ser acessada.
    :param payload: Dicionário com os dados a serem enviados no corpo da requisição.
    :param max_attempts: Número máximo de tentativas (padrão: 3).
    :return: Dicionário contendo a resposta. Caso ocorra erro, retorna None.
    """

    def parse_service_response(texto: str) -> dict:
        """
        Tenta extrair status, message e data de uma string no formato:
        ServiceResponse [status=OK, messages=[], data=null]
        Caso não encontre, retorna {'raw': texto}.
        """
        import re
        padrao = r"status=(\w+).*?messages?=\[([^\]]*)\].*?data=(\w+)"
        match = re.search(padrao, texto)
        if match:
            status, message, data = match.groups()
            return {
                'status': status,
                'message': message,
                'data': data
            }
        else:
            # Se não casou, retorna o texto cru
            return {'raw': texto}
    attempts = 0
    while attempts < max_attempts:
        try:
            print("Iniciando requisição POST...")
            # Abaixo, usamos response.text() e tentamos converter para JSON;
            # se falhar, retornamos o texto cru para tratar manualmente.
            response_data = driver.execute_async_script("""
                const api_url = arguments[0];
                const payload = arguments[1];
                const callback = arguments[arguments.length - 1];

                fetch(api_url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload),
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.text();
                })
                .then(text => {
                    try {
                        // Tenta interpretar como JSON
                        const parsed = JSON.parse(text);
                        callback(parsed);
                    } catch (err) {
                        // Se não for JSON, devolve a string para tratar no Python
                        callback({ rawText: text });
                    }
                })
                .catch(error => callback({ error: error.toString() }));
            """, api_url, payload)

            # Verifica se houve erro de rede ou similar
            if 'error' in response_data:
                print(f"Erro na requisição: {response_data['error']}")
                return None

            # Se não for JSON, virá no formato: {'rawText': '...'}
            if 'rawText' in response_data:
                parsed = parse_service_response(response_data['rawText'])
                print("Requisição POST bem-sucedida (formato não-JSON).")
                return parsed

            # Caso seja JSON válido
            print("Requisição POST bem-sucedida (JSON).")
            return response_data

        except Exception as e:
            print("Ocorreu um erro ao fazer a requisição POST via navegador:", e)
        
        attempts += 1
        if attempts < max_attempts:
            print("Tentando novamente em 1 segundo...")
            time.sleep(1)
    
    print("Número máximo de tentativas alcançado. Retornando None.")
    return None
    
def put_api_navegador(driver: WebDriver, api_url: str, payload: dict, max_attempts: int = 3):
    """
    Faz uma requisição PUT para uma API via navegador e retorna o JSON obtido.
    
    :param driver: Instância do Webdriver do Selenium.
    :param api_url: URL da API a ser acessada.
    :param payload: Dicionário com os dados a serem enviados no corpo da requisição.
    :param max_attempts: Número máximo de tentativas (padrão: 3).
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            print("Iniciando requisição PUT...")
            json_data = driver.execute_async_script("""
                const api_url = arguments[0];
                const payload = arguments[1];
                const callback = arguments[arguments.length - 1];
                fetch(api_url, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload),
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => callback(data))
                .catch(error => callback({'error': error.toString()}));
            """, api_url, payload)
            
            if 'error' in json_data:
                print(f"Erro na requisição: {json_data['error']}") 
                return None
            print("Requisição PUT bem-sucedida!")
            return json_data

        except Exception as e:
            print("Ocorreu um erro ao fazer a requisição PUT via navegador:", e)
        attempts += 1
        if attempts < max_attempts:
            print("Tentando novamente em 1 segundo...")
            time.sleep(1)
    print("Número máximo de tentativas alcançado. Retornando None.")
    return None

def baixar_documento(driver, id_documento: str, caminho_destino: str = None) -> str:
    """
    Baixa um documento via navegador sem abrir uma nova guia, define a extensão do arquivo
    automaticamente com base no Content-Type retornado pela API e retorna o conteúdo do documento
    como uma string codificada em base64, que é JSON serializable.
    
    :param driver: Instância do WebDriver do Selenium.
    :param id_documento: ID do documento a ser baixado.
    :param caminho_destino: (Opcional) Caminho (incluindo o nome do arquivo) para salvar o documento.
                            Se None, o arquivo não será salvo.
    :return: O conteúdo do documento em uma string base64.
    """
    if not isinstance(id_documento, str):
        raise Exception("O ID do documento deve ser uma string!")
    
    url = f'https://juridico.intranet.bb.com.br/paj/resources/app/v0/processo/documento/download/{id_documento}'
    
    try:
        print(f"Baixando documento {id_documento}...")
        # Executa script assíncrono no navegador para buscar o arquivo e retornar dados em base64 e o Content-Type
        resultado = driver.execute_async_script("""
            const url = arguments[0];
            const callback = arguments[arguments.length - 1];
            fetch(url, {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta: ' + response.statusText);
                }
                // Obtém o Content-Type
                const contentType = response.headers.get('Content-Type');
                return response.blob().then(blob => ({ blob, contentType }));
            })
            .then(result => {
                const reader = new FileReader();
                reader.onloadend = function() {
                    // O resultado vem no formato "data:[<mediatype>];base64,<dados>"
                    const b64data = reader.result.split(',')[1];
                    callback({ base64: b64data, contentType: result.contentType });
                };
                reader.readAsDataURL(result.blob);
            })
            .catch(error => callback({ error: error.toString() }));
        """, url)
        
        # Trata erros do script JavaScript
        if isinstance(resultado, dict) and 'error' in resultado:
            raise Exception(resultado['error'])
        
        b64 = resultado.get('base64')
        content_type = resultado.get('contentType')
        if not b64 or not content_type:
            raise Exception("Não foi possível obter os dados do arquivo ou seu tipo.")
        
        # Mapeia alguns content types para extensões de arquivo
        extensoes = {
            'application/pdf': '.pdf',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            # Adicione outros mapeamentos conforme necessário
        }
        extensao = extensoes.get(content_type, '')
        
        # Se for informado um caminho para salvar o arquivo, converte o conteúdo base64 para bytes e salva
        if caminho_destino:
            # Se o caminho não possuir extensão, adiciona a extensão obtida
            if not os.path.splitext(caminho_destino)[1] and extensao:
                caminho_destino += extensao
            file_data = base64.b64decode(b64)
            with open(caminho_destino, 'wb') as f:
                f.write(file_data)
            print(f"Download concluído com sucesso! Arquivo salvo em: {caminho_destino}")
        
        # Retorna a string base64, que é JSON serializable
        return b64

    except Exception as e:
        raise Exception(f"Erro ao baixar o documento {id_documento}: {e}")


def baixar_documento_pdf(driver, id_documento: str, npj: str, caminho_destino: str = None) -> bool:
    """
    Baixa um documento somente se ele for do tipo PDF, salvando com um nome único.

    :param driver: Instância do Selenium WebDriver.
    :param id_documento: ID do documento a ser baixado.
    :param npj: Identificador NPJ utilizado para nomear o arquivo.
    :return: True se o download do PDF foi bem-sucedido, False se o documento não for PDF.
    """
    url = f'https://juridico.intranet.bb.com.br/paj/resources/app/v0/processo/documento/download/{id_documento}'

    try:
        print(f"Verificando documento {id_documento} para confirmação de PDF...")
        resultado = driver.execute_async_script("""
            const url = arguments[0];
            const callback = arguments[arguments.length - 1];
            fetch(url, {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta: ' + response.statusText);
                }
                const contentType = response.headers.get('Content-Type');
                return response.blob().then(blob => ({ blob, contentType }));
            })
            .then(result => {
                const reader = new FileReader();
                reader.onloadend = function() {
                    const b64data = reader.result.split(',')[1];
                    callback({ base64: b64data, contentType: result.contentType });
                };
                reader.readAsDataURL(result.blob);
            })
            .catch(error => callback({ error: error.toString() }));
        """, url)

        if isinstance(resultado, dict) and 'error' in resultado:
            raise Exception(resultado['error'])

        b64 = resultado.get('base64')
        content_type = resultado.get('contentType')
        if not b64 or not content_type:
            raise Exception("Não foi possível obter os dados do arquivo ou seu tipo.")

        # Verifica se o documento é PDF
        if content_type != 'application/pdf' and content_type != 'application/zip':
            print(f"Documento {id_documento} não é PDF ou ZIP (Content-Type: {content_type}). Download abortado.")
            return False
        
        if content_type == 'application/zip':
            print(f"Documento {id_documento} é um arquivo ZIP. Download para validação.")
            return True
        
         # Mapeia alguns content types para extensões de arquivo
        extensoes = {
            'application/pdf': '.pdf',
            'application/zip': '.zip'
            # Adicione outros mapeamentos conforme necessário
        }
        extensao = extensoes.get(content_type, '')

        # Define o caminho de destino com base no NPJ e no ID do documento, garantindo um nome único
        if caminho_destino:
            # Se o caminho não possuir extensão, adiciona a extensão obtida
            if not os.path.splitext(caminho_destino)[1] and extensao:
                caminho_destino += extensao
            
            file_data = base64.b64decode(b64)
            
            with open(caminho_destino, 'wb') as f:
                f.write(file_data)
            print(f"Download concluído com sucesso! Arquivo salvo em: {caminho_destino}")
            return True
        
        # Retorna a string base64, que é JSON serializable
        return b64

    except Exception as e:
        raise Exception(f"Erro ao baixar o documento {id_documento}: {e}")


def comparar_str(str1: str, str2: str):
    """
    Compara duas strings e retorna a similaridade entre elas.
    
    :param str1: Primeira string a ser comparada.
    :param str2: Segunda string a ser comparada.
    :return: Similaridade entre as strings (de 0 a 1), (1 = strings iguais).
    :example: comparar_str("João da Silva", "João Silva") -> 0.9
    """
    def normalize(text):
        # Remove acentos
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode("utf-8")
        # Converte para minúsculas
        text = text.lower()
        # Remove pontuação
        text = re.sub(r'[^\w\s]', '', text)
        # Remove espaços
        text = text.replace(" ", "")
        # Remove números
        text = re.sub(r'\d+', '', text)
        
        return text
    
    norm_str1 = normalize(str1)
    norm_str2 = normalize(str2)
    
    similarity_ratio = difflib.SequenceMatcher(None, norm_str1, norm_str2).ratio()
    return similarity_ratio