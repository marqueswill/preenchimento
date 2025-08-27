import os
import locale
import pandas as pd
import numpy as np
from datetime import datetime
from pandas import DataFrame

# Importa as classes de serviço que contêm a lógica de negócio
from drivers.pagamento.view import ConsoleView
from drivers.preenchimento_nl import PreenchimentoNL
from excel.excel_service import ExcelService

# Define a configuração regional para datas e horários em português
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    # Se falhar, tenta uma localidade comum para Windows
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')

ANO_ATUAL = datetime.now().year
MES_ATUAL = datetime.now().month

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

view = ConsoleView()


def get_root_paths() -> str:
    """
    Determina o caminho correto para o arquivo de template,
    verificando se o usuário está usando o caminho base ou o do OneDrive.
    """
    username = os.getlogin().strip()
    caminho_base = f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\"
    caminho_onedrive = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"

    if os.path.exists(caminho_base):
        caminho_raiz = caminho_base
    elif os.path.exists(caminho_onedrive):
        caminho_raiz = caminho_onedrive
    else:
        raise FileNotFoundError(
            f"Não foi possível encontrar o caminho base ou do OneDrive para o usuário {username}."
        )

    return caminho_raiz


def get_template_paths(tipo_folha: str) -> str:
    """
    Determina o caminho correto para o arquivo de template,
    verificando se o usuário está usando o caminho base ou o do OneDrive.
    """
    caminho_raiz = get_root_paths()
    return f"{caminho_raiz}SECON - General\\CÓDIGOS\\TEMPLATES_NL_{tipo_folha.upper()}.xlsx"


def get_template_names(tipo_folha: str) -> str:
    caminho_completo = get_template_paths(tipo_folha)
    excel_file = pd.ExcelFile(caminho_completo)
    nomes_templates = excel_file.sheet_names
    return nomes_templates


class GeradorFolhaPagamento:
    """_summary_
    Classe para gerar NLs das folhas de pagamento. Ela lida com os templates, carregamento de dados e geração das folhas.
    """

    nome_template: str
    cod_fundo: int

    def __init__(self, nome_fundo: str, nome_template: str, test=False):
        """_summary_
        Inicializa a classe GeradorFolhaPagamento.
        Args:
            nome_fundo (str): _description_ - deve ser um dos seguintes: "rgps", "financeiro", "capitalizado", "inativo", "pensão".
            nome_template (str): _description_ - deve ser igual a um dos nomes de template disponíveis no arquivo de templates.
            test (bool, optional): _description_. Defaults to False. - se True, imprime os dados no console para teste.
        Raises:
        """

        cod_fundos = {
            "rgps": 1,
            "financeiro": 2,
            "capitalizado": 3,
            "inativo": 4,
            "pensão": 5,
        }

        self.caminho_raiz = get_root_paths()
        self.cod_fundo = cod_fundos[nome_fundo.lower()]
        self.nome_fundo = nome_fundo.lower()
        self.nome_template = nome_template
        self.test = test

    def carregar_planilha(self, caminho_planilha):
        caminho_completo = self.caminho_raiz + caminho_planilha
        dataframe = pd.read_excel(caminho_completo)
        return dataframe

    def carregar_template_nl(self):
        caminho_completo = get_template_paths(self.nome_fundo)

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=self.nome_template,
            usecols="A:I",
            dtype=str,
        ).astype(str)

        dataframe["CLASS. ORC"] = (
            dataframe["CLASS. ORC"]
            .apply(lambda x: x[1:] if len(x) == 9 else x)
            .astype(str)
        )

        return dataframe

    def carregar_template_cabecalho(self):
        caminho_completo = (
            self.caminho_raiz
            + f"SECON - General\\CÓDIGOS\\TEMPLATES_NL_{self.nome_fundo.upper()}.xlsx"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=None,
            sheet_name=self.nome_template,
            usecols="A:I",
        ).astype(str)

        return dataframe

    def gerar_conferencia(self, agrupar=True, adiantamento_ferias=False):
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
            f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}",
        )

        caminho_completo = caminho_pasta + "\\DEMOFIN_TABELA.xlsx"

        # Lê a planilha com o nome da aba "DEMOFIN - T"
        tabela_demofin = pd.read_excel(
            caminho_completo, sheet_name="DEMOFIN - T", header=1
        )

        # Remove "." dos códigos
        tabela_demofin["CDG_NAT_DESPESA"] = tabela_demofin[
            "CDG_NAT_DESPESA"
        ].str.replace(".", "")

        # Filtra a tabela para o fundo específico
        filtro_fundo = tabela_demofin["CDG_FUNDO"] == self.cod_fundo

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
        plan_folha["RUBRICA"] = plan_folha.apply(cria_coluna_rubrica, axis=1)
        plan_folha["TIPO_DESPESA"] = plan_folha.apply(cria_coluna_tipo, axis=1)

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
                ["CDG_PROVDESC", "NME_NAT_DESPESA",
                    "CDG_NAT_DESPESA", "TIPO_DESPESA"]
            )[["PROVENTO", "DESCONTO"]]
            .agg(lambda x: np.sum(np.abs(x)))
            .reset_index()
        )

        # Aplica a função pra criar a coluna "AJUSTE"
        conferencia_folha["AJUSTE"] = conferencia_folha["CDG_PROVDESC"].apply(
            categorizar_rubrica
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

    def gerar_proventos(self, conferencia_rgps_final: DataFrame):
        prov_folha = conferencia_rgps_final.loc[
            conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_proventos = prov_folha["PROVENTO"] - \
            prov_folha["DESCONTO"]
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

    def gerar_descontos(self, conferencia_rgps_final: DataFrame):
        desc_folha = conferencia_rgps_final.loc[
            ~conferencia_rgps_final["CDG_NAT_DESPESA"].str.startswith("3")
        ]

        coluna_saldo_descontos = desc_folha["DESCONTO"] - \
            desc_folha["PROVENTO"]

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

    def gerar_saldos(self):
        dados_conferencia = self.gerar_conferencia()
        dados_conferencia_ferias = self.gerar_conferencia(
            adiantamento_ferias=True)
        dados_proventos = self.gerar_proventos(dados_conferencia)
        dados_descontos = self.gerar_descontos(dados_conferencia)

        # Transforma a tabela com os dados de proventos em uma lista
        saldos_proventos = list(
            zip(
                dados_proventos["TIPO_DESPESA"],
                dados_proventos["CDG_NAT_DESPESA"],
                dados_proventos["SALDO"],
            )
        )

        # Transforma a tabela com os dados de descontos em uma lista
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
        saldos_dict = {
            "ATIVO": {},
            "INATIVO": {},
            "COMPENSATÓRIA": {},
            "PENSIONISTA": {},
            "PROVENTO ADIANTAMENTO FÉRIAS": {},
            "DESCONTO ADIANTAMENTO FÉRIAS": {},
        }

        for line in saldos_proventos + saldos_descontos:
            saldos_dict[line[0]][line[1]] = line[2]
        for line in proventos_ferias:
            saldos_dict["PROVENTO ADIANTAMENTO FÉRIAS"][line[1]] = line[2]
        for line in descontos_ferias:
            saldos_dict["DESCONTO ADIANTAMENTO FÉRIAS"][line[1]] = line[2]

        return saldos_dict

    def gerar_folha(self):
        # Função para somar os saldos de uma lista de códigos
        def soma_codigos(codigos: str, dicionario: dict):
            lista_codigos = list(map(str.strip, codigos.split(",")))
            lista_codigos = [
                c[1:] if c.startswith("33") and len(c) == 9 else c
                for c in lista_codigos
            ]
            resultado = sum(float(dicionario.get(str(c), 0.0))
                            for c in lista_codigos)

            return resultado

        print()
        print("*" * 50)
        print("Gerando folha de pagamento com base no template:", self.nome_template)
        folha_pagamento = self.carregar_template_nl()
        folha_pagamento["VALOR"] = 0.0

        saldos_dict = self.gerar_saldos()

        # Calcula o valor para cada linha
        for idx, row in folha_pagamento.iterrows():
            class_orc = row.get("CLASS. ORC", "")
            class_cont = row.get("CLASS. CONT", "")
            somar = row.get("SOMAR", [])
            subtrair = row.get("SUBTRAIR", [])
            tipo = "ATIVO" if row.get("TIPO", "") in {
                "", "nan"} else row.get("TIPO", "")

            if tipo == "MANUAL":
                # Coloca um valor pequeno pra abrir a página pro preenchimento manual
                folha_pagamento.at[idx, "VALOR"] = 0.000001
                if self.test:
                    ConsoleView.color_print(
                        f"VALOR DEVE SER PREENCHIDO MANUALMENTE",
                        color="yellow",
                        style="bold",
                    )
                    print()
            else:
                valor_somar = soma_codigos(somar, saldos_dict[tipo])
                valor_subtrair = soma_codigos(subtrair, saldos_dict[tipo])
                valor = valor_somar - valor_subtrair
                folha_pagamento.at[idx, "VALOR"] = valor
                # TODO:mover isso pra uma view
                if self.test and valor != 0 and False:
                    print(f"\nLINHA {idx}: {class_orc} / {class_cont}")
                    print(f"TIPO     : {tipo}")
                    print(f"SOMAR    : {somar}".replace("nan", ""))
                    print(f"SUBTRAIR : {subtrair}".replace("nan", ""))
                    print(
                        f"CALCULO  : "
                        + color_text(f"{locale.currency(valor_somar)}".replace('.', ','), "green")
                        + " - "
                        + color_text(f"{locale.currency(valor_subtrair)}".replace('.', ','), "red")
                        + " = "
                        + color_text(f"{locale.currency(valor)}".replace('.', ','), "green", "underline"))

        folha_pagamento.drop(
            columns=["SOMAR", "SUBTRAIR", "TIPO"], inplace=True)

        folha_pagamento = folha_pagamento[folha_pagamento["VALOR"] > 0]
        if self.test:
            if folha_pagamento.empty:
                print()
                ConsoleView.color_print(
                    "FOLHA VAZIA", color="yellow", style="bold")
            else:
                print()
                print(folha_pagamento)
        folha_pagamento = folha_pagamento.sort_values(by="INSCRIÇÃO")

        return folha_pagamento


class FolhaPagamentoService:
    """
    Camada de serviço do Model para orquestrar a geração e o processamento
    dos dados da folha de pagamento.
    """

    def __init__(self, nome_fundo: str, nome_template: list[str] | str, run=True, test=False):
        self.nome_fundo = nome_fundo.lower()
        self.nome_template = nome_template
        self.run = run
        self.test = test
        self.preenchedor = PreenchimentoNL(run, test)

    def gerar_folhas(self):
        """Gera as folhas de pagamento a partir dos templates selecionados."""
        if not isinstance(self.nome_template, list):
            nomes_templates = [self.nome_template]
        else:
            nomes_templates = self.nome_template

        # Instancia a classe FolhaPagamento, que é parte do Model
        folhas = [GeradorFolhaPagamento(nome_fundo=self.nome_fundo, nome_template=nome_template, test=self.test)
                  for nome_template in nomes_templates]

        folhas_pagamento_data = []
        for folha in folhas:
            folha_gerada = folha.gerar_folha()
            cabecalho = folha.carregar_template_cabecalho()
            folhas_pagamento_data.append({
                "folha": folha_gerada,
                "cabecalho": cabecalho
            })
        return folhas_pagamento_data

    def preencher_nl(self, folhas_pagamento_data):
        """Executa o preenchimento dos NLs se o modo 'run' estiver ativado."""
        if self.run and not self.test:
            self.preenchedor.executar(folhas_pagamento_data)


class ConferenciaService:
    def __init__(self, nome_fundo: str, test=False):
        self.caminho_raiz = get_root_paths()
        self.nome_template = "CONFERÊNCIA"
        self.nome_fundo = nome_fundo.upper()
        if test:
            caminho_arquivo_excel = self.caminho_raiz + \
                f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{MESES[MES_ATUAL]}\\CONFERÊNCIA_{self.nome_fundo}.xlsx"
        else:
            caminho_arquivo_excel = self.caminho_raiz + \
                f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\TESTES\\CONFERÊNCIA_{self.nome_fundo}.xlsx"

        self.excel_service = ExcelService(caminho_arquivo_excel)

    def exportar_conferencia(self):
        folha_pagamento = GeradorFolhaPagamento(
            self.nome_fundo.lower(), "PRINCIPAL", test=True)

        dados_conferencia_financeiro = folha_pagamento.gerar_conferencia()

        proventos_folha = folha_pagamento.gerar_proventos(
            dados_conferencia_financeiro)
        descontos_folha = folha_pagamento.gerar_descontos(
            dados_conferencia_financeiro)

        # Exporta proventos na coluna A
        self.excel_service.exportar_para_planilha(
            proventos_folha, self.nome_template, clear=True)

        # Exporta descontos na coluna G
        self.excel_service.exportar_para_planilha(
            descontos_folha, self.nome_template, start_column="H", clear=False
        )

        # Calcula os totais
        total_proventos = (
            proventos_folha["PROVENTO"].sum(
            ) + descontos_folha["PROVENTO"].sum()
        )
        total_descontos = (
            proventos_folha["DESCONTO"].sum(
            ) + descontos_folha["DESCONTO"].sum()
        )
        total_liquido = total_proventos - total_descontos
        totais = DataFrame(
            {
                "TOTAIS": ["PROVENTOS", "DESCONTOS", "LÍQUIDO_FINANCEIRO"],
                "VALOR": [total_proventos, total_descontos, total_liquido],
            }
        )

        ultima_linha = len(descontos_folha) + 3

        # Exporta os totais abaixo dos dados
        self.excel_service.exportar_para_planilha(
            totais,
            self.nome_template,
            start_column="H",
            start_line=str(ultima_linha),
            clear=False,
        )

    def exportar_adiantamento_ferias(self):
        folha_pagamento = GeradorFolhaPagamento(
            self.nome_fundo, "PRINCIPAL", test=True)
        df = folha_pagamento.gerar_conferencia(agrupar=False)

        df = df[df["AJUSTE"] == "ADIANTAMENTO FÉRIAS"]
        self.excel_service.exportar_para_planilha(df, "ADIANTAMENTO_FÉRIAS")

    def exportar_nls(self):
        caminho_raiz = self.caminho_raiz + f"SECON - General\\CÓDIGOS\\"

        excel_rgps = pd.ExcelFile(
            caminho_raiz + "TEMPLATES_NL_RGPS.xlsx")
        templates_rgps = excel_rgps.sheet_names

        excel_financeiro = pd.ExcelFile(
            caminho_raiz + "TEMPLATES_NL_FINANCEIRO.xlsx")
        templates_financeiro = excel_financeiro.sheet_names

        excel_capitalizado = pd.ExcelFile(
            caminho_raiz + "TEMPLATES_NL_CAPITALIZADO.xlsx")
        templates_capitalizado = excel_capitalizado.sheet_names

        nomes_templates = {
            "RGPS": templates_rgps,
            "FINANCEIRO": templates_financeiro,
            "CAPITALIZADO": templates_capitalizado
        }

        # print(nomes_templates)

        drivers_pagamento = [
            GeradorFolhaPagamento(self.nome_fundo.lower(), nome_template, test=True) for nome_template in nomes_templates[self.nome_fundo]
        ]

        nls = {
            driver.nome_template: driver.gerar_folha() for driver in drivers_pagamento
        }

        print(nls.keys())
        for sheet_name, table_data in nls.items():
            print(f"Exportando {sheet_name}...")
            # print(table_data.head())
            self.excel_service.exportar_para_planilha(table_data, sheet_name)

    def destacar_linhas(self, sheet_name: str, cor_fundo="FF9999", negrito=True):
        # Usa o serviço de Excel para destacar linhas
        self.excel_service.destacar_linhas(
            sheet_name, cor_fundo, negrito, coluna_alvo="CDG_NAT_DESPESA", valor_alvo="31901157")

    def executar(self):
        self.exportar_conferencia()
        self.exportar_nls()

        if self.nome_fundo == "RGPS":
            self.exportar_adiantamento_ferias()
            
        
        # formato_monetario = '_-R$ * #,##0.00_-;-R$ * #,##0.00_-;_-R$ * "-"??_-;_-@_-'
        #     # if col_name.upper() in {"VALOR", "TOTAL", "SALDO", "DESCONTO", "PROVENTO"} and isinstance(value, (int, float)):
        #     #     cell.number_format = '_-R$ * #,##0.00_-;-R$ * #,##0.00_-;_-R$ * "-"??_-;_-@_-'

        #     self.apply_format()
        
        self.destacar_linhas(sheet_name="CONFERÊNCIA")


