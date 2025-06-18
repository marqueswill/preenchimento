import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSSubstituicoes


try:
    driver = PreenchimentoRGPSSubstituicoes(test=True)
    driver.executar()

except Exception as e:
    print(e)
    sys.exit()
