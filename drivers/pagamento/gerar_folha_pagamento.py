import glob
import numpy as np
from pandas import DataFrame

import pandas as pd

import os
import locale
from datetime import datetime


locale.setlocale(locale.LC_TIME, "pt_BR.utf8")


ANO_ATUAL = datetime.now().year
MES_ATUAL = datetime.now().month
# MES_ATUAL = 6


MESES = {
    1: "01-JANEIRO",
    2: "02-FEVEREIRO",
    3: "03-MARÇO",
    4: "04-ABRIL",
    5: "05-MAIO",
    6: "06-JUNHO",
    7: "07-JULHO",
    8: "08-AGOSTO",
    9: "09-SETEMBRO",
    10: "10-OUTUBRO",
    11: "11-NOVEMBRO",
    12: "12-DEZEMBRO",
}


class FolhaPagamento():
    """_summary_
    Classe para gerar NLs das folhas de pagamento.
    """

    nome_template: str
    cod_fundo: int

    def __init__(self, nome_fundo: str, nome_template: str, test=False):
        """_summary_
        Inicializa a classe FolhaPagamento.
        Args:
            nome_fundo (str): _description_ - deve ser um dos seguintes: "rgps", "financeiro", "capitalizado", "inativo", "pensão".
            nome_template (str): _description_ - deve ser igual a um dos nomes de template disponíveis no arquivo de templates.
            test (bool, optional): _description_. Defaults to False. - se True, imprime os dados no console para teste.
        Raises:
        """

        username = os.getlogin().strip()
        self.caminho_raiz = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"

        cod_fundos = {"rgps": 1, "financeiro": 2,
                      "capitalizado": 3, "inativo": 4, "pensão": 5}

        self.cod_fundo = cod_fundos[nome_fundo.lower()]
        self.nome_fundo = nome_fundo.lower()
        self.nome_template = nome_template
        self.test = test
        # self.run = run
        # self.preenchedor = PreenchimentoNL(
        #     nome_fundo, nome_template, run, test)

    def carregar_planilha(self, caminho_planilha):
        caminho_completo = self.caminho_raiz + caminho_planilha
        dataframe = pd.read_excel(caminho_completo)
        return dataframe

    def carregar_template_nl(self):
        caminho_completo = (
            self.caminho_raiz +
            f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_{self.nome_fundo.upper()}.xlsx"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=self.nome_template,
            usecols="A:I",
        ).astype(str)

        dataframe["CLASS. ORC"] = dataframe["CLASS. ORC"].apply(
            lambda x: x[1:] if len(x) == 9 else x
        ).astype(str)

        
        return dataframe

    def carregar_template_cabecalho(self):
        caminho_completo = (
            self.caminho_raiz +
            f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_{self.nome_fundo.upper()}.xlsx"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=None,
            sheet_name=self.nome_template,
            usecols="A:I",
        ).astype(str)

        return dataframe
    
    def gerar_conferencia(self, agrupar=True):
        # Faz distinção entre proventos e descontos
        def cria_coluna_rubrica(row):
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
        def categorizar_rubrica(rubrica):
            if rubrica in [11962, 21962, 32191, 42191, 52191, 61962]:
                return "ADIANTAMENTO FÉRIAS"
            return ""

        def cria_coluna_tipo(row):
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


        # Define o caminho até a pasta onde está o arquivo
        caminho_pasta = os.path.join(
            self.caminho_raiz,
            f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}"
        )

        # Usa glob para encontrar qualquer arquivo que comece com "DEMOFIN" e contenha "TABELA"
        padrao_arquivo = os.path.join(caminho_pasta, "DEMOFIN*TAB*LA.xlsx")
        arquivos_encontrados = glob.glob(padrao_arquivo)

        if not arquivos_encontrados:
            raise FileNotFoundError(
                "Arquivo DEMOFIN_TABELA ou DEMOFIN - TABELA não encontrado.")

        # Usa o primeiro arquivo encontrado
        caminho_completo = arquivos_encontrados[0]

        # Lê a planilha com o nome da aba "DEMOFIN - T"
        tabela_demofin = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1)

        # Remove "." dos códigos
        tabela_demofin["CDG_NAT_DESPESA"] = tabela_demofin["CDG_NAT_DESPESA"].str.replace(
            ".", "")

        # Filtra a tabela para o fundo específico
        filtro_fundo = tabela_demofin["CDG_FUNDO"] == self.cod_fundo

        # Seleciona colunas de interesse
        plan_folha = tabela_demofin.loc[
            filtro_fundo,
            ["CDG_PROVDESC", "NME_NAT_DESPESA",
                "CDG_NAT_DESPESA", "VALOR_AUXILIAR", "NME_PROVDESC"],
        ]

        # Identifica os proventos e descontos e os tipos de cada (compensatoria, inativo, ativo, pensionista...)
        plan_folha["RUBRICA"] = plan_folha.apply(cria_coluna_rubrica, axis=1)
        plan_folha["TIPO_DESPESA"] = plan_folha.apply(cria_coluna_tipo, axis=1)

        # Apenas valores absolutos (lógica de saldo)
        plan_folha["VALOR_AUXILIAR"] = plan_folha["VALOR_AUXILIAR"].abs()

        # Agrupa os dados por CDG_PROVDESC, NME_NAT_DESPESA, CDG_NAT_DESPESA e TIPO_DESPESA
        plan_folha = pd.pivot_table(
            plan_folha,
            values="VALOR_AUXILIAR",
            index=["CDG_PROVDESC", "NME_NAT_DESPESA",
                   "CDG_NAT_DESPESA", "TIPO_DESPESA"],
            columns="RUBRICA",
            aggfunc="sum",
        )

        conferencia_folha = (
            plan_folha.groupby(["CDG_PROVDESC", "NME_NAT_DESPESA", "CDG_NAT_DESPESA", "TIPO_DESPESA"])[
                ["PROVENTO", "DESCONTO"]
            ]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        # Aplica a função pra criar a coluna "AJUSTE"
        conferencia_folha["AJUSTE"] = conferencia_folha["CDG_PROVDESC"].apply(
            categorizar_rubrica
        )

        conferencia_folha.sort_values(by=["CDG_NAT_DESPESA"])

        if not agrupar:
            return conferencia_folha
        
        conferencia_folha_final = (
            conferencia_folha.groupby(["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "TIPO_DESPESA"])[
                ["PROVENTO", "DESCONTO"]
            ]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        return conferencia_folha_final

    def gerar_proventos(self, conferencia_rgps_final: DataFrame):
        prov_folha = conferencia_rgps_final.loc[
            conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_proventos = prov_folha["PROVENTO"] - \
            prov_folha["DESCONTO"]
        prov_folha = prov_folha.loc[
            :, ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "PROVENTO", "DESCONTO", "TIPO_DESPESA"]
        ].assign(SALDO=coluna_saldo_proventos)

        prov_folha["CDG_NAT_DESPESA"] = prov_folha[
            "CDG_NAT_DESPESA"
        ].str.slice(1)

        prov_folha.sort_values(by=["CDG_NAT_DESPESA"])

        return prov_folha

    def gerar_descontos(self, conferencia_rgps_final: DataFrame):
        desc_folha = conferencia_rgps_final.loc[
            ~conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_descontos = desc_folha["DESCONTO"] - \
            desc_folha["PROVENTO"]

        desc_folha = desc_folha.loc[
            :, ["NME_NAT_DESPESA", "CDG_NAT_DESPESA", "DESCONTO", "PROVENTO", "TIPO_DESPESA"]
        ].assign(SALDO=coluna_saldo_descontos)

        desc_folha.sort_values(by=["CDG_NAT_DESPESA"])

        return desc_folha

    def gerar_saldos(self):
        dados_conferencia = self.gerar_conferencia()
        dados_proventos = self.gerar_proventos(dados_conferencia)
        dados_descontos = self.gerar_descontos(dados_conferencia)

        # Transforma a tabela com os dados de proventos em uma lista
        proventos_list = list(
            zip(dados_proventos["TIPO_DESPESA"], dados_proventos["CDG_NAT_DESPESA"], dados_proventos["SALDO"]))

        # Transforma a tabela com os dados de descontos em uma lista
        descontos_list = list(
            zip(dados_descontos["TIPO_DESPESA"], dados_descontos["CDG_NAT_DESPESA"], dados_descontos["SALDO"]))

        # Faz um dicionário com todos os saldos (proventos e descontos) segmentados pelo tipo do saldo
        saldos_dict = {"ATIVO": {}, "INATIVO": {},
                       "COMPENSATÓRIA": {}, "PENSIONISTA": {}}
        for line in proventos_list + descontos_list:
            saldos_dict[line[0]][line[1]] = line[2]

        # if self.test:
        #     print(dados_conferencia)
            # print(dados_proventos)
            # print(dados_descontos)

        return saldos_dict

    def gerar_folha(self):
        # Função para somar os saldos de uma lista de códigos
        def soma_codigos(codigos: str, dicionario: dict):
            lista_codigos = list(map(str.strip, codigos.split(",")))
            lista_codigos = [c[1:] if c.startswith("33") and len(
                c) == 9 else c for c in lista_codigos]
            resultado = sum(float(dicionario.get(str(c), 0.0))
                            for c in lista_codigos)

            return resultado

        folha_pagamento = self.carregar_template_nl()
        folha_pagamento["VALOR"] = 0.0

        # if self.test:
        #     print(folha_pagamento)

        saldos_dict = self.gerar_saldos()

        # if self.test:
        #     print("\nSaldos:")
        #     print(saldos_dict)
        #     print("\n\n")

        # Calcula o valor para cada linha
        for idx, row in folha_pagamento.iterrows():
            somar = row.get("SOMAR", [])
            subtrair = row.get("SUBTRAIR", [])
            tipo = row.get("TIPO", "")
            if tipo == "nan" or tipo == "":
                tipo = "ATIVO"

            if self.test:
                print(f"\nProcessando linha {idx}:")
                print(f"TIPO           : {tipo}")
                print(f"SOMAR          : {somar}")
                print(f"SUBTRAIR       : {subtrair}")

            if tipo != "MANUAL":
                valor_somar = soma_codigos(somar, saldos_dict[tipo])
                valor_subtrair = soma_codigos(subtrair, saldos_dict[tipo])
                valor = valor_somar - valor_subtrair
                folha_pagamento.at[idx, "VALOR"] = valor
                if self.test:
                    print(
                        f"VALOR calculado: {valor_somar:.2f} - {valor_subtrair:.2f}  = {valor:.2f}")
            else:
                # Coloca um valor pequeno pra abrir a página pro preenchimento manual
                folha_pagamento.at[idx, "VALOR"] = 0.000001
                if self.test:
                    print(
                        f"VALOR DEVE SER PREENCHIDO MANUALMENTE")
                    print()

        folha_pagamento.drop(
            columns=["SOMAR", "SUBTRAIR", "TIPO"], inplace=True)
        folha_pagamento = folha_pagamento.sort_values(by="INSCRIÇÃO")
        folha_pagamento = folha_pagamento[folha_pagamento["VALOR"] > 0]

        return folha_pagamento
