from typing import Dict, List
from pandas import DataFrame
from src.core.usecases.pagamento_usecase import PagamentoUseCase
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class PreenchimentoFolhaUseCase:

    def __init__(
        self, pagamento_uc: PagamentoUseCase, preenchedor_gw: IPreenchimentoGateway
    ):
        self.pagamento_uc = pagamento_uc
        self.preenchedor_gw = preenchedor_gw

    def get_nomes_templates(self, fundo: str):
        return self.pagamento_uc.nl_folha_gw.get_nomes_templates(fundo)

    def get_dados_preenchidos(self) -> dict[str, dict[str, DataFrame]]:
        return self.preenchedor_gw.extrair_dados_preenchidos()

    def executar(
        self, fundo: str, templates: list[str]
    ) -> dict[str, dict[str, DataFrame]]:
        saldos = self.pagamento_uc.get_saldos(fundo)
        dados_gerados = self._gerar_dados_para_preenchimento(
            fundo, templates, saldos
        )
        self.preenchedor_gw.executar(dados_gerados)
        return dados_gerados

    def _gerar_dados_para_preenchimento(
        self, fundo: str, nomes_templates: list[str], saldos: dict
    ) -> dict[str, dict[str, DataFrame]]:
        folhas = {}
        for template in nomes_templates:
            folhas[template] = {
                "cabecalho": self.pagamento_uc.nl_folha_gw.carregar_cabecalho(
                    fundo, template
                ),
                "folha": self.pagamento_uc.gerar_nl_folha(fundo, template, saldos),
            }
        return folhas
