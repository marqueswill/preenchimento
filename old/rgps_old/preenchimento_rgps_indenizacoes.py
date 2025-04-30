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
        # Configurar Pandas para exibir todas as colunas e linhas
        pd.set_option("display.max_rows", None)  # Exibir todas as linhas
        pd.set_option("display.max_columns", None)  # Exibir todas as colunas
        pd.set_option(
            "display.max_colwidth", None
        )  # Exibir conteúdo completo das células

        self.carregar_planilha()

        if not test:
            self.setup_driver()
            self.esperar_login()

    # Métodos setup e controle
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

    def executar(self):
        raise NotImplementedError("Método deve ser implementado na subclasse.")

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

    def separar_por_pagina(self, dataframe, tamanho_pagina=24):
        return [
            dataframe.iloc[i : i + tamanho_pagina]
            for i in range(0, len(dataframe), tamanho_pagina)
        ]

    def preencher_nota_de_lancamento(self, dados):
        dados_por_pagina = self.separar_por_pagina(dados)
        for dados_lancamentos in dados_por_pagina:
            self.nova_aba()
            self.acessar_link(
                f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
            )

            campos_cabecalho = self.preparar_preechimento_cabecalho()
            self.selecionar_opcoes(campos_cabecalho["opcoes"])
            self.preencher_campos(campos_cabecalho["campos"])

            campos_lancamentos = self.preparar_preenchimento_nl(dados_lancamentos)
            self.preencher_campos(campos_lancamentos)

        self.fechar_primeira_aba()

    def preparar_preechimento_cabecalho(self):
        username = os.getlogin().strip()
        caminho_completo = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"

        # Carregar o arquivo inteiro para acessar células específicas
        df = pd.read_excel(caminho_completo, sheet_name="INDENIZAÇÕES", header=None)

        prioridade = df.iloc[0, 1]  # B1
        credor = df.iloc[1, 1]  # B2
        gestao = df.iloc[2, 1]  # B3
        processo = df.iloc[3, 1]  # B4
        observacao = df.iloc[4, 1]  # B5

        return {
            "campos": {
                '//*[@id="prioridadePagamento"]/input': prioridade,
                '//*[@id="codigoCredor"]/input': gestao,
                '//*[@id="nuProcesso"]/input': processo,
                '//*[@id="observacao"]': observacao,
            },
            "opcoes": {
                '//*[@id="tipoCredor"]': credor,
            },
        }

    def preparar_preenchimento_nl(self, dados):
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.driver.find_element(By.XPATH, delete_button).click()

        linhas = dados.shape[0]
        campos = {}

        for i in range(linhas):
            self.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            evento = dados.iloc[i]["EVENTO"]
            inscricao = dados.iloc[i]["INSCRIÇÃO"]
            class_cont = dados.iloc[i]["CLASS. CONT"].replace(".", "")
            class_orc = dados.iloc[i]["CLASS. ORC"].replace(".", "")
            fonte = dados.iloc[i]["FONTE"]
            valor = round(float(dados.iloc[i]["VALOR"]), 2)

            valores = [evento, inscricao, class_cont, class_orc, fonte, valor]

            for j in range(6):
                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                campos[seletor] = str(valores[j])

        return campos

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


class PreenchimentoRGPSIndenizacoes(SiggoDriver):
    def __init__(self, test=False):
        self.caminho_planilha = f"\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"
        super().__init__(test)

    def carregar_template_nl(self):
        username = os.getlogin().strip()
        caminho_completo = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"

        dataframe = pd.read_excel(
            caminho_completo, header=6, sheet_name="INDENIZAÇÕES", usecols="A:E"
        ).astype(str)

        return dataframe

    def carregar_planilha_rgps(self):
        username = os.getlogin().strip()
        plan_folha = pd.read_excel(
            f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}\\DEMOFIN_TABELA.xlsx",
            sheet_name="DEMOFIN - T",
            header=1,
        )

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].astype(str)

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].str.replace(
            ".", ""
        )

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].apply(
            lambda x: x[1:] if x.startswith("33") else x
        )

        filtro_fundo = plan_folha["NME_FUNDO"] == "RGPS"

        plan_rgps_copia = plan_folha.loc[
            filtro_fundo, ["CDG_NAT_DESPESA", "NME_PROVDESC", "VALOR", "RUBRICA"]
        ]

        # Função para criar a coluna "AJUSTE"
        def categorizar_rubrica(rubrica):
            if rubrica in [11962, 21962, 32191, 42191, 52191, 61962]:
                return "Adiantamento_ferias"
            return ""

        # Aplica a função pra criar a coluna "AJUSTE"
        plan_rgps_copia["AJUSTE"] = plan_folha["CDG_PROVDESC"].apply(
            categorizar_rubrica
        )
        plan_rgps_copia.reset_index(drop=True, inplace=True)

        plan_rgps_copia["VALOR"] = plan_rgps_copia.apply(
            lambda row: -row["VALOR"] if row["RUBRICA"] == "Desconto" else row["VALOR"],
            axis=1,
        )

        plan_rgps_agrupado = plan_rgps_copia.groupby("CDG_NAT_DESPESA", as_index=False)[
            "VALOR"
        ].sum()

        return plan_rgps_agrupado

    def gerar_folha_rgps(self):
        folha_rgps = self.carregar_template_nl()
        dados_demofim = self.carregar_planilha_rgps()

        # Fazendo o LEFT JOIN (merge) com base nas colunas correspondentes
        folha_rgps = folha_rgps.merge(
            dados_demofim[["CDG_NAT_DESPESA", "VALOR"]],
            left_on="CLASS. ORC",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        folha_rgps.loc[
            (folha_rgps["INSCRIÇÃO"] == "2025NE00135")
            & (folha_rgps["CLASS. CONT"] == "211110101"),
            "VALOR",
        ] = folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33909317", "VALOR"].values[0]

        folha_rgps.loc[
            (folha_rgps["INSCRIÇÃO"] == "2025NE00136")
            & (folha_rgps["CLASS. CONT"] == "211110101"),
            "VALOR",
        ] = folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33909315", "VALOR"].values[0]

        folha_rgps.loc[
            (folha_rgps["INSCRIÇÃO"] == "2025NE00137")
            & (folha_rgps["CLASS. CONT"] == "211110101"),
            "VALOR",
        ] = folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33909304", "VALOR"].values[0]

        return folha_rgps

    def executar(self):
        folha_rgps = self.gerar_folha_rgps()
        self.preencher_nota_de_lancamento(folha_rgps)


try:
    driver = PreenchimentoRGPSIndenizacoes()
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
