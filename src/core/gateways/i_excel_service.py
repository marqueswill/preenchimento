# /src/core/gateways/i_excel_service.py

from abc import ABC, abstractmethod
from typing import Any, List, Optional
from pandas import DataFrame


class IExcelService(ABC):
    """
    Define a interface (contrato) para um serviço que
    manipula arquivos de planilha (Excel).
    """

    @abstractmethod
    def get_sheet(
        self,
        sheet_name: str,
        as_dataframe: bool = False,
        header_row: int = 1,
        columns: Optional[List[str]] = None,
    ) -> DataFrame | Any: ...

    @abstractmethod
    def delete_sheet(self, sheet_name: str) -> None: ...

    @abstractmethod
    def move_to_first(self, sheet_name: str) -> None: ...

    @abstractmethod
    def exportar_para_planilha(
        self,
        table: DataFrame,
        sheet_name: str,
        start_column: str = "A",
        start_line: str = "1",
        clear: bool = False,
        sum_numeric: bool = False,
        fit_columns: bool = True,
        write_headers: bool = True,
    ) -> None: ...

    @abstractmethod
    def destacar_linhas(
        self,
        sheet_name: str,
        cor_fundo: str = "FFFF00",
        negrito: bool = False,
        coluna_alvo: str = None,
        valor_alvo: Any = None,
        header_row: int = 1,
    ) -> None: ...
