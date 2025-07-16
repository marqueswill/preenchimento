import numpy as np
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import pandas as pd

import sys, time, os, locale
from datetime import datetime

locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

ANO_ATUAL = datetime.now().year
MES_ATUAL = datetime.now().month
# MES_ATUAL = 6

MESES = {
    1: "01-JANEIRO",
    2: "02-FEVEREIRO",
    3: "03-MARÇO",
    4: "04-ABRIL",
    5: "05-MAIO",
    6: "06-JUNHO",
    7: "07-JULHO",
    8: "08-AGOSTO",
    9: "09-SETEMBRO",
    10: "10-OUTUBRO",
    11: "11-NOVEMBRO",
    12: "12-DEZEMBRO",
}


class SiggoDriver:
    """_summary_
    Driver para automação e interação com o SIGGO  
    """
    def __init__(self):

        # Configurar Pandas para exibir todas as colunas e linhas
        pd.set_option("display.max_rows", None)  # Exibir todas as linhas
        pd.set_option("display.max_columns", None)  # Exibir todas as colunas
        pd.set_option(
            "display.max_colwidth", None
        )  # Exibir conteúdo completo das células


    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=options)

    def finalizar(self):
        self.driver.quit()

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

    def esperar_login(self, timeout=60):
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
                self.driver.quit()  # TODO: unificar método para finalizar o SiggoDriver
                raise TimeoutException("Tempo limite para login excedido.")

    def esperar_carregamento(self, timeout=60):
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


    # Método controle de páginas
    def nova_aba(self):
        self.driver.execute_script("window.open('');")
        abas = self.driver.window_handles
        self.driver.switch_to.window(abas[-1])

    def acessar_link(self, link):
        self.driver.get(link)
        self.esperar_carregamento(timeout=120)

    def fechar_primeira_aba(self):
        abas = self.driver.window_handles
        self.driver.switch_to.window(abas[0])
        self.driver.close()
        self.driver.switch_to.window(abas[1])

    def executar(self):
        raise NotImplementedError("Método deve ser implementado na subclasse.")
