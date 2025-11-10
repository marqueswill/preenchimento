from src.infrastructure.cli.console_service import ConsoleService
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.factories import UseCaseFactory



def BaixaDiariaController( run=True):
    app_view = ConsoleService()
    app_view.clear_console()

    factory = UseCaseFactory()
    baixa_diaria_uc = factory.criar_baixa_diaria_usecase()
    nomes_planilhas = baixa_diaria_uc.listar_planilhas()

    while True:
        app_view.display_menu(
            nomes_planilhas,
            "Selecione a planilha:",
            selecionar_todos=True,
            permitir_voltar=True,
        )
        planilhas_selecionadas = app_view.get_user_input(
            nomes_planilhas,
            selecionar_todos=True,
            permitir_voltar=True,
            multipla_escolha=True,
        )

        if planilhas_selecionadas is None:
            continue

        if run:
            baixa_diaria_uc.executar(planilhas_selecionadas)
