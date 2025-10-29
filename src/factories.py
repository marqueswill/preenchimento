# Importe as classes CONCRETAS de infrastructure
from src.infrastructure.services.nl_folha_gateway import NLFolhaGateway
from src.infrastructure.services.pathing_gateway import PathingGateway
from src.infrastructure.files.excel_service import ExcelService
from src.infrastructure.services.conferencia_gateway import ConferenciaGateway

# Importe o Use Case de core
from src.core.usecases.gerar_conferencia_usecase import GerarConferenciaUseCase

# Importe as INTERFACES (opcional, mas bom para type hints)
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway


class UseCaseFactory:
    """
    Responsável por "montar" (construir) os use cases
    com todas as suas dependências.
    """

    def create_gerar_conferencia_use_case(self) -> GerarConferenciaUseCase:
        """Cria o use case de Geração de Conferência pronto para usar."""

        # 1. Criar dependências de nível mais baixo
        nl_folha_gw: INLFolhaGateway = NLFolhaGateway()
        pathing_gw: IPathingGateway = PathingGateway()

        # 2. Lógica de configuração
        caminho_planilha_conferencia = pathing_gw.get_caminho_conferencia()
        excel_svc: IExcelService = ExcelService(caminho_planilha_conferencia)

        # 3. Injetar tudo no ConferenciaGateway
        conferencia_gw: IConferenciaGateway = ConferenciaGateway(
            nl_gateway=nl_folha_gw, path_gateway=pathing_gw, excel_svc=excel_svc
        )

        # 4. Montar o Use Case final
        use_case = GerarConferenciaUseCase(conferencia_gw)

        return use_case
