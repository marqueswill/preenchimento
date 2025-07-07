from typing import Optional
import numpy as np
from pandas import DataFrame

import pandas as pd

import os
import locale
from datetime import datetime

from drivers.pagamento.gerar_folha_pagamento import FolhaPagamento
from drivers.preenchimento_nl import PreenchimentoNL
from drivers.template_nls.carregar_nl import CarregarNL

locale.setlocale(locale.LC_TIME, "pt_BR.utf8")


ANO_ATUAL = datetime.now().year
# MES_ATUAL = datetime.now().month
MES_ATUAL = 6

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


class PreenchimentoTemplates():
    """_summary_ Classe que pega NLs da planilha de templates e utiliza o driver PreenchimentoNL para preencher os dados na plataforma.
    """

    def __init__(self, run=True, test=False):

        username = os.getlogin().strip()
        self.caminho_raiz = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"
        self.run = run
        self.test = test
        self.preenchedor = PreenchimentoNL(run, test)

    def carregar_nl(self, nome_planilha: str, nome_aba: str):
        print(f"Carregando NL: {nome_planilha} - {nome_aba}")
        caminho_completo = (
            self.caminho_raiz +
            f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA\\{nome_planilha}"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=nome_aba,
            usecols="A:F",
        ).astype(str)

        dataframe["CLASS. ORC"] = dataframe["CLASS. ORC"].apply(
            lambda x: x[1:] if len(x) == 9 else x
        ).astype(str)

        return dataframe

    def carregar_cabecalho(self, nome_planilha: str, nome_aba: str):
        caminho_completo = (
            self.caminho_raiz +
            f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA\\{nome_planilha}"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=None,
            sheet_name=nome_aba,
            #usecols="A:I",
        ).astype(str)

        return dataframe

    def executar(self):
        caminho_completo = self.caminho_raiz + \
            f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA"
        nomes_planilhas = [
            nome for nome in os.listdir(caminho_completo)
            # ignora arquivos temporários
            if nome.endswith(('.xlsx', '.xls')) and not nome.startswith('~$')
        ]

        nls_carregadas = []

        for planilha in nomes_planilhas:
            caminho_arquivo = os.path.join(caminho_completo, planilha)

            try:
                xls = pd.ExcelFile(caminho_arquivo)
                nomes_templates = xls.sheet_names

                nls_carregadas.extend(
                    [
                        {
                            "folha": self.carregar_nl(planilha, aba),
                            "template": self.carregar_cabecalho(planilha, aba)
                        }
                        for aba in nomes_templates
                    ])
            except Exception as e:
                print(f"Erro ao processar {planilha}: {e}")

        if self.test:
            for i, folha in enumerate(nls_carregadas):
                print(folha["folha"])
                print(folha["template"])
        if self.run:
            self.preenchedor.executar(nls_carregadas)
