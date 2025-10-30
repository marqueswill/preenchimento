from typing import Dict
from pandas import DataFrame
from selenium.webdriver.common.by import By

from src.core.gateways.i_preenchimento_gateway import IPreenchimentoGateway
from src.config import *

class PreenchimentoGateway(IPreenchimentoGateway):
    def __init__(self, siggo_service):
        super().__init__(siggo_service)

    def executar(self, dados:  list[Dict[str, DataFrame]]):
        self.siggo_driver.start()

        for dado in dados:
            # feito assim para não ter que fazer login para cada folha
            folha = dado["folha"]
            template = dado["cabecalho"]

            if folha.empty:
                continue

            dados_por_pagina = self.separar_por_pagina(folha)
            for dados_lancamentos in dados_por_pagina:
                self.siggo_driver.nova_aba()
                self.siggo_driver.acessar_link(
                    f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
                )

                campos_cabecalho = self.preparar_preechimento_cabecalho(template)
                self.siggo_driver.selecionar_opcoes(campos_cabecalho["opcoes"])
                self.siggo_driver.preencher_campos(campos_cabecalho["campos"])

                campos_lancamentos = self.preparar_preenchimento_nl(dados_lancamentos)
                self.siggo_driver.preencher_campos(campos_lancamentos)

        self.siggo_driver.fechar_primeira_aba()

    def preparar_preechimento_cabecalho(self, template: DataFrame):
        prioridade: str = template.iloc[0, 1]  # B1
        credor: str = template.iloc[1, 1]  # B2
        gestao: str = template.iloc[2, 1]  # B3
        processo: str = template.iloc[3, 1]  # B4
        observacao: str = template.iloc[4, 1]  # B5

        id_campo_gestao = {
            "2 - CNPJ": '//*[@id = "cocredorCNPJ"]/input',
            "4 - UG/Gestão": '//*[@id="codigoCredor"]/input',
        }[credor]

        return {
            "campos": {
                '//*[@id="prioridadePagamento"]/input': prioridade,
                id_campo_gestao: gestao,
                '//*[@id="nuProcesso"]/input': processo,
                '//*[@id="observacao"]': observacao.replace(
                    "<MONTH>", NOME_MES_ATUAL
                ).replace("<YEAR>", str(ANO_ATUAL)),
            },
            "opcoes": {
                '//*[@id="tipoCredor"]': credor,
            },
        }

    def preparar_preenchimento_nl(self, dados):
        delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
        self.siggo_driver.driver.find_element(By.XPATH, delete_button).click()

        linhas = dados.shape[0]
        campos = {}

        for i in range(linhas):
            self.siggo_driver.driver.find_element(
                By.XPATH, '//*[@id="incluirCampoLancamentos"]'
            ).click()

            evento = dados.iloc[i]["EVENTO"]
            inscricao = dados.iloc[i]["INSCRIÇÃO"]
            class_cont = dados.iloc[i]["CLASS. CONT"].replace(".", "")
            class_orc = dados.iloc[i]["CLASS. ORC"].replace(".", "")
            fonte = dados.iloc[i]["FONTE"]
            valor = "{:.2f}".format(round(float(dados.iloc[i]["VALOR"]), 2))

            valores = [evento, inscricao, class_cont, class_orc, fonte, valor]

            for j in range(6):
                seletor = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'
                campos[seletor] = str(valores[j])

        return campos

    def separar_por_pagina(self, dataframe: DataFrame, tamanho_pagina=24):
        return [
            dataframe.iloc[i : i + tamanho_pagina]
            for i in range(0, len(dataframe), tamanho_pagina)
        ]
