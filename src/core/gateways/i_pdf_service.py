from abc import ABC, abstractmethod
from pypdf import PageObject
from src.core.gateways.i_pathing_gateway import IPathingGateway


class IPdfService(ABC):

    def __init__(self, pathing_gw: IPathingGateway):
        self.pathing_gw = pathing_gw
        super().__init__()

    @abstractmethod
    def parse_dados_diaria(self, caminho_pdf: str) -> dict: ...

    @abstractmethod
    def parse_relatorio_folha(self): ...

    @abstractmethod
    def parse_dados_inss(self): ...

    @abstractmethod
    def parse_pdf_driss(self, file) -> dict[str, list[PageObject]]: ...

    @abstractmethod
    def export_pages(self, pages: list[PageObject], path: str): ...
