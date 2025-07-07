import numpy as np
from pandas import DataFrame

import pandas as pd

import os
import locale
from datetime import datetime


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


class CarregarNL():
    """_summary_
    Classe base para gerar folhas de pagamento no SIGGO.
    """

    nome_template: str
    cod_fundo: int

    def __init__(self, test=False):
        """_summary_
        Inicializa a classe FolhaPagamento.
        Args:
            nome_fundo (str): _description_ - deve ser um dos seguintes: "rgps", "financeiro", "capitalizado", "inativo", "pensão".
            nome_template (str): _description_ - deve ser igual a um dos nomes de template disponíveis no arquivo de templates.
            test (bool, optional): _description_. Defaults to False. - se True, imprime os dados no console para teste.
        Raises:
        """

        username = os.getlogin().strip()
        self.caminho_raiz = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"

        self.nome_fundo = nome_fundo.lower()
        self.test = test


