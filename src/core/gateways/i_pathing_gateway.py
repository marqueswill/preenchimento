from abc import ABC, abstractmethod


class IPathingGateway(ABC):
    """_summary_ Gateway usado para unificar a personalização de caminhos"""

    @abstractmethod
    def get_secon_root_path(self) -> str:
        pass

    @abstractmethod
    def get_caminho_template(self, tipo_folha: str) -> str:
        pass

    @abstractmethod
    def get_caminho_conferencia(self, fundo: str):
        pass

    @abstractmethod
    def get_caminho_tabela_demofin() -> str:
        pass

    @abstractmethod
    def get_caminho_pdf_relatorio() -> str:
        pass

    @abstractmethod
    def get_current_file_path(self) -> str:
        pass
    
    @abstractmethod
    def listar_arquivos(self, caminho: str) -> list[str]:
        pass