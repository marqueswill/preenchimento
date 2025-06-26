import sys
from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


try:
    # TODO: automatizar pra ler as abas do excel
    nomes_templates = [
        "PRINCIPAL",
        "SUBSTITUICOES",
        "BENEFICIOS",
        "DEA_BENEFÍCIOS",
        "INDENIZACOES_RESTITUICOES",
        "INDENIZACOES_PESSOAL",
    ]

    driver = FolhaPagamentoBase("rgps", nomes_templates, test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
