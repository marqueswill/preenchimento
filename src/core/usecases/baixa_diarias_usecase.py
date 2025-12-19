import pandas as pd
import re
from pandas import DataFrame
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_excel_service import IExcelService
from src.core.entities.entities import DadosPreenchimento, NotaLancamento, CabecalhoNL
from src.config import NOME_MES_ATUAL


class BaixaDiariasUseCase:
    def __init__(
        self,
        pathing_gw: IPathingGateway,
        excel_svc: IExcelService,
        preenchimento_gw: IPreenchimentoGateway,
    ):
        self.pathing_gw = pathing_gw
        self.excel_svc = excel_svc
        self.preenchimento_gw = preenchimento_gw

    def executar(self):
        dados = self.obter_dados()
        dados_preenchimento = self.gerar_nls_baixa(dados)
        self.preencher_nls(dados_preenchimento)

    def obter_dados(self) -> DataFrame:
        return self.excel_svc.get_sheet(sheet_name="data", as_dataframe=True)

    def gerar_nls_baixa(self, dados_baixa: DataFrame) -> list[DadosPreenchimento]:

        # 1. Separar por processo
        grupos = dados_baixa.groupby(["PROCESSO"], dropna=False)

        dados_preenchimento: list[DadosPreenchimento] = []
        for (processo), df in grupos:
            evento_baixa = "560379"
            class_cont = "332110100"
            observacao = f"BAIXA DE ADIANTAMENTO DE VIAGENS (DIÁRIAS) REFERENTE A EVENTOS REALIZADOS NO MÊS DE {NOME_MES_ATUAL}."

            processo_limpo = re.sub(r"[ -.;]", "", str(processo))

            nl_df = df[["COCREDOR", "FONTE", "SALDO"]].copy()
            nl_df = nl_df.rename(
                columns={"COCREDOR": "INSCRIÇÃO", "FONTE": "FONTE", "SALDO": "VALOR"}
            ) # type: ignore

            nl_df["EVENTO"] = evento_baixa
            nl_df["CLASS. CONT"] = class_cont
            nl_df["CLASS. ORC"] = ""

            colunas_finais = [
                "EVENTO",
                "INSCRIÇÃO",
                "CLASS. CONT",
                "CLASS. ORC",
                "FONTE",
                "VALOR",
            ]
            nl_df = nl_df[colunas_finais].reset_index()

            lancamento = NotaLancamento(nl_df)

            cabecalho = CabecalhoNL(
                prioridade="Z0",
                credor="4 - UG/Gestão",
                gestao="020101-00001",
                processo=processo_limpo,
                observacao=observacao,
            )

            dados_nl = DadosPreenchimento(lancamento, cabecalho)
            dados_preenchimento.append(dados_nl)

        return dados_preenchimento

    def preencher_nls(self, dados_preenchimento: list[DadosPreenchimento]):
        self.preenchimento_gw.executar(dados_preenchimento, divisao_par=False)
