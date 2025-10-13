from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Teste_cadastro(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        service = Service("/usr/local/bin/chromedriver")  # ajuste se necessário
        cls.navegador = webdriver.Chrome(service=service, options=opcoes)
        cls.navegador.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.navegador.quit()
        super().tearDownClass()

    def setUp(self):
        self.espera = WebDriverWait(self.navegador, 10)

    def test_formulario_cadastro(self):
        url = self.live_server_url + reverse("cadastro")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        formulario = self.navegador.find_element(By.TAG_NAME, "form")
        self.assertTrue(formulario.is_displayed())
        campo_usuario = self.navegador.find_element(By.ID, "id_username")
        campo_senha1 = self.navegador.find_element(By.ID, "id_password1")
        campo_senha2 = self.navegador.find_element(By.ID, "id_password2")
        botao_cadastrar = self.navegador.find_element(By.TAG_NAME, "button")
        link_login = self.navegador.find_element(By.LINK_TEXT, "Entre aqui")
        self.assertTrue(campo_usuario.is_displayed())
        self.assertTrue(campo_senha1.is_displayed())
        self.assertTrue(campo_senha2.is_displayed())
        self.assertTrue(botao_cadastrar.is_displayed())
        self.assertTrue(link_login.is_displayed())

class Teste_login(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        service = Service("/usr/local/bin/chromedriver")  # ajuste se necessário
        cls.navegador = webdriver.Chrome(service=service, options=opcoes)
        cls.navegador.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.navegador.quit()
        super().tearDownClass()

    def setUp(self):
        self.espera = WebDriverWait(self.navegador, 10)
        # Criar usuário de teste para login
        self.usuario = User.objects.create_user(username="bernardo", password="123456")

    def test_formulario_login(self):
        url = self.live_server_url + reverse("login")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        formulario = self.navegador.find_element(By.TAG_NAME, "form")
        self.assertTrue(formulario.is_displayed())

        campo_login = self.navegador.find_element(By.ID, "id_login")
        campo_senha = self.navegador.find_element(By.ID, "id_senha")
        botao_entrar = self.navegador.find_element(By.TAG_NAME, "button")
        link_cadastro = self.navegador.find_element(By.LINK_TEXT, "Cadastre-se")
        self.assertTrue(campo_login.is_displayed())
        self.assertTrue(campo_senha.is_displayed())
        self.assertTrue(botao_entrar.is_displayed())
        self.assertTrue(link_cadastro.is_displayed())

    # ---------- Novas funções adicionadas ----------
    def test_login_sucesso(self):
        url = self.live_server_url + reverse("login")
        self.navegador.get(url)

        campo_usuario = self.navegador.find_element(By.ID, "id_login")
        campo_senha = self.navegador.find_element(By.ID, "id_senha")
        botao = self.navegador.find_element(By.TAG_NAME, "button")

        campo_usuario.send_keys("bernardo")
        campo_senha.send_keys("123456")
        botao.click()

        self.espera.until(EC.url_contains(reverse("nav")))
        self.assertIn(reverse("nav"), self.navegador.current_url)

    def test_login_falha_senha_errada(self):
        url = self.live_server_url + reverse("login")
        self.navegador.get(url)

        campo_usuario = self.navegador.find_element(By.ID, "id_login")
        campo_senha = self.navegador.find_element(By.ID, "id_senha")
        botao = self.navegador.find_element(By.TAG_NAME, "button")

        campo_usuario.send_keys("bernardo")
        campo_senha.send_keys("senhaerrada")
        botao.click()

        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
        mensagem_erro = self.navegador.find_element(By.TAG_NAME, "p").text
        self.assertIn("inválidos", mensagem_erro)

    def test_login_falha_campos_vazios(self):
        url = self.live_server_url + reverse("login")
        self.navegador.get(url)

        botao = self.navegador.find_element(By.TAG_NAME, "button")
        botao.click()

        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "p")))
        mensagem_erro = self.navegador.find_element(By.TAG_NAME, "p").text
        self.assertIn("Preencha", mensagem_erro)
