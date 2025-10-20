from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Teste_cadastro(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

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
        self.assertTrue(campo_usuario.is_displayed())
        self.assertTrue(campo_senha1.is_displayed())
        self.assertTrue(campo_senha2.is_displayed())
        self.assertTrue(botao_cadastrar.is_displayed())
        link_login = self.navegador.find_element(By.LINK_TEXT, "Entre aqui")
        self.assertTrue(link_login.is_displayed())
        
class Teste_login(StaticLiveServerTestCase):
    def setUp(self):
        opcoes = Options()
        opcoes.add_argument("--headless=new")
        self.navegador = webdriver.Chrome(options=opcoes)
        self.espera = WebDriverWait(self.navegador, 10)

    def tearDown(self):
        self.navegador.quit()

    def test_formulario_login(self):
        url = self.live_server_url + reverse("login")
        self.navegador.get(url)
        self.espera.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        formulario = self.navegador.find_element(By.TAG_NAME, "form")
        self.assertTrue(formulario.is_displayed())
        campo_login = self.navegador.find_element(By.ID, "id_login")
        campo_senha = self.navegador.find_element(By.ID, "id_senha")
        botao_entrar = self.navegador.find_element(By.TAG_NAME, "button")
        self.assertTrue(campo_login.is_displayed())
        self.assertTrue(campo_senha.is_displayed())
        self.assertTrue(botao_entrar.is_displayed())
        link_cadastro = self.navegador.find_element(By.LINK_TEXT, "Cadastre-se")
        self.assertTrue(link_cadastro.is_displayed())

