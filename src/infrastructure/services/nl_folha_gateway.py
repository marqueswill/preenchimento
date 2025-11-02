from typing import List
from pandas import DataFrame
import pandas as pd

from src.config import *
from src.core.gateways.i_nl_folha_gateway import INLFolhaGateway


class NLFolhaGateway(INLFolhaGateway):
    def __init__(self, pathing_gw):
        super().__init__(pathing_gw)

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

    def gerar_nl_folha(self, fundo: str, template: str, saldos: dict) -> DataFrame:
        """_summary_ Recebe um fundo e o nome de um nome de uma nl e preenche o template encontrado
        com os valores de saldo passados.
        """
        folha_pagamento = self._carregar_template_nl(fundo, template)

        # Calcula o valor para cada linha
        for idx, row in folha_pagamento.iterrows():
            class_orc = row.get("CLASS. ORC", "")
            class_cont = row.get("CLASS. CONT", "")
            somar = row.get("SOMAR", [])
            subtrair = row.get("SUBTRAIR", [])
            tipo = (
                "ATIVO" if row.get("TIPO", "") in {"", "nan"} else row.get("TIPO", "")
            )

            if tipo == "MANUAL":
                folha_pagamento.at[idx, "VALOR"] = 0.000001
            else:
                valor_somar = self._soma_codigos(somar, saldos[tipo])
                valor_subtrair = self._soma_codigos(subtrair, saldos[tipo])
                valor = valor_somar - valor_subtrair
                folha_pagamento.at[idx, "VALOR"] = valor

        folha_pagamento.drop(columns=["SOMAR", "SUBTRAIR", "TIPO"], inplace=True)
        folha_pagamento = folha_pagamento[folha_pagamento["VALOR"] > 0]
        folha_pagamento = folha_pagamento.sort_values(by="INSCRIÇÃO")

        return folha_pagamento

    def _carregar_template_nl(self, nome_fundo: str, template: str) -> DataFrame:
        try:
            caminho_completo = self.pathing_gw.get_template_paths(nome_fundo)
            dataframe = pd.read_excel(
                caminho_completo,
                header=6,
                sheet_name=template,
                usecols="A:I",
                dtype=str,
            ).astype(str)

            dataframe["CLASS. ORC"] = (
                dataframe["CLASS. ORC"]
                .apply(lambda x: x[1:] if len(x) == 9 else x)
                .astype(str)
            )
            dataframe["VALOR"] = 0.0
            return dataframe
        except Exception as e:
            print("Feche todas planilhas de template e tente novamente.")

    def carregar_cabecalho(self, nome_fundo, template) -> DataFrame:
        try:
            caminho_completo = self.pathing_gw.get_template_paths(nome_fundo)
            dataframe = pd.read_excel(
                caminho_completo,
                header=None,
                sheet_name=template,
                usecols="A:I",
            ).astype(str)

            return dataframe
        except:
            print("Feche as planilhas de template e tente novamente.")

    def _soma_codigos(self, codigos: str, dicionario: dict):
        lista_codigos = list(map(str.strip, codigos.split(",")))
        lista_codigos = [
            c[1:] if c.startswith("33") and len(c) == 9 else c for c in lista_codigos
        ]
        resultado = sum(float(dicionario.get(str(c), 0.0)) for c in lista_codigos)

        return resultado
