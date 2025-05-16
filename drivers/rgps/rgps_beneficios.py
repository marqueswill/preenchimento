import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSBeneficios


try:
    driver = PreenchimentoRGPSBeneficios(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
