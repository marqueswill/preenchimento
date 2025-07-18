from typing import Optional
import numpy as np
from pandas import DataFrame

import pandas as pd

import os
import locale
from datetime import datetime

from drivers.pagamento.gerar_folha_pagamento import FolhaPagamento
from drivers.preenchimento_nl import PreenchimentoNL
from interface import color_text

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


class FolhaPagamentoBase():
    """_summary_ Classe que gera NLs para folha de pagamento e utiliza o driver PreenchimentoNL para preencher os dados na plataforma.
    """

    def __init__(self, nome_fundo: str, nome_template: list[str] | str, run=True, test=False):
        self.nome_fundo = nome_fundo.lower()
        self.nome_template = nome_template
        self.run = run
        self.test = test
        self.preenchedor = PreenchimentoNL(run, test)

    def executar(self):

        # Padroniza o nome_template para uma lista, se necessário
        if not isinstance(self.nome_template, list):
            nomes_templates = [self.nome_template]
        else:
            nomes_templates = self.nome_template

        # Cria um dicionário associando o nome do template à folha gerada
        folhas = [FolhaPagamento(nome_fundo=self.nome_fundo, nome_template=nome_template, test=self.test)
                  for nome_template in nomes_templates]

        folhas_pagamento = []

        for folha in folhas:
            if self.test:
                print("_" * 100)
                print(f"Gerando NLs para o fundo: "+color_text(f"{self.nome_fundo.upper()}", style="bold"))
                print(f"Usando template(s)      : "+color_text(f"{folha.nome_template}",style="bold"))

            folha_gerada = folha.gerar_folha()
            cabecalho = folha.carregar_template_cabecalho()

            folhas_pagamento.append({
                "folha": folha_gerada,
                "cabecalho": cabecalho
            })

        if self.run:
            self.preenchedor.executar(folhas_pagamento)
