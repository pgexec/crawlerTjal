import re
from cgi import print_form

from jsonschema import validate, ValidationError
import json

class Miner:
    def __init__(self, site, json_schema_path):

        self.site = site
        self.json_schema = json_schema_path
        self.dados_processo = {}

        try:
            with open(json_schema_path,"r",encoding="utf-8") as schema_file:
                self.json_schema = json.load(schema_file)
        except Exception as e:
            print(f"Erro ao carregar o JSON Schema:{e}")

    def extrair_dado(self, elemento, id):
        dado = self.site.find(elemento, attrs={"id": id})
        if not dado:
            print(f"Elemento {id} não encontrado no HTML.")  # Depuração
        else:
            print(f"Elemento {id} encontrado: {dado}")  # Depuração
        return dado.text.strip() if dado else None

    def extrair_partes(self):

        partes = {"autor": [], "reu": [], "Testemunha": []}
        partesdoprocesso = self.site.findAll("td", attrs={'class': 'nomeParteEAdvogado'})
        if partesdoprocesso:
            if len(partesdoprocesso) >= 1:
                autores = re.sub(r'\s+', ' ', partesdoprocesso[0].text.strip())
                partes["autor"].append({'nome': autores})
            if len(partesdoprocesso) >= 2:
                reus = re.sub(r'\s+', ' ', partesdoprocesso[1].text.strip())
                partes["reu"].append({'nome': reus})
            if len(partesdoprocesso) >= 3:
                testemunha = re.sub(r'\s+', ' ', partesdoprocesso[2].text.strip())
                partes["Testemunha"].append({'nome': testemunha})
        return partes

    def extrair_movimentacoes(self):

        movimentacoes = []
        tblMovimentacoes = self.site.find('tbody', attrs={'id': 'tabelaUltimasMovimentacoes'})
        if tblMovimentacoes:
            linhas = tblMovimentacoes.find_all("tr")
            for linha in linhas:
                data = linha.find('td', attrs={'class': 'dataMovimentacao'})
                movimento_elemento = linha.find('td', attrs={'class': 'descricaoMovimentacao'})
                if data and movimento_elemento:
                    data_texto = data.text.strip()
                    movimento_texto = re.sub(r'\s+', ' ', movimento_elemento.text.strip())
                    movimentacoes.append({
                        "data": data_texto,
                        "movimento": movimento_texto
                    })
        return movimentacoes

    def extrair_peticoes(self):

        peticoes = []
        AllTbody = self.site.findAll('tbody')
        if len(AllTbody) > 2:
            linhas = AllTbody[2].findAll('tr')
            for linha in linhas:
                colunas = linha.findAll('td')
                if len(colunas) >= 2:
                    data_texto = colunas[0].text.strip()
                    tipo_texto = colunas[1].text.strip()
                    peticoes.append({"data": data_texto, "tipo": tipo_texto})
        return peticoes

    def extrair_tabela_simples(self, index, label):

        try:
            AllTabelas = self.site.findAll('table')
            if len(AllTabelas) > index:
                dado = re.sub(r'\s+', ' ', AllTabelas[index].text.strip())
                return [{label: dado}]
        except Exception as e:
            print(f"Erro ao processar {label}: {e}")
        return []

    def salvar_como_json(self, nome_arquivo="dados_processo.json"):

        #Salva os dados processados em um arquivo JSON.
        try:
            if self.validar_json():
                with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                    json.dump(self.dados_processo, arquivo, indent=4, ensure_ascii=False)
                print(f"Dados salvos com sucesso no arquivo {nome_arquivo}.")
            else:
                print("Erro: Dados inválidos. JSON não foi salvo.")
        except Exception as e:
            print(f"Erro ao salvar os dados no arquivo JSON: {e}")

    def extrair_audiencias(self):

        audiencias = []
        try:
            AllTabelas = self.site.findAll('table')
            if len(AllTabelas) > 6:
                linhas = AllTabelas[6].findAll('tr')
                for linha in linhas[1:]:
                    colunas = linha.findAll('td')
                    if len(colunas) >= 4:
                        data = colunas[0].text.strip()
                        audiencia = colunas[1].text.strip()
                        situacao = colunas[2].text.strip()
                        qt_pessoas = colunas[3].text.strip()
                        audiencias.append({
                            "data": data,
                            "audiencia": audiencia,
                            "situacao": situacao,
                            "qtPessoas": qt_pessoas
                        })
        except Exception as e:
            print(f"Erro ao processar audiências: {e}")
        return audiencias

    def validar_json(self):

        if not self.json_schema:
            print('Erro: JSON Schema não carregado')
        try:
            validate(instance=self.dados_processo, schema=self.json_schema)
            return True
        except ValidationError as e:
            print(f"Erro na validação do JSON: {e}")
            return False

    def processar_dados(self, nome_arquivo="dados_TJAL.json"):
        try:
            self.dados_processo["numero_processo"] = self.extrair_dado("span", "numeroProcesso")
            self.dados_processo["classe"] = self.extrair_dado("span", "classeProcesso")
            self.dados_processo["assunto"] = self.extrair_dado("span", "assuntoProcesso")
            self.dados_processo["foro"] = self.extrair_dado("span", "foroProcesso")
            self.dados_processo["vara"] = self.extrair_dado("span", "varaProcesso")
            self.dados_processo["juiz"] = self.extrair_dado("span", "juizProcesso")
            self.dados_processo["partes"] = self.extrair_partes()
            self.dados_processo["movimentacoes"] = self.extrair_movimentacoes()
            self.dados_processo["peticoes"] = self.extrair_peticoes()
            self.dados_processo["incidentes"] = self.extrair_tabela_simples(4, "incidente")
            self.dados_processo["Apensos"] = self.extrair_tabela_simples(5, "apensos")
            self.dados_processo["audiencias"] = self.extrair_audiencias()

            # Salvar os dados no arquivo JSON
            print(self.dados_processo)
            self.salvar_como_json(nome_arquivo)
            return True
        except Exception as e:
            print(f"Erro ao processar os dados: {e}")
            return False



