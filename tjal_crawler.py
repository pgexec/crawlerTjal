
import requests
from bs4 import BeautifulSoup
import json
import re
from jsonschema import validate, ValidationError

with open("json_schemaAlagoas.json", "r", encoding="utf-8") as f:
    json_schema = json.load(f)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Cookie": "JSESSIONID=C7AA94409F7DA142B70B5D2DFBAF6A25.cpopg4"
}

url = "https://www2.tjal.jus.br/cpopg/show.do"

params = {
    "processo.codigo": "01000I1FT0000",
    "processo.foro": "1",
    "processo.numero": "0731425-82.2014.8.02.0001"
}
def salvar_json(nome_arquivo, dados):
    try:
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        print(f"Dados salvos com sucesso no arquivo: {nome_arquivo}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")
        return False

def validar_json(dados,schema):
    try:
        validate(instance=dados,schema=schema)
        print("JSON válido de acordo com o schema")
        return True
    except ValidationError as e:
        print(f"Erro na validação do JSON:{e}")
        return False

def extrair_partes(site):
    partes = {"autor": [], "reu": [], "Testemunha": []}
    partesdoprocesso = site.findAll("td", attrs={'class':'nomeParteEAdvogado'})
    if partesdoprocesso:
        if len(partesdoprocesso) >= 1:
            autoresformatados = re.sub(r'\s+', ' ', partesdoprocesso[0].text.strip())
            partes["autor"].append({'nome': autoresformatados})
        if len(partesdoprocesso) >= 2:
            reuformatados = re.sub(r'\s+', ' ', partesdoprocesso[1].text.strip())
            partes["reu"].append({'nome': reuformatados})
        if len(partesdoprocesso) >= 3:
            testemunhaformatada = re.sub(r'\s+', ' ', partesdoprocesso[2].text.strip())
            partes["Testemunha"].append({'nome': testemunhaformatada})
    return partes

def extrair_dado(elemento, id):
    dado = site.find(elemento, attrs={"id": id})
    return dado.text.strip() if dado else None

def fazer_requisicao(ulr,headers,params):
    try:
        response  = requests.get(url,headers=headers,params=params)
        if response.status_code == 200:
            print("Página acessada com sucesso")
            site = BeautifulSoup(response.text,"html.parser")
            return site
        else:
            print(f"Erro ao acessar a página: {response.status_code}")
            exit()
    except Exception as e:
        print(f"Ocorreu um erro ao fazer a requisição{e}")
        exit()

site = fazer_requisicao(url,headers,params)

dados_processo = {}
dados_processo["numero_processo"] = extrair_dado("span", "numeroProcesso")
dados_processo["classe"] = extrair_dado("span", "classeProcesso")
dados_processo["assunto"] = extrair_dado("span", "assuntoProcesso")
dados_processo["foro"] = extrair_dado("span", "foroProcesso")
dados_processo["vara"] = extrair_dado("span", "varaProcesso")
dados_processo["juiz"] = extrair_dado("span", "juizProcesso")


dados_processo["partes"] = extrair_partes(site)



movimentacoes = []
tblMovimentacoes = site.find('tbody',attrs={'id':'tabelaUltimasMovimentacoes'})
if tblMovimentacoes:
    linhas = tblMovimentacoes.find_all("tr")
    for linha in linhas:
        data = linha.find('td', attrs={'class':'dataMovimentacao'})  # Ajuste para encontrar a coluna com a data
        movimento_elemento = linha.find('td', attrs={'class','descricaoMovimentacao'})  # Busca pela classe "descricaoMovimentacao"
        if data and movimento_elemento:
            data_texto = data.text.strip()
            movimento_texto = re.sub(r'\s+', ' ', movimento_elemento.text.strip())

            if movimento_texto:
                movimentacoes.append({
                    "data": data_texto,
                    "movimento": movimento_texto
                })
else:
    print('tabela de movimentação não encontrada')

dados_processo["movimentacoes"] = movimentacoes

peticoes = []
AllTbody = site.findAll('tbody')
linhas = AllTbody[2].findAll('tr')

if linhas:
    for linha in linhas:
        colunas = linha.findAll('td')
        dataTexto = colunas[0].text.strip()
        tipoTexto = colunas[1].text.strip()

        if dataTexto and tipoTexto:
            peticoes.append({"data":dataTexto,
                             "tipo": tipoTexto
            })
    dados_processo["peticoes"] = peticoes
else:
    print('Conteudo de Petições não encontrado!')



incidentes = []
try:
    AllTabelas = site.findAll('table')
    if len(AllTabelas) > 0:
        incidente = re.sub(r'\s+', ' ', AllTabelas[4].text.strip())
        incidentes.append({"incidente":incidente})
    else:
        print("Não foi possivel achar as tabelas")
except Exception as e:
    print(f"Erro ao processar incidentes:{e}")
dados_processo["incidentes"] = incidentes


Apensos = []
try:
    AllTabelas = site.findAll('table')
    if len(AllTabelas) > 0:
        apenso = AllTabelas[5].text.strip()
        Apensos.append({"apensos":apenso})
    else:
        print('Ocorreu um erro ao procurar a informação ')
except Exception as e:
    print(f"Erro ao processar incidentes: {e}")
dados_processo["Apensos"] = Apensos


audiencias = []
try:
    AllTabelas = site.findAll('table')
    if len(AllTabelas) > 0:
        linhas = AllTabelas[6].findAll('tr')
        for linha in linhas[1:]:
            try:
                colunas = linha.findAll('td')
                if len(colunas) >= 4:
                    data = colunas[0].text.strip()
                    audiencia = colunas[1].text.strip()
                    situacao = colunas[2].text.strip()
                    qtPessoas = colunas[3].text.strip()
                    audiencias.append({
                        "data": data,
                        "audiencia": audiencia,
                        "situacao": situacao,
                        "qtPessoas": qtPessoas
                    })
            except Exception as e:
                print(f"Erro ao processar uma linha de audiência: {e}")
    else:
        print("Tabela de audiências não encontrada ou índice fora do alcance.")
except Exception as e:
    print(f"Erro ao localizar a tabela de audiências: {e}")
dados_processo["audiencias"] = audiencias


if validar_json(dados_processo, json_schema):
    print("Arquivo está efetivamente no formato correto!")
else:
    print("Erro, dados não estão no formato schemaJSON")


nome_arquivo = "dados_JustiçaDeAlagoas.json"
if salvar_json(nome_arquivo, dados_processo):
    print("criação do arquivo JSON feita com sucesso!")
else:
    print("Falha ao criar o arquivo JSON")