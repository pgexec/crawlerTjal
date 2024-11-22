import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs,urlparse,quote,urlencode,unquote


class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www2.tjal.jus.br/"
        self.headers = {
             "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            "Connection": "keep-alive",
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

    def obter_cookies_iniciais(self):
        """
        Acessa a página inicial para capturar os cookies necessários.
        """
        url = f"{self.base_url}/cpopg/open.do"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            print("Cookies capturados com sucesso.")
        else:
            print(f"Erro ao capturar cookies: {response.status_code}")

    def extrair_foro(self, numero_processo):
        """
        Extrai o foro dos dois últimos dígitos do número do processo.
        """
        return numero_processo.split(".")[-1][:2]

    def enviar_requisicao(self, numero_processo):
        """
        Envia a requisição inicial e captura o valor do parâmetro 'retorno'.
        """

        foro_numero = numero_processo.split(".")[-1][:4]

        retorno_params = {
            "conversationId": "",
            "cbPesquisa": "NUMPROC",
            "numeroDigitoAnoUnificado": numero_processo,
            "foroNumeroUnificado": foro_numero,
            "dadosConsulta.valorConsultaNuUnificado": "UNIFICADO",
            "dadosConsulta.valorConsulta": numero_processo,
            "dadosConsulta.tipoNuProcesso": "UNIFICADO",
        }
        retorno_url = f"{self.base_url}/cpopg/search.do?{urlencode(retorno_params)}"
        retorno_url_encoded = unquote(retorno_url)
        print(retorno_url_encoded)


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
