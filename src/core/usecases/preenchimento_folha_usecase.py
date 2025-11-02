from typing import Dict, List
from pandas import DataFrame
from core.usecases.pagamento_usecase import PagamentoUseCase
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class PreenchimentoFolhaUseCase:

    def __init__(
        self,
        pagamento_uc: PagamentoUseCase,
        nl_folha_gw: INLFolhaGateway,
        preenchedor_gw: IPreenchimentoGateway
    ):
        self.pagamento_uc = pagamento_uc
        self.nl_folha_gw = nl_folha_gw
        self.preenchedor_gw = preenchedor_gw

    def preencher_nls_siggo(self, fundo: str, templates: list[str]):
        saldos = self.pagamento_uc.gerar_saldos(fundo)
        dados_preenchimento = self._gerar_dados_para_preenchimento(fundo, templates, saldos)
        self.preenchedor_gw.executar(dados_preenchimento)

    def _gerar_dados_para_preenchimento(
        self, fundo: str, nomes_templates: list[str], saldos: dict
    )-> list[dict[str,DataFrame]]:
        folhas = []
        for template in nomes_templates:
            folhas.append(
                {
                    "cabecalho": self.nl_folha_gw.carregar_cabecalho(fundo, template),
                    "folha": self.nl_folha_gw.gerar_nl_folha(fundo, template, saldos),
                }
            )
        return folhas
