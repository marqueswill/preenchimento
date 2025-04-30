from preenchimento_rgps_beneficios import PreenchimentoRGPSBeneficios
from preenchimento_rgps_dea_beneficios import PreenchimentoRGPSDeaBeneficios
from preenchimento_rgps_indenizacoes import PreenchimentoRGPSIndenizacoes
from preenchimento_rgps_principal import PreenchimentoRGPSPrincipal
from preenchimento_rgps_substituicoes import PreenchimentoRGPSSubstituicoes


preenchimentos = [
    PreenchimentoRGPSPrincipal(),
    PreenchimentoRGPSSubstituicoes(),
    PreenchimentoRGPSBeneficios(),
    PreenchimentoRGPSDeaBeneficios(),
    PreenchimentoRGPSIndenizacoes(),
]

for p in preenchimentos:
    p.executar()