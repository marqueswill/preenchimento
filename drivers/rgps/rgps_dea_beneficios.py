import sys

from drivers.rgps.rgps_base import PreenchimentoRGPSBase


class PreenchimentoRGPSDeaBeneficios(PreenchimentoRGPSBase):
    def __init__(self, test=False):
        self.nome_template = "DEA-BENEFÍCIOS"
        super().__init__(test)

    def gerar_folha_rgps(self):
        folha_rgps = self.carregar_template_nl()
        dados_conferencia_rgps = self.gerar_conferencia()
        proventos_rgps = self.gerar_proventos(dados_conferencia_rgps)

        folha_rgps = folha_rgps.merge(
            proventos_rgps[["CDG_NAT_DESPESA", "SALDO"]].rename(
                columns={"SALDO": "VALOR"}
            ),
            left_on="CLASS. ORC",
            right_on="CDG_NAT_DESPESA",
            how="left",
        )
        folha_rgps.drop(columns=["CDG_NAT_DESPESA"], inplace=True)

        folha_rgps.loc[folha_rgps["CLASS. CONT"] == "211115101", "VALOR"] = (
            folha_rgps.loc[folha_rgps["CLASS. ORC"] == "33909208", "VALOR"].values[0]
        )
        folha_rgps = folha_rgps.sort_values(by="INSCRIÇÃO")

        return folha_rgps


try:
    driver = PreenchimentoRGPSDeaBeneficios(test=False)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
