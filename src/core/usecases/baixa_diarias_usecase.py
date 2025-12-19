from pandas import DataFrame
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.entities.entities import *


class BaixaDiariasUseCase:
    def __init__(self, preenchimento_gw: IPreenchimentoGateway) -> None:
        self.preenchimento_gw = preenchimento_gw

    def executar(self):
        dados = self.obter_dados()
        dados_preenchimento = self.gerar_nls_baixa(dados)
        self.preencher_nls(dados_preenchimento)

    def obter_dados(self) -> DataFrame: ...
    def gerar_nls_baixa(self, dados: DataFrame) -> list[DadosPreenchimento]: ...
    def preencher_nls(self, dados_preenchimento: list[DadosPreenchimento]):
        self.preenchimento_gw.executar(dados_preenchimento)
