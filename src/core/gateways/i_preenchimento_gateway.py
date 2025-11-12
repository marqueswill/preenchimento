from abc import ABC, abstractmethod
from typing import Dict
from pandas import DataFrame


class IPreenchimentoGateway(ABC):
    """_summary_ Preenche os dados de NLs no siggo."""

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
