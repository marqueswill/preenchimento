import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


try:
    # TODO: automatizar pra ler as abas do excel
    nomes_templates = [
        "PRINCIPAL",
        # "SUBSTITUIÇÕES",
    ]
    driver = FolhaPagamentoBase(
        "capitalizado", nomes_templates, test=True, run=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
