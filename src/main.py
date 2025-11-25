from src.adapters.controllers.emails_driss_controller import EmailsDrissController
from src.adapters.controllers.exportar_valores_pagos_controller import (
    ExportarValoresPagosController,
)
from src.adapters.controllers.extrair_dados_r2000_controller import (
    ExtrairDadosR2000Controller,
)
from src.adapters.controllers.nl_automatica_controller import NLAutomaticaController
from src.adapters.controllers.pagamento_diarias_controller import (
    PagamentoDiariaController,
)
from src.adapters.controllers.pagamento_controller import FolhaPagamentoController


def exibir_menu(opcoes:list):
    """Exibe o menu de opções."""
    print("=" * 40)
    print("      MENU DE SELEÇÃO DE PROCESSOS")
    print("=" * 40)
    for i, controller in enumerate(opcoes):
        print(f" {i+1}. {controller.__name__.split("Controller")[0]}")
    print("-" * 40)
    print(" X. Sair")
    print("=" * 40)


def main():
    """Função principal para gerenciar o loop do menu."""

    opcoes = {
        "1": FolhaPagamentoController,
        "2": NLAutomaticaController,
        "3": PagamentoDiariaController,
        "4": ExtrairDadosR2000Controller,
        "5": ExportarValoresPagosController,
        "6": EmailsDrissController,
    }

    while True:
        exibir_menu(opcoes.values())

        # Pede a entrada do usuário
        escolha = input("Digite a opção: ").upper()

        if escolha == "X":
            break

        # Verifica se a opção é válida
        if escolha in opcoes:
            ControllerClass = opcoes[escolha]
            nome_controller = ControllerClass.__name__.split("Controller")[0]
            print(f"\nExecutando: {nome_controller}...")

            try:
                ControllerClass()
                print(f"Execução de {nome_controller} concluída com sucesso. Aperte qualquer tecla para continuar.")
                input()
            except Exception as e:
                print(f"Erro durante a execução de {nome_controller}: {e}")

            print("\n")
        else:
            print("\nOpção inválida\n")


if __name__ == "__main__":
    main()
