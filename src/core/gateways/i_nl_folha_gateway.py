from abc import ABC, abstractmethod

from pandas import DataFrame

from src.core.gateways.i_pathing_gateway import IPathingGateway


class INLFolhaGateway:
    """_summary_ Gera uma NL para folha de pagamento a partir de um fundo e um template fornecido.
    """

    def __init__(self, pathing_gw: IPathingGateway):
        self.pathing = pathing_gw

    @abstractmethod
    def gerar_nl_folha(self, fundo: str, template: str, saldos: str) -> DataFrame:
        pass

    @abstractmethod
    def carregar_cabecalho(self, nome_fundo, template) -> DataFrame:
        pass
