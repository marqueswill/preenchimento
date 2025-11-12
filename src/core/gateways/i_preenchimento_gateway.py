from abc import ABC, abstractmethod
from typing import Dict
from pandas import DataFrame

from src.core.gateways.i_siggo_service import ISiggoService


class IPreenchimentoGateway(ABC):
    """_summary_ Preenche os dados de NLs no siggo."""

    def __init__(self, siggo_service: ISiggoService):
        self.siggo_driver = siggo_service
        super().__init__()

    @abstractmethod
    def executar(self, dados: list[dict[str, DataFrame]]): ...

    @abstractmethod
    def separar_por_pagina(
        self, dataframe: DataFrame, tamanho_pagina=24
    ) -> list[DataFrame]: ...

    @abstractmethod
    def preparar_preechimento_cabecalho(self, template: DataFrame): ...

    @abstractmethod
    def preparar_preenchimento_nl(self, dados): ...

    def extrair_dados_preenchidos(self) -> list[dict[str, DataFrame]]: ...
