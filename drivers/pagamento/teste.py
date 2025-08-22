
import os
import sys
import time

import pandas as pd

from drivers.pagamento.conferencias.gerar_conferencias import GerarConferencia
from drivers.pagamento.folha_pagamento_base import FolhaPagamentoBase


def clear_console():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


def tela_selecao(opcoes: list[str], mensagem="Selecione uma opção:", selecionar_todos=False, permitir_voltar=False) -> list[str] | None:
    clear_console()
    while True:
        print(mensagem)
        if selecionar_todos:
            print("0. TODOS")
        for i, opcao in enumerate(opcoes, start=1):
            print(f"{i}. {opcao}")
        
        print()
        if permitir_voltar:
            print("V. VOLTAR")
        print("X. SAIR\n")

        escolha = input("Digite o número correspondente: ").strip().upper()

        if escolha == 'X':
            sys.exit()
        elif permitir_voltar and escolha == 'V':
            return None
        elif selecionar_todos and escolha == '0':
            return opcoes
        elif escolha.isdigit() and int(escolha) in range(1, len(opcoes) + 1):
            return [opcoes[int(escolha) - 1]]
        else:
            input("Opção inválida. Pressione ENTER para tentar novamente.")
            clear_console()


clear_console()
while True:
    try:
        fundos = {
            1: "RGPS",
            2: "FINANCEIRO",
            3: "CAPITALIZADO",
            4: "GERAR CONFERÊNCIAS"
        }

        tipo_folha = tela_selecao(
            list(fundos.values()),
            "Selecione o tipo de folha:"
        )[0]

        if tipo_folha is None:  # usuário escolheu VOLTAR
            continue
        
        if tipo_folha == "GERAR CONFERÊNCIAS":
            for fundo in ["RGPS", "FINANCEIRO", "CAPITALIZADO"]:
                gerador = GerarConferencia(fundo)
                gerador.executar()
            continue

        username = os.getlogin().strip()
        caminho_base = f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\"
        caminho_onedrive = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"

        if os.path.exists(caminho_base):
            caminho_raiz = caminho_base
        elif os.path.exists(caminho_onedrive):
            caminho_raiz = caminho_onedrive
        else:
            raise FileNotFoundError(
                "Arquivo TEMPLATES_NL_RGPS.xlsx não encontrado em nenhum dos caminhos possíveis."
            )

        caminho_completo = (
            caminho_raiz +
            f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_{tipo_folha.upper()}.xlsx"
        )

        excel_file = pd.ExcelFile(caminho_completo)
        nomes_templates = excel_file.sheet_names

        templates_selecionados = tela_selecao(
            nomes_templates,
            "Selecione o template:",
            selecionar_todos=True,
            permitir_voltar=True
        )

        if templates_selecionados is None:  # usuário escolheu VOLTAR
            continue

        for template in templates_selecionados:
            print(f"Template selecionado: {template}")

        print("\nIniciando o processamento", end='', flush=True)
        for _ in range(3):
            print(".",end='', flush=True)
            time.sleep(0.5)

        clear_console()
        driver = FolhaPagamentoBase(
            tipo_folha, templates_selecionados, test=True, run=False
        )
        clear_console()
        driver.executar()
        input("\nProcessamento concluído. Pressione ENTER para sair.")
        sys.exit()
    except Exception as e:
        print(e)
        sys.exit()
