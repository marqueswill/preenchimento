from abc import ABC, abstractmethod
from typing import List, Tuple
from pandas import DataFrame

from infrastructure.files.excel_service import ExcelService
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class IConferenciaGateway(ABC):
    """_summary_ Extração e transformação dos dados para gerar a conferência da folha de pagamentos.



    Args:
        ABC (_type_): _description_
    """

    def __init__(self):
        self.excel_service = ExcelService
        self.nl_folha_gw = INLFolhaGateway
        super().__init__()

    @abstractmethod
    def get_nomes_templates(self, fundo: str) -> List[str]:
        pass

    @abstractmethod
    def get_nls_folha(self, fundo: str, nomes_templates: List[str]) -> List[DataFrame]:
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
