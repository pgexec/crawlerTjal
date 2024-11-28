import os
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from jsonschema.exceptions import ValidationError
from classMiner import Miner
import json


class TestMiner(unittest.TestCase):

    def setUp(self):
        # HTML simulado para os testes
        html_content = """
           <html>
               <span id="numeroProcesso">123456</span>
               <span id="classeProcesso">Classe Teste</span>
               <span id="assuntoProcesso">Assunto Teste</span>
               <span id="foroProcesso">Foro Teste</span>
               <span id="varaProcesso">Vara Teste</span>
               <span id="juizProcesso">Juiz Teste</span>
               <div id="dataHoraDistribuicaoProcesso">09/03/2016 às 14:40 - Prevenção</div>
               <div id="numeroControleProcesso">Controle Teste</div>
               <div id="areaProcesso">Área Teste</div>
               <div id="valorAcaoProcesso">R$ 10.000,00</div>
               <td class="nomeParteEAdvogado">Autor Teste</td>
               <td class="nomeParteEAdvogado">Réu Teste</td>
               <td class="nomeParteEAdvogado">Testemunha Teste</td>
               <tbody id="tabelaUltimasMovimentacoes">
                   <tr>
                       <td class="dataMovimentacao">10/03/2023</td>
                       <td class="descricaoMovimentacao">Movimentação Teste</td>
                   </tr>
               </tbody>
               <table>
                   <tr><td>Incidente Teste</td></tr>
               </table>
               <table>
                   <tr><td>Apenso Teste</td></tr>
               </table>
               <table>
                   <tr>
                       <td>01/04/2023</td>
                       <td>Petição Teste</td>
                   </tr>
               </table>
               <table>
                   <tr><th>Data</th><th>Descrição</th><th>Situação</th><th>Qt Pessoas</th></tr>
                   <tr>
                       <td>01/05/2023</td>
                       <td>Audiencia Teste</td>
                       <td>Concluída</td>
                       <td>5</td>
                   </tr>
               </table>
           </html>
           """
        self.site = BeautifulSoup(html_content, "html.parser")
        self.miner = Miner(self.site, "json_schemaAlagoas.json")


        try:
            with open("json_schemaAlagoas.json", "r", encoding="utf-8") as schema_file:
                self.json_schema = json.load(schema_file)
        except Exception as e:
            self.json_schema = None
            print(f"Erro ao carregar JSON Schema: {e}")

    def test_processar_dados(self):
        with patch("classMiner.Miner.validar_json", return_value=True):
            result = self.miner.processar_dados()
            self.assertTrue(result)
            self.assertEqual(self.miner.dados_processo["numero_processo"], "123456")
            self.assertEqual(self.miner.dados_processo["classe"], "Classe Teste")



    def test_extrair_dado(self):
        numero_processo = self.miner.extrair_dado("span", "numeroProcesso")
        self.assertEqual(numero_processo, "123456")

    def test_extrair_movimentacoes(self):
        movimentacoes = self.miner.extrair_movimentacoes()
        self.assertEqual(movimentacoes[0]["data"], "10/03/2023")
        self.assertEqual(movimentacoes[0]["movimento"], "Movimentação Teste")




    def test_validar_json(self):

        arquivo_json = None
        try:
            for arquivo in os.listdir("."):
                if arquivo.startswith("dados_TJAL") and arquivo.endswith(".json"):
                    arquivo_json = arquivo
                    break

            if not arquivo_json:
                self.fail("Nenhum arquivo JSON começando com 'dados_TJAL' foi encontrado no diretório.")


            with open(arquivo_json, "r", encoding="utf-8") as json_file:
                conteudo_json = json.load(json_file)


            self.miner.dados_processo = conteudo_json
            is_valid = self.miner.validar_json()

            self.assertTrue(is_valid, f"O JSON no arquivo {arquivo_json} não é válido de acordo com o esquema.")

        except FileNotFoundError:
            self.fail(f"Arquivo {arquivo_json} não encontrado para validação.")
        except json.JSONDecodeError as e:
            self.fail(f"Erro ao carregar o JSON: {e}")
        except ValidationError as e:
            self.fail(f"Erro na validação do JSON gerado: {e}")
