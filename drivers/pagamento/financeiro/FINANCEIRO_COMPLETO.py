import os
import sys

import pandas as pd

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


try:
    username = os.getlogin().strip()

    # Caminhos possíveis
    caminho_base = f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\SECON - General\\CÓDIGOS\\TEMPLATES_NL_FINANCEIRO.xlsx"
    caminho_onedrive = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\SECON - General\\CÓDIGOS\\TEMPLATES_NL_FINANCEIRO.xlsx"

    # Escolher o primeiro caminho válido
    if os.path.exists(caminho_base):
        caminho_completo = caminho_base
    elif os.path.exists(caminho_onedrive):
        caminho_completo = caminho_onedrive
    else:
        raise FileNotFoundError(
            "Arquivo TEMPLATES_NL_FINANCEIRO.xlsx não encontrado em nenhum dos caminhos possíveis.")

    excel_file = pd.ExcelFile(caminho_completo)
    nomes_templates = excel_file.sheet_names
    
    driver = FolhaPagamentoBase("financeiro", nomes_templates, test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
