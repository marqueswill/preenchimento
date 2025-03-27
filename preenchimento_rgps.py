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
    caminho_planilha: str

    def __init__(self, test=False):
        self.carregar_planilha()

        if not test:
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


class PreenchimentoRGPS(SiggoDriver):
    def __init__(self, test=False):
        self.caminho_planilha = f"\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}\\DEMOFIN_TABELA.xlsx"
        super().__init__(test)

    def carregar_planilha(self):
        username = os.getlogin().strip()
        caminho_completo = (
            f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\"
            + self.caminho_planilha
        )

        dataframe = pd.read_excel(caminho_completo, header=1)
        self.planilha = dataframe

    def resumir_proventos(self):
        plan_folha = self.planilha.copy()

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].str.replace(
            ".", ""
        )

        plan_rgps = plan_folha.loc[
            plan_folha["NME_FUNDO"] == "RGPS", ["CDG_NAT_DESPESA", "VALOR_AUXILIAR"]
        ].copy()

        proventos_rgps = plan_rgps.loc[
            plan_rgps["CDG_NAT_DESPESA"].str.startswith("3")
        ].copy()

        proventos_rgps["CDG_NAT_DESPESA"] = proventos_rgps["CDG_NAT_DESPESA"].str.slice(
            1
        )

        proventos_rgps["CDG_NAT_DESPESA"] = proventos_rgps["CDG_NAT_DESPESA"].replace(
            ["31901101", "31901102", "31901104"], "31901167"
        )

        proventos_rgps_final = (
            proventos_rgps.groupby("CDG_NAT_DESPESA")["VALOR_AUXILIAR"]
            .sum()
            .reset_index()
        )

        return proventos_rgps_final

    def resumir_descontos(self):
        plan_folha = self.planilha.copy()

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].str.replace(
            ".", ""
        )

        plan_rgps = plan_folha.loc[
            plan_folha["NME_FUNDO"] == "RGPS", ["CDG_NAT_DESPESA", "VALOR_AUXILIAR"]
        ].copy()

        descontos_rgps = plan_rgps.loc[
            plan_rgps["CDG_NAT_DESPESA"].str.startswith("2")
        ].copy()

        descontos_rgps["VALOR_AUXILIAR"] = descontos_rgps["VALOR_AUXILIAR"].abs()

        descontos_rgps_final = (
            descontos_rgps.groupby(["CDG_NAT_DESPESA"])["VALOR_AUXILIAR"]
            .sum()
            .reset_index()
        )

        return descontos_rgps_final

    def gerar_folha_rgps(self):
        data = {
            "EVENTO": ["510001"] * 13
            + [
                "520206",
                "520222",
                "520264",
                "520295",
            ],
            "INSCRIÇÃO": ["2025NE00128"] * 13 + ["2025NE00128FP0201010"] * 4,
            "CLASS. CONT": [
                "311210106",
                "311210122",
                "311210123",
                "311210124",
                "311210134",
                "311210141",
                "311210132",
                "311210157",
                "311210132",
                "311410195",
                "211110101",
                "211110102",
                "211110103",
                "218810110",
                "218810199",
                "218820104",
                "218830102",
            ],
            "CLASS. ORC": [
                "31901107",
                "31901122",
                "31901131",
                "31901132",
                "31901134",
                "31901141",
                "31901156",
                "31901157",
                "31901167",
                "31901195",
                "31901100",
                "31901100",
                "31901100",
                "",
                "",
                "",
                "",
            ],
            "FONTE": ["100000000"] * 17,
        }

        folha_rgps = DataFrame(data)
        proventos_rgps = self.resumir_proventos()
        descontos_rgps = self.resumir_descontos()

        # Merge de proventos
        folha_rgps = folha_rgps.merge(
            proventos_rgps[["CDG_NAT_DESPESA", "VALOR_AUXILIAR"]],
            left_on="CLASS. ORC",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        # Merge de descontos
        folha_rgps = folha_rgps.merge(
            descontos_rgps[["CDG_NAT_DESPESA", "VALOR_AUXILIAR"]],
            left_on="CLASS. CONT",
            right_on="CDG_NAT_DESPESA",
            how="left",
            suffixes=(None, "_descontos"),  # Apenas o segundo merge precisa de sufixo
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        folha_rgps["VALOR_AUXILIAR"] = folha_rgps[
            ["VALOR_AUXILIAR", "VALOR_AUXILIAR_descontos"]
        ].sum(axis=1, skipna=True)
        folha_rgps.drop(columns=["VALOR_AUXILIAR_descontos"], inplace=True)

        # valor do 211110101 = soma de todos que começam com "311" exceto 311210122, 311210123 e 311210124
        # menos o valor dos que começam com "218"

        soma_311 = folha_rgps.loc[
            folha_rgps["CLASS. CONT"].str.startswith("311")
            & ~folha_rgps["CLASS. CONT"].isin(["311210122", "311210123", "311210124"]),
            "VALOR_AUXILIAR",
        ].sum()

        subtrai_218 = folha_rgps.loc[
            folha_rgps["CLASS. CONT"].str.startswith("2188"), "VALOR_AUXILIAR"
        ].sum()

        folha_rgps.loc[folha_rgps["CLASS. CONT"] == "211110101", "VALOR_AUXILIAR"] = (
            soma_311 - subtrai_218
        )

        # valor do 211110102
        folha_rgps.loc[folha_rgps["CLASS. CONT"] == "211110102", "VALOR_AUXILIAR"] = (
            folha_rgps.loc[
                folha_rgps["CLASS. CONT"] == "311210122", "VALOR_AUXILIAR"
            ].values[0]
        )

        # valor do 211110103
        folha_rgps.loc[folha_rgps["CLASS. CONT"] == "211110103", "VALOR_AUXILIAR"] = (
            folha_rgps.loc[
                folha_rgps["CLASS. CONT"] == "311210123", "VALOR_AUXILIAR"
            ].values[0]
            + folha_rgps.loc[
                folha_rgps["CLASS. CONT"] == "311210124", "VALOR_AUXILIAR"
            ].values[0]
        )

        folha_rgps = folha_rgps[folha_rgps["VALOR_AUXILIAR"] != 0]

        return folha_rgps

    def preencher_rgps(self, dados):
        self.preencher_cabecalho(dados)
        self.preencher_lancamentos(dados)

    def preencher_cabecalho(self, dados):

        prioridade = "F0"
        cod_ug = "130101-00001"

        campos = {
            '//*[@id="prioridadePagamento"]/input': prioridade,
            '//*[@id="codigoCredor"]/input': cod_ug,
        }
        opcoes = {
            '//*[@id="tipoCredor"]': "4 - UG/Gestão",
        }

        self.selecionar_opcoes(opcoes)
        self.preencher_campos(campos)

    def preencher_lancamentos(self, dados):
        # TODO: padronizar DF para o formato do form da NL
        # TODO: extrair preparar_formulario daqui
        # TODO: adicionar lógica 24 linhas
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.driver.find_element(By.XPATH, delete_button).click()

        ### def preparar_formulario(self, dados)
        linhas = dados.shape[0]
        campos = {}
        for i in range(linhas):
            self.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            evento = dados.iloc[i]["EVENTO"]
            inscricao = dados.iloc[i]["INSCRIÇÃO"]
            class_cont = dados.iloc[i]["CLASS. CONT"]
            class_orc = dados.iloc[i]["CLASS. ORC"]
            fonte = dados.iloc[i]["FONTE"]
            valor = round(dados.iloc[i]["VALOR_AUXILIAR"], 2)

            valores = [evento, inscricao, class_cont, class_orc, fonte, valor]
            print(valores)
            for j in range(6):
                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                campos[seletor] = str(valores[j])
        ###
        self.preencher_campos(campos)

    def executar(self):
        folha_rgps = self.gerar_folha_rgps()
        print(folha_rgps)
        link = f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"

        self.nova_aba()
        self.acessar_link(link)
        self.preencher_rgps(folha_rgps)

        self.fechar_primeira_aba()


try:
    driver = PreenchimentoRGPS()
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
