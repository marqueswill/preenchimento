from typing import List
from pandas import DataFrame
import pandas as pd

from src.config import *
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class NLFolhaGateway(INLFolhaGateway):
    def __init__(self, pathing_gw):
        super().__init__(pathing_gw)

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


    def carregar_template_nl(self, nome_fundo: str, template: str) -> DataFrame:
        try:
            caminho_completo = self.pathing_gw.get_template_paths(nome_fundo)
            dataframe = pd.read_excel(
                caminho_completo,
                header=6,
                sheet_name=template,
                usecols="A:I",
                dtype=str,
            ).astype(str)

            dataframe["CLASS. ORC"] = (
                dataframe["CLASS. ORC"]
                .apply(lambda x: x[1:] if len(x) == 9 else x)
                .astype(str)
            )
            dataframe["VALOR"] = 0.0
            return dataframe
        except Exception as e:
            print("Feche todas planilhas de template e tente novamente.")

    def carregar_cabecalho(self, nome_fundo, template) -> DataFrame:
        try:
            caminho_completo = self.pathing_gw.get_template_paths(nome_fundo)
            dataframe = pd.read_excel(
                caminho_completo,
                header=None,
                sheet_name=template,
                usecols="A:I",
            ).astype(str)

            return dataframe
        except:
            print("Feche as planilhas de template e tente novamente.")
