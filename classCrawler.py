from ast import parse

import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs,urlparse,urlencode
from multidict import MultiDict
import re

class Crawler:
    def __init__(self,numero_processo):
        self.numero_processo = numero_processo
        self.session = requests.Session()
        self.base_url = "https://www2.tjal.jus.br"
        self.url_processo = ""
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

    def havest(self):

        if not self.validar_numero_processo():
            print(f"Erro: Número do processo '{self.numero_processo}' inválido.")
            return None
        try:
            if not self.obter_cookies_iniciais():
                print('Erro ao capturar cookies, Interropendo o processo')
                return None
            self.url_processo = self.enviar_requisicao()
            print(self.url_processo)
            if self.url_processo:
                html = self.acessar_detalhes()
                return html
            else:
                print("Erro ao obter a URL do processo.")
                return None
        except Exception as e:
            print(f"Erro no processo de coleta: {e}")
            return None

    def validar_numero_processo(self):
        padrao = r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$'
        return re.match(padrao, self.numero_processo) is not None

    def obter_cookies_iniciais(self):

        url = f"{self.base_url}/cpopg/open.do"
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            print("Cookies capturados com sucesso.")
            return True
        else:
            print(f"Erro ao capturar cookies: {response.status_code}")
            return None


    def construir_url(self, numero_processo):

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
        url = f"{self.base_url}/cpopg/search.do?{query_string}"
        return url


    def enviar_requisicao(self):


        url = self.construir_url(self.numero_processo)
        if not url:
            print("Erro: A URL não pôde ser construída. Interrompendo a requisição.")
            return None

        response = self.session.get(url, headers=self.headers, allow_redirects=False)
        if response.status_code == 302:

            redirect_url = f"{self.base_url}{response.headers.get('Location')}"
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

    def acessar_detalhes(self):

        headers = self.headers.copy()
        headers["Referer"] = self.url_processo

        try:
            response = self.session.get(self.url_processo, headers=headers)
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
