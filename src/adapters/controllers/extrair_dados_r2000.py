from src.factories import UseCaseFactory
from src.infrastructure.cli.console_service import ConsoleService
from src.config import *


def ExtrairDadosR2000Controller():
    app_view = ConsoleService()
    factory = UseCaseFactory()
    use_case = factory.create_extrair_dados_r2000_usecase()
    use_case.executar()


if __name__ == "__main__":
    ExtrairDadosR2000Controller()