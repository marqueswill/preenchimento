import sys

# Importa as classes de Model e as funções de View
from drivers.pagamento.services import ConferenciaService, FolhaPagamentoService, get_template_names, get_template_paths
from drivers.pagamento.view import ConsoleView


def main(test=False, run=True):
    """Função principal que atua como o Controller da aplicação."""
    app_view = ConsoleView()
    app_view.clear_console()
    
    while True:
        try: 
            fundos = {
                1: "RGPS",
                2: "FINANCEIRO",
                3: "CAPITALIZADO",
                4: "GERAR CONFERÊNCIAS"
            }

            # View: Exibe o menu principal e obtém a seleção do usuário
            app_view.display_menu(list(fundos.values()),
                                  "Selecione o tipo de folha:")
            tipo_folha_selecionado = app_view.get_user_input(
                list(fundos.values()))[0]

            if tipo_folha_selecionado is None:
                continue

            if tipo_folha_selecionado == "GERAR CONFERÊNCIAS":
                # Model: Chama o serviço para geração de conferências
                for fundo in ["RGPS", "FINANCEIRO", "CAPITALIZADO"]:
                    gerador = ConferenciaService(fundo,test)
                    gerador.executar()
                app_view.show_message("Conferências geradas com sucesso.")
                continue

            # Model: Obtém os caminhos dos templates
            nomes_templates = get_template_names(tipo_folha_selecionado)

            # View: Exibe o menu de templates e obtém a seleção do usuário
            app_view.display_menu(nomes_templates, "Selecione o template:",
                         selecionar_todos=True, permitir_voltar=True)
            templates_selecionados = app_view.get_user_input(
                nomes_templates, selecionar_todos=True, permitir_voltar=True)

            if templates_selecionados is None:
                continue

            # View: Exibe a mensagem de processamento
            app_view.show_processing_message("Iniciando o processamento")

            # Model: Chama o serviço para processar a folha de pagamento
            service = FolhaPagamentoService(
                tipo_folha_selecionado, templates_selecionados, test=test, run=run)
            folhas_pagamento_data = service.gerar_folhas()
            service.preencher_nl(folhas_pagamento_data)

            # View: Exibe a mensagem de conclusão
            app_view.show_message("Processamento concluído.")
            app_view.clear_console()
            sys.exit()

        except Exception as e:
            # Em caso de erro, exibe a mensagem de erro e sai
            app_view.show_message(f"Ocorreu um erro: {e}")
            sys.exit()


if __name__ == "__main__":
    main()
