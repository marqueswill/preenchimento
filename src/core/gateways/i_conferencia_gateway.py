from abc import ABC, abstractmethod
from typing import List, Tuple
from pandas import DataFrame

from infrastructure.files.excel_service import ExcelService


class IConferenciaGateway(ABC):

    def __init__(self, excel_service: ExcelService):
        self.excel_service = excel_service
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
