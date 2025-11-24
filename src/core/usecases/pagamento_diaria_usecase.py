import os
from pandas import DataFrame
import pandas as pd

from src.core.gateways.i_pdf_service import IPdfService
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway


class PagamentoDiariaUseCase:
    def __init__(
        self,
        preenchimento_gw: IPreenchimentoGateway,
        pathing_gw: IPathingGateway,
        pdf_svc: IPdfService,
    ):
        self.preenchimento_gw = preenchimento_gw
        self.pathing_gw = pathing_gw
        self.pdf_svc = pdf_svc

    def listar_planilhas(self) -> list[str]:
        dir_path = os.path.join(
            self.pathing_gw.get_caminho_raiz_secon(),
            "SECON - General",
            "ANO_ATUAL",
            "NL_AUTOMATICA",
            "NE_DIÁRIAS",
        )
        return self.pathing_gw.listar_arquivos(dir_path)

    def gerar_nl_diarias(
        self, arquivos_selecionados: list[str]
    ) -> list[dict[str, DataFrame]]:
        dados_preenchimento: list[dict[str, DataFrame]] = []
        caminhos_pdf = self.pathing_gw.get_caminhos_nes_diaria(arquivos_selecionados)
        for i, caminho_pdf in enumerate(caminhos_pdf):
            nl = DataFrame(
                columns=[
                    "EVENTO",
                    "INSCRIÇÃO",
                    "CLASS. CONT",
                    "CLASS. ORC",
                    "FONTE",
                    "VALOR",
                ]
            )
            cabecalho = DataFrame(
                columns=[
                    "Coluna 1",
                    "Coluna 2",
                ],
            )

            dados_extraidos = self.pdf_svc.parse_dados_diaria(caminho_pdf)

            if i == 0:
                processo = dados_extraidos["processo"]
                observacao = dados_extraidos["observacao"]
                coluna2 = ["F0", "4 - UG/Gestão", "020101-00001", processo, observacao]
                cabecalho["Coluna 2"] = coluna2

            for dados in dados_extraidos["dados"]:
                evento1 = "510379"
                evento2 = "520379"
                incricao = dados["nune"]
                classcont1 = "113110105"
                classcont2 = "218910200"
                classorc = str(dados["natureza"]) + str(dados["subitem"])
                fonte = dados["fonte"]
                valor = dados["valor"]

                linha1 = [evento1, incricao, classcont1, classorc, fonte, valor]
                linha2 = [evento2, incricao, classcont2, classorc, fonte, valor]

                nl.loc[len(nl)] = linha1
                nl.loc[len(nl)] = linha2

        nl = nl.sort_values(by=["EVENTO", "INSCRIÇÃO"]).reset_index(drop=True)

        dados_preenchimento.append(
            {
                "folha": nl,
                "cabecalho": cabecalho,
            }
        )

        return dados_preenchimento

    def executar(self, arquivos_selecionados: list[str]):
        dados_preenchimento = self.gerar_nl_diarias(arquivos_selecionados)
        self.preenchimento_gw.executar(dados_preenchimento)
