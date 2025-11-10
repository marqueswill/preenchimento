import re
import pypdf
from pypdf import PdfReader, PdfWriter
import tabula
import pandas as pd
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_pdf_service import IPdfService
from pandas import DataFrame


class PdfService(IPdfService):

    def parse_relatorio_folha(self, fundo_escolhido) -> dict[str, DataFrame]:
        caminho_pdf_relatorio = self.pathing_gw.get_caminho_pdf_relatorio()
        with open(caminho_pdf_relatorio, "rb") as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text.find("DEMOFIM - ATIVOS") != -1:
                    text += extracted_text.replace("\n", " ").replace("  ", " ")
                else:
                    break

        file.close()
        # text = self.pdf_svc.parse_relatorio()
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

    def parse_dados_diaria(self, caminho_pdf: str) -> dict:
        """Extrai dados de um PDF de diárias."""

        with open(caminho_pdf, "rb") as file:
            reader = PdfReader(file)
            text = ""
            notas_empenho = []
            for page in reader.pages:
                text = page.extract_text()
                text = re.sub(r"\s+", " ", text)
                text.strip()
                notas_empenho.append(text)

        file.close()

        dados = []

        for dados_brutos in notas_empenho:
            processo_match = re.search(r"Número do Processo ([\d/-]+)", dados_brutos)
            processo = processo_match.group(1)

            nune_match = re.search(r"Número do Documento ([A-Z0-9]+)", dados_brutos)
            nune = nune_match.group(1) if nune_match else None

            credor_match = re.search(r"Credor (\d+)", dados_brutos)
            credor = credor_match.group(1) if credor_match else None
            # credor = table.iloc[5, 0].split("-")[0].strip()  # linha 5, coluna 0

            valor_match = re.search(r"Transferência Valor ([\d.,]+)", dados_brutos)
            valor = (
                float(valor_match.group(1).replace(".", "").replace(",", "."))
                if valor_match
                else None
            )

            fonte_match = re.search(
                r"(?s)Natureza da Despesa.*?(\d+\.\d+).*?Cronograma de Desembolso",
                dados_brutos,
            )
            fonte = fonte_match.group(1).split(".")[1]

            match_natureza = re.search(
                r"(?s)Natureza da Despesa.*?(\d+)\s*Cronograma de Desembolso",
                dados_brutos,
            )
            natureza = match_natureza.group(1)

            bloco_match = re.search(
                r"(?s)Subitens da Despesa(.*?)(?=No\. Licitação)", dados_brutos
            )
            if bloco_match:
                bloco_de_subitens = bloco_match.group(1)
                padrao_pares = r"(\d+)\s+([\d\.]+,\d{2})"
                pares = re.findall(padrao_pares, bloco_de_subitens)
                subitems = [par[0] for par in pares]

            subitem = subitems[0]

            dados.append(
                {
                    "nune": nune,
                    "credor": credor,
                    "fonte": fonte,
                    "valor": valor,
                    "natureza": natureza,
                    "subitem": subitem,
                }
            )

        # TODO: extrair observacao da NE
        observacao = ""

        return {"processo": processo, "observacao": observacao, "dados": dados}
