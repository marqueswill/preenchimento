from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pandas import DataFrame

from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_pathing_gateway import IPathingGateway


class IConferenciaGateway(ABC):
    """_summary_ Extração e transformação dos dados para gerar a conferência da folha de pagamentos.
    Inclui os dados de proventos e descontos do Demofin, os dados do relatório e as NLs geradas.
    """

    def __init__(
        self,
        pathing_gw: IPathingGateway,  # Configuração do pathing
        excel_svc: IExcelService,  # Exportação e importação
    ):
        self.pathing_gw = pathing_gw
        self.excel_svc = excel_svc
        super().__init__()

    @abstractmethod
    def get_tabela_demofin() -> DataFrame:
        pass

    @abstractmethod
    def parse_relatorio(self) -> str:
        pass

    @abstractmethod
    def salvar_nls_conferencia(self, nls: List[DataFrame]):
        pass

    @abstractmethod
    def salvar_dados_conferencia(
        self, proventos: DataFrame, descontos: DataFrame, totais: DataFrame
    ):
        pass

    @abstractmethod
    def salvar_dados_relatorio(self, dados_relatorio: DataFrame):
        pass
