from classCrawler import Crawler
from classMiner import Miner

def main():

    numero_processo = '0731425-82.2014.8.02.0001'
    crawler = Crawler(numero_processo)
    detalhes_html = crawler.havest()
    print(detalhes_html)
    if detalhes_html:
        print("Página carregada com sucesso. Processando...")
        miner = Miner(detalhes_html, "json_schemaAlagoas.json")
        miner.processar_dados()
    else:
        print("Erro ao carregar os detalhes do processo.")

if __name__ == "__main__":
    main()
