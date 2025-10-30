from abc import ABC, abstractmethod


# Fiz isso pra conseguir personalizar os caminhos durante os testes
class ISiggoService(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def start(self, run=True, test=False):
        pass

    @abstractmethod
    def setup_pandas(self):
        pass

    @abstractmethod
    def setup_driver(self):
        pass

    @abstractmethod
    def finalizar(self):
        pass

    @abstractmethod
    def login_siggo(self, cpf, password):
        pass

    @abstractmethod
    def esperar_login(self, timeout=60):
        pass

    @abstractmethod
    def esperar_carregamento(self, timeout=60):
        pass

    @abstractmethod
    def preencher_campos(self, campos: dict):
        pass

    @abstractmethod
    def selecionar_opcoes(self, opcoes: dict):
        pass

    @abstractmethod
    def nova_aba(self):
        pass

    @abstractmethod
    def acessar_link(self, link):
        pass

    @abstractmethod
    def fechar_primeira_aba(self):
        pass

    @abstractmethod
    def executar(self):
        pass
