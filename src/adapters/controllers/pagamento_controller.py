import sys


from src.factories import UseCaseFactory
from src.infrastructure.cli.console_service import ConsoleService
from src.config import *


def FolhaPagamentoController(test=False, run=True):
    """Função principal que atua como o Controller da aplicação."""
    app_view = ConsoleService()
    app_view.clear_console()

    while True:
        try:
            factory = UseCaseFactory()
            fundos = {
                1: "RGPS",
                2: "FINANCEIRO",
                3: "CAPITALIZADO",
                4: "GERAR CONFERÊNCIAS",
            }

            # View: Exibe o menu principal e obtém a seleção do usuário
            app_view.display_menu(list(fundos.values()), "Selecione o tipo de folha:")
            tipo_folha_selecionado = app_view.get_user_input(list(fundos.values()))[0]

            if tipo_folha_selecionado is None:
                continue

            if tipo_folha_selecionado == "GERAR CONFERÊNCIAS":
                # Model: Chama o serviço para geração de conferências
                app_view.display_menu(
                    list(fundos.values())[:-1],
                    "Selecione o fundo para gerar a sua conferência:",
                )
                fundo_para_conferencia = app_view.get_user_input(list(fundos.values()))[
                    0
                ]

                # Instanciar usecase de coferencia, passando o fundo escolhido

                use_case = factory.create_gerar_conferencia_use_case(
                    fundo_para_conferencia
                )
                use_case.executar(fundo_para_conferencia)

                app_view.show_message("Conferência gerada com sucesso.")
                continue

            # Model: Obtém os caminhos dos templates
            use_case = factory.create_preenchimento_folha_use_case(
                tipo_folha_selecionado
            )
            nomes_templates = use_case.get_nomes_templates(tipo_folha_selecionado)

            # View: Exibe o menu de templates e obtém a seleção do usuário
            app_view.display_menu(
                nomes_templates,
                "Selecione o template:",
                selecionar_todos=True,
                permitir_voltar=True,
            )
            templates_selecionados = app_view.get_user_input(
                nomes_templates,
                selecionar_todos=True,
                permitir_voltar=True,
                multipla_escolha=True,
            )

            if templates_selecionados is None:
                continue

            app_view.show_processing_message("Iniciando o processamento")

            use_case.executar(tipo_folha_selecionado, templates_selecionados)

            app_view.show_message("Processamento concluído.")

        except Exception as e:
            # Em caso de erro, exibe a mensagem de erro e sai
            app_view.show_message(f"Ocorreu um erro: {e}")
            continue


if __name__ == "__main__":
    FolhaPagamentoController()
