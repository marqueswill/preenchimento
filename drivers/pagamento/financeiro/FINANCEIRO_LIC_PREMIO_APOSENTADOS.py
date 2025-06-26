import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase

try:
    driver = FolhaPagamentoBase(
        "financeiro", "LIC_PREMIO_APOSENTADOS", test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
