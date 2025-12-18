from abc import ABC, abstractmethod
from typing import Dict
from pandas import DataFrame

from src.core.entities.entities import (
    DadosPreenchimento,
    TemplateNotaLancamento,
    NotaLancamento,
)


class IPreenchimentoGateway(ABC):
    """_summary_ Preenche os dados de NLs no siggo."""

    @abstractmethod
    def executar(self, dados: list[DadosPreenchimento]): ...

    @abstractmethod
    def separar_por_pagina(
        self, dataframe: NotaLancamento, tamanho_pagina=24
    ) -> list[NotaLancamento]: ...

    @abstractmethod
    def preparar_preechimento_cabecalho(self, template: TemplateNotaLancamento): ...

    @abstractmethod
    def preparar_preenchimento_nl(self, dados): ...

    def extrair_dados_preenchidos(self) -> list[DadosPreenchimento]: ...
