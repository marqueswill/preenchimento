import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSCompleto


try:
    driver = PreenchimentoRGPSCompleto(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
