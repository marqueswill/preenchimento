import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSBase


class PreenchimentoRGPSBeneficios(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "BENEFICIOS"
        super().__init__(test)

    def gerar_folha_rgps(self):
        folha_rgps = self.carregar_template_nl()
        dados_conferencia_rgps = self.gerar_conferencia()
        proventos_rgps = self.gerar_proventos(dados_conferencia_rgps)

        # Fazendo o LEFT JOIN (merge) com base nas colunas correspondentes
        folha_rgps = folha_rgps.merge(
            proventos_rgps[["CDG_NAT_DESPESA", "SALDO"]].rename(
                columns={"SALDO": "VALOR"}
            ),
            left_on="CLASS. ORC",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33900800", "VALOR"] = (
            folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33900855", "VALOR"].values[0]
            + folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33900811", "VALOR"].values[0]
        )

        folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33904600", "VALOR"] = (
            folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33904602", "VALOR"].values[0]
        )
        folha_rgps = folha_rgps.sort_values(by="INSCRIÇÃO")

        return folha_rgps


try:
    driver = PreenchimentoRGPSBeneficios(test=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
