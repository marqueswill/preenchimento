import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSIndenizacoesRestituicoes


try:
    driver = PreenchimentoRGPSIndenizacoesRestituicoes(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
