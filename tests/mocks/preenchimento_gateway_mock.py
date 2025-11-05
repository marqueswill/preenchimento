from typing import Dict
from pandas import DataFrame
from selenium.webdriver.common.by import By

from src.infrastructure.services.preenchimento_gateway import PreenchimentoGateway
from src.config import *


class PreenchimentoGatewayMock(PreenchimentoGateway):
    def __init__(self, siggo_service):
        super().__init__(siggo_service)