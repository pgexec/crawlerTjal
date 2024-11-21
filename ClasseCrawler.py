import requests

class Crawler:
    def __init__(self, url, headers, params=None):
        self.url = url
        self.headers = headers
        self.params = params
        self.html_content = ""

    def fetch_content(self):
        """
        Realiza uma requisição GET para buscar o conteúdo HTML da página.
        """
        try:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code == 200:
                print("Página acessada com sucesso!")
                self.html_content = response.text
                return self.html_content
            else:
                print(f"Erro ao acessar a página: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao fazer a requisição: {e}")
            return None
