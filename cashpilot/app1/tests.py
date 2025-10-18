from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from app1.models import Entradas, Saidas, Saldo

class Teste_base(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
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

class Teste_entradas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
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
        campo_desc = self.espera.until(EC.presence_of_element_located((By.ID, "id_descricao")))
        campo_valor = self.navegador.find_element(By.ID, "id_valor")
        campo_data = self.navegador.find_element(By.ID, "id_date")
        botao_enviar = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(campo_desc.is_displayed())
        self.assertTrue(campo_valor.is_displayed())
        self.assertTrue(campo_data.is_displayed())
        self.assertTrue(botao_enviar.is_displayed())
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

    def test_enviar_receita_atualiza_lista_e_saldo(self):
        self.navegador.get(self.live_server_url + reverse("entradas"))
        self.preencher_formulario("Venda produto", 1500, "2025-10-18")
        lista_transacoes = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "lista-transacoes")))
        self.assertTrue(lista_transacoes.is_displayed())
        corpo_pagina = lista_transacoes.text
        self.assertIn("Venda produto", corpo_pagina)
        self.assertIn("1500", corpo_pagina)
        self.navegador.get(self.live_server_url + reverse("nav"))
        saldo = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "saldo-valor")))
        self.assertTrue(saldo.is_displayed())
        self.assertTrue("1500" in saldo.text or "1.500" in saldo.text)

    def test_abas_receita_despesa_visiveis(self):
        self.navegador.get(self.live_server_url + reverse("entradas"))
        abas = self.navegador.find_elements(By.CLASS_NAME, "tab")
        textos = [aba.text for aba in abas]
        self.assertIn("Receita", textos)
        self.assertIn("Despesas", textos)
        for aba in abas:
            self.assertTrue(aba.is_displayed())

class Teste_saidas(Teste_entradas):
    def test_enviar_saida_atualiza_lista_e_saldo(self):
        self.navegador.get(self.live_server_url + reverse("saidas"))
        self.preencher_formulario("Conta luz", 300, "2025-10-18")
        lista_transacoes = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "lista-transacoes")))
        self.assertTrue(lista_transacoes.is_displayed())
        corpo_pagina = lista_transacoes.text
        self.assertIn("Conta luz", corpo_pagina)
        self.assertIn("300", corpo_pagina)
        self.navegador.get(self.live_server_url + reverse("nav"))
        saldo = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "saldo-valor")))
        self.assertTrue(saldo.is_displayed())
        self.assertTrue("300" in saldo.text or "3.00" in saldo.text)

class Teste_extrato(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
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
        lista_entradas = self.navegador.find_elements(By.CSS_SELECTOR, ".movimentacoes-list .valor.entrada")
        lista_saidas = self.navegador.find_elements(By.CSS_SELECTOR, ".movimentacoes-list .valor.saida")
        for elem in lista_entradas + lista_saidas:
            self.assertTrue(elem.is_displayed())
        self.assertIn("Venda", container.text)
        self.assertIn("Compra", container.text)

class Teste_dashboard(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
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
        self.assertIn("saldo_positivo", html)
        self.assertIn("saldo_negativo", html)
        self.assertIn("500", html)
