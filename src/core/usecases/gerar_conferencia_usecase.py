from typing import Dict, List
from pandas import DataFrame
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway
from src.core.usecases.pagamento_usecase import PagamentoUseCase
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class GerarConferenciaUseCase:

    def __init__(
        self,
        pagamento_uc: PagamentoUseCase,
    ):
        self.pagamento_uc = pagamento_uc

    def executar(self, fundo):
        conferencia_completa = self.pagamento_uc.get_dados_conferencia(fundo)
        conferencia_ferias = self.pagamento_uc.get_dados_conferencia(
            fundo, adiantamento_ferias=True
        )

        proventos = self.pagamento_uc.separar_proventos(conferencia_completa)
        descontos = self.pagamento_uc.separar_descontos(conferencia_completa)
        dados_relatorio = self.pagamento_uc.extrair_dados_relatorio(fundo)

        saldos = self.pagamento_uc.gerar_saldos(
            conferencia_ferias, proventos, descontos
        )

        nls_fundo = self._gerar_nls_folha(fundo, saldos)
        totais = self._calcular_totais(nls_fundo, proventos, descontos)

   
        self.pagamento_uc.conferencia_gw.salvar_dados_conferencia(
            proventos, descontos, totais
        )
        self.pagamento_uc.conferencia_gw.salvar_dados_relatorio(dados_relatorio)
        self.pagamento_uc.conferencia_gw.salvar_nls_conferencia(nls_fundo)

    def _calcular_totais(
        self,
        nls: Dict[str, DataFrame],
        proventos_folha: DataFrame,
        descontos_folha: DataFrame,
    ) -> DataFrame:

        total_liquidado = 0
        for nl in [v for k, v in nls.items() if k != "ADIANTAMENTO_FERIAS"]:
            total_liquidado += nl.loc[
                nl["EVENTO"].astype(str).str.startswith("510", na=False), "VALOR"
            ].sum()

        total_proventos = (
            proventos_folha["PROVENTO"].sum() + descontos_folha["PROVENTO"].sum()
        )
        total_descontos = (
            proventos_folha["DESCONTO"].sum() + descontos_folha["DESCONTO"].sum()
        )
        total_liquido = total_proventos - total_descontos
        total_saldo = proventos_folha["SALDO"].sum()

        totais = DataFrame(
            {
                "TOTAIS": [
                    "PROVENTOS",
                    "DESCONTOS",
                    "LÍQUIDO FINANCEIRO",
                    "",
                    "TOTAL DE SALDO",
                    "TOTAL LIQUIDADO",
                ],
                "VALOR": [
                    total_proventos,
                    total_descontos,
                    total_liquido,
                    None,  # TODO: tirar essa gambiarra aqui
                    total_saldo,
                    total_liquidado,
                ],
            }
        )

        return totais

    def _gerar_nls_folha(self, fundo: str, saldos: dict):
        nomes_nls = self.pagamento_uc.nl_folha_gw.get_nomes_templates(fundo)
        caminho_planilha_templates = (
            self.pagamento_uc.conferencia_gw.pathing_gw.get_caminho_template(fundo)
        )
        nls = {}
        for nome_nl in nomes_nls:
            nls[nome_nl] = self.pagamento_uc.gerar_nl_folha(
                caminho_planilha_templates, nome_nl, saldos
            )
        return nls
