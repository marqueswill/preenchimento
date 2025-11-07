import sys
import pandas as pd

import os
import locale
from datetime import datetime

from drivers.preenchimento_nl import PreenchimentoNL
from drivers.view import ConsoleView

locale.setlocale(locale.LC_TIME, "pt_BR.utf8")

TESTE = False
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


def get_root_paths() -> str:
    """
    Determina o caminho correto para o arquivo de template,
    verificando se o usuário está usando o caminho base ou o do OneDrive.
    """
    username = os.getlogin().strip()
    caminho_base = f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\"
    caminho_onedrive = (
        f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"
    )

    if os.path.exists(caminho_base):
        caminho_raiz = caminho_base
    elif os.path.exists(caminho_onedrive):
        caminho_raiz = caminho_onedrive
    else:
        raise FileNotFoundError(
            f"Não foi possível encontrar o caminho base ou do OneDrive para o usuário {username}."
        )

    return caminho_raiz


class NLAutomatica:
    """_summary_ Classe que pega NLs da planilha de templates e utiliza o driver PreenchimentoNL para preencher os dados na plataforma."""

    def __init__(self, run=True, test=False):

        self.caminho_raiz = get_root_paths()
        self.run = run
        self.test = test

    def carregar_nl(self, nome_planilha: str, nome_aba: str):
        print(f"Carregando NL: {nome_planilha} - {nome_aba}")
        caminho_completo = (
            self.caminho_raiz
            + f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA\\{nome_planilha}"
        )

        dataframe = pd.read_excel(
            caminho_completo,
            header=6,
            sheet_name=nome_aba,
            usecols="A:F",
        ).astype(str)

        dataframe["CLASS. ORC"] = (
            dataframe["CLASS. ORC"]
            .apply(lambda x: x[1:] if len(x) == 9 else x)
            .astype(str)
        )

        return dataframe

    def carregar_cabecalho(self, nome_planilha: str, nome_aba: str):
        try:
            caminho_completo = (
                self.caminho_raiz
                + f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA\\{nome_planilha}"
            )

            dataframe = pd.read_excel(
                caminho_completo,
                header=None,
                sheet_name=nome_aba,
                usecols="A:F",
            ).astype(str)

            return dataframe
        except Exception as e:
            print(e)
            # print("Feche as planilhas de template e tente novamente.")

    def executar(self):
        app_view = ConsoleView()
        app_view.clear_console()

        caminho_completo = (
            self.caminho_raiz + f"SECON - General\\ANO_ATUAL\\NL_AUTOMATICA"
        )
        nomes_planilhas = [
            nome
            for nome in os.listdir(caminho_completo)
            # ignora arquivos temporários
            if nome.endswith((".xlsx", ".xls")) and not nome.startswith("~$")
        ]

        while True:
            app_view.display_menu(
                nomes_planilhas,
                "Selecione a planilha:",
                selecionar_todos=True,
                permitir_voltar=True,
            )
            planilhas_selecionadas = app_view.get_user_input(
                nomes_planilhas,
                selecionar_todos=True,
                permitir_voltar=True,
                multipla_escolha=True,
            )

            if planilhas_selecionadas is None:
                continue

            nls_carregadas = []
            templates_selecionados=  []
            for planilha in planilhas_selecionadas:
                while True:
                    caminho_arquivo = os.path.join(caminho_completo, planilha)
                    try:
                        xls = pd.ExcelFile(caminho_arquivo)
                        nomes_templates = xls.sheet_names

                        app_view.display_menu(
                            nomes_templates,
                            f"Selecione as NLs da planilha {planilha.split(".")[0]} para serem preenchidas:",
                            selecionar_todos=True,
                            # permitir_voltar=True,
                        )
                        escolhas_planilha = app_view.get_user_input(
                            nomes_templates,
                            selecionar_todos=True,
                            # permitir_voltar=True,
                            multipla_escolha=True,
                        )

                        if escolhas_planilha is not None:
                            templates_selecionados.extend(escolhas_planilha)
                            break

                    except Exception as e:
                        print(f"Erro ao processar {planilha}: {e}")

                nls_carregadas.extend(
                    [
                        {
                            "folha": self.carregar_nl(planilha, aba),
                            "cabecalho": self.carregar_cabecalho(planilha, aba),
                        }
                        for aba in templates_selecionados
                    ]
                )

            break

        if self.test:
            app_view.clear_console()
            print("NLs que serão preenchidas:")
            for i, folha in enumerate(nls_carregadas):
                print(folha["folha"])
                print()
        if self.run:
            preenchedor = PreenchimentoNL(self.run, self.test)
            preenchedor.executar(nls_carregadas)


if __name__ == "__main__":
    try:
        driver = NLAutomatica(test=TESTE, run=not TESTE)
        driver.executar()
    except Exception as e:
        print(e)
        sys.exit()
