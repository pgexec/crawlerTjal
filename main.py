import requests
from bs4 import BeautifulSoup


def acessar_pagina_inicial():
    url = "https://www2.tjal.jus.br/cpopg/open.do"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    session = requests.Session()  # Usar sessão para manter cookies
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            print("Página inicial acessada com sucesso.")
            return session
        else:
            print(f"Erro ao acessar a página inicial: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao acessar a página inicial: {e}")
        return None


def consultar_processo(session, numero_processo):
    # Endpoint de consulta
    url = "https://www2.tjal.jus.br/sajcas/conteudoIdentificacaoJson"

    # Parâmetros da requisição GET
    params = {
        "script": "1732172568957",  # Valor fixo ou variável
        "retorno": f"https://www2.tjal.jus.br/cpopg/show.do?processo.codigo=01000I1FT0000&processo.foro=1&processo.numero={numero_processo}"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www2.tjal.jus.br/cpopg/open.do",  # Referer inicial
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        # Fazer a requisição GET
        response = session.get(url, headers=headers, params=params)

        if response.status_code == 200:
            print("Consulta realizada com sucesso!")
            dados = response.json()
            url_login = dados.get("urlLogin")  # Obter a URL da próxima etapa
            if url_login:
                print(f"URL do processo encontrada: {url_login}")
                return url_login
            else:
                print("URL do processo não encontrada no JSON.")
                return None
        else:
            print(f"Erro na consulta: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao realizar a consulta: {e}")
        return None


def acessar_detalhes(session, url_processo):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": url_processo,  # Referer com a URL do processo
    }

    try:
        # Fazer a requisição para a URL do processo
        response = session.get(url_processo, headers=headers)
        if response.status_code == 200:
            print("Detalhes do processo acessados com sucesso!")
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"Erro ao acessar os detalhes do processo: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao acessar os detalhes do processo: {e}")
        return None


def main():
    numero_processo = input("Digite o número do processo (ex: 0731425-82.2014.8.02.0001): ").strip()

    print("Acessando página inicial...")
    session = acessar_pagina_inicial()

    if session:
        print("Realizando consulta...")
        url_processo = consultar_processo(session, numero_processo)

        if url_processo:
            print("Acessando detalhes do processo...")
            detalhes_html = acessar_detalhes(session, url_processo)

            if detalhes_html:
                print("Página carregada com sucesso. Processando...")
                print(detalhes_html.prettify())  # Exibe o HTML
            else:
                print("Erro ao carregar os detalhes do processo.")
        else:
            print("Não foi possível acessar os detalhes do processo.")
    else:
        print("Erro ao acessar a página inicial.")


if __name__ == "__main__":
    main()
