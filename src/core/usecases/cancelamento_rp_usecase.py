from pandas import DataFrame
import pandas as pd
from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.config import *


class CancelamentoRPUseCase:
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
        # 1. Obter os dados da planilha
        dados_planilha = self.obter_dados_cacelamento()

        # 2. Montar os dados para o preenchimento
        dados_preenchimento = self.preparar_dados_preenchimento(dados_planilha)

        # 3. Preencher no navegador
        self.preencher_dados_siggo(dados_preenchimento)

    def obter_dados_cacelamento(self) -> DataFrame:
        dados_brutos = self.excel_svc.get_sheet(
            sheet_name="CANCELAMENTO_RP", as_dataframe=True
        )

        dados_brutos.columns = dados_brutos.columns.str.strip()

        dados_brutos = dados_brutos[dados_brutos["SALDO"] > 0].reset_index(drop=True)
        dados_brutos["FONTE"] = (
            pd.to_numeric(dados_brutos["FONTE"], errors="coerce")
            .fillna(0)
            .astype(int)
            .astype(str)
        )
        dados_brutos["CONTRATO"] = (
            pd.to_numeric(dados_brutos["CONTRATO"], errors="coerce")
            .fillna(0)
            .astype(int)
            .astype(str)
        )

        return dados_brutos

    def _preparar_dados_preenchimento(
        self, dados_brutos: DataFrame
    ) -> list[dict[str, DataFrame]]:
        # Agrupar por processo e contrato
        dados_preenchimento =[]
        grupos = dados_brutos.groupby(["PROCESSO", "CONTRATO", "NE"], dropna=False)
        trocas_digito_fonte = {
            "1": "3",
            "2": "4",
            "7": "8",
            "3": "3",
            "4": "4",
            "8": "8",
        }
        for (processo, contrato, ne), df in grupos:
            nl = pd.DataFrame(
                {
                    "EVENTO": "540032",  # Valor fixo repetido para todas as linhas
                    "INSCRIÇÃO": df["NE"],  # Copia a coluna inteira
                    "CLASS. CONT": "",  # Valor vazio repetido
                    "CLASS. ORC": df["NATUREZA"],  # Copia a coluna
                    "FONTE": df["FONTE"],  # Copia a coluna
                    "VALOR": df["SALDO"],  # Copia a coluna
                }
            )

            # Lógica eventos 550
            total550 = nl["VALOR"].sum()
            segundo_digito = str(nl["CLASS. ORC"].iloc[0])[1]
            inscricao_natureza = "02101" + segundo_digito + f"{ANO_ATUAL}{MES_ATUAL}"
            fonte550 = nl["FONTE"].iloc[0]
            linha550 = ["570569", inscricao_natureza, "", "", fonte550, total550]
            nl.loc[len(nl)] = linha550

            # Lógica eventos 570: agrupamento por NE, fonte sempre a mesma
            total570 = df["SALDO"].sum()
            digito_fonte = df["FONTE"].iloc[0][0]
            resto_fonte = df["FONTE"].iloc[0][1:]
            fonte570 = trocas_digito_fonte[digito_fonte] + resto_fonte

            linha570 = ["570569", "", "", "", fonte570, total570]
            nl.loc[len(nl)] = linha570

            prioridade = "Z0"
            credor = "4 - UG/Gestão"
            gestao = "020101-00001"
            observacao = f"CANCELAMENTO DO SALDO DE RESTOS A PAGAR NÃO PROCESSADOS RELATIVOS A {ANO_ATUAL-1} PELA NÃO UTILIZAÇÃO."
            cabecalho = pd.DataFrame(
                [
                    ["Prioridade de Pagamento:", prioridade],
                    ["Credor:", credor],  # Ex: "4 - UG/Gestão"
                    ["UG/Gestão:", gestao],  # Ex: "020101-00001"
                    ["Processo:", processo],  # Ex: "00600-0000..."
                    ["Observação:", observacao],  # Ex: "PROVISÃO..."
                    ["Observação:", observacao],  # Ex: "PROVISÃO..."
                    ["Contrato:", contrato],  # Ex: "PROVISÃO..."
                ],
                columns=["RÓTULO", "VALOR"],
            )

            dados_preenchimento.append( {
                "folha": nl,
                "cabecalho": cabecalho,
            })

            print(nl)
            print(cabecalho)
            print("\n\n" + "-" * 100)

        return dados_preenchimento

    def preparar_dados_preenchimento(
            self, dados_brutos: DataFrame
        ) -> list[dict[str, DataFrame]]:

        dados_preenchimento = []

        # 1. Agrupamos primeiramente APENAS por PROCESSO
        grupos_processo = dados_brutos.groupby("PROCESSO", dropna=False)

        trocas_digito_fonte = {
                "1": "3", "2": "4", "7": "8", 
                "3": "3", "4": "4", "8": "8",
            }

        for processo, df_processo in grupos_processo:

            dfs_para_concatenar = []

            # 2. Agora sub-agrupamos por Contrato e NE para fazer os cálculos específicos
            subgrupos = df_processo.groupby(["CONTRATO", "NE"], dropna=False)

            for (contrato, ne), df in subgrupos:

                # --- Lógica Evento 540032 (Detalhes) ---
                nl_parcial = pd.DataFrame({
                        "EVENTO": "540032",
                        "INSCRIÇÃO": df["NE"],
                        "CLASS. CONT": "",
                        "CLASS. ORC": df["NATUREZA"],
                        "FONTE": df["FONTE"],
                        "VALOR": df["SALDO"],
                    })

                # --- Lógica Evento 550 ---
                total550 = nl_parcial["VALOR"].sum()
                # Pega o primeiro valor disponível para gerar a inscrição
                segundo_digito = str(nl_parcial["CLASS. ORC"].iloc[0])[1]
                inscricao_natureza = f"02101{segundo_digito}{ANO_ATUAL}{MES_ATUAL}"
                fonte550 = nl_parcial["FONTE"].iloc[0]

                linha550 = pd.DataFrame([{
                        "EVENTO": "550923", # Assumindo o código do evento
                        "INSCRIÇÃO": inscricao_natureza,
                        "CLASS. CONT": "",
                        "CLASS. ORC": "",
                        "FONTE": fonte550,
                        "VALOR": total550
                    }])

                # --- Lógica Evento 570 ---
                total570 = df["SALDO"].sum()
                fonte_orig = str(df["FONTE"].iloc[0])
                digito_fonte = fonte_orig[0]
                resto_fonte = fonte_orig[1:]
                novo_digito = trocas_digito_fonte.get(digito_fonte, digito_fonte) 
                fonte570 = novo_digito + resto_fonte

                linha570 = pd.DataFrame([{
                        "EVENTO": "570569",
                        "INSCRIÇÃO": "",
                        "CLASS. CONT": "",
                        "CLASS. ORC": "",
                        "FONTE": fonte570,
                        "VALOR": total570
                    }])

                # Adiciona tudo na lista deste processo
                dfs_para_concatenar.extend([nl_parcial, linha550, linha570])

            # 3. Consolidação do Processo
            if not dfs_para_concatenar:
                continue

            df_final_processo = pd.concat(dfs_para_concatenar, ignore_index=True)

            # --- PASSO CRUCIAL: AGREGAR LINHAS IGUAIS ---
            # Agrupa por todas as colunas exceto VALOR e soma o VALOR
            colunas_agrupamento = [c for c in df_final_processo.columns if c != "VALOR"]

            df_agrupado = (
                    df_final_processo
                    .groupby(colunas_agrupamento, dropna=False, as_index=False)["VALOR"]
                    .sum()
                )

            # Opcional: Ordenar para que 540 venha antes de 550/570 visualmente
            df_agrupado = df_agrupado.sort_values(by=["EVENTO", "INSCRIÇÃO"]).reset_index(drop=True)

            # 4. Montagem do Cabeçalho
            prioridade = "Z0"
            credor = "4 - UG/Gestão"
            gestao = "130101-00001"
            observacao = f"CANCELAMENTO DO SALDO DE RESTOS A PAGAR NÃO PROCESSADOS RELATIVOS A {ANO_ATUAL-1} PELA NÃO UTILIZAÇÃO."

            dados_cabecalho = [
                    ["Prioridade de Pagamento:", prioridade],
                    ["Credor:", credor],
                    ["UG/Gestão:", gestao],
                    ["Processo:", processo],
                    ["Observação:", observacao],
                    ["Contrato:", contrato]
                ]

            cabecalho = pd.DataFrame(
                dados_cabecalho
            )  # Sem colunas definidas fica índice 0 e 1, ideal para export

            dados_preenchimento.append(
                {
                    "folha": df_agrupado,
                    "cabecalho": cabecalho,
                }
            )

            print(f"Processo: {processo}")
            print(df_agrupado)
            print("-" * 50)

        return dados_preenchimento

    def preencher_dados_siggo(self, dados_preenchimento):
        self.preenchimento_gw.executar(dados_preenchimento)
