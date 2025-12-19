from pandas import DataFrame
import pandas as pd
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.services.i_excel_service import IExcelService
from src.core.entities.entities import DadosPreenchimento,NotaLancamento,CabecalhoNL
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
        return self.excelsvc.get_sheet(sheet_name="data", as_dataframe=True, columns="A:F")
    
    def gerar_nls_baixa(self, dados_baixa: DataFrame) -> list[DadosPreenchimento]:

        # 1. Separar por processo
        grupos = dados_baixa.groupby(["PROCESSO"], dropna=False)

        dados_preenchimento: list[DadosPreenchimento] = []
        for (processo), df in grupos:
            evento_baixa = "560379"
            class_cont =  "332110100"
            observacao = f"BAIXA DE ADIANTAMENTO DE VIAGENS (DIÁRIAS) REFERENTE A EVENTOS REALIZADOS NO MÊS DE {NOME_MES_ATUAL}."

            # 2. Criar a NL para cada processo
            for _, dados in df.iterrows():
                lancamento = NotaLancamento(
                        pd.DataFrame({
                        "EVENTO": evento_baixa,
                        "INSCRIÇÃO": dados["COCREDOR"],
                        "CLASS. CONT": class_cont,
                        "CLASS. ORC": "",
                        "FONTE": dados["FONTE"],
                        "VALOR":dados["SALDO"]
                    })
                )

            # 3. Criar o cabecalho de cada um
            cabecalho = CabecalhoNL(
                prioridade="Z0",
                credor="4 - UG/Gestão",
                gestao="020101-00001",
                processo=processo,
                observacao=observacao,
            )

            dados_nl = DadosPreenchimento(lancamento, cabecalho)
            dados_preenchimento.append(dados_nl)

    def preencher_nls(self, dados_preenchimento: list[DadosPreenchimento]):
        return # Pular por enquanto
        self.preenchimento_gw.executar(dados_preenchimento)

