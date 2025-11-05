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
    def executar(self, dados: list[Dict[str, DataFrame]]):
        pass

    @abstractmethod
    def separar_por_pagina(
        self, dataframe: DataFrame, tamanho_pagina=24
    ) -> list[DataFrame]:
        pass

    @abstractmethod
    def preparar_preechimento_cabecalho(self, template: DataFrame):
        pass

    @abstractmethod
    def preparar_preenchimento_nl(self, dados):
        pass

    def extrair_dados_preenchidos(self) -> dict[str, dict[str, DataFrame]]:
        pass
        # Iterar sobre as abas abertas no navegador
        # Extrair os dados preenchidos de cada aba
