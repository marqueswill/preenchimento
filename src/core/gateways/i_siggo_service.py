from abc import ABC, abstractmethod


class ISiggoService(ABC):
    """_summary_ Faz a interação com o sistema Siggo.

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def start(self):
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
