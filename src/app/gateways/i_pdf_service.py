from abc import ABC, abstractmethod

from src.app.gateways.i_pathing_gateway import IPathingGateway


class IPdfService(ABC):

    def __init__(self, pathing_gw: IPathingGateway):
        self.pathing_gw = pathing_gw
        super().__init__()

    @abstractmethod
    def parse_dados_diaria(self, caminho_pdf: str) -> dict: ...

    @abstractmethod
    def parse_relatorio_folha(self): ...

    @abstractmethod
    def parse_dados_inss(self):...