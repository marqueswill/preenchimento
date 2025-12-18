from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from pandas import DataFrame


class IConferenciaGateway(ABC):
    """_summary_ Extração e transformação dos dados para gerar a conferência da folha de pagamentos.
    Inclui os dados de proventos e descontos do Demofin, os dados do relatório e as NLs geradas.
    """

    @abstractmethod
    def get_tabela_demofin() -> DataFrame: ...

    @abstractmethod
    def salvar_nls_conferencia(self, nls: List[DataFrame]): ...

    @abstractmethod
    def salvar_dados_conferencia(
        self, proventos: DataFrame, descontos: DataFrame, totais: DataFrame
    ): ...

    @abstractmethod
    def salvar_dados_relatorio(self, dados_relatorio: DataFrame): ...
