from src.factories import UseCaseFactory
from src.infrastructure.cli.console_service import ConsoleService
from src.config import *


def ExportarValoresPagosController():
    app_view = ConsoleService()
    factory = UseCaseFactory()
    use_case = factory.create_exportar_valores_pagos_usecase()
    use_case.exportar_valores_pagos()


if __name__ == "__main__":
    ExportarValoresPagosController()