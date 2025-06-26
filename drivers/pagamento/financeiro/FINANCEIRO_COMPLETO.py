import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


try:
    # TODO: automatizar pra ler as abas do excel
    nomes_templates = [
        "PRINCIPAL",
        "SUBSTITUICOES",
        "GRATIF_ENCARGOS_CURSO",
        # "BENEFICIOS_ATIVO",
        # "PROSAUDE_INATIVO",
        # "PROSAUDE_PENSIONISTA",
        "LIC_PREMIO_APOSENTADOS",
        # "INDENIZ_FERIAS_LIC_COMPENSATORI",
        "INDENIZAÇÕES_E_RESTITUIÇOES",
        "DEA_VENCIMENTOS",
        "DEA_SUBSTITUICOES",
        "DEA_INDENIZAÇOES",
        # "DEA_BENEFÍCIOS",
        "RETENCAO_IPREV",
        "RETENÇAO_IRRF",
        "RETENCAO_DF_PREVICOM_FINANCEIRO",
        # "PATRONAL_IPREV",
    ]
    driver = FolhaPagamentoBase("financeiro", nomes_templates, test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
