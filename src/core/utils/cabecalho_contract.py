
# Contrato que define os campos esperados no cabeçalho do documento

CAMPOS_CABECALHO = {
    "prioridade_pagamento": {
        "labels": ["prioridade de pagamento", "prioridade"],
        "obrigatorio": True,
    },
    "tipo_credor": {
        "labels": ["credor", "tipo credor"],
        "obrigatorio": True,
    },
    "gestao": {
        "labels": ["ug/gestão", "ug/gestao", "gestao", "cnpj"],
        "obrigatorio": True,
    },
    "processo": {
        "labels": ["processo"],
        "obrigatorio": True,
    },
    "observacao": {
        "labels": ["observação", "observacao"],
        "obrigatorio": True,
    },
    "contrato": {
        "labels": ["contrato"],
        "obrigatorio": False,
    },
}
