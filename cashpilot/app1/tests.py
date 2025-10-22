from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from .models import Entradas, Saidas, Saldo
import time
import os
import glob
import csv
import pdfplumber


# ==========================================================
# TESTES BASE
# ==========================================================

class Teste_base(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="pedro", password="123456")
        self.client.login(username="pedro", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

    def tearDown(self):
        self.navegador.quit()

    def test_cabecalho_links_usuario_logado(self):
        url = self.live_server_url + reverse("nav")
        self.navegador.get(url)
        cabecalho = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
        self.assertTrue(cabecalho.is_displayed())
        texto = cabecalho.text
        self.assertIn("Olá, pedro", texto)
        self.assertIn("SAIR", texto)
        self.assertNotIn("ENTRAR", texto)


# ==========================================================
# TESTES DE ENTRADAS
# ==========================================================

class Teste_entradas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

    def tearDown(self):
        self.navegador.quit()

    def preencher_formulario(self, descricao, valor, data):
        """Para entradas, campo de descrição é texto livre"""
        campo_desc = self.espera.until(EC.presence_of_element_located((By.ID, "id_descricao")))
        campo_valor = self.navegador.find_element(By.ID, "id_valor")
        campo_data = self.navegador.find_element(By.ID, "id_date")
        botao_enviar = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")

        campo_desc.clear()
        campo_valor.clear()
        campo_data.clear()
        campo_desc.send_keys(descricao)
        campo_valor.send_keys(str(valor))
        campo_data.send_keys(data)
        botao_enviar.click()
        time.sleep(1)

    def test_formulario_nova_receita_visivel(self):
        self.navegador.get(self.live_server_url + reverse("entradas"))
        for campo_id in ["id_descricao", "id_valor", "id_date"]:
            elemento = self.espera.until(EC.presence_of_element_located((By.ID, campo_id)))
            self.assertTrue(elemento.is_displayed())
        botao = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(botao.is_displayed())

    def test_enviar_receita_cria_objeto(self):
        self.navegador.get(self.live_server_url + reverse("entradas"))
        self.preencher_formulario("Salário", 5000, "2025-10-22")
        self.assertTrue(Entradas.objects.filter(descricao="Salário").exists())

    def test_abas_receita_despesa_visiveis(self):
        self.navegador.get(self.live_server_url + reverse("entradas"))
        abas = self.navegador.find_elements(By.CLASS_NAME, "tab")
        textos = [aba.text for aba in abas]
        if abas:
            self.assertIn("Receita", textos)
            self.assertIn("Despesas", textos)
            for aba in abas:
                self.assertTrue(aba.is_displayed())


# ==========================================================
# TESTES DE SAÍDAS CORRIGIDOS
# ==========================================================



class Teste_saidas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        # sincroniza cookie
        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

    def tearDown(self):
        self.navegador.quit()

    def preencher_formulario_saida(self, descricao, valor, data):
        # Campo de descrição é uma select
        campo_desc = Select(self.espera.until(EC.presence_of_element_located((By.ID, "id_descricao"))))
        campo_desc.select_by_visible_text(descricao)

        campo_valor = self.navegador.find_element(By.ID, "id_valor")
        campo_data = self.navegador.find_element(By.ID, "id_date")
        botao_enviar = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")

        # Preenche valor e data normalmente
        campo_valor.clear()
        campo_data.clear()
        campo_valor.send_keys(str(valor))
        campo_data.send_keys(data)
        botao_enviar.click()
        time.sleep(1)

    def test_enviar_saida_cria_objeto(self):
        self.navegador.get(self.live_server_url + reverse("saidas"))
        self.preencher_formulario_saida("Lazer", 300, "2025-10-22")
        self.assertTrue(Saidas.objects.filter(descricao="Lazer").exists())


# ==========================================================
# TESTES DE EXTRATO
# ==========================================================

class Teste_extrato(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

        Entradas.objects.create(descricao="Venda", valor=200, date="2025-10-18", owner=self.usuario)
        Saidas.objects.create(descricao="Compra", valor=100, date="2025-10-18", owner=self.usuario)

    def tearDown(self):
        self.navegador.quit()

    def test_extrato_exibe_transacoes_visiveis(self):
        self.navegador.get(self.live_server_url + reverse("extrato"))
        container = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "extrato-container")))
        self.assertTrue(container.is_displayed())
        self.assertIn("Venda", container.text)
        self.assertIn("Compra", container.text)


# ==========================================================
# TESTES DE DASHBOARD
# ==========================================================

class Teste_dashboard(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

        Saldo.objects.create(owner=self.usuario, valor=500)

    def tearDown(self):
        self.navegador.quit()

    def test_dashboard_graficos_e_totais_visiveis(self):
        self.navegador.get(self.live_server_url + reverse("dashboard"))
        body = self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertTrue(body.is_displayed())
        html = body.get_attribute("innerHTML")
        self.assertIn("500", html)


# ==========================================================
# TESTES DE EXPORTAÇÃO (CSV/PDF)
# ==========================================================

class TesteExtracao(StaticLiveServerTestCase):
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "test_downloads")

    @staticmethod
    def extrair_texto_pdf(caminho_arquivo):
        texto = ""
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                texto += pagina.extract_text() + "\n"
        return texto

    def setUp(self):
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        prefs = {
            "download.default_directory": self.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True
        }
        opcoes.add_experimental_option("prefs", prefs)

        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

        self.usuario = User.objects.create_user(username="extrator", password="123456")
        self.client.login(username="extrator", password="123456")
        cookie = self.client.cookies["sessionid"]
        self.navegador.get(self.live_server_url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()

    def tearDown(self):
        self.navegador.quit()
        for f in glob.glob(os.path.join(self.DOWNLOAD_DIR, "*")):
            os.remove(f)
        os.rmdir(self.DOWNLOAD_DIR)

    def test_extracao_dados_pdf_e_validacao(self):
        url = self.live_server_url + reverse("extrato")
        self.navegador.get(url)
        botao = self.espera.until(EC.presence_of_element_located((By.ID, "botao_exportar_pdf")))
        botao.click()
        time.sleep(3)
        arquivos = glob.glob(os.path.join(self.DOWNLOAD_DIR, "*.pdf"))
        self.assertTrue(arquivos)
        texto = self.extrair_texto_pdf(arquivos[0])
        self.assertIn("Extrato Financeiro", texto)
