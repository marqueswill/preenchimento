from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver


class IWebDriverService(ABC):

    @abstractmethod
    def inicializar(self) -> SeleniumWebDriver: ...
    
    @abstractmethod
    def finalizar(self): ...

    @abstractmethod
    def setup_pandas(self): ...

    @abstractmethod
    def setup_driver(self): ...

    @abstractmethod
    def nova_aba(self): ...

    @abstractmethod
    def acessar_link(self, link): ...

    @abstractmethod
    def fechar_primeira_aba(self): ...

    @abstractmethod
    def fechar_pagina_atual(self): ...

    @abstractmethod
    def recarregar_pagina(self): ...

    @abstractmethod
    def esperar_carregamento(self, timeout=60): ...
