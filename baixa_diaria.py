import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

import pandas as pd
import time
import os
from datetime import datetime

ANO_ATUAL = datetime.now().year


def carregar_planilha():
    username = os.getlogin().strip()
    caminho_nl_diaria = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\General - SECON\\FLUXO_DIÁRIAS\\BAIXA_DIARIAS.xlsx"
    dataframe = pd.read_excel(caminho_nl_diaria)
    return dataframe


def separar_processos(dataframe):
    dataframes_separados = {
        processo: df for processo, df in dataframe.groupby("PROCESSO")
    }
    return dataframes_separados


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options)
    return driver


def login_siggo(driver):
    url = "https://siggo.fazenda.df.gov.br/Account/Login"
    driver.get(url)

    cpf_input_selector = '//*[@id="cpf"]'
    password_input_selector = '//*[@id="Password"]'
    button_selector = "/html/body/div[2]/div/div/div[1]/div/div/div[2]/form/button"

    cpf = "00350352267"
    password = "ac1ja15"

    driver.find_element(By.XPATH, value=cpf_input_selector).send_keys(cpf)
    driver.find_element(By.XPATH, value=password_input_selector).send_keys(password)
    driver.find_element(By.XPATH, button_selector).click()


def esperar_login(driver, timeout=60):
    url = "https://siggo.fazenda.df.gov.br/Account/Login"
    driver.get(url)

    start_time = time.time()

    while True:
        try:
            title = driver.find_element(
                By.XPATH, '//*[@id="SIAC"]/div/div/div/div[2]/div/a/h4'
            )
            if title.text == "AFC":
                break
        except:
            pass

        time.sleep(2)

        if time.time() - start_time > timeout:
            driver.quit()
            raise TimeoutException("Tempo limite para login excedido.")


def esperar_carregamento(driver):
    while True:
        try:
            loading = driver.find_element(
                By.XPATH, "/html/body/app-root/lib-login-callback/p"
            )
            if loading.text == "carregando...":
                time.sleep(2)
                continue
        except:
            break


# TODO: generalizar as funções de preenchimento
def preencher_cabecalho(driver, processo, dados):
    # num_proc = str(dados.iloc[0, 6])
    prioridade = "Z0"
    cod_ug = "020101-00001"
    # texto_obs = "CONCESSÃO DE DIÁRIAS A SERVIDORES P/ PARTICIPAÇÃO NO (nome_evento), PROMOVIDO PELO(A) (instituição), NO PERÍODO DE XXXX, EM (cidade)."

    driver.find_element(By.XPATH, '//*[@id="nuProcesso"]/input').send_keys(
        processo,
    )
    driver.find_element(By.XPATH, '//*[@id="prioridadePagamento"]/input').send_keys(
        prioridade
    )

    Select(
        driver.find_element(By.XPATH, '//*[@id="tipoCredor"]')
    ).select_by_visible_text("4 - UG/Gestão")

    driver.find_element(By.XPATH, '//*[@id="codigoCredor"]/input').send_keys(
        cod_ug,
    )

    # driver.find_element(By.XPATH, '//*[@id="observacao"]').send_keys(
    #     texto_obs,
    # )


def preencher_nl(driver, dados, num_aba):
    delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
    driver.find_element(By.XPATH, delete_button).click()

    lines = dados.shape[0]

    for i in range(lines):
        index = i + num_aba * 24

        if i == 24 or index == lines:
            break

        driver.find_element(By.XPATH, '//*[@id="incluirCampoLancamentos"]').click()

        for j in range(6):
            if j == 2:
                continue
            selector = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'

            dado = str(dados.iloc[index, j])
            driver.find_element(By.XPATH, selector).send_keys(dado)


def preencher_baixa(driver, dados):
    delete_button = '//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr/td[7]/button'
    driver.find_element(By.XPATH, delete_button).click()

    lines = dados.shape[0]

    for i in range(lines):
        driver.find_element(By.XPATH, '//*[@id="incluirCampoLancamentos"]').click()

        evento = 560379  # coluna 1
        inscricao = dados.iloc[i]["CPF"]  # coluna 2
        classificacao_contabil = 332110100  # coluna 3
        valor = dados.iloc[i]["BAIXAR"]  # coluna 6

        valores = [evento, inscricao, classificacao_contabil, None, None, valor]

        for j in range(6):
            if valores[j] is None:
                continue

            selector = f'//*[@id="ui-fieldset-0-content"]/div/div/div[1]/div/table/tbody/tr[{i+1}]/td[{j+1}]/input'

            driver.find_element(By.XPATH, selector).send_keys(str(valores[j]))


def nova_aba(driver):
    driver.execute_script("window.open('');")
    abas = driver.window_handles
    driver.switch_to.window(abas[-1])


def acessar_link(driver, link):
    driver.get(link)
    esperar_carregamento(driver)
    time.sleep(2)


def fechar_primeira_aba(driver):
    abas = driver.window_handles
    driver.switch_to.window(abas[0])
    driver.close()
    driver.switch_to.window(abas[1])


def run():
    dataframe = carregar_planilha()
    dataframes_por_processo = separar_processos(dataframe)

    driver = setup_driver()

    # login_siggo(driver)
    esperar_login(driver)
    link = f"https://siggo.fazenda.df.gov.br/{ANO_ATUAL}/afc/nota-de-lancamento"
    for processo, dado in dataframes_por_processo.items():
        nova_aba(driver)
        acessar_link(driver, link)
        preencher_cabecalho(driver, processo, dado)
        preencher_baixa(driver, dado)

    fechar_primeira_aba(driver)


try:
    run()
except:
    sys.exit()
