from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import pandas as pd

import sys, time, os
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
            f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\General - SECON\\"
            + self.caminho_planilha
        )

        dataframe = pd.read_excel(caminho_completo)
        self.planilha = dataframe

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
                self.driver.quit()  
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


class PreenchimentoDiaria(SiggoDriver):
    def __init__(self, test=False):
        self.caminho_planilha = "FLUXO_DIÁRIAS\\TABELA_NL_DIARIAS_1.xlsx"
        super().__init__(test)

    def separar_por_pagina(self, dataframe, tamanho_pagina=24):
        return [
            dataframe.iloc[i : i + tamanho_pagina]
            for i in range(0, len(dataframe), tamanho_pagina)
        ]

    def preencher_diaria(self, dados):
        self.preencher_cabecalho(dados)
        self.preencher_lancamentos(dados)

    def preencher_cabecalho(self, dados):
        num_proc = str(dados.iloc[0, 6])
        prioridade = "F0"
        cod_ug = "020101-00001"
        texto_obs = """CONCESSÃO DE DIÁRIAS A SERVIDORES P/ PARTICIPAÇÃO NO (nome_evento), PROMOVIDO PELO(A) (instituição), NO PERÍODO DE XXXX, EM (cidade)."""

        opcoes = {'//*[@id="tipoCredor"]': "4 - UG/Gestão"}
        campos = {
            '//*[@id="nuProcesso"]/input': num_proc,
            '//*[@id="prioridadePagamento"]/input': prioridade,
            '//*[@id="codigoCredor"]/input': cod_ug,
            '//*[@id="observacao"]': texto_obs,
        }

        self.selecionar_opcoes(opcoes)
        self.preencher_campos(campos)

    def preencher_lancamentos(self, dados):
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.driver.find_element(By.XPATH, delete_button).click()

        lines = dados.shape[0]
        for i in range(lines):
            self.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            campos = {}
            for j in range(6):
                if j == 2:
                    continue

                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                dado = str(dados.iloc[i, j])

                campos[seletor] = dado

            self.preencher_campos(campos)

    def executar(self):
        dados_por_pagina = self.separar_por_pagina(self.planilha)
        link = f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
        for dados in dados_por_pagina:
            self.nova_aba()
            self.acessar_link(link)
            self.preencher_diaria(dados)

        self.fechar_primeira_aba()


try:
    driver = PreenchimentoDiaria()
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
