import re
from jsonschema import validate, ValidationError
import json

class Miner:


    def __init__(self, site, json_schema_path):

        self.site = site
        self.dados_processo = {}
        try:
            with open(json_schema_path,"r",encoding="utf-8") as schema_file:
                self.json_schema = json.load(schema_file)
        except Exception as e:
            self.json_schema = None
            print(f"Erro ao carregar o JSON Schema:{e}")




    def extrair_dado(self, elemento,id):
        dado = self.site.find(elemento, attrs={"id": id})
        if not dado:
            print(f"Elemento {id} não encontrado no HTML.")
        else:
            print(f"Elemento {id} encontrado: {dado}")

        return re.sub(r'\s+', ' ', dado.text).strip() if dado else None




    def extrair_partes(self):
        partes = {"autor": [], "reu": [], "Testemunha": []}  # Conformidade com o JSON Schema


        linhas = self.site.find_all("tr", class_="fundoClaro")
        for linha in linhas:

            tipo_participacao_elem = linha.find("span", class_="mensagemExibindo tipoDeParticipacao")

            nome_elem = linha.find("td", class_="nomeParteEAdvogado")

            if tipo_participacao_elem and nome_elem:

                tipo_participacao = re.sub(r'\s+', ' ', tipo_participacao_elem.text.strip()).lower()


                if tipo_participacao in ["autora", "autor"]:
                    tipo_chave = "autor"
                elif tipo_participacao in ["réu", "reu"]:
                    tipo_chave = "reu"
                elif tipo_participacao == "testemunha":
                    tipo_chave = "Testemunha"
                else:
                    continue

                nome = re.sub(r'\s+', ' ', nome_elem.text.strip())  # Remove múltiplos espaços
                nome = re.sub(r'(Defensor|Advogado|Advogada):?\s*', '', nome)  # Remove prefixos irrelevantes

                # Evitar duplicação
                if not any(p["nome"] == nome for p in partes[tipo_chave]):
                    partes[tipo_chave].append({"nome": nome})

        partes = {k: v for k, v in partes.items() if v}

        return partes



    def extrair_movimentacoes(self):

        movimentacoes = []
        tabela_movimentacoes = self.site.find('tbody', attrs={'id': 'tabelaUltimasMovimentacoes'})
        if tabela_movimentacoes:

            linhas = tabela_movimentacoes.find_all("tr")
            for linha in linhas:

                data_elem = linha.find('td', class_='dataMovimentacao')
                descricao_elem = linha.find('td', class_='descricaoMovimentacao')


                if data_elem and descricao_elem:
                    data = data_elem.text.strip()
                    descricao = re.sub(r'\s+', ' ', descricao_elem.text.strip())  # Remove múltiplos espaços

                    movimentacoes.append({
                        "data": data,
                        "movimento": descricao
                    })
        return movimentacoes

    def extrair_peticoes(self):

        peticoes = []
        alltbody = self.site.findAll('tbody')
        if len(alltbody) > 2:
            linhas = alltbody[2].findAll('tr')
            for linha in linhas:
                colunas = linha.findAll('td')
                if len(colunas) >= 2:
                    data_texto = colunas[0].text.strip()
                    tipo_texto = colunas[1].text.strip()
                    peticoes.append({"data": data_texto, "tipo": tipo_texto})
        return peticoes



    def extrair_tabela_simples(self, index, label):

        try:
            alltabelas = self.site.findAll('table')
            if len(alltabelas) > index:
                dado = re.sub(r'\s+', ' ', alltabelas[index].text.strip())
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
            # Encontra todas as tabelas no site
            tabelas = self.site.find_all('table')

            # Itera pelas tabelas para encontrar aquela que contém "Audiências"
            for tabela in tabelas:
                # Verifica se a tabela contém o cabeçalho de "Audiências"
                cabecalhos = tabela.find_all('th')
                if cabecalhos and any("Audiência" in th.text for th in cabecalhos):

                    linhas = tabela.find_all('tr')[1:]  # Pula a primeira linha (cabeçalho)

                    # Processa as linhas da tabela
                    for linha in linhas:
                        colunas = linha.find_all('td')
                        if len(colunas) >= 4:
                            data = colunas[0].text.strip()
                            audiencia = colunas[1].text.strip()
                            situacao = colunas[2].text.strip()
                            qt_pessoas = colunas[3].text.strip()

                            # Adiciona a audiência à lista
                            audiencias.append({
                                "data": data,
                                "audiencia": audiencia,
                                "situacao": situacao,
                                "qtPessoas": qt_pessoas
                            })

                    # Saí do loop após encontrar e processar a tabela de audiências
                    break
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


            distribuicao_completa = self.extrair_dado("div", "dataHoraDistribuicaoProcesso")
            data_match = re.search(r"\d{2}/\d{2}/\d{4}", distribuicao_completa)
            self.dados_processo["distribuicao"] = data_match.group(0)

            self.dados_processo["controle"] = self.extrair_dado("div","numeroControleProcesso")
            self.dados_processo["area"] = self.extrair_dado("div","areaProcesso")
            self.dados_processo["valor_acao"] = self.extrair_dado("div", "valorAcaoProcesso")
            self.dados_processo["partes"] = self.extrair_partes()
            self.dados_processo["movimentacoes"] = self.extrair_movimentacoes()
            self.dados_processo["peticoes"] = self.extrair_peticoes()
            self.dados_processo["incidentes"] = self.extrair_tabela_simples(4, "incidente")
            self.dados_processo["Apensos"] = self.extrair_tabela_simples(5, "apensos")
            self.dados_processo["audiencias"] = self.extrair_audiencias()
            outros_assuntos_elem = self.site.find('div', attrs={'class': 'line-clamp__2'})
            self.dados_processo["outros_assuntos"] = (
                re.sub(r'\s+', ' ', outros_assuntos_elem.text).strip() if outros_assuntos_elem else "Não informado"
            )
            # Salvar os dados no arquivo JSON
            print(self.dados_processo)
            self.salvar_como_json(nome_arquivo)
            return True
        except Exception as e:
            print(f"Erro ao processar os dados: {e}")
            return False



