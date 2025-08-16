import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase

try:
    driver = FolhaPagamentoBase(
        "financeiro", "RETENCAO_DF_PREVICOM_FINANCEIRO", test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
