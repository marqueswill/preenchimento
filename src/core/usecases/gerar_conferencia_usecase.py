from typing import Dict, List
from pandas import DataFrame
from core.gateways.i_conferencia_gateway import IConferenciaGateway
from core.gateways.i_excel_service import IExcelService
from core.gateways.i_nl_folha_gateway import INLFolhaGateway


class GerarConferenciaUseCase:

    def __init__(
        self, conferencia_gw: IConferenciaGateway, nl_folha_gw: INLFolhaGateway, excel_svc:IExcelService
    ):
        self.conferencia_gw = conferencia_gw
        self.nl_folha_gw = nl_folha_gw
        self.excel_service = excel_svc

    def executar(self, fundo):
        # --- Lógica NLs ---
        # 1. obter nome dos templates para o fundo informado
        # 2. gerar as nls para o fundo
        # 3. exportar nls
        nomes_templates = self.conferencia_gw.get_nomes_templates(fundo)
        nls_fundo = self.conferencia_gw.get_nls_folha(
            fundo, nomes_templates, self.nl_folha_gw
        )
        self.conferencia_gw.salvar_nls_conferencia(nls_fundo)

        # --- Lógica conferência da folha ---
        # 1. Obter dados conferencia de "DEMOFIN - T"
        # 2. Obter proventos e descontos passando dados conferencia
        # 3. Calcular os totais
        # 4. Exportar dados
        conferencia_completa = self.conferencia_gw.get_dados_conferencia(fundo)
        proventos = self.conferencia_gw.separar_proventos(conferencia_completa)
        descontos = self.conferencia_gw.separar_descontos(conferencia_completa)
        totais = self._calcular_totais(nls_fundo, proventos, descontos)
        self.conferencia_gw.salvar_dados_conferencia(proventos, descontos, totais)

        # --- Lógica relatórios ---
        # 1. Extrair dados de proventos e descontos do relatório
        # 2. Exportar dados para conferencia
        dados_relatorio = self.conferencia_gw.extrair_dados_relatorio(fundo)
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
