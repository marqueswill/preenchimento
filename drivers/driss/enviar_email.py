import os, re, sys
import time
import PyPDF2
import pandas as pd
import win32com.client as win32

from datetime import datetime
from typing import Dict, List
from pandas import DataFrame

from drivers.view import ConsoleView

TESTE = True
ANO_ATUAL = datetime.now().year
MES_REFERENCIA = datetime.now().month - 1 if not TESTE else 0
MESES = {
    0: "TESTES",
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
NOME_MES_ATUAL = MESES[MES_REFERENCIA].split("-")[1] if MES_REFERENCIA > 0 else "TESTES"

# Padronizar com orientação objetos? Precisa? Se eu for fazer outro EmailSender eu faço
# class EmailSenderDRISS:
#     def __init__(self):
#         pass


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


def listar_pdfs():
    caminho_completo = (
        get_root_paths()
        + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\{MESES[MES_REFERENCIA]}\\ENVIADOS"
    )
    nomes_pdfs = [
        nome
        for nome in os.listdir(caminho_completo)
        # ignora arquivos temporários
        if (nome.endswith((".pdf")) or nome.endswith((".PDF")))
        and not nome.startswith("~$")
    ]
    return nomes_pdfs


def enviar_email(empresa, email_empresa, caminho_pdf, test=False, display=False):
    try:
        outlook = win32.Dispatch("outlook.application")
        mail = outlook.CreateItem(0)
        mail.To = email_empresa
        mail.Subject = "Declaração de Retenção do ISS"
        msg_txt, msg_html = gerar_mensagem(empresa)
        mail.Body = msg_txt
        mail.HTMLBody = msg_html
        mail.Attachments.Add(caminho_pdf)

        if display:
            mail.Display()

        if not test and not TESTE:
            pass
            # mail.Send()

    except Exception as e:
        ConsoleView.color_print(
            f"Ocorreu um erro inesperado ao processar {empresa}: {e}\n", color="red"
        )


def gerar_mensagem(empresa):
    hora = datetime.now().hour
    if 0 <= hora < 12:
        saudacao = "Bom dia"
    elif 12 <= hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    msg_html = f"""
    <p>{saudacao},</p>
    <p>Segue anexa a Declaração de Retenção do ISS referente ao mês de {NOME_MES_ATUAL}/{ANO_ATUAL}.</p>
    <p>Solicito a confirmação de recebimento desta mensagem.</p>
    <br>
    <p>Atenciosamente,</p>
    <p>Serviço de Contabilidade</p>
    <p>Tribunal de Contas do Distrito Federal</p>
    """

    msg_txt = re.sub("<[^>]+>", "", msg_html).strip().replace("  ", "")

    return msg_txt, msg_html

    # def enviar_emails_driss(emails_empresa: List[str], caminho_pdf: str, nome_empresa: str):
    #     if emails_empresa == []:
    #         ConsoleView.color_print(
    #             f"E-mail para a empresa '{nome_empresa}' não encontrado na planilha.",
    #             color="yellow",
    #         )
    #         return

    #     for email_empresa in emails_empresa:
    #         enviar_email(
    #             nome_empresa,
    #             email_empresa,
    #             caminho_pdf,
    #             test=TESTE,
    #         )
    #         ConsoleView.color_print(f"E-mail enviado para {email_empresa}", color="green")


def enviar_emails_driss(emails_para_enviar: List[Dict], test=True):

    # Primeiro testa pra ver se tá tudo ok
    envio_falhou = False
    for email_data in emails_para_enviar:
        for email_empresa in email_data["emails"]:
            try:
                enviar_email(
                    email_data["nome_empresa"],
                    email_empresa,
                    email_data["caminho_saida"],
                    test=True,  # Mantém o modo de teste
                )
            except Exception as e:
                ConsoleView.color_print(
                    f"Erro ao preparar e-mail para {email_empresa}: {e}",
                    color="red",
                )
                envio_falhou = True
                break  # Sai do loop interno

        if envio_falhou:
            break  # Sai do loop externo

    # Se não for teste e nenhum erro foi detectado, envia todos os e-mails
    if not envio_falhou:
        ConsoleView.color_print(
            "Nenhum erro encontrado. Iniciando o envio de todos os e-mails",
            color="green",
            style="bold",
        )

        time.sleep(1.5)

        for email_data in emails_para_enviar:
            for email_empresa in email_data["emails"]:
                try:
                    enviar_email(
                        email_data["nome_empresa"],
                        email_empresa,
                        email_data["caminho_saida"],
                        test=test,
                        display=False,
                    )
                    ConsoleView.color_print(f"E-mail enviado para {email_empresa}")
                except Exception as e:
                    ConsoleView.color_print(
                        f"Erro crítico ao enviar e-mail para {email_empresa}: {e}",
                        color="red",
                    )
                    # Se um erro ocorrer aqui, alguns e-mails já podem ter sido enviados.
                    # É por isso que o teste preliminar é importante.
                    break

    if envio_falhou:
        ConsoleView.color_print(
            "\n\nProcesso abortado devido a um erro. Nenhum e-mail foi enviado.",
            color="red",
            style="bold",
        )
    else:
        ConsoleView.color_print(
            "\nProcesso concluído.".upper(), color="green", style="bold"
        )


def exportar_pdf_driss(
    paginas_driss: List[PyPDF2.PageObject], caminho_saida: str, nome_empresa: str
):

    try:
        writer = PyPDF2.PdfWriter()
        for page in paginas_driss:
            writer.add_page(page)

        with open(caminho_saida, "wb") as saida:
            writer.write(saida)

        ConsoleView.color_print(f"PDF salvo para {nome_empresa}.")

    except Exception as e:
        ConsoleView.color_print(
            f"Erro ao exportar PDF para empresa {nome_empresa}: {e}", color="red"
        )


caminho_raiz = get_root_paths()


def extrair_emails_empresa(nome_empresa_pdf):
    # TODO: função chamada toda iteração do loop
    planilha_emails = obter_planilha_emails()
    nome_pdf_limpo = nome_empresa_pdf.upper().strip()
    emails_encontrados = []
    for index, row in planilha_emails.iterrows():
        nome_planilha = row["EMPRESA"].upper().strip()
        inicio_nome_empresa = nome_planilha.split()[0]
        if (
            nome_pdf_limpo == nome_planilha
            or nome_pdf_limpo.startswith(  # TODO: melhorar essa lógica de singla/abreviação
                inicio_nome_empresa
            )
        ):
            emails_encontrados += str(row["E-MAIL"]).strip().replace(" ", "").split(";")
            return (nome_planilha, emails_encontrados)
    return None


def extrair_paginas_por_empresa(file) -> Dict[str, List[PyPDF2.PageObject]]:
    paginas_por_empresa = {}
    reader = PyPDF2.PdfReader(file)
    # Identifica a empresa em cada página e agrupa as páginas por empresa
    for page in reader.pages[:-1]:
        text = page.extract_text().replace("\n", " ").replace("  ", " ").strip()
        # nome da empresa sempre vem nesse padrão: relativo ao ISS proveniente dos serviços prestados por WINDOC GESTÃO DE DOCUMENTOS LTDA, com endereço:
        padrao = r"relativo ao ISS proveniente dos serviços prestados por (.*?), com endereço:"
        nome_empresa_match = re.search(padrao, text)
        if nome_empresa_match:
            nome_empresa = nome_empresa_match.group(1).strip()
            paginas_por_empresa[nome_empresa] = paginas_por_empresa.get(
                nome_empresa, []
            ) + [page]
            ConsoleView.color_print(f"Declaração encontrada: {nome_empresa}")
        else:
            ConsoleView.color_print(
                "\nPadrão não encontrado nesta página:", color="yellow"
            )
            ConsoleView.color_print(f"{text}\n\n")

    return paginas_por_empresa


def obter_planilha_emails() -> DataFrame:
    caminho_planilha_emails = (
        caminho_raiz
        + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\EMAIL_EMPRESAS.xlsx"
    )

    dataframe = pd.read_excel(
        caminho_planilha_emails,
        header=0,
        usecols="B:C",
    ).astype(str)

    return dataframe


def main(test=False):
    caminho_pdf = (
        caminho_raiz
        + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\{MESES[MES_REFERENCIA]}\\DRISS_{f"{MES_REFERENCIA:02d}" if MES_REFERENCIA >
                                                                                           0 else "TESTES"}_{ANO_ATUAL}.pdf"
    )

    emails_para_enviar = []
    try:
        with open(caminho_pdf, "rb") as file:
            ConsoleView.color_print("Separando páginas DRISS".upper(), style="bold")
            paginas_por_empresa = extrair_paginas_por_empresa(file)
            for nome_pdf, paginas in paginas_por_empresa.items():
                # Procura o e-mail correspondente na planilha
                nome_planilha, emails_encontrados = extrair_emails_empresa(nome_pdf)

                caminho_saida = (
                    caminho_raiz
                    + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\{MESES[MES_REFERENCIA]}\\ENVIADOS\\DRISS_{NOME_MES_ATUAL} - {nome_planilha}.pdf"
                )

                # Salvar o PDF da empresa

                exportar_pdf_driss(paginas, caminho_saida, nome_planilha)

                emails_para_enviar.append(
                    {
                        "nome_empresa": nome_planilha,
                        "caminho_saida": caminho_saida,
                        "emails": emails_encontrados,
                    }
                )
                # break
    except FileNotFoundError as e:
        ConsoleView.color_print(f"Erro: Arquivo não encontrado - {e}", color="red")
        sys.exit(1)

    # Enviar e-mails para todos os endereços encontrados
    ConsoleView.color_print("\nEnviando emails paras empresas".upper(), style="bold")
    enviar_emails_driss(emails_para_enviar)


if __name__ == "__main__":
    main(test=TESTE)
