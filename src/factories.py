# Importe as classes CONCRETAS de infrastructure
from src.infrastructure.email.email_service import EmailService
from src.infrastructure.files.pdf_service import PdfService
from src.infrastructure.services.preenchimento_gateway import PreenchimentoGateway
from src.infrastructure.web.siggo_service import SiggoService
from src.infrastructure.services.nl_folha_gateway import NLFolhaGateway
from src.infrastructure.services.pathing_gateway import PathingGateway
from src.infrastructure.files.excel_service import ExcelService
from src.infrastructure.services.conferencia_gateway import ConferenciaGateway

# Importe o Use Case de core
from src.core.usecases.emails_driss_usecase import EmailsDrissUseCase
from src.core.usecases.gerar_conferencia_usecase import GerarConferenciaUseCase
from src.core.usecases.preenchimento_folha_usecase import PreenchimentoFolhaUseCase
from src.core.usecases.pagamento_usecase import PagamentoUseCase
from src.core.usecases.preenchimento_nl_usecase import PreenchimentoNLUseCase
from src.core.usecases.baixa_diaria_usecase import BaixaDiariaUseCase
from src.core.usecases.extrair_dados_r2000_usecase import ExtrairDadosR2000UseCase

# Importe as INTERFACES (opcional, mas bom para type hints)
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_siggo_service import ISiggoService
from src.core.gateways.i_pdf_service import IPdfService
from src.core.gateways.i_email_service import IEmailService

from src.config import *
from tests.mocks.siggo_service_mock import SiggoServiceMock


class UseCaseFactory:
    """
    Responsável por "montar" (construir) os use cases
    com todas as suas dependências.
    """

    def create_pagamento_use_case(self, fundo: str) -> PagamentoUseCase:
        pathing_gw: IPathingGateway = PathingGateway()

        caminho_planilha_conferencia = pathing_gw.get_caminho_conferencia(fundo)
        excel_svc: IExcelService = ExcelService(caminho_planilha_conferencia)
        pdf_svc: IPdfService = PdfService(pathing_gw)

        conferencia_gw: IConferenciaGateway = ConferenciaGateway(
            pathing_gw=pathing_gw, excel_svc=excel_svc
        )
        nl_folha_gw: INLFolhaGateway = NLFolhaGateway(pathing_gw)

        use_case = PagamentoUseCase(conferencia_gw, nl_folha_gw, pdf_svc)

        return use_case

    def create_gerar_conferencia_use_case(self, fundo: str) -> GerarConferenciaUseCase:
        """Cria o use case de Geração de Conferência pronto para usar."""

        pagamento_uc: PagamentoUseCase = self.create_pagamento_use_case(fundo)
        use_case = GerarConferenciaUseCase(pagamento_uc)
        return use_case

    def create_preenchimento_folha_use_case(
        self, fundo: str
    ) -> PreenchimentoFolhaUseCase:
        pagamento_uc: PagamentoUseCase = self.create_pagamento_use_case(fundo)

        siggo_service: ISiggoService = SiggoServiceMock()
        preenchedor_gw: IPreenchimentoGateway = PreenchimentoGateway(siggo_service)

        use_case = PreenchimentoFolhaUseCase(pagamento_uc, preenchedor_gw)

        return use_case

    def create_preenchimento_nl_use_case(self) -> PreenchimentoNLUseCase:
        pathing_gw: IPathingGateway = PathingGateway()
        nl_folha_gw: INLFolhaGateway = NLFolhaGateway(pathing_gw)

        siggo_service: ISiggoService = SiggoService()
        preenchedor_gw: IPreenchimentoGateway = PreenchimentoGateway(siggo_service)

        use_case = PreenchimentoNLUseCase(nl_folha_gw, preenchedor_gw)

        return use_case

    def criar_baixa_diaria_usecase(self) -> BaixaDiariaUseCase:
        pathing_gw: IPathingGateway = PathingGateway()
        siggo_service: ISiggoService = SiggoService()
        preenchedor_gw: IPreenchimentoGateway = PreenchimentoGateway(siggo_service)
        pdf_svc: IPdfService = PdfService(pathing_gw)

        use_case = BaixaDiariaUseCase(preenchedor_gw, pathing_gw, pdf_svc)
        return use_case

    def create_extrair_dados_r2000_usecase(self) -> ExtrairDadosR2000UseCase:
        pathing_gw: IPathingGateway = PathingGateway()
        pdf_svc: IPdfService = PdfService(pathing_gw)

        caminho_planilha_reinf = pathing_gw.get_caminho_reinf(PASTA_MES_ANTERIOR)
        excel_svc: IExcelService = ExcelService(caminho_planilha_reinf)

        use_case = ExtrairDadosR2000UseCase(excel_svc, pdf_svc, pathing_gw)

        return use_case

    def create_exportar_valores_pagos_usecase(self) -> ExtrairDadosR2000UseCase:
        pathing_gw: IPathingGateway = PathingGateway()
        pdf_svc: IPdfService = PdfService(pathing_gw)

        caminho_planilha_reinf = pathing_gw.get_caminho_valores_pagos()
        excel_svc: IExcelService = ExcelService(caminho_planilha_reinf)

        use_case = ExtrairDadosR2000UseCase(excel_svc, pdf_svc, pathing_gw)

        return use_case

    def create_emails_driss_usecase(self) -> EmailsDrissUseCase:
        pathing_gw: IPathingGateway = PathingGateway()
        pdf_svc: IPdfService = PdfService(pathing_gw)

        caminho_planilha_emails = (
            pathing_gw.get_secon_root_path()
            + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\EMAIL_EMPRESAS.xlsx"
        )
        excel_svc: IExcelService = ExcelService(caminho_planilha_emails)
        email_svc: IEmailService = EmailService()
        use_case = EmailsDrissUseCase(pathing_gw, pdf_svc, excel_svc, email_svc)
        return use_case
