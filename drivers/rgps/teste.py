import sys

from drivers.rgps.rgps_base import *

try:

    drivers = [
        RGPSFolha("PRINCIPAL",run=False,test=True),
        RGPSFolha("SUBSTITUICOES",run=False,test=True),
        RGPSFolha("BENEFICIOS",run=False,test=True),
        RGPSFolha("DEA_BENEFÍCIOS",run=False,test=True),
        RGPSFolha("INDENIZACOES_RESTITUICOES",run=False,test=True),
        RGPSFolha("INDENIZACOES_PESSOAL",run=False,test=True),
    ]

    for d in drivers:
        try:
            print(f'Iniciando {d.__class__.__name__}')
            d.executar()
        except Exception as e:
            print(e)
            continue

except Exception as e:
    print(e)
    sys.exit()
