from typing import List
import numpy as np
from pandas import DataFrame
from selenium.webdriver.common.by import By

import pandas as pd

import sys
import time
import os
import locale
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

        super().__init__(test=test)

    def carregar_template_nl(self):
        caminho_completo = (
            self.caminho_raiz + f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=self.nome_template,
            usecols="A:H",
        ).astype(str)

        return dataframe

    def preencher_nota_de_lancamento(self, dados: DataFrame | List[DataFrame]):
        if isinstance(dados, list):
            dataframes = dados
        else:
            dataframes = [dados]

        for df in dataframes:
            dados_por_pagina = self.separar_por_pagina(df)
            for dados_lancamentos in dados_por_pagina:
                self.nova_aba()
                self.acessar_link(
                    f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
                )

                campos_cabecalho = self.preparar_preechimento_cabecalho()
                self.selecionar_opcoes(campos_cabecalho["opcoes"])
                self.preencher_campos(campos_cabecalho["campos"])

                campos_lancamentos = self.preparar_preenchimento_nl(
                    dados_lancamentos)
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
            valor = "{:.2f}".format(round(float(dados.iloc[i]["VALOR"]), 2))

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
                return "ADIANTAMENTO FÉRIAS"
            return ""

        caminho_planilha = f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}\\DEMOFIN_TABELA.xlsx"
        # caminho_planilha = f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_2025\\03-MARÇO\\DEMOFIN_TABELA.xlsx"

        caminho_completo = self.caminho_raiz + caminho_planilha

        plan_folha = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1)

        plan_folha["CDG_NAT_DESPESA"] = plan_folha["CDG_NAT_DESPESA"].str.replace(
            ".", ""
        )

        filtro_fundo = plan_folha["CDG_FUNDO"] == 1
        plan_rgps = plan_folha.loc[
            filtro_fundo,
            ["CDG_PROVDESC", "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA", "VALOR_AUXILIAR"],
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
        folha_rgps = self.carregar_template_nl()

        dados_conferencia_rgps = self.gerar_conferencia()
        proventos_rgps = self.gerar_proventos(dados_conferencia_rgps)
        descontos_rgps = self.gerar_descontos(dados_conferencia_rgps)

        # Inicializa a coluna VALOR com zeros
        folha_rgps["VALOR"] = 0.0

        # Cria dicionários para acesso rápido aos saldos por código
        proventos_dict = dict(
            zip(proventos_rgps["CDG_NAT_DESPESA"], proventos_rgps["SALDO"]))
        descontos_dict = dict(
            zip(descontos_rgps["CDG_NAT_DESPESA"], descontos_rgps["SALDO"]))
        saldos_dict = {
            **proventos_dict,
            **descontos_dict,
        }

        # Função para somar os saldos de uma lista de códigos

        def soma_codigos(codigos: str, dicionario: dict):
            lista_codigos = list(map(str.strip, codigos.split(",")))
            lista_codigos = [c[1:] if c.startswith(
                "33") else c for c in lista_codigos]
            resultado = sum(float(dicionario.get(str(c), 0.0))
                            for c in lista_codigos)

            return resultado

        # print(proventos_dict)
        # print(descontos_dict)
        # Calcula o valor para cada linha
        for idx, row in folha_rgps.iterrows():
            # print()
            somar = row.get("SOMAR", [])
            subtrair = row.get("SUBTRAIR", [])

            # print(f"Processando linha {idx}:")
            # print(f"SOMAR: {somar}"
            #       f"\nSUBTRAIR: {subtrair}")
            # print(soma_codigos(somar, saldos_dict),
            #       soma_codigos(subtrair, saldos_dict))
            valor = soma_codigos(somar, saldos_dict) - \
                soma_codigos(subtrair, saldos_dict)
            # print(f"VALOR calculado: {valor}")
            folha_rgps.at[idx, "VALOR"] = valor

        folha_rgps.drop(columns=["SOMAR", "SUBTRAIR"], inplace=True)
        folha_rgps = folha_rgps.sort_values(by="INSCRIÇÃO")
        folha_rgps = folha_rgps[folha_rgps["VALOR"] > 0]

        return folha_rgps

    def executar(self):
        folha_rgps = self.gerar_folha_rgps()
        print(folha_rgps)
        self.preencher_nota_de_lancamento(folha_rgps)


class PreenchimentoRGPSCompleto(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "COMPLETO"
        super().__init__(test)

    def executar(self):
        folha_rgps_princial = PreenchimentoRGPSPrincipal(
            test=self.test).gerar_folha_rgps()
        folha_rgps_substituicoes = PreenchimentoRGPSSubstituicoes(
            test=self.test).gerar_folha_rgps()
        folha_rgps_indenizacoes = PreenchimentoRGPSIndenizacoesRestituicoes(
            test=self.test).gerar_folha_rgps()
        folha_rgps_dea_beneficios = PreenchimentoRGPSDeaBeneficios(
            test=self.test).gerar_folha_rgps()
        folha_rgps_beneficios = PreenchimentoRGPSBeneficios(
            test=self.test).gerar_folha_rgps()
        folha_rgps_indenizacoes_pessoal = PreenchimentoRGPSIndenizacoesPessoal(
            test=self.test).gerar_folha_rgps()

        # Combina todas as folhas em um único DataFrame
        folha_rgps = [
            folha_rgps_princial,
            folha_rgps_substituicoes,
            folha_rgps_indenizacoes,
            folha_rgps_dea_beneficios,
            folha_rgps_beneficios,
            folha_rgps_indenizacoes_pessoal
        ]

        self.preencher_nota_de_lancamento(folha_rgps)


class PreenchimentoRGPSPrincipal(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "PRINCIPAL"
        super().__init__(test)


class PreenchimentoRGPSSubstituicoes(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "SUBSTITUICOES"
        super().__init__(test)


class PreenchimentoRGPSIndenizacoesRestituicoes(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = (
            "INDENIZAÇÕES_RESTITUIÇÕES"
        )
        super().__init__(test)


class PreenchimentoRGPSDeaBeneficios(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "DEA-BENEFÍCIOS"
        super().__init__(test)


class PreenchimentoRGPSBeneficios(PreenchimentoRGPSBase):
    def __init__(self, test=False):

        self.nome_template = "BENEFICIOS"
        super().__init__(test=test)


class PreenchimentoRGPSIndenizacoesPessoal(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "INDENIZAÇÕES_PESSOAL"
        super().__init__(test=test)
