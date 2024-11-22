import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs,urlparse,unquote


class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www2.tjal.jus.br/"
        self.headers = {
             "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            "Connection": "keep-alive",
            "Cookie": "JSESSIONID=8A1DBEA85ED2543D2F4925939D599410.esajlayout3",  # Atualize o cookie conforme necessário
            "Host": "www2.tjal.jus.br",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    def enviar_requisicao(self, numero_processo):
        """
        Envia a requisição inicial e captura o valor do parâmetro 'retorno'.
        """
        url = f"{self.base_url}/sajcas/conteudoIdentificacaoJson"

        params = {
            "script": "1732258966787",  # Exemplo de script
            "retorno": f"{self.base_url}/cpopg/show.do",  # Padrão inicial (será sobrescrito)
            "dadosConsulta.pesquisaNuUnificado": numero_processo,
            "dadosConsulta.valorConsulta": numero_processo,
            "cbPesquisa": "NUMPROC",
            "tipoNuProcesso": "UNIFICADO",
        }

        try:
            # Enviar a requisição
            response = self.session.get(url, headers=self.headers, params=params, allow_redirects=False)

            if response.status_code == 200:
                print("Requisição inicial realizada com sucesso.")
                # Captura o valor do parâmetro `retorno` na URL
                query_params = parse_qs(urlparse(response.url).query)
                retorno_encoded = query_params.get("retorno", [None])[0]
                if retorno_encoded:
                    retorno_decoded = unquote(retorno_encoded)
                    print(f"Valor do parâmetro 'retorno': {retorno_decoded}")
                    return retorno_decoded
                else:
                    print("Parâmetro 'retorno' não encontrado na URL.")
                    return None
            else:
                print(f"Erro ao realizar a requisição inicial: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao enviar a requisição inicial: {e}")
            return None



    def acessar_detalhes(self, url_processo):
        """
        Acessa a página de detalhes do processo e retorna o HTML.
        """
        headers = self.headers.copy()
        headers["Referer"] = url_processo

        try:
            response = self.session.get(url_processo, headers=headers)
            if response.status_code == 200:
                print("Detalhes do processo acessados com sucesso!")
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            else:
                print(f"Erro ao acessar os detalhes do processo: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao acessar os detalhes do processo: {e}")
            return None
