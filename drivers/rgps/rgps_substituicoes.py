import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSSubstituicoes


try:
    driver = PreenchimentoRGPSSubstituicoes(test=False)
    driver.executar()

except Exception as e:
    print(e)
    sys.exit()
