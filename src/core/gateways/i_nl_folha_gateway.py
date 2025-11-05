from abc import ABC, abstractmethod
from typing import List
from pandas import DataFrame

from src.core.gateways.i_pathing_gateway import IPathingGateway


class INLFolhaGateway(ABC):
    """_summary_ Gera uma NL para folha de pagamento a partir de um fundo e um template fornecido.
    Também interage com as planilhas de template das NLs de folha de pagamento.
    """

    def __init__(self, pathing_gw: IPathingGateway):
        self.pathing_gw = pathing_gw
        super().__init__()

    @abstractmethod
    def get_nomes_templates(self, fundo: str) -> List[str]:
        pass

    @abstractmethod
    def carregar_template_nl(self, nome_fundo: str, template: str) -> DataFrame:
        pass

    @abstractmethod
    def carregar_cabecalho(self, nome_fundo, template) -> DataFrame:
        pass
