import os
import re
import PyPDF2
import numpy as np
import pandas as pd

from typing import List
from pandas import DataFrame

from src.config import ANO_ATUAL, PASTA_MES_ATUAL
from src.core.gateways.i_conferencia_gateway import IConferenciaGateway
from src.core.gateways.i_excel_service import IExcelService
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway


class ConferenciaGateway(IConferenciaGateway):

    def __init__(self, path_gateway, excel_svc):
        super().__init__(path_gateway, excel_svc)

    def get_nomes_templates(self, fundo: str) -> List[str]:
        caminho_raiz = (
            self.pathing_gw.get_root_path()
            + f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\TEMPLATES\\"
        )

        # Carrega as planilhas de templates
        excel_rgps = pd.ExcelFile(caminho_raiz + "TEMPLATES_NL_RGPS.xlsx")
        excel_financeiro = pd.ExcelFile(caminho_raiz + "TEMPLATES_NL_FINANCEIRO.xlsx")
        excel_capitalizado = pd.ExcelFile(
            caminho_raiz + "TEMPLATES_NL_CAPITALIZADO.xlsx"
        )

        # Carrega todos os templates das NLs
        templates_rgps = excel_rgps.sheet_names
        templates_financeiro = excel_financeiro.sheet_names
        templates_capitalizado = excel_capitalizado.sheet_names

        # Categoriza os templates das NLs
        nomes_templates = {
            "RGPS": templates_rgps,
            "FINANCEIRO": templates_financeiro,
            "CAPITALIZADO": templates_capitalizado,
        }

        return nomes_templates[fundo]

    def salvar_nls_conferencia(self, nls: dict[str, DataFrame]):
        for sheet_name, table_data in nls.items():
            self.excel_service.exportar_para_planilha(table_data, sheet_name)

    def get_dados_conferencia(self, fundo, agrupar=True, adiantamento_ferias=False):
        cod_fundos = {
            "RGPS": 1,
            "FINANCEIRO": 2,
            "CAPITALIZADO": 3,
            "INATIVO": 4,
            "PENSÃO": 5,
        }

        # Define o caminho até a pasta onde está o arquivo
        caminho_completo = self.pathing_gw.get_caminho_tabela_demofin()

        # Lê a planilha com o nome da aba "DEMOFIN - T"
        tabela_demofin = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1
        )

        # Remove "." dos códigos
        tabela_demofin["CDG_NAT_DESPESA"] = tabela_demofin[
            "CDG_NAT_DESPESA"
        ].str.replace(".", "")

        tabela_demofin["NME_NAT_DESPESA"] = tabela_demofin[
            "NME_NAT_DESPESA"
        ].str.strip()

        tabela_demofin["NME_NAT_DESPESA"] = tabela_demofin[
            "NME_NAT_DESPESA"
        ].str.replace(r"\s+", " ", regex=True)

        # Filtra a tabela para o fundo específico
        filtro_fundo = tabela_demofin["CDG_FUNDO"] == cod_fundos[fundo]

        # Seleciona colunas de interesse
        plan_folha = tabela_demofin.loc[
            filtro_fundo,
            [
                "CDG_PROVDESC",
                "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA",
                "VALOR_AUXILIAR",
                "NME_PROVDESC",
            ],
        ]

        # Identifica os proventos e descontos e os tipos de cada (compensatoria, inativo, ativo, pensionista...)
        plan_folha["RUBRICA"] = plan_folha.apply(self._cria_coluna_rubrica, axis=1)
        plan_folha["TIPO_DESPESA"] = plan_folha.apply(self._cria_coluna_tipo, axis=1)

        # Apenas valores absolutos (lógica de saldo)
        plan_folha["VALOR_AUXILIAR"] = plan_folha["VALOR_AUXILIAR"].abs()

        # Agrupa os dados por CDG_PROVDESC, NME_NAT_DESPESA, CDG_NAT_DESPESA e TIPO_DESPESA
        plan_folha = pd.pivot_table(
            plan_folha,
            values="VALOR_AUXILIAR",
            index=[
                "CDG_PROVDESC",
                "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA",
                "TIPO_DESPESA",
            ],
            columns="RUBRICA",
            aggfunc="sum",
        )

        conferencia_folha = (
            plan_folha.groupby(
                ["CDG_PROVDESC", "NME_NAT_DESPESA", "CDG_NAT_DESPESA", "TIPO_DESPESA"]
            )[["PROVENTO", "DESCONTO"]]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        # Aplica a função pra criar a coluna "AJUSTE"
        conferencia_folha["AJUSTE"] = conferencia_folha["CDG_PROVDESC"].apply(
            self._categorizar_rubrica
        )

        conferencia_folha.sort_values(by=["CDG_NAT_DESPESA"])

        mask = (conferencia_folha["CDG_NAT_DESPESA"].str.startswith("3")) & (
            conferencia_folha["CDG_NAT_DESPESA"].str.len() == 9
        )

        conferencia_folha.loc[mask, "CDG_NAT_DESPESA"] = conferencia_folha.loc[
            mask, "CDG_NAT_DESPESA"
        ].str.slice(1)

        if not agrupar:
            return conferencia_folha

        if adiantamento_ferias:
            conferencia_folha_final = (
                conferencia_folha.groupby(
                    ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "TIPO_DESPESA", "AJUSTE"]
                )[["PROVENTO", "DESCONTO"]]
                .agg(lambda x: np.sum(np.abs(x)))
                .reset_index()
            )
        else:
            conferencia_folha_final = (
                conferencia_folha.groupby(
                    ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "TIPO_DESPESA"]
                )[["PROVENTO", "DESCONTO"]]
                .agg(lambda x: np.sum(np.abs(x)))
                .reset_index()
            )

        return conferencia_folha_final

    # Faz distinção entre proventos e descontos
    def _cria_coluna_rubrica(self, row):
        cdg_nat_despesa = str(row["CDG_NAT_DESPESA"])
        valor = row["VALOR_AUXILIAR"]

        if cdg_nat_despesa.startswith("3"):
            if valor > 0:
                return "PROVENTO"
            else:
                return "DESCONTO"
        elif cdg_nat_despesa.startswith("2") or cdg_nat_despesa.startswith("4"):
            if valor < 0:
                return "DESCONTO"
            else:
                return "PROVENTO"
        else:
            return ""  # Ou algum outro valor padrão, se necessário

    # Identifica a rubrica de adiantamento de férias
    def _categorizar_rubrica(self, rubrica):
        if rubrica in [11962, 21962, 32191, 42191, 52191, 61962]:
            return "ADIANTAMENTO FÉRIAS"
        return ""

    def _cria_coluna_tipo(self, row):
        cdg_nat_despesa = str(row["CDG_NAT_DESPESA"])
        nome_despesa = str(row["NME_PROVDESC"])

        tipo = "ATIVO"
        if cdg_nat_despesa == "331909401" and "COMPENSATÓRIA" in nome_despesa:
            tipo = "COMPENSATÓRIA"

        if cdg_nat_despesa == "333900811":
            if "INATIVO" in nome_despesa:
                tipo = "INATIVO"
            elif "PENSIONISTA" in nome_despesa:
                tipo = "PENSIONISTA"

        return tipo

    def salvar_dados_conferencia(
        self, proventos_folha: DataFrame, descontos_folha: DataFrame, totais: DataFrame
    ):
        # Exporta proventos na coluna A
        self.excel_service.exportar_para_planilha(
            table=proventos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="A",
            clear=True,
        )

        # Exporta descontos na coluna H
        self.excel_service.exportar_para_planilha(
            table=descontos_folha,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            clear=False,
        )

        # Exporta os totais para coluna H, abaixo dos descontos
        ultima_linha = str(len(descontos_folha) + 3)
        self.excel_service.exportar_para_planilha(
            table=totais,
            sheet_name="CONFERÊNCIA",
            start_column="H",
            start_line=ultima_linha,
            clear=False,
        )

        self.excel_service.delete_sheet("Sheet")
        self.excel_service.move_to_first("CONFERÊNCIA")

    def separar_proventos(self, conferencia_rgps_final: DataFrame):
        prov_folha = conferencia_rgps_final.loc[
            conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_proventos = prov_folha["PROVENTO"] - prov_folha["DESCONTO"]
        prov_folha = prov_folha.loc[
            :,
            [
                "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA",
                "PROVENTO",
                "DESCONTO",
                "TIPO_DESPESA",
            ],
        ].assign(SALDO=coluna_saldo_proventos)

        prov_folha = prov_folha.sort_values(by=["CDG_NAT_DESPESA"])

        return prov_folha

    def separar_descontos(self, conferencia_rgps_final: DataFrame):
        desc_folha = conferencia_rgps_final.loc[
            ~conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_descontos = desc_folha["DESCONTO"] - desc_folha["PROVENTO"]

        desc_folha = desc_folha.loc[
            :,
            [
                "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA",
                "DESCONTO",
                "PROVENTO",
                "TIPO_DESPESA",
            ],
        ].assign(SALDO=coluna_saldo_descontos)

        desc_folha = desc_folha.sort_values(by=["CDG_NAT_DESPESA"])

        return desc_folha

    def get_saldos(self, dados_conferencia_ferias, dados_proventos, dados_descontos):
        saldos_proventos = list(
            zip(
                dados_proventos["TIPO_DESPESA"],
                dados_proventos["CDG_NAT_DESPESA"],
                dados_proventos["SALDO"],
            )
        )
        saldos_descontos = list(
            zip(
                dados_descontos["TIPO_DESPESA"],
                dados_descontos["CDG_NAT_DESPESA"],
                dados_descontos["SALDO"],
            )
        )

        proventos_ferias = list(
            zip(
                dados_conferencia_ferias["AJUSTE"],
                dados_conferencia_ferias["CDG_NAT_DESPESA"],
                dados_conferencia_ferias["PROVENTO"],
            )
        )
        descontos_ferias = list(
            zip(
                dados_conferencia_ferias["AJUSTE"],
                dados_conferencia_ferias["CDG_NAT_DESPESA"],
                dados_conferencia_ferias["DESCONTO"],
            )
        )

        # Faz um dicionário com todos os saldos (proventos e descontos) segmentados pelo tipo do saldo
        saldos = {
            "ATIVO": {},
            "INATIVO": {},
            "COMPENSATÓRIA": {},
            "PENSIONISTA": {},
            "PROVENTO ADIANTAMENTO FÉRIAS": {},
            "DESCONTO ADIANTAMENTO FÉRIAS": {},
        }

        for line in saldos_proventos + saldos_descontos:
            saldos[line[0]][line[1]] = line[2]
        for line in proventos_ferias:
            saldos["PROVENTO ADIANTAMENTO FÉRIAS"][line[1]] = line[2]
        for line in descontos_ferias:
            saldos["DESCONTO ADIANTAMENTO FÉRIAS"][line[1]] = line[2]

        return saldos

    def gerar_saldos(self, fundo) -> dict[str, dict]:
        conferencia_completa = self.get_dados_conferencia(fundo)
        conferencia_ferias = self.get_dados_conferencia(fundo, adiantamento_ferias=True)

        proventos = self.separar_proventos(conferencia_completa)
        descontos = self.separar_descontos(conferencia_completa)

        saldos = self.get_saldos(conferencia_ferias, proventos, descontos)

        return saldos

    def extrair_dados_relatorio(self, fundo_escolhido: str):
        caminho_pdf_relatorio = self.pathing_gw.get_caminho_pdf_relatorio()
        with open(caminho_pdf_relatorio, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text.find("DEMOFIM - ATIVOS") != -1:
                    text += extracted_text.replace("\n", " ").replace("  ", " ")
                else:
                    break

        relatorios = {
            "RGPS": {"PROVENTOS": None, "DESCONTOS": None},
            "FINANCEIRO": {"PROVENTOS": None, "DESCONTOS": None},
            "CAPITALIZADO": {"PROVENTOS": None, "DESCONTOS": None},
        }

        dados_brutos = text.split("Total por Fundo de Previdência:")
        for fundo, relatorio in zip(relatorios.keys(), dados_brutos[:3]):
            inicio_proventos = relatorio.find("Proventos")
            inicio_descontos = relatorio.find("Descontos Elem. Despesa:")

            relatorios[fundo]["PROVENTOS"] = relatorio[
                inicio_proventos:inicio_descontos
            ]
            relatorios[fundo]["DESCONTOS"] = relatorio[inicio_descontos:]

        for nome_fundo, relatorio_fundo in relatorios.items():
            if (
                nome_fundo != fundo_escolhido
            ):  # Pulo extração se não for do fundo que escolhi
                continue

            padrao = re.compile(
                r"(\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{1,2})\s-\s(.*?)\sRubrica.*?Total por Natureza:\s([\d\.,]+)"
            )

            dados_proventos = []
            for item in relatorio_fundo["PROVENTOS"].split("Elem. Despesa:"):
                correspondencia = padrao.search(item)
                if correspondencia:
                    cod_nat = correspondencia.group(1).replace(".", "")
                    cod_nat = (
                        cod_nat[1:]
                        if cod_nat.startswith("3") and len(cod_nat) == 9
                        else cod_nat
                    )
                    nome_nat = correspondencia.group(2).strip()
                    total_natureza = float(
                        correspondencia.group(3).replace(".", "").replace(",", ".")
                    )
                    dados_proventos.append([nome_nat, cod_nat, total_natureza])

            dados_descontos = []
            for item in relatorio_fundo["DESCONTOS"].split("Elem. Despesa:"):
                correspondencia = padrao.search(item)
                if correspondencia:
                    cod_nat = correspondencia.group(1).replace(".", "")
                    cod_nat = (
                        cod_nat[1:]
                        if cod_nat.startswith("3") and len(cod_nat) == 9
                        else cod_nat
                    )

                    nome_nat = correspondencia.group(2).strip()
                    total_natureza = float(
                        correspondencia.group(3).replace(".", "").replace(",", ".")
                    )
                    dados_descontos.append([nome_nat, cod_nat, total_natureza])

            colunas_p = ["NOME NAT", "COD NAT", "PROVENTO"]
            df_proventos = pd.DataFrame(dados_proventos, columns=colunas_p)

            colunas_d = ["NOME NAT", "COD NAT", "DESCONTO"]
            df_descontos = pd.DataFrame(dados_descontos, columns=colunas_d)

            return {
                "PROVENTOS": df_proventos,
                "DESCONTOS": df_descontos,
            }

    def salvar_dados_relatorio(self, dados_relatorio):
        self.excel_service.exportar_para_planilha(
            dados_relatorio["PROVENTOS"],
            sheet_name="RELATÓRIO",
            start_column="A",
            clear=True,
        )

        self.excel_service.exportar_para_planilha(
            dados_relatorio["DESCONTOS"],
            sheet_name="RELATÓRIO",
            start_column="E",
            clear=False,
        )

        self.excel_service.move_to_first("RELATÓRIO")
