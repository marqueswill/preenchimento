import os
import sys

import pandas as pd
from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


try:
    username = os.getlogin().strip()
    caminho_completo = (
        f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\" +
        f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_RGPS.xlsx"
    )

    excel_file = pd.ExcelFile(caminho_completo)
    nomes_templates = excel_file.sheet_names

    driver = FolhaPagamentoBase("rgps", nomes_templates, test=True, run=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
