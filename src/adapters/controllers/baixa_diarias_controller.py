from src.factories import UseCaseFactory
from src.infrastructure.cli.console_service import ConsoleService

def BaixaDiariasController(run=True, test=False):
    app_view = ConsoleService()
    factory = UseCaseFactory()
    use_case = factory.create_baixa_diarias_usecase()
    use_case.executar()
    app_view.show_message("Processamento concluído.")

if __name__ == "__main__":
    BaixaDiariasController()
