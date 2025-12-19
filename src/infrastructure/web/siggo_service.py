import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from src.core.gateways.i_siggo_service import ISiggoService
from src.infrastructure.web.web_driver import WebDriver
from src.config import *


class SiggoService(WebDriver, ISiggoService):
    """_summary_ Um driver especializado para o sistema SIGGO. Herda de WebDriver e adiciona lógicas específicas de negócio, como o fluxo de login no portal da fazenda, espera por elementos específicos de carregamento do sistema e métodos facilitadores para preencher campos e selecionar itens em menus dropdown."""

    def inicializar(self):
        self.setup_pandas()
        self.setup_driver()
        self.esperar_login()

    # Métodos controle de login
    def login_siggo(self, cpf, password):
        url = "https://siggo.fazenda.df.gov.br/Account/Login"
        self.driver.get(url)

        cpf_input_selector = '//*[@id="cpf"]'
        password_input_selector = '//*[@id="Password"]'
        button_selector = "/html/body/div[2]/div/div/div[1]/div/div/div[2]/form/button"

        self.driver.find_element(By.XPATH, value=cpf_input_selector).send_keys(
            cpf,
        )
        self.driver.find_element(By.XPATH, value=password_input_selector).send_keys(
            password,
        )
        self.driver.find_element(By.XPATH, button_selector).click()
        time.sleep(2)

    def esperar_login(
        self,
        timeout=300,
    ):
        url = "https://siggo.fazenda.df.gov.br/Account/Login"
        self.driver.get(url)

        start_time = time.time()

        while True:
            try:
                title = self.driver.find_element(
                    By.XPATH, '//*[@id="SIAC"]/div/div/div/div[2]/div/a/h4'
                )
                if title.text == "AFC":
                    break
            except:
                pass

            time.sleep(1)
            current_time = time.time()
            if current_time - start_time > timeout:
                self.driver.quit()
                raise TimeoutException("Tempo limite para login excedido.")

    def esperar_carregamento_login(self, timeout=60):
        start_time = time.time()

        while True:
            try:
                loading = self.driver.find_element(
                    By.XPATH, "/html/body/app-root/lib-login-callback/p"
                )

                current_time = time.time()
                if current_time - start_time > timeout:
                    self.driver.quit()
                    raise TimeoutException("Tempo limite para login excedido.")

                if loading.text == "carregando...":
                    time.sleep(1)
                    continue
            except:
                time.sleep(1)
                break

    # Métodos preenchimento de campos
    def preencher_campos(self, campos: dict):
        for campo, dado in campos.items():
            self.driver.find_element(By.XPATH, campo).send_keys(dado)

    def selecionar_opcoes(self, opcoes: dict):
        for campo, opcao in opcoes.items():
            Select(self.driver.find_element(By.XPATH, campo)).select_by_visible_text(
                opcao
            )
