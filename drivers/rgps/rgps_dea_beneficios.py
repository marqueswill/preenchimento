import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSDeaBeneficios


try:
    driver = PreenchimentoRGPSDeaBeneficios(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
