import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSBase


class PreenchimentoRGPSPrincipal(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "PRINCIPAL"
        super().__init__(test)

    def gerar_folha_rgps(self):
        folha_rgps = self.carregar_template_nl()
        dados_conferencia_rgps = self.gerar_conferencia()

        proventos_rgps = self.gerar_proventos(dados_conferencia_rgps)
        descontos_rgps = self.gerar_descontos(dados_conferencia_rgps)

        folha_rgps = folha_rgps.merge(
            proventos_rgps[["CDG_NAT_DESPESA", "SALDO"]].rename(
                columns={"SALDO": "SALDO_PROVENTO"}
            ),
            left_on="CLASS. ORC",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        folha_rgps = folha_rgps.merge(
            descontos_rgps[["CDG_NAT_DESPESA", "SALDO"]].rename(
                columns={"SALDO": "SALDO_DESCONTO"}
            ),
            left_on="CLASS. CONT",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        # Combina os valores, dando prioridade a PROVENTO, senão usa DESCONTO
        folha_rgps["VALOR"] = folha_rgps["SALDO_PROVENTO"].combine_first(
            folha_rgps["SALDO_DESCONTO"]
        )

        # Remove colunas auxiliares
        folha_rgps.drop(columns=["SALDO_PROVENTO", "SALDO_DESCONTO"], inplace=True)

        # CDG_NAT_DESPESA
        classificacao_somar = {
            "31901167": [
                "31901167",
                "31901101",  # 20
                "31901102",  # 8
                "31901104",  # 1
            ],
            "211110102": [
                "31901122",
            ],
            "211110103": [
                "31901131",
                "31901132",
            ],
        }

        for cod, somas in classificacao_somar.items():
            if cod[0] == "3":
                rgps_key_column = "CLASS. ORC"

            else:
                rgps_key_column = "CLASS. CONT"

            total = proventos_rgps.loc[
                proventos_rgps["CDG_NAT_DESPESA"].isin(somas),
                "SALDO",
            ].sum()

            folha_rgps.loc[folha_rgps[rgps_key_column] == cod, "VALOR"] = total

        soma_311 = folha_rgps.loc[
            folha_rgps["CLASS. ORC"].isin(
                ["31901107", "31901134", "31901141", "31901156", "31901157", "31901167"]
            ),
            "VALOR",
        ].sum()
        subtrai_218 = descontos_rgps.loc[
            descontos_rgps["CDG_NAT_DESPESA"].isin(
                ["218810110", "218810199", "218820104", "218830102"]
            ),
            "SALDO",
        ].sum()

        folha_rgps.loc[folha_rgps["CLASS. CONT"] == "211110101", "VALOR"] = (
            soma_311 - subtrai_218
        )

        folha_rgps = folha_rgps[folha_rgps["VALOR"] > 0]
        folha_rgps = folha_rgps.sort_values(by="INSCRIÇÃO")

        return folha_rgps


try:
    driver = PreenchimentoRGPSPrincipal(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
