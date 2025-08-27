import os
import re
import PyPDF2
import pandas as pd
from datetime import datetime
from pandas import DataFrame

from drivers.pagamento.services import get_root_paths
from drivers.pagamento.view import ConsoleView
from drivers.preenchimento_nl import PreenchimentoNL
from excel.excel_service import ExcelService

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

# TODO: renomear classe e generalizar para uma classe de Extração de dados de PDFs


class ExtrairDadosR2000:
    """Classe para baixar e processar diárias do SIGGO."""

    def __init__(self, run=True, test=False):
        """Inicializa a classe BaixaDiaria."""
        app_view = ConsoleView()
        app_view.clear_console()
        self.caminho_raiz = get_root_paths()
        self.run = run
        self.test = test
        self.preenchedor = PreenchimentoNL(run=self.run, test=self.test)

        caminho_planilha_template = (
            self.caminho_raiz
            + f"\\SECON - General\\ANO_ATUAL\\EFD-REINF\\Preenchimento Reinf.xlsx"
        )

        caminho_mes_atual = (
            self.caminho_raiz
            + f"\\SECON - General\\ANO_ATUAL\\EFD-REINF\\{MESES[MES_ATUAL] if not self.test else "TESTES"}"
        )

        self.caminho_planilha = caminho_mes_atual + f"\\Preenchimento Reinf.xlsx"
        
        ExcelService.copy_to(caminho_planilha_template, caminho_mes_atual)
        # ExcelService.copy_data_with_pandas(caminho_planilha_template, caminho_mes_atual)

        self.excel_service = ExcelService(self.caminho_planilha)

    def obter_caminhos_pdf(self):
        if self.test:
            caminho_completo = (
                self.caminho_raiz + f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\TESTES"
            )
        else:
            caminho_completo = (
                self.caminho_raiz
                + f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\{MESES[MES_ATUAL]}"
            )
        nomes_pdfs = [
            nome
            for nome in os.listdir(caminho_completo)
            # ignora arquivos temporários
            if (nome.endswith((".pdf")) or nome.endswith((".PDF")))
            and not nome.startswith("~$")
        ]
        return nomes_pdfs

    def extrair_dados_pdf(self, caminho_pdf: str):
        """Extrai dados de um PDF de diárias."""
        # print(caminho_pdf)

        with open(caminho_pdf, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        # print(text)

        # Use a safe way to extract data with regex
        processo_match = re.search(r"PROCESSO Nº : ([\d/]+)", text)
        processo = processo_match.group(1) if processo_match else None

        cnpj_match = re.search(r"CNPJ DO PRESTADOR/FORNCEDOR: ([\d./-]+)", text)
        cnpj = cnpj_match.group(1) if cnpj_match else None

        tipo_servico_match = re.search(r"TIPO DE SERVIÇO: (.*?)[\s\n]", text)
        tipo_servico = (
            tipo_servico_match.group(1).strip() if tipo_servico_match else None
        )

        valor_nf_match = re.search(r"VALOR DA NF: ([\d.,]+) R\$", text)
        valor_nf = (
            valor_nf_match.group(1).replace(".", "").replace(",", ".")
            if valor_nf_match
            else None
        )

        num_nf_match = re.search(r"[\s\n]+([\d.,]+) Emissão:", text)
        num_nf = num_nf_match.group(1).strip() if num_nf_match else None

        data_emissao_match = re.search(r"Emissão: ([\d/]+)", text)
        data_emissao = data_emissao_match.group(1) if data_emissao_match else None

        serie_match = re.search(r"Série: ([\d]+)", text)
        serie = serie_match.group(1).strip() if serie_match else None

        tipo_inss_match = re.search(r"TIPO DE SERVIÇO INSS: ([\d]+)", text)
        tipo_inss = tipo_inss_match.group(1).strip() if tipo_inss_match else None

        base_calculo_inss_match = re.search(
            r"BASE DE CÁLCULO INSS: ([\d.,]+) R\$", text
        )
        base_calculo_inss = (
            base_calculo_inss_match.group(1).replace(".", "").replace(",", ".")
            if base_calculo_inss_match
            else None
        )

        valor_inss_retido_match = re.search(
            r"VALOR DE INSS RETIDO: ([\d.,]+) R\$", text
        )
        valor_inss_retido = (
            valor_inss_retido_match.group(1).replace(".", "").replace(",", ".")
            if valor_inss_retido_match
            else None
        )

        cprb_match = re.search(r"EMPRESA É CONTRIBUINTE DA CPRB\? ([\w])", text)
        cprb = cprb_match.group(1) if cprb_match else None

        dados_pdf = {
            "PROCESSO": processo,
            "CNPJ": (
                str(cnpj.replace(".", "").replace("/", "").replace("-", ""))
                if cnpj
                else None
            ),
            "TIPO_SERVICO": tipo_servico,
            "VALOR_NF": float(valor_nf) if valor_nf else None,
            "NUM_NF": num_nf.replace(".", "") if num_nf else None,
            "DATA_EMISSAO": (
                datetime.strptime(data_emissao, "%d/%m/%Y").date()
                if data_emissao
                else None
            ),
            "SERIE": serie,
            "TIPO_INSS": tipo_inss,
            "BASE_CALCULO_INSS": (
                float(base_calculo_inss) if base_calculo_inss else None
            ),
            "VALOR_INSS_RETIDO": (
                float(valor_inss_retido) if valor_inss_retido else None
            ),
            "CPRB": 0 if cprb == "N" else 1,
        }

        # print(dados_pdf)
        # if cprb != "N":
        #     return None
        if valor_inss_retido and cnpj:
            return dados_pdf
        else:
            return None

    def gerar_dataframes_reinf(self, df_principal):
        """
        Preenche os DataFrames R-2010-1 e R-2010-2 a partir de um DataFrame principal.
        """
        # Ordena o DataFrame principal, conforme a sua lógica
        if not df_principal.empty:
            df_principal = df_principal.sort_values(by=["CNPJ", "NUM_NF"])
        else:
            print("O DataFrame principal está vazio, não há dados para preencher.")
            return None, None

        # Inicializa os DataFrames R-2010-1 e R-2010-2
        df_r2010_1 = DataFrame(
            columns=[
                "LINHA",
                "REGISTRO",
                "NRINSCESTABTOM",
                "CNPJPRESTADOR",
                "INDOBRA",
                "INDCPRB",
                "NUMDOCTO",
                "SERIE",
                "DTEMISSAONF",
                "VLRBRUTO",
                "OBS",
                "MÊS",
            ]
        )
        df_r2010_2 = DataFrame(
            columns=[
                "LINHA",
                "REGISTRO",
                "TPSERVICO",
                "VLRBASERET",
                "VLRRETENCAO",
                "VLRRETSUB",
                "VLRNRETPRINC",
                "VLRSERVICOS15",
                "VLRSERVICOS20",
                "VLRSERVICOS25",
                "VLRADICIONAL",
                "VLRNRETADIC",
            ]
        )

        # O seu CNPJ de tomador fixo
        cnpj_tomador = "00534560000126"
        # Acumula as linhas em listas
        linhas_r2010_1 = []
        linhas_r2010_2 = []
        # Itera sobre as linhas do DataFrame principal para preencher os novos DFs
        for i, dados in df_principal.iterrows():
            # Preenche a linha para df_r2010_1
            nova_linha_r2010_1 = {
                "LINHA": i + 1,
                "REGISTRO": "R-2010-1",
                "NRINSCESTABTOM": cnpj_tomador,
                "CNPJPRESTADOR": dados["CNPJ"],
                "INDOBRA": 0,
                "INDCPRB": dados["CPRB"],
                "NUMDOCTO": dados["NUM_NF"],
                "SERIE": dados["SERIE"],
                "DTEMISSAONF": dados["DATA_EMISSAO"],
                "VLRBRUTO": dados["VALOR_NF"],
                "OBS": dados["PROCESSO"],
                "MÊS": (
                    int(dados["DATA_EMISSAO"].month)
                    if pd.notnull(dados["DATA_EMISSAO"])
                    else None
                ),
            }
            linhas_r2010_1.append(nova_linha_r2010_1)

            # Preenche a linha para df_r2010_2
            nova_linha_r2010_2 = {
                "LINHA": i + 1,
                "REGISTRO": "R-2010-2",
                # Usando o tipo de serviço INSS
                "TPSERVICO": dados["TIPO_INSS"],
                "VLRBASERET": dados["BASE_CALCULO_INSS"],
                "VLRRETENCAO": dados["VALOR_INSS_RETIDO"],
                "VLRRETSUB": 0,
                "VLRNRETPRINC": 0,
                "VLRSERVICOS15": 0,
                "VLRSERVICOS20": 0,
                "VLRSERVICOS25": 0,
                "VLRADICIONAL": 0,
                "VLRNRETADIC": 0,
            }
            linhas_r2010_2.append(nova_linha_r2010_2)

        df_r2010_1 = DataFrame(
            linhas_r2010_1,
            columns=[
                "LINHA",
                "REGISTRO",
                "NRINSCESTABTOM",
                "CNPJPRESTADOR",
                "INDOBRA",
                "INDCPRB",
                "NUMDOCTO",
                "SERIE",
                "DTEMISSAONF",
                "VLRBRUTO",
                "OBS",
                "MÊS",
            ],
        )
        df_r2010_2 = DataFrame(
            linhas_r2010_2,
            columns=[
                "LINHA",
                "REGISTRO",
                "TPSERVICO",
                "VLRBASERET",
                "VLRRETENCAO",
                "VLRRETSUB",
                "VLRNRETPRINC",
                "VLRSERVICOS15",
                "VLRSERVICOS20",
                "VLRSERVICOS25",
                "VLRADICIONAL",
                "VLRNRETADIC",
            ],
        )

        print("DataFrame R-2010-1:")
        print(df_r2010_1)

        print("\nDataFrame R-2010-2:")
        print(df_r2010_2)

        return df_r2010_1, df_r2010_2

    def executar(self):
        caminhos_pdf = self.obter_caminhos_pdf()

        lista_de_dados = []
        for pdf in caminhos_pdf:

            if self.test:
                caminho_pdf = (
                    self.caminho_raiz
                    + f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\TESTES"
                    + f"\\{pdf}"
                )
            else:
                caminho_pdf = (
                    self.caminho_raiz
                    + f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\{MESES[MES_ATUAL]}"
                    + f"\\{pdf}"
                )

            dados_extraidos = self.extrair_dados_pdf(caminho_pdf)

            if dados_extraidos:
                lista_de_dados.append(dados_extraidos)

        if lista_de_dados:
            df = DataFrame(lista_de_dados)
            df = df.sort_values(by=["CNPJ", "NUM_NF"]).reset_index(drop=True)

        # print(df)

        df_r2010_1, df_r2010_2 = self.gerar_dataframes_reinf(df)

        # Procurar correspondências na tabela da aba VALIDAÇÃO_BD
        # usar CNPJ.NUM_NF para tabela validacao, CNPJPRESTADOR.NUMDOCTO para R-2010-1
        # colunas validacao:  CNPJ/CPF, NUMERO DA NF, NUMERO DE SERIE, DATA DE LANÇAMENTO, DATA EMISSAO NF, NUMERO DO PROCESSO, VALOR
        planilha_validacao = (
            self.excel_service.get_sheet("VALIDAÇÃO_BD", as_dataframe=True)
            .iloc[:, :6]
            .dropna(subset=["CNPJ/CPF"])
        )

        # print(planilha_validacao)

        # Adicionar a coluna 'CORRESPONDENCIA' A R-2010-1 COM VALORES BOOLEANOS PARA IDENTIFICAR CORRESPONDÊNCIAS

        # Criar uma chave de busca unificada na planilha de validação
        planilha_validacao["CHAVE_BUSCA"] = (
            planilha_validacao["CNPJ/CPF"].astype(str)
            + "."
            + planilha_validacao["NUMERO DA NF"].astype(str)
        )

        # Criar uma chave de busca unificada no DataFrame R-2010-1
        # Assumindo que df_r2010_1 é um DataFrame já disponível no escopo da função
        df_r2010_1["IDENTIFICADOR CNPJ-NF"] = (
            df_r2010_1["CNPJPRESTADOR"].astype(str)
            + "."
            + df_r2010_1["NUMDOCTO"].astype(str)
        )

        # Adicionar a coluna 'CORRESPONDENCIA' verificando se a chave de R-2010-1 existe na planilha de validação
        df_r2010_1["CORRESPONDENCIA"] = df_r2010_1["IDENTIFICADOR CNPJ-NF"].isin(
            planilha_validacao["CHAVE_BUSCA"]
        )


        # O DataFrame df_r2010_1 agora tem a coluna 'CORRESPONDENCIA'
        self.exportar_para_planilha(df_r2010_1, "R-2010-1")
        self.exportar_para_planilha(df_r2010_2, "R-2010-2")

    def exportar_para_planilha(self, df, aba):
        """
        Exporta um DataFrame para uma planilha Excel específica.

        Args:
            df (DataFrame): O DataFrame a ser exportado.
            aba (str): O nome da aba na qual os dados serão escritos.
            caminho_planilha (str): O caminho completo para o arquivo Excel.
        """

        numero_linhas = len(df)

        # Cria uma instância de ExcelService

        self.excel_service.delete_rows(aba, 4)

        # Escreva os valores nas abas R-2010-1 e R-2010-2 da planilha a partir da linha 4
        self.excel_service.exportar_para_planilha(
            table=df,
            sheet_name=aba,
            start_line="4",  # Inicia a escrita a partir da linha 4
            clear=False,  # Não limpa a planilha antes de escrever
            write_headers=False,
            fit_columns=False,
        )


baixa = ExtrairDadosR2000(run=False, test=True)
baixa.executar()
