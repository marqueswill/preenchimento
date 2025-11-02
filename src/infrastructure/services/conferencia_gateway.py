import os
import re
import PyPDF2
import numpy as np
import pandas as pd

from typing import List
from pandas import DataFrame

from src.config import *
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway


# TODO: Emburrecer o gateway:
# mover processamento, lógica de negócio e orquestrações para usecase, manter somente I/O
class ConferenciaGateway(IConferenciaGateway):

    def __init__(self, path_gateway, excel_svc):
        super().__init__(path_gateway, excel_svc)

    def get_nomes_templates(self, fundo: str) -> List[str]:
        caminho_raiz = (
            self.pathing_gw.get_root_path()
            + f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\TEMPLATES\\"
        )

        # Carrega as planilhas de templates
        excel_rgps = pd.ExcelFile(caminho_raiz + "TEMPLATES_NL_RGPS.xlsx")
        excel_financeiro = pd.ExcelFile(caminho_raiz + "TEMPLATES_NL_FINANCEIRO.xlsx")
        excel_capitalizado = pd.ExcelFile(
            caminho_raiz + "TEMPLATES_NL_CAPITALIZADO.xlsx"
        )

        # Carrega todos os templates das NLs
        templates_rgps = excel_rgps.sheet_names
        templates_financeiro = excel_financeiro.sheet_names
        templates_capitalizado = excel_capitalizado.sheet_names

        # Categoriza os templates das NLs
        nomes_templates = {
            "RGPS": templates_rgps,
            "FINANCEIRO": templates_financeiro,
            "CAPITALIZADO": templates_capitalizado,
        }

        return nomes_templates[fundo]

    def get_tabela_demofin(self):
        caminho_completo = self.pathing_gw.get_caminho_tabela_demofin()
        tabela_demofin = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1
        )
        return tabela_demofin

    def parse_relatorio(self, fundo):
        caminho_pdf_relatorio = self.pathing_gw.get_caminho_pdf_relatorio()
        with open(caminho_pdf_relatorio, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text.find("DEMOFIM - ATIVOS") != -1:
                    text += extracted_text.replace("\n", " ").replace("  ", " ")
                else:
                    break
        file.close()
        return text

    def salvar_nls_conferencia(self, nls: dict[str, DataFrame]):
        for sheet_name, table_data in nls.items():
            self.excel_service.exportar_para_planilha(table_data, sheet_name)

    def salvar_dados_conferencia(
        self, proventos_folha: DataFrame, descontos_folha: DataFrame, totais: DataFrame
    ):
        # Exporta proventos na coluna A
        self.excel_service.exportar_para_planilha(
            table=proventos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="A",
            clear=True,
        )

        # Exporta descontos na coluna H
        self.excel_service.exportar_para_planilha(
            table=descontos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            clear=False,
        )

        # Exporta os totais para coluna H, abaixo dos descontos
        ultima_linha = str(len(descontos_folha) + 3)
        self.excel_service.exportar_para_planilha(
            table=totais,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            start_line=ultima_linha,
            clear=False,
        )

        self.excel_service.delete_sheet("Sheet")
        self.excel_service.move_to_first("CONFERÊNCIA")

    def salvar_dados_relatorio(self, dados_relatorio):
        self.excel_service.exportar_para_planilha(
            dados_relatorio["PROVENTOS"],
            sheet_name="RELATÓRIO",
            start_column="A",
            clear=True,
        )

        self.excel_service.exportar_para_planilha(
            dados_relatorio["DESCONTOS"],
            sheet_name="RELATÓRIO",
            start_column="E",
            clear=False,
        )

        self.excel_service.move_to_first("RELATÓRIO")
