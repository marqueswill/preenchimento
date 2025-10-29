from typing import Dict, List
from pandas import DataFrame
from core.gateways.i_conferencia_gateway import IConferenciaGateway
from core.gateways.i_excel_service import IExcelService
from core.gateways.i_nl_folha_gateway import INLFolhaGateway


class GerarConferenciaUseCase:

    def __init__(
        self,
        conferencia_gw: IConferenciaGateway,
        nl_folha_gw: INLFolhaGateway,
        excel_svc: IExcelService,
    ):
        self.conferencia_gw = conferencia_gw
        self.nl_folha_gw = nl_folha_gw
        self.excel_service = excel_svc

    def executar(self, fundo):
        conferencia_completa = self.conferencia_gw.get_dados_conferencia(fundo)
        conferencia_ferias = self.conferencia_gw.get_dados_conferencia(
            fundo, adiantamento_ferias=True
        )

        proventos = self.conferencia_gw.separar_proventos(conferencia_completa)
        descontos = self.conferencia_gw.separar_descontos(conferencia_completa)
        
        saldos = self.conferencia_gw.gerar_saldos(
            conferencia_ferias, proventos, descontos
        )
        nls_fundo = self._gerar_nls_folha(fundo, saldos)
        
        totais = self._calcular_totais(nls_fundo, proventos, descontos)

        dados_relatorio = self.conferencia_gw.extrair_dados_relatorio(fundo)

        self.conferencia_gw.salvar_nls_conferencia(nls_fundo)
        self.conferencia_gw.salvar_dados_conferencia(proventos, descontos, totais)
        self.conferencia_gw.salvar_dados_relatorio(dados_relatorio)

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
                    None,  # FIXME: tirar essa gambiarra aqui
                    total_saldo,
                    total_liquidado,
                ],
            }
        )

        return totais

    def _gerar_nls_folha(self, fundo: str, saldos: dict):
        nomes_templates = self.conferencia_gw.get_nomes_templates(fundo)
        nls = {}
        for template in nomes_templates:
            nls[template] = self.nl_folha_gw.gerar_nl_folha(fundo, template, saldos)
        return nls
