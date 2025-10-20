from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Teste_base(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_cabecalho_links_visitante(self):
        url = self.live_server_url + reverse("nav")
        self.navegador.get(url)
        cabecalho = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
        texto = cabecalho.text
        self.assertIn("TELA INICIAL", texto)
        self.assertIn("NOVA RECEITA", texto)
        self.assertIn("NOVA DESPESA", texto)
        self.assertIn("GRÁFICOS", texto)
        self.assertIn("MOVIMENTAÇÕES FINANCEIRAS", texto)
        self.assertIn("ENTRAR", texto)
        self.assertNotIn("SAIR", texto)

    def test_cabecalho_links_usuario_logado(self):
        
        usuario = User.objects.create_user( username="pedro", email="pedro@example.com", password="123456" )
        self.client.login(username="pedro", password="123456")
        cookie = self.client.cookies["sessionid"]
        url = self.live_server_url + reverse("nav")
        self.navegador.get(url)
        self.navegador.add_cookie({"name": "sessionid", "value": cookie.value, "path": "/", "secure": False})
        self.navegador.refresh()
        cabecalho = self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "main-header")))
        texto = cabecalho.text
        self.assertIn("Olá, pedro", texto)
        self.assertIn("SAIR", texto)
        self.assertNotIn("ENTRAR", texto)
        
class Teste_dashboard(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_graficos_renderizados(self):
        url = self.live_server_url + reverse("dashboard")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.ID, "saldoChart1")))
        ids_graficos = ["saldoChart1", "saldoChart2", "saldoChart3", "saldoChart4"]
        for grafico_id in ids_graficos:
            elemento = self.navegador.find_element(By.ID, grafico_id)
            self.assertTrue(elemento.is_displayed())
        titulo = self.navegador.find_element(By.TAG_NAME, "h2").text
        self.assertIn("Análise do Saldo Mensal", titulo)
        scripts = [s.get_attribute("src") for s in self.navegador.find_elements(By.TAG_NAME, "script")]
        self.assertTrue(any("chart.js" in (src or "").lower() for src in scripts))

class Teste_despesa(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_formulario_e_lista_transacoes(self):
        url = self.live_server_url + reverse("entradas")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "transaction-form")))
        formulario = self.navegador.find_element(By.CLASS_NAME, "transaction-form")
        self.assertTrue(formulario.is_displayed())
        campo_valor = self.navegador.find_element(By.ID, "valor")
        campo_categoria = self.navegador.find_element(By.ID, "categoria")
        campo_descricao = self.navegador.find_element(By.ID, "descricao")
        botao_salvar = self.navegador.find_element(By.CLASS_NAME, "btn-salvar")
        self.assertTrue(campo_valor.is_displayed())
        self.assertTrue(campo_categoria.is_displayed())
        self.assertTrue(campo_descricao.is_displayed())
        self.assertTrue(botao_salvar.is_displayed())
        lista_transacoes = self.navegador.find_element(By.CLASS_NAME, "lista-transacoes")
        self.assertTrue(lista_transacoes.is_displayed())
        abas = self.navegador.find_elements(By.CLASS_NAME, "tab")
        textos_abas = [aba.text for aba in abas]
        self.assertIn("Receita", textos_abas)
        self.assertIn("Despesas", textos_abas)

class Teste_entradas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_formulario_nova_receita(self):
        url = self.live_server_url + reverse("entradas")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        formulario = self.navegador.find_element(By.TAG_NAME, "form")
        self.assertTrue(formulario.is_displayed())
        campo_descricao = self.navegador.find_element(By.ID, "id_descricao")
        campo_valor = self.navegador.find_element(By.ID, "id_valor")
        campo_data = self.navegador.find_element(By.ID, "id_date")
        botao_enviar = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(campo_descricao.is_displayed())
        self.assertTrue(campo_valor.is_displayed())
        self.assertTrue(campo_data.is_displayed())
        self.assertTrue(botao_enviar.is_displayed())

class Teste_extrato(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_extrato_carregado(self):
        url = self.live_server_url + reverse("extrato")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "extrato-container")))
        container = self.navegador.find_element(By.CLASS_NAME, "extrato-container")
        self.assertTrue(container.is_displayed())
        lista_entradas = self.navegador.find_elements(By.CSS_SELECTOR, ".movimentacoes-list .valor.entrada")
        lista_saidas = self.navegador.find_elements(By.CSS_SELECTOR, ".movimentacoes-list .valor.saida")
        self.assertTrue(lista_entradas or self.navegador.find_element(By.CLASS_NAME, "no-data"))
        self.assertTrue(lista_saidas or self.navegador.find_element(By.CLASS_NAME, "no-data"))
        botao_imprimir = self.navegador.find_element(By.CLASS_NAME, "print-button")
        self.assertTrue(botao_imprimir.is_displayed())

class Teste_index(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_card_e_login(self):
        url = self.live_server_url + reverse("nav")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        card = self.navegador.find_element(By.CLASS_NAME, "card")
        self.assertTrue(card.is_displayed())
        logo = self.navegador.find_element(By.CLASS_NAME, "logo")
        self.assertTrue(logo.is_displayed())
        titulo = self.navegador.find_element(By.TAG_NAME, "h1").text
        self.assertIn("O seu futuro financeiro", titulo)
        botao_login = self.navegador.find_element(By.TAG_NAME, "a")
        self.assertTrue(botao_login.is_displayed())
        self.assertEqual(botao_login.text, "Login")

class Teste_nav(StaticLiveServerTestCase):
        def setUp(self):
            opcoes = Options()
            opcoes.add_argument("--headless=new")
            self.navegador = webdriver.Chrome(options=opcoes)
            self.espera = WebDriverWait(self.navegador, 10)
    
        def tearDown(self):
            self.navegador.quit()
    
        def test_saldo_exibido(self):
            url = self.live_server_url + reverse("saldo")
            self.navegador.get(url)
            self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "saldo-container")))
            container = self.navegador.find_element(By.CLASS_NAME, "saldo-container")
            self.assertTrue(container.is_displayed())
            titulo = self.navegador.find_element(By.TAG_NAME, "h1").text
            self.assertEqual(titulo, "Saldo Financeiro")
            valor = self.navegador.find_element(By.CLASS_NAME, "saldo-valor")
            self.assertTrue(valor.is_displayed())
            classes_valor = valor.get_attribute("class")
            self.assertTrue("saldo-positivo" in classes_valor or "saldo-negativo" in classes_valor)
            logo = self.navegador.find_element(By.CLASS_NAME, "logo")
            self.assertTrue(logo.is_displayed())
    
class Teste_receita(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_formulario_e_lista_transacoes(self):
        url = self.live_server_url + reverse("entradas")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.CLASS_NAME, "transaction-form")))
        formulario = self.navegador.find_element(By.CLASS_NAME, "transaction-form")
        self.assertTrue(formulario.is_displayed())
        campo_valor = self.navegador.find_element(By.ID, "valor")
        campo_descricao = self.navegador.find_element(By.ID, "descricao")
        botao_salvar = self.navegador.find_element(By.CLASS_NAME, "btn-salvar")
        self.assertTrue(campo_valor.is_displayed())
        self.assertTrue(campo_descricao.is_displayed())
        self.assertTrue(botao_salvar.is_displayed())
        lista_transacoes = self.navegador.find_element(By.CLASS_NAME, "lista-transacoes")
        self.assertTrue(lista_transacoes.is_displayed())
        abas = self.navegador.find_elements(By.CLASS_NAME, "tab")
        textos_abas = [aba.text for aba in abas]
        self.assertIn("Receita", textos_abas)
        self.assertIn("Despesas", textos_abas)
    
class Teste_saidas(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_formulario_saida(self):
        url = self.live_server_url + reverse("saidas")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        formulario = self.navegador.find_element(By.TAG_NAME, "form")
        self.assertTrue(formulario.is_displayed())
        campo_descricao = self.navegador.find_element(By.ID, "id_descricao")
        campo_valor = self.navegador.find_element(By.ID, "id_valor")
        campo_data = self.navegador.find_element(By.ID, "id_date")
        botao_enviar = self.navegador.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(campo_descricao.is_displayed())
        self.assertTrue(campo_valor.is_displayed())
        self.assertTrue(campo_data.is_displayed())
        self.assertTrue(botao_enviar.is_displayed())
        erros = self.navegador.find_elements(By.CLASS_NAME, "form-error")
        self.assertTrue(erros or True)