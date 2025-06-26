from datetime import datetime
import os
from typing import Dict
import pandas as pd
from pandas import DataFrame
from drivers.siggo_driver import SiggoDriver
from selenium.webdriver.common.by import By

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


class PreenchimentoNL():
    """_summary_

    Driver para preenchimento de Notas Fiscais no SIGGO.

    Utiliza o SiggoDriver para gerenciar a sessão do navegador.
    """

    def __init__(self, nome_fundo: str, nome_template: str,  run=True, test=False):
        username = os.getlogin().strip()
        self.caminho_raiz = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"
        self.nome_fundo = nome_fundo.lower()
        self.nome_template = nome_template
        if run:
            self.siggo_driver = SiggoDriver()
            self.siggo_driver.setup_driver()
            self.siggo_driver.esperar_login()

    def separar_por_pagina(self, dataframe: DataFrame, tamanho_pagina=24):
        return [
            dataframe.iloc[i: i + tamanho_pagina]
            for i in range(0, len(dataframe), tamanho_pagina)
        ]

    def executar(self, dados: DataFrame | Dict[str, DataFrame]):
        if isinstance(dados, dict):
            dataframes = dados
        else:
            dataframes = {self.nome_template: dados}  # padroniza

        for dado in dataframes.items():
            self.nome_template = dado[0]
            df = dado[1]

            if df.empty:
                continue

            dados_por_pagina = self.separar_por_pagina(df)
            for dados_lancamentos in dados_por_pagina:
                self.siggo_driver.nova_aba()
                self.siggo_driver.acessar_link(
                    f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
                )

                campos_cabecalho = self.preparar_preechimento_cabecalho()
                self.siggo_driver.selecionar_opcoes(campos_cabecalho["opcoes"])
                self.siggo_driver.preencher_campos(campos_cabecalho["campos"])

                campos_lancamentos = self.preparar_preenchimento_nl(
                    dados_lancamentos)
                self.siggo_driver.preencher_campos(campos_lancamentos)

        self.siggo_driver.fechar_primeira_aba()

    def preparar_preechimento_cabecalho(self):
        caminho_completo = (
            self.caminho_raiz +
            f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_{self.nome_fundo.upper()}.xlsx"
        )

        # TODO: remover o self.nome_template dessa classe de alguma forma
        df = pd.read_excel(
            caminho_completo, sheet_name=self.nome_template, usecols="A:E", header=None
        ).astype(str)

        prioridade: str = df.iloc[0, 1]  # B1
        credor: str = df.iloc[1, 1]  # B2
        gestao: str = df.iloc[2, 1]  # B3
        processo: str = df.iloc[3, 1]  # B4
        observacao: str = df.iloc[4, 1]  # B5

        id_campo_gestao = {
            "2 - CNPJ": '//*[@id = "cocredorCNPJ"]/input',
            "4 - UG/Gestão": '//*[@id="codigoCredor"]/input'}[credor]

        return {
            "campos": {
                '//*[@id="prioridadePagamento"]/input': prioridade,
                id_campo_gestao: gestao,
                '//*[@id="nuProcesso"]/input': processo,
                '//*[@id="observacao"]': observacao.replace(
                    "<MONTH>", MESES[MES_ATUAL].split("-")[1]
                ).replace("<YEAR>", str(ANO_ATUAL)),
            },
            "opcoes": {
                '//*[@id="tipoCredor"]': credor,
            },
        }

    def preparar_preenchimento_nl(self, dados):
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.siggo_driver.driver.find_element(By.XPATH, delete_button).click()

        linhas = dados.shape[0]
        campos = {}

        for i in range(linhas):
            self.siggo_driver.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            evento = dados.iloc[i]["EVENTO"]
            inscricao = dados.iloc[i]["INSCRIÇÃO"]
            class_cont = dados.iloc[i]["CLASS. CONT"].replace(".", "")
            class_orc = dados.iloc[i]["CLASS. ORC"].replace(".", "")
            fonte = dados.iloc[i]["FONTE"]
            valor = "{:.2f}".format(round(float(dados.iloc[i]["VALOR"]), 2))

            valores = [evento, inscricao, class_cont, class_orc, fonte, valor]

            for j in range(6):
                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                campos[seletor] = str(valores[j])

        return campos
