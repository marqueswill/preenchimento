import numpy as np
from pandas import DataFrame
from pandas import read_excel
from src.infrastructure.files.excel_service import ExcelService


class ExcelServiceMock(ExcelService):
    def __init__(self, caminho_arquivo):
        super().__init__(caminho_arquivo)

    def get_proventos_conferencia(self) -> DataFrame:
        df = read_excel(
            self.caminho_arquivo,
            sheet_name="CONFERÊNCIA",
            usecols="A:F",
        )

        df["NME_NAT_DESPESA"] = (
            df["NME_NAT_DESPESA"].str.replace(r"\s{2,}", " ", regex=True).str.strip()
        )

        return df

    def get_descontos_conferencia(self) -> DataFrame:
        df = read_excel(
            self.caminho_arquivo,
            sheet_name="CONFERÊNCIA",
            usecols="H:M",
        )

        if df.empty:
            return df

        nome_coluna_m = df.columns[-1]
        df[nome_coluna_m] = df[nome_coluna_m].replace(r'^\s*$', np.nan, regex=True)
        df = df.dropna(subset=[nome_coluna_m])
        return df

    def get_totais_conferencia(self) -> DataFrame:
        descontos = self.get_descontos_conferencia()
        header_totais = descontos.shape[0] +2

        df = read_excel(
            self.caminho_arquivo,
            sheet_name="CONFERÊNCIA",
            usecols="H:I",
            header= header_totais
        )

        if df.empty:
            return df

        df = df.dropna(how="all")

        return df

    def get_nls_conferencia(self) -> DataFrame:
        pass

    def get_proventos_relatorio(self) -> DataFrame:
        df = read_excel(
            self.caminho_arquivo,
            sheet_name="RELATÓRIO",
            usecols="A:C",
        )


        df = df.dropna(how="all")

        return df

    def get_descontos_relatorio(self) -> DataFrame:
        df = read_excel(
            self.caminho_arquivo,
            sheet_name="RELATÓRIO",
            usecols="E:G",
        )

        df = df.dropna(how="all")

        return df
