from ast import parse

import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs,urlparse,urlencode
from multidict import MultiDict


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

        url = f"{self.base_url}/cpopg/open.do"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            print("Cookies capturados com sucesso.")
        else:
            print(f"Erro ao capturar cookies: {response.status_code}")

    def construir_url(self, numero_processo):
        """
        Constrói uma URL dinâmica para a requisição.
        """
        params = MultiDict([
            ("conversationId", ""),
            ("cbPesquisa", "NUMPROC"),
            ("numeroDigitoAnoUnificado", numero_processo[:15]),
            ("foroNumeroUnificado", numero_processo[-4:]),
            ("dadosConsulta.valorConsultaNuUnificado", numero_processo),
            ("dadosConsulta.valorConsultaNuUnificado", "UNIFICADO"),
            ("dadosConsulta.valorConsulta", ""),
            ("dadosConsulta.tipoNuProcesso", "UNIFICADO"),
        ])

        query_string = urlencode(params, doseq=True)
        url = f"{self.base_url}cpopg/search.do?{query_string}"
        return url


    def enviar_requisicao(self, numero_processo):


        url = self.construir_url(numero_processo)
        print(f"URL gerada: {url}")

        response = self.session.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code == 302:

            redirect_url = f"{self.base_url}{response.headers.get("Location")}"
            print(f"Redirecionado para: {redirect_url}")



            if redirect_url:
                print("Detalhes capturados com sucesso!")
                return redirect_url
            else:
                print(f"Erro ao acessar a URL redirecionada: {response.status_code}")
                return None
        elif response.status_code == 200:
            print("Requisição bem-sucedida!")
            return response.text
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None

    def acessar_detalhes(self, url_processo):

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
