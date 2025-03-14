import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import pandas as pd
import time
import os
from datetime import datetime

ANO_ATUAL = datetime.now().year


class SiggoDriver:
    caminho_planilha: str

    def __init__(self, test=False):
        self.carregar_planilha()
        self.setup_driver()
        self.esperar_login()

    def carregar_planilha(self):
        username = os.getlogin().strip()

        caminho_completo = (
            f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\"
            + self.caminho_planilha
        )

        dataframe = pd.read_excel(caminho_completo)
        self.planilha = dataframe

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=options)

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
        self.esperar_carregamento()

    def fechar_primeira_aba(self):
        abas = self.driver.window_handles
        self.driver.switch_to.window(abas[0])
        self.driver.close()
        self.driver.switch_to.window(abas[1])

    def executar(self):
        raise NotImplementedError("Método deve ser implementado na subclasse.")


class PreenchimetoBaixa(SiggoDriver):
    def __init__(self, test=False):
        self.caminho_planilha = "FLUXO_DIÁRIAS\\BAIXA_DIARIAS.xlsx"
        super().__init__(test)

    def separar_processos(self, dataframe):
        dataframes_separados = {
            processo: df for processo, df in dataframe.groupby("PROCESSO")
        }
        return dataframes_separados

    def preencher_baixa(self, dados):
        self.preencher_cabecalho(dados)
        self.preencher_lancamentos(dados)

    def preencher_lancamentos(self, dados):
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.driver.find_element(By.XPATH, delete_button).click()

        linhas = dados.shape[0]
        campos = {}
        for i in range(linhas):
            self.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            evento = 560379  # coluna 1
            inscricao = dados.iloc[i]["CPF"]  # coluna 2
            classificacao_contabil = 332110100  # coluna 3
            valor = dados.iloc[i]["BAIXAR"]  # coluna 6

            valores = [evento, inscricao, classificacao_contabil, None, None, valor]

            for j in range(6):
                if valores[j] is None:
                    continue

                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                campos[seletor] = str(valores[j])

        self.preencher_campos(campos)

    def preencher_cabecalho(self, dados):
        processo = dados.iloc[0]["PROCESSO"]
        prioridade = "Z0"
        cod_ug = "020101-00001"

        campos = {
            '//*[@id="nuProcesso"]/input': processo,
            '//*[@id="prioridadePagamento"]/input': prioridade,
            '//*[@id="codigoCredor"]/input': cod_ug,
        }
        opcoes = {
            '//*[@id="tipoCredor"]': "4 - UG/Gestão",
        }

        self.selecionar_opcoes(opcoes)
        self.preencher_campos(campos)

    def executar(self):

        dados_por_processo = self.separar_processos(self.planilha)

        link = f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
        for processo, dados in dados_por_processo.items():
            self.nova_aba()
            self.acessar_link(link)
            self.preencher_baixa(dados)

        self.fechar_primeira_aba()


try:
    driver = PreenchimetoBaixa()
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
