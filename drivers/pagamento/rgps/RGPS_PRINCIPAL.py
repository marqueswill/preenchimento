# import sys

# from drivers.pagamento.rgps.rgps_base import RGPSFolha

# try:
#     driver = RGPSFolha("PRINCIPAL")
#     driver.executar()
# except Exception as e:
#     print(e)
#     sys.exit()

import sys

from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase

try:
    driver = FolhaPagamentoBase("rgps", "PRINCIPAL", test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
