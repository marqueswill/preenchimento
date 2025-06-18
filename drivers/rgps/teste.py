import sys

from drivers.rgps.rgps_base import *

try:

    drivers = [PreenchimentoRGPSPrincipal(test=True),
               PreenchimentoRGPSSubstituicoes(test=True),
               PreenchimentoRGPSIndenizacoesRestituicoes(test=True),
               PreenchimentoRGPSDeaBeneficios(test=True),
               PreenchimentoRGPSBeneficios(test=True),
               PreenchimentoRGPSIndenizacoesPessoal(test=True)]

    for d in drivers:
        try:
            print(f'Iniciando {d.__class__.__name__}')
            d.executar()
            print("\n\n")
        except Exception as e:
            continue

except Exception as e:
    print(e)
    sys.exit()
