import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase

try:
    driver = FolhaPagamentoBase("rgps", "PRINCIPAL", test=True, run=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
