# Importe as classes CONCRETAS de infrastructure
from src.infrastructure.services.preenchimento_gateway import PreenchimentoGateway
from src.infrastructure.web.siggo_service import SiggoService
from src.infrastructure.services.nl_folha_gateway import NLFolhaGateway
from src.infrastructure.services.pathing_gateway import PathingGateway
from src.infrastructure.files.excel_service import ExcelService
from src.infrastructure.services.conferencia_gateway import ConferenciaGateway

# Importe o Use Case de core
from src.core.usecases.gerar_conferencia_usecase import GerarConferenciaUseCase
from src.core.usecases.preenchimento_folha_usecase import PreenchimentoFolhaUseCase

# Importe as INTERFACES (opcional, mas bom para type hints)
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_siggo_service import ISiggoService

class UseCaseFactory:
    """
    Responsável por "montar" (construir) os use cases
    com todas as suas dependências.
    """

    def create_gerar_conferencia_use_case(self, fundo: str) -> GerarConferenciaUseCase:
        """Cria o use case de Geração de Conferência pronto para usar."""

        # 1. Criar dependências de nível mais baixo
        pathing_gw: IPathingGateway = PathingGateway()
        nl_folha_gw: INLFolhaGateway = NLFolhaGateway(pathing_gw)

        # 2. Lógica de configuração
        caminho_planilha_conferencia = pathing_gw.get_caminho_conferencia(fundo)
        excel_svc: IExcelService = ExcelService(caminho_planilha_conferencia)

        # 3. Injetar tudo no ConferenciaGateway
        conferencia_gw: IConferenciaGateway = ConferenciaGateway(
            path_gateway=pathing_gw, excel_svc=excel_svc
        )

        # 4. Montar o Use Case final
        use_case = GerarConferenciaUseCase(conferencia_gw, nl_folha_gw)

        return use_case

    def create_preenchimento_folha_use_case(self, fundo: str, run=True):
        # 1. Criar dependências de nível mais baixo
        pathing_gw: IPathingGateway = PathingGateway()
        nl_folha_gw: INLFolhaGateway = NLFolhaGateway(pathing_gw)

        # 2. Lógica de configuração
        caminho_planilha_conferencia = pathing_gw.get_caminho_conferencia(fundo)
        excel_svc: IExcelService = ExcelService(caminho_planilha_conferencia)

        # 3. Injetar tudo no ConferenciaGateway
        conferencia_gw: IConferenciaGateway = ConferenciaGateway(
            path_gateway=pathing_gw, excel_svc=excel_svc
        )

        # Lógica preenchedor
        siggo_service: ISiggoService = SiggoService(run)
        preenchedor_gw: IPreenchimentoGateway = PreenchimentoGateway(siggo_service)

        use_case = PreenchimentoFolhaUseCase(
            conferencia_gw, nl_folha_gw, preenchedor_gw
        )

        return use_case
