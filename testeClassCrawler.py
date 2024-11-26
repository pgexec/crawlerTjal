import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from classCrawler import Crawler
from jsonschema import validate, ValidationError
from urllib.parse import urlparse

class TestCrawler(unittest.TestCase):
    def setUp(self):
        # Instancia o Crawler para os testes
        self.crawler = Crawler()
        self.numero_processo = "0731425-82.2014.8.02.0001"

    @patch('requests.Session.get')
    def test_obter_cookies_iniciais(self, mock_get):

        # Simula a resposta do servidor
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Testa com URL padrão
        self.crawler.obter_cookies_iniciais()
        mock_get.assert_called_with(f"{self.crawler.base_url}/cpopg/open.do", headers=self.crawler.headers)

    def test_construir_url(self):

        # Testa se a URL gerada contém os parâmetros esperados
        url = self.crawler.construir_url(self.numero_processo)
        self.assertIn("dadosConsulta.valorConsultaNuUnificado", url)
        self.assertIn(self.numero_processo, url)



    @patch('requests.Session.get')
    def test_enviar_requisicao_redirecionamento(self, mock_get):

        # Mocka um redirecionamento (302)
        mock_response = Mock()
        mock_response.status_code = 302
        mock_response.headers = {"Location": "/redirect/path"}
        mock_get.return_value = mock_response

        redirect_url = self.crawler.enviar_requisicao(self.numero_processo)

        # Usa urlparse para validar a estrutura da URL
        expected_url = "https://www2.tjal.jus.br/redirect/path"
        self.assertEqual(urlparse(redirect_url).geturl(), urlparse(expected_url).geturl())

    @patch('requests.Session.get')
    def test_acessar_detalhes(self, mock_get):

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Detalhes do Processo</body></html>"
        mock_get.return_value = mock_response

        soup = self.crawler.acessar_detalhes("https://www2.tjal.jus.br/details")
        self.assertIn("Detalhes do Processo", soup.text)