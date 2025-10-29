from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pandas import DataFrame

from core.gateways.i_excel_service import IExcelService
from core.gateways.i_pathing_gateway import IPathingGateway
from infrastructure.files.excel_service import ExcelService
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class IConferenciaGateway(ABC):
    """_summary_ Extração e transformação dos dados para gerar a conferência da folha de pagamentos.



    Args:
        ABC (_type_): _description_
    """

    def __init__(
        self,
        nl_folha_gw: INLFolhaGateway,  # Gerar NLs
        pathing_gw: IPathingGateway,  # Configuração do pathing
        excel_service: IExcelService,  # Exportação e importação
    ):
        self.nl_folha_gw = nl_folha_gw
        self.pathing_gw = pathing_gw
        self.excel_service = excel_service
        super().__init__()

    @abstractmethod
    def get_nomes_templates(self, fundo: str) -> List[str]:
        pass

    @abstractmethod
    def salvar_nls_conferencia(self, nls: List[DataFrame]):
        pass

    @abstractmethod
    def get_dados_conferencia(
        self, fundo: str, agrupar=True, adiantamento_ferias=False
    ):
        pass

    @abstractmethod
    def separar_proventos(self, conferencia_rgps_final: DataFrame) -> DataFrame:
        pass

    @abstractmethod
    def separar_descontos(self, conferencia_rgps_final: DataFrame) -> DataFrame:
        pass

    def gerar_saldos(
        self,
        dados_conferencia_ferias: DataFrame,
        dados_proventos: DataFrame,
        dados_descontos: DataFrame,
    ) -> DataFrame:
        pass

    @abstractmethod
    def salvar_dados_conferencia(
        self, proventos: DataFrame, descontos: DataFrame, totais: DataFrame
    ):
        pass

    @abstractmethod
    def extrair_dados_relatorio(self, fundo: str) -> DataFrame:
        pass

    @abstractmethod
    def salvar_dados_relatorio(self, dados_relatorio: DataFrame):
        pass
