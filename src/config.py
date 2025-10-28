from datetime import datetime


TESTE = False
ANO_ATUAL = datetime.now().year
MES_ATUAL = datetime.now().month if not TESTE else 0

NOMES_MESES = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]

PASTAS_MESES = {
    0: "TESTES",
    1: "01-JANEIRO",
    2: "02-FEVEREIRO",
    3: "03-MARÇO",
    4: "04-ABRIL",
    5: "05-MAIO",
    6: "06-JUNHO",
    7: "07-JULHO",
    8: "08-AGOSTO",
    9: "09-SETEMBRO",
    10: "10-OUTUBRO",
    11: "11-NOVEMBRO",
    12: "12-DEZEMBRO",
}

PASTA_MES_ATUAL = PASTAS_MESES[MES_ATUAL]
PASTA_MES_ANTERIOR = PASTAS_MESES[MES_ATUAL - 1] if MES_ATUAL > 2 else PASTAS_MESES[12]

NOME_MES_ATUAL = NOMES_MESES[MES_ATUAL]
NOME_MES_ANTERIOR = NOMES_MESES[MES_ATUAL - 1] if MES_ATUAL > 2 else NOMES_MESES[12]
