
# Valida o cabeçalho do documento de acordo com o contrato definido em cabecalho_contract.py

from src.core.utils.cabecalho_contract import CAMPOS_CABECALHO


def validar_cabecalho(cabecalho: dict):
    faltantes = []

    for campo, config in CAMPOS_CABECALHO.items():
        if config["obrigatorio"] and not cabecalho.get(campo):
            faltantes.append(campo)

    if faltantes:
        raise Exception(
            "Cabeçalho inválido. Campos obrigatórios ausentes: "
            + ", ".join(faltantes)
        )
