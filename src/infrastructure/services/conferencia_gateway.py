import pandas as pd

from pandas import DataFrame

from src.config import *

from src.core.gateways.i_conferencia_gateway import IConferenciaGateway


class ConferenciaGateway(IConferenciaGateway):

    def get_tabela_demofin(self):
        caminho_completo = self.pathing_gw.get_caminho_tabela_demofin()
        tabela_demofin = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1
        )
        return tabela_demofin

    def salvar_nls_conferencia(self, nls: dict[str, DataFrame]):
        for sheet_name, table_data in nls.items():
            self.excel_svc.exportar_para_planilha(table_data, sheet_name)

    def salvar_dados_conferencia(
        self, proventos_folha: DataFrame, descontos_folha: DataFrame, totais: DataFrame
    ):
        # Exporta proventos na coluna A
        self.excel_svc.exportar_para_planilha(
            table=proventos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="A",
            clear=True,
        )

        # Exporta descontos na coluna H
        self.excel_svc.exportar_para_planilha(
            table=descontos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            clear=False,
        )

        # Exporta os totais para coluna H, abaixo dos descontos
        ultima_linha = str(len(descontos_folha) + 3)
        self.excel_svc.exportar_para_planilha(
            table=totais,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            start_line=ultima_linha,
            clear=False,
        )

        self.excel_svc.delete_sheet("Sheet")
        self.excel_svc.move_to_first("CONFERÊNCIA")

    def salvar_dados_relatorio(self, dados_relatorio):
        self.excel_svc.exportar_para_planilha(
            dados_relatorio["PROVENTOS"],
            sheet_name="RELATÓRIO",
            start_column="A",
            clear=True,
        )

        self.excel_svc.exportar_para_planilha(
            dados_relatorio["DESCONTOS"],
            sheet_name="RELATÓRIO",
            start_column="E",
            clear=False,
        )

        self.excel_svc.move_to_first("RELATÓRIO")
