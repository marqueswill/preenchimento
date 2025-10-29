from abc import ABC, abstractmethod


# Fiz isso pra conseguir personalizar os caminhos durante os testes
class IPathingGateway(ABC):
    @abstractmethod
    def get_root_path(self) -> str:
        pass

    @abstractmethod
    def get_template_paths(self, tipo_folha: str) -> str:
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