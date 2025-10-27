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
import os
import glob
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

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="pedro", password="123456")
        self.client.force_login(self.usuario)

        self.driver.get(self.live_server_url)
        cookie = self.client.cookies["sessionid"]
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

    def tearDown(self):
        self.driver.quit()

    def test_cabecalho_links_usuario_logado(self):
        url = self.live_server_url + reverse("nav")
        self.driver.get(url)
        cabecalho = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
        self.assertTrue(cabecalho.is_displayed())
        texto = cabecalho.text
        self.assertIn("Olá, pedro", texto)
        self.assertIn("SAIR", texto)
        self.assertNotIn("ENTRAR", texto)


# ==========================================================
# FUNÇÕES AUXILIARES DE FORMULÁRIO
# ==========================================================

def preencher_formulario_entrada(self, descricao, valor, data):
    driver = self.driver
    espera = WebDriverWait(driver, 20)

    driver.get(f"{self.live_server_url}/entradas/")

    # Espera pelos campos
    descricao_input = espera.until(EC.element_to_be_clickable((By.ID, "id_descricao")))
    valor_input = espera.until(EC.element_to_be_clickable((By.ID, "id_valor")))
    data_input = espera.until(EC.element_to_be_clickable((By.ID, "id_date")))

    descricao_input.clear()
    descricao_input.send_keys(descricao)
    valor_input.clear()
    valor_input.send_keys(str(valor))
    data_input.clear()
    data_input.send_keys(data)

    # Enviar formulário
    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()

    # Esperar o redirecionamento (elemento específico da lista)
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".lista-transacoes")))


def preencher_formulario_saida(self, descricao, valor, data):
    driver = self.driver
    espera = WebDriverWait(driver, 20)

    driver.get(f"{self.live_server_url}/saidas/")

    descricao_select = espera.until(EC.element_to_be_clickable((By.ID, "id_descricao")))
    valor_input = espera.until(EC.element_to_be_clickable((By.ID, "id_valor")))
    data_input = espera.until(EC.element_to_be_clickable((By.ID, "id_date")))

    Select(descricao_select).select_by_visible_text(descricao)
    valor_input.clear()
    valor_input.send_keys(str(valor))
    data_input.clear()
    data_input.send_keys(data)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Esperar o reload da lista de transações
    espera.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".lista-transacoes")))


# ==========================================================
# TESTES DE ENTRADAS
# ==========================================================

class Teste_entradas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.force_login(self.usuario)

        self.driver.get(self.live_server_url)
        cookie = self.client.cookies["sessionid"]
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

    def tearDown(self):
        self.driver.quit()

    def test_formulario_nova_receita_visivel(self):
        self.driver.get(self.live_server_url + reverse("entradas"))
        for campo_id in ["id_descricao", "id_valor", "id_date"]:
            elemento = self.espera.until(EC.presence_of_element_located((By.ID, campo_id)))
            self.assertTrue(elemento.is_displayed())
        botao = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(botao.is_displayed())

    def test_abas_receita_despesa_visiveis(self):
        self.driver.get(self.live_server_url + reverse("entradas"))
        abas = self.driver.find_elements(By.CLASS_NAME, "tab")
        textos = [aba.text for aba in abas]
        if abas:
            self.assertIn("Receita", textos)
            self.assertIn("Despesas", textos)
            for aba in abas:
                self.assertTrue(aba.is_displayed())


# ==========================================================
# TESTES DE SAÍDAS
# ==========================================================

class Teste_saidas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.force_login(self.usuario)

        self.driver.get(self.live_server_url)
        cookie = self.client.cookies["sessionid"]
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

    def tearDown(self):
        self.driver.quit()


# ==========================================================
# TESTES DE EXTRATO
# ==========================================================

class Teste_extrato(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.driver.get(self.live_server_url)
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

        Entradas.objects.create(descricao="Venda", valor=200, date="2025-10-18", owner=self.usuario)
        Saidas.objects.create(descricao="Compra", valor=100, date="2025-10-18", owner=self.usuario)

    def tearDown(self):
        self.driver.quit()

    def test_extrato_exibe_transacoes_visiveis(self):
        self.driver.get(self.live_server_url + reverse("extrato"))
        container = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "movimentacoes-list")))
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

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")

        cookie = self.client.cookies["sessionid"]
        self.driver.get(self.live_server_url)
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

        Saldo.objects.create(owner=self.usuario, valor=500)

    def tearDown(self):
        self.driver.quit()

    def test_dashboard_graficos_e_totais_visiveis(self):
        self.driver.get(self.live_server_url + reverse("dashboard"))
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
                texto += pagina.extract_text() or ""
        return texto

    def setUp(self):
        os.makedirs(self.DOWNLOAD_DIR, exist_ok=True)

        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        opcoes.add_experimental_option("prefs", {
            "download.default_directory": self.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })

        self.driver = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.driver, 10)

        self.usuario = User.objects.create_user(username="teste", password="123456")
        self.client.login(username="teste", password="123456")
        cookie = self.client.cookies["sessionid"]
        self.driver.get(self.live_server_url)
        self.driver.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.driver.refresh()

        Entradas.objects.create(descricao="Venda", valor=200, date="2025-10-18", owner=self.usuario)
        Saidas.objects.create(descricao="Compra", valor=100, date="2025-10-18", owner=self.usuario)

    def tearDown(self):
        self.driver.quit()
        arquivos = glob.glob(os.path.join(self.DOWNLOAD_DIR, "*"))
        for arquivo in arquivos:
            os.remove(arquivo)
