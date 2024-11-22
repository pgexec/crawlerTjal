from classCrawler import Crawler
from classMiner import Miner

def main():

    numero_processo = input("Digite o número do processo (ex: 0731425-82.2014.8.02.0001): ").strip()
    crawler = Crawler()

    print("Realizando consulta...")
    url_processo = crawler.enviar_requisicao(numero_processo)

    if not url_processo:
        print("Não foi possível obter a URL do processo. Encerrando.")
        return

    print("Acessando detalhes do processo...")
    detalhes_html = crawler.acessar_detalhes(url_processo)
    print(detalhes_html.prettify())

    if detalhes_html:
        print("Página carregada com sucesso. Processando...")
        miner = Miner(detalhes_html, "json_schemaAlagoas.json")  # Use o schema apropriado

        # Processa os dados e salva no arquivo JSON
        if miner.processar_dados(nome_arquivo=f"{numero_processo}.json"):
            print(f"Dados do processo {numero_processo} salvos com sucesso!")
        else:
            print("Erro ao processar e salvar os dados do processo.")
    else:
        print("Erro ao carregar os detalhes do processo.")


if __name__ == "__main__":
    main()
