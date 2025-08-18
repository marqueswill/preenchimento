import os
from pandas import DataFrame
from tabula import read_pdf

from drivers.preenchimento_nl import PreenchimentoNL


class BaixaDiaria:
    """Classe para baixar e processar diárias do SIGGO."""

    def __init__(self, run=True, test=False):
        """Inicializa a classe BaixaDiaria."""
        username = os.getlogin().strip()
        self.caminho_raiz = f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\"
        self.run = run
        self.test = test

        self.preenchedor = PreenchimentoNL(run=self.run, test=self.test)

    def obter_caminhos_pdf(self):
        caminho_completo = self.caminho_raiz + \
            f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA\\NE_DIÁRIAS"
        nomes_pdfs = [
            nome for nome in os.listdir(caminho_completo)
            # ignora arquivos temporários
            if (nome.endswith(('.pdf')) or nome.endswith(('.PDF'))) and not nome.startswith('~$')
        ]
        return nomes_pdfs

    def extrair_dados_pdf(self, caminho_pdf: str):
        """Extrai dados de um PDF de diárias."""
        tables = read_pdf(caminho_pdf, pages="all",
                          multiple_tables=True, pandas_options={"header": None})


        processo = tables[0].iloc[3, 2].strip().split(" ")[
            0]  # linha 3, coluna 2
        observacao = ""
        i = 0
        while True:
            # append em observacao até achar "Gestor Administrativo"
            celula1 = str(tables[0].iloc[30+i, 0]).strip()
            celula2 = str(tables[0].iloc[30+i, 1]).strip()
            if "Gestor Administrativo" in celula1:
                break
            observacao += celula1+celula2
            i += 1
        observacao = observacao.split(" ", 2)[2]

        dados:list[dict] = []
        for table in tables:
            nune = table.iloc[1, 2]    # linha 1, coluna 2
            credor = table.iloc[5, 0].split(
                "-")[0].strip()  # linha 5, coluna 0
            fonte = table.iloc[16, 1].split(".")[1]  # linha 16, coluna 1
            valor = float(table.iloc[30, 3].replace(
                ".", "").replace(",", "."))  # linha 13, coluna 3
            natureza = table.iloc[16, 2].strip().split(" ")[
                1]  # linha 16, coluna 2
            subitem = table.iloc[26, 0].strip().split(" ")[
                0]  # linha 26, coluna 0

            dados.append({
                "credor": credor,
                "nune": nune,
                "fonte": fonte,
                "valor": valor,
                "natureza": natureza,
                "subitem": subitem
            })

        return {
            "processo": processo,
            "observacao": observacao,
            "dados": dados
        }

    def gerar_nls(self):
        """_Gera as NLS de diárias a partir dos PDFs na pasta NE_DIÁRIAS._

        Returns:
            _type_: _Retorna um DataFrame com as NLS e um DataFrame com o cabeçalho._
        """
        nl = DataFrame(columns=["EVENTO", "INSCRIÇÃO",
                                "CLASS. CONT", "CLASS. ORC", "FONTE", "VALOR"])
        cabecalho = DataFrame(columns=["Coluna 1", "Coluna 2"])

        caminhos_pdf = self.obter_caminhos_pdf()
        for i, pdf in enumerate(caminhos_pdf):
            # print(pdf)
            caminho_pdf = os.path.join(
                self.caminho_raiz, "SECON - General", "ANO_ATUAL", "NL_AUTOMATICA", "NE_DIÁRIAS", pdf)

            dados_extraidos = self.extrair_dados_pdf(caminho_pdf)

            if i == 0:
                processo = dados_extraidos["processo"]
                observacao = dados_extraidos["observacao"]
                coluna2 = ["F0", "4 - UG/Gestão",
                           "020101-00001", processo, observacao]
                cabecalho["Coluna 2"] = coluna2
                
            for dados in dados_extraidos["dados"]:
                evento1 = "510379"
                evento2 = "520379"
                incricao = dados["nune"]
                classcont1 = "113110105"
                classcont2 = "218910200"
                classorc = str(dados["natureza"]) + str(dados["subitem"])
                fonte = dados["fonte"]
                valor = dados["valor"]

                linha1 = [evento1, incricao, classcont1, classorc, fonte, valor]
                linha2 = [evento2, incricao, classcont2, classorc, fonte, valor]

                nl.loc[len(nl)] = linha1
                nl.loc[len(nl)] = linha2

        nl = nl.sort_values(by=["EVENTO", "INSCRIÇÃO"]).reset_index(drop=True)
        return nl, cabecalho

    def executar(self):
        nl, cabecalho = self.gerar_nls()

        if self.test:
            print(cabecalho["Coluna 2"])
            print(nl)
        if self.run:
            self.preenchedor.executar({"folha": nl, "cabecalho": cabecalho})


baixa = BaixaDiaria(run=True, test=True)
baixa.executar()
