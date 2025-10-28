import sys


from infrastructure.cli.console_service import ConsoleService


def FolhaPagamentoController(test=False, run=True):
    """Função principal que atua como o Controller da aplicação."""
    app_view = ConsoleService()
    app_view.clear_console()

    while True:
        try:
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

            print(tipo_folha_selecionado)
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
                # Executar o usecase

                app_view.show_message("Conferência gerada com sucesso.")
                continue

            break
            # Model: Obtém os caminhos dos templates
            nomes_templates = get_template_names(tipo_folha_selecionado)

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

            # View: Exibe a mensagem de processamento
            app_view.show_processing_message("Iniciando o processamento")

            # Model: Chama o serviço para processar a folha de pagamento
            service = FolhaPagamentoService(
                tipo_folha_selecionado, templates_selecionados, test=test, run=run
            )
            service.preencher_folhas()

            # View: Exibe a mensagem de conclusão
            app_view.show_message("Processamento concluído.")
            sys.exit()

        except Exception as e:
            # Em caso de erro, exibe a mensagem de erro e sai
            app_view.show_message(f"Ocorreu um erro: {e}")
            continue


if __name__ == "__main__":
    FolhaPagamentoController()
