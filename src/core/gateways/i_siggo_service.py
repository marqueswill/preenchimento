from abc import ABC, abstractmethod


class ISiggoService(ABC):
    """_summary_ Faz a interação com o sistema Siggo."""

    @abstractmethod
    def start(self): ...

    @abstractmethod
    def setup_pandas(self): ...

    @abstractmethod
    def setup_driver(self): ...

    @abstractmethod
    def finalizar(self): ...

    @abstractmethod
    def login_siggo(self, cpf, password): ...

    @abstractmethod
    def esperar_login(self, timeout=60): ...

    @abstractmethod
    def esperar_carregamento(self, timeout=60): ...

    @abstractmethod
    def preencher_campos(self, campos: dict): ...

    @abstractmethod
    def selecionar_opcoes(self, opcoes: dict): ...

    @abstractmethod
    def nova_aba(self): ...

    @abstractmethod
    def acessar_link(self, link): ...

    @abstractmethod
    def fechar_primeira_aba(self): ...

    @abstractmethod
    def executar(self): ...
