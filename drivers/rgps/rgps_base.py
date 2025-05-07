import numpy as np
from pandas import DataFrame
from selenium.webdriver.common.by import By

import pandas as pd

import sys, time, os, locale
from datetime import datetime


from drivers.siggo_driver import SiggoDriver

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


class PreenchimentoRGPSBase(SiggoDriver):
    nome_template: str

    def __init__(self, test=False):
        super().__init__(test)

    def carregar_template_nl(self):
        caminho_completo = (
            self.caminho_raiz + f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=self.nome_template,
            usecols="A:E",
        ).astype(str)

        return dataframe

    def preencher_nota_de_lancamento(self, dados: DataFrame):
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
        caminho_completo = (
            self.caminho_raiz + f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"
        )

        df = pd.read_excel(
            caminho_completo, sheet_name=self.nome_template, usecols="A:E", header=None
        ).astype(str)

        prioridade: str = df.iloc[0, 1]  # B1
        credor: str = df.iloc[1, 1]  # B2
        gestao: str = df.iloc[2, 1]  # B3
        processo: str = df.iloc[3, 1]  # B4
        observacao: str = df.iloc[4, 1]  # B5

        return {
            "campos": {
                '//*[@id="prioridadePagamento"]/input': prioridade,
                '//*[@id="codigoCredor"]/input': gestao,
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

    def gerar_conferencia(self):
        def cria_coluna_rubrica(row):  # lógica redundante?
            cdg_nat_despesa = str(row["CDG_NAT_DESPESA"])
            valor = row["VALOR_AUXILIAR"]

            if cdg_nat_despesa.startswith("3"):
                if valor > 0:
                    return "PROVENTO"
                else:
                    return "DESCONTO"
            elif cdg_nat_despesa.startswith("2"):
                if valor < 0:
                    return "DESCONTO"
                else:
                    return "PROVENTO"
            else:
                return ""  # Ou algum outro valor padrão, se necessário

        def categorizar_rubrica(rubrica):
            if rubrica in [11962, 21962, 32191, 42191, 52191, 61962]:
                return "Adiantamento_ferias"
            return ""

        caminho_planilha = f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}\\DEMOFIN_TABELA.xlsx"
        #caminho_planilha = f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_2025\\03-MARÇO\\DEMOFIN_TABELA.xlsx"

        caminho_completo = self.caminho_raiz + caminho_planilha

        plan_folha = pd.read_excel(caminho_completo, sheet_name="DEMOFIN - T", header=1)

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].str.replace(
            ".", ""
        )

        filtro_fundo = plan_folha["CDG_FUNDO"] == 1
        plan_rgps = plan_folha.loc[
            filtro_fundo,
            ["CDG_PROVDESC", "NME_NAT_DESPESA", "CDG_NAT_DESPESA", "VALOR_AUXILIAR"],
        ]

        plan_rgps["RUBRICA"] = plan_rgps.apply(cria_coluna_rubrica, axis=1)

        plan_rgps["VALOR_AUXILIAR"] = plan_rgps["VALOR_AUXILIAR"].abs()

        plan_rgps = pd.pivot_table(
            plan_rgps,
            values="VALOR_AUXILIAR",
            index=["CDG_PROVDESC", "NME_NAT_DESPESA", "CDG_NAT_DESPESA"],
            columns="RUBRICA",
            aggfunc="sum",
        )

        conferencia_rgps = (
            plan_rgps.groupby(["CDG_PROVDESC", "NME_NAT_DESPESA", "CDG_NAT_DESPESA"])[
                ["PROVENTO", "DESCONTO"]
            ]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        # Aplica a função pra criar a coluna "AJUSTE"
        conferencia_rgps["AJUSTE"] = conferencia_rgps["CDG_PROVDESC"].apply(
            categorizar_rubrica
        )
        conferencia_rgps.sort_values(by=["CDG_NAT_DESPESA"])

        conferencia_rgps_final = (
            conferencia_rgps.groupby(["NME_NAT_DESPESA", "CDG_NAT_DESPESA"])[
                ["PROVENTO", "DESCONTO"]
            ]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        return conferencia_rgps_final

    def gerar_proventos(self, conferencia_rgps_final: DataFrame):
        prov_rgps = conferencia_rgps_final.loc[
            conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_proventos = prov_rgps["PROVENTO"] - prov_rgps["DESCONTO"]
        prov_rgps_final = prov_rgps.loc[
            :, ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "PROVENTO", "DESCONTO"]
        ].assign(SALDO=coluna_saldo_proventos)

        prov_rgps_final["CDG_NAT_DESPESA"] = prov_rgps_final[
            "CDG_NAT_DESPESA"
        ].str.slice(1)

        prov_rgps_final.sort_values(by=["CDG_NAT_DESPESA"])

        return prov_rgps_final

    def gerar_descontos(self, conferencia_rgps_final: DataFrame):
        desc_rgps = conferencia_rgps_final.loc[
            ~conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]
        desc_rgps

        coluna_saldo_descontos = desc_rgps["DESCONTO"] - desc_rgps["PROVENTO"]
        coluna_saldo_descontos
        desc_rgps = desc_rgps.loc[
            :, ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "DESCONTO", "PROVENTO"]
        ].assign(SALDO=coluna_saldo_descontos)
        desc_rgps.sort_values(by=["CDG_NAT_DESPESA"])
        return desc_rgps

    def gerar_folha_rgps(self):
        raise NotImplementedError("Método deve ser implementado na subclasse.")

    def executar(self):
        folha_rgps = self.gerar_folha_rgps()
        self.preencher_nota_de_lancamento(folha_rgps)
