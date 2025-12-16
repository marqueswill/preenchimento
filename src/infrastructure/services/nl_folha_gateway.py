from typing import List
from pandas import DataFrame
import pandas as pd

from src.config import *
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway


class NLFolhaGateway(INLFolhaGateway):
    """_summary_ Responsável por interagir com os arquivos de Templates das Notas de Lançamento (NL). Ele lista as abas disponíveis (templates), carrega os dados do cabeçalho da NL e os dados das linhas de lançamento para serem usados no preenchimento.

    Args:
        INLFolhaGateway (_type_): _description_
    """

    def __init__(self, pathing_gw: IPathingGateway):
        self.pathing_gw = pathing_gw
        super().__init__()

    def get_nomes_templates(self, fundo: str) -> List[str]:
        caminho_template = self.pathing_gw.get_caminho_template(fundo)
        template_excel = pd.ExcelFile(caminho_template)
        nomes_nls = template_excel.sheet_names

        return nomes_nls

    # TODO: verificação formato template
    def carregar_template_nl(
        self, caminho_completo: str, template: str, incluir_calculos=True
    ) -> DataFrame:
        try:
            dataframe = pd.read_excel(
                caminho_completo,
                header=6,
                sheet_name=template,
                usecols="A:I" if incluir_calculos else "A:F",
                dtype=str,
            ).astype(str)

            dataframe.replace(["nan", ""], ".", inplace=True)
            dataframe["CLASS. ORC"] = (
                dataframe["CLASS. ORC"]
                .apply(lambda x: x[1:] if len(x) == 9 else x)
                .astype(str)
            )
            return dataframe
        except Exception as e:
            print("Feche todas planilhas de template e tente novamente.", e)

    # TODO: verificação formato cabeçalho
    def carregar_cabecalho(self, caminho_completo: str, template: str) -> DataFrame:
        try:
            # dataframe = pd.read_excel(
            #     caminho_completo,
            #     header=None,
            #     sheet_name=template,
            #     usecols="A:I",
            # ).astype(str)
            dataframe = pd.read_excel(
                caminho_completo,
                sheet_name=template,
                dtype=str,
                header=None,
            ).astype(str)
            return dataframe
        except Exception as e:
            print("Feche as planilhas de template e tente novamente.", e)

    def listar_abas(self, caminho_arquivo: str) -> List[str]:
        xls = pd.ExcelFile(caminho_arquivo)
        return xls.sheet_names
