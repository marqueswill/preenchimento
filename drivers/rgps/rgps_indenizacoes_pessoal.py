import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSIndenizacoesPessoal


try:
    driver = PreenchimentoRGPSIndenizacoesPessoal(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
