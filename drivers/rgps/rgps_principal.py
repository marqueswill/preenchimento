import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSPrincipal

try:
    driver = PreenchimentoRGPSPrincipal(test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
