from typing import List
from pandas import DataFrame
import pandas as pd

from src.config import *
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class NLFolhaGateway(INLFolhaGateway):

    def get_nomes_templates(self, fundo: str) -> List[str]:
        caminho_template = self.pathing_gw.get_caminho_template(fundo)
        template_excel = pd.ExcelFile(caminho_template)
        nomes_nls = template_excel.sheet_names

        return nomes_nls

    def carregar_template_nl(self, nome_fundo: str, template: str) -> DataFrame:
        try:
            caminho_completo = self.pathing_gw.get_caminho_template(nome_fundo)
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
            caminho_completo = self.pathing_gw.get_caminho_template(nome_fundo)
            dataframe = pd.read_excel(
                caminho_completo,
                header=None,
                sheet_name=template,
                usecols="A:I",
            ).astype(str)

            return dataframe
        except:
            print("Feche as planilhas de template e tente novamente.")
