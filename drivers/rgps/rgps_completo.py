import sys

from drivers.rgps.rgps_base import RGPSCompleto


try:
    driver = RGPSCompleto(test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
