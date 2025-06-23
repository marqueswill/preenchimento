import sys

from drivers.rgps.rgps_base import RGPSFolha

try:
    driver = RGPSFolha("INDENIZACOES_RESTITUICOES")
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
