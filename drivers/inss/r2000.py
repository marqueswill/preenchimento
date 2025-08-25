from datetime import datetime
import os
from pandas import DataFrame
from tabula import read_pdf
import PyPDF2
import re

from drivers.pagamento.services import get_root_paths
from drivers.pagamento.view import ConsoleView
from drivers.preenchimento_nl import PreenchimentoNL

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


class BaixaDiaria:
    """Classe para baixar e processar diárias do SIGGO."""

    def __init__(self, run=True, test=False):
        """Inicializa a classe BaixaDiaria."""
        app_view = ConsoleView()
        app_view.clear_console()
        self.caminho_raiz = get_root_paths()
        self.run = run
        self.test = test
        self.preenchedor = PreenchimentoNL(run=self.run, test=self.test)

    def obter_caminhos_pdf(self):
        if self.test:
            caminho_completo = self.caminho_raiz + \
                f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\TESTES"
        else:
            caminho_completo = self.caminho_raiz + \
                f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\{MESES[MES_ATUAL]}"
        nomes_pdfs = [
            nome for nome in os.listdir(caminho_completo)
            # ignora arquivos temporários
            if (nome.endswith(('.pdf')) or nome.endswith(('.PDF'))) and not nome.startswith('~$')
        ]
        return nomes_pdfs

    def extrair_dados_pdf(self, caminho_pdf: str):
        """Extrai dados de um PDF de diárias."""
        # print(caminho_pdf)

        with open(caminho_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text()

        # print(text)

        # Use a safe way to extract data with regex
        processo_match = re.search(r'PROCESSO Nº : ([\d/]+)', text)
        processo = processo_match.group(1) if processo_match else None

        cnpj_match = re.search(
            r'CNPJ DO PRESTADOR/FORNCEDOR: ([\d./-]+)', text)
        cnpj = cnpj_match.group(1) if cnpj_match else None

        tipo_servico_match = re.search(r'TIPO DE SERVIÇO: (.*?)[\s\n]', text)
        tipo_servico = tipo_servico_match.group(
            1).strip() if tipo_servico_match else None

        valor_nf_match = re.search(r'VALOR DA NF: ([\d.,]+) R\$', text)
        valor_nf = valor_nf_match.group(1).replace(
            '.', '').replace(',', '.') if valor_nf_match else None

        num_nf_match = re.search(r'[\s\n]+([\d.,]+) Emissão:', text)
        num_nf = num_nf_match.group(1).strip() if num_nf_match else None

        data_emissao_match = re.search(r'Emissão: ([\d/]+)', text)
        data_emissao = data_emissao_match.group(
            1) if data_emissao_match else None

        serie_match = re.search(r'Série: ([\d]+)', text)
        serie = serie_match.group(1).strip() if serie_match else None

        tipo_inss_match = re.search(r'TIPO DE SERVIÇO INSS: ([\d]+)', text)
        tipo_inss = tipo_inss_match.group(
            1).strip() if tipo_inss_match else None

        base_calculo_inss_match = re.search(
            r'BASE DE CÁLCULO INSS: ([\d.,]+) R\$', text)
        base_calculo_inss = base_calculo_inss_match.group(1).replace(
            '.', '').replace(',', '.') if base_calculo_inss_match else None

        valor_inss_retido_match = re.search(
            r'VALOR DE INSS RETIDO: ([\d.,]+) R\$', text)
        valor_inss_retido = valor_inss_retido_match.group(1).replace(
            '.', '').replace(',', '.') if valor_inss_retido_match else None

        cprb_match = re.search(
            r'EMPRESA É CONTRIBUINTE DA CPRB\? ([\w])', text)
        cprb = cprb_match.group(1) if cprb_match else None

        dados_pdf = {
            "PROCESSO": processo,
            "CNPJ": str(cnpj.replace(".", "").replace("/", "").replace("-", "")) if cnpj else None,
            "TIPO_SERVICO": tipo_servico,
            "VALOR_NF": float(valor_nf) if valor_nf else None,
            "NUM_NF": num_nf.replace('.', '') if num_nf else None,
            "DATA_EMISSAO": data_emissao,
            "SERIE": serie,
            "TIPO_INSS": tipo_inss,
            "BASE_CALCULO_INSS": base_calculo_inss,
            "VALOR_INSS_RETIDO": valor_inss_retido,
            "CPRB": cprb
        }

        # print(dados_pdf)
        # if cprb != "N":
        #     return None
        if valor_inss_retido and cnpj:
            return dados_pdf
        else:
            return None

    def salvar_dados_excel(self):
        caminhos_pdf = self.obter_caminhos_pdf()

        lista_de_dados = []
        for pdf in caminhos_pdf:

            if self.test:
                caminho_pdf = self.caminho_raiz + \
                    f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\TESTES" + \
                    f"\\{pdf}"
            else:
                caminho_pdf = self.caminho_raiz + \
                    f"SECON - General\\ANO_ATUAL\\LIQ_DESPESA\\{MESES[MES_ATUAL]}" + f"\\{pdf}"

            dados_extraidos = self.extrair_dados_pdf(caminho_pdf)

            if dados_extraidos:
                lista_de_dados.append(dados_extraidos)

        if lista_de_dados:
            df = DataFrame(lista_de_dados)
            df = df.sort_values(by=["CNPJ", "NUM_NF"]).reset_index(drop=True)

        print(df)
        caminho_planilha = self.caminho_raiz + \
            f"\\SECON - General\\ANO_ATUAL\\EFD-REINF\\Preenchimento Reinf.xlsx"
        # Apagar linhas da linha 4 em diante das abas R-2010-1 e R-2010-2

        df_r2010_1, df_r2010_2 = self.preencher_dataframes_reinf(df)

        # Escreva os valores nas abas R-2010-1 e R-2010-2 da planilha a partir da linha 4

    def preencher_dataframes_reinf(self, df_principal):
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
        df_r2010_1 = DataFrame(columns=[
            "LINHA", "REGISTRO", "NRINSCESTABTOM", "CNPJPRESTADOR", "INDOBRA", "INDCPRB", "NUMDOCTO", "SERIE", "DTEMISSAONF", "VLRBRUTO", "OBS"
        ])
        df_r2010_2 = DataFrame(columns=[
            "LINHA", "REGISTRO", "TPSERVICO", "VVLRBASERET", "VLRRETENCAO", "VLRRETSUB", "VLRNRETPRINC",
            "VLRSERVICOS15", "VLRSERVICOS20", "VLRSERVICOS25", "VLRADICIONAL", "VLRNRETADIC"
        ])

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
                "INDOBRA": '0',
                "INDCPRB": dados["CPRB"],
                "NUMDOCTO": dados["NUM_NF"],
                "SERIE": dados["SERIE"],
                "DTEMISSAONF": dados["DATA_EMISSAO"],
                "VLRBRUTO": dados["VALOR_NF"],
                "OBS": dados["PROCESSO"]
            }
            linhas_r2010_1.append(nova_linha_r2010_1)

            # Preenche a linha para df_r2010_2
            nova_linha_r2010_2 = {
                "LINHA": i + 1,
                "REGISTRO": "R-2010-2",
                # Usando o tipo de serviço INSS
                "TPSERVICO": dados["TIPO_INSS"],
                "VVLRBASERET": dados["BASE_CALCULO_INSS"],
                "VLRRETENCAO": dados["VALOR_INSS_RETIDO"],
                "VLRRETSUB": 0,
                "VLRNRETPRINC": 0,
                "VLRSERVICOS15": 0,
                "VLRSERVICOS20": 0,
                "VLRSERVICOS25": 0,
                "VLRADICIONAL": 0,
                "VLRNRETADIC": 0
            }
            linhas_r2010_2.append(nova_linha_r2010_2)

        df_r2010_1 = DataFrame(linhas_r2010_1, columns=[
            "LINHA", "REGISTRO", "NRINSCESTABTOM", "CNPJPRESTADOR", "INDOBRA", "INDCPRB", "NUMDOCTO", "SERIE", "DTEMISSAONF", "VLRBRUTO", "OBS"
        ])
        df_r2010_2 = DataFrame(linhas_r2010_2, columns=[
            "LINHA", "REGISTRO", "TPSERVICO", "VVLRBASERET", "VLRRETENCAO", "VLRRETSUB", "VLRNRETPRINC",
            "VLRSERVICOS15", "VLRSERVICOS20", "VLRSERVICOS25", "VLRADICIONAL", "VLRNRETADIC"
        ])

        print("DataFrame R-2010-1:")
        print(df_r2010_1)

        print("\nDataFrame R-2010-2:")
        print(df_r2010_2)

        return df_r2010_1, df_r2010_2

    def executar(self):
        self.salvar_dados_excel()

        # if self.test:
        #     print(cabecalho["Coluna 2"])
        #     print(nl)
        # if self.run:
        #     self.preenchedor.executar({"folha": nl, "cabecalho": cabecalho})


baixa = BaixaDiaria(run=False, test=True)
baixa.executar()
