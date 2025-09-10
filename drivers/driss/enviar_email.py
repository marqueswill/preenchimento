from datetime import datetime
import os
import re
import sys
import PyPDF2
import pandas as pd
import win32com.client as win32

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


def enviar_email(empresa, email_empresa, caminho_pdf, test=False):
    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)
    mail.To = email_empresa
    mail.Subject = "Declaração de Retenção do ISS"
    mail.Body = "TESTE"

    mail.HTMLBody = gerar_mensagem(empresa)

    # To attach a file to the email (optional):
    attachment = caminho_pdf
    mail.Attachments.Add(attachment)

    if not test:
        pass
        # print("fiz merda?")
        # mail.Send()
    else:
        mail.Display()


def gerar_mensagem(empresa):
    hora = datetime.now().hour
    if 0 <= hora < 12:
        saudacao = "Bom dia"
    elif 12 <= hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    return f"""
    <p>{saudacao},</p>
    <p>Segue anexa a Declaração de Retenção do ISS referente ao mês de {NOME_MES_ATUAL}/{ANO_ATUAL}.</p>
    <p>Solicito a confirmação de recebimento desta mensagem.</p>
    <br>
    <p>Atenciosamente,</p>
    <p>Serviço de Contabilidade</p>
    <p>Tribunal de Contas do Distrito Federal</p>
    """


caminho_raiz = get_root_paths()

def pegar_emails():
    caminho_planilha_emails = (
        caminho_raiz + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\EMAIL_EMPRESAS.xlsx"
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
    paginas_por_empresa = {}
    try:
        with open(caminho_pdf, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            
            # Identifica a empresa em cada página e agrupa as páginas por empresa
            for page in reader.pages:
                text = page.extract_text().replace("\n", " ").replace("  ", " ").strip()
                # nome da empresa sempre vem nesse padrão: relativo ao ISS proveniente dos serviços prestados por WINDOC GESTÃO DE DOCUMENTOS LTDA, com endereço:
                padrao = r"relativo ao ISS proveniente dos serviços prestados por (.*?), com endereço:"
                nome_empresa_match = re.search(padrao, text)
                if nome_empresa_match:
                    nome_empresa = nome_empresa_match.group(1).strip()
                    paginas_por_empresa[nome_empresa] = paginas_por_empresa.get(
                        nome_empresa, []
                    ) + [page]
                    print(f"Nome da empresa encontrado: {nome_empresa}")
                else:
                    print(text)
                    print("Padrão não encontrado nesta página.\n")

            # Itera sobre as empresas e envia os e-mails
            for nome_pdf, paginas in paginas_por_empresa.items():
                

                # Procura o e-mail correspondente na planilha
                # Lógica de correspondência: nome exato ou começa com a primeira palavra
                # Possíveis problemas: "Associação", "A. nome nome", "Nome - Filial"
                nome_pdf_limpo = nome_pdf.upper().strip()
                email_empresa = None
                nome_empresa_planilha = None
                
                planilha_emails = pegar_emails()
                emails_encontrados = []
                for index, row in planilha_emails.iterrows():
                    nome_planilha = row["EMPRESA"].upper().strip()
                    inicio_nome_empresa = nome_planilha.split()[0]
                    if nome_pdf_limpo == nome_planilha or nome_pdf_limpo.startswith(
                        inicio_nome_empresa
                    ):
                        emails_encontrados += str(row["E-MAIL"]).strip().replace(" ", "").split(";")
                        nome_empresa_planilha = nome_planilha
                        break

                # Salvar o PDF da empresa
                writer = PyPDF2.PdfWriter()
                for page in paginas:
                    writer.add_page(page)
                caminho_saida = (
                    caminho_raiz
                    + f"SECON - General\\ANO_ATUAL\\DRISS_{ANO_ATUAL}\\{MESES[MES_REFERENCIA]}\\ENVIADOS\\DRISS_{NOME_MES_ATUAL} - {nome_planilha}.pdf"
                )
                with open(caminho_saida, "wb") as saida:
                    writer.write(saida)
                print(f"\nPDF salvo para {nome_planilha}.")


                # Enviar e-mails para todos os endereços encontrados
                if emails_encontrados == []:
                    print(
                        f"E-mail para a empresa '{nome_pdf}' não encontrado na planilha."
                    )
                    continue
                for email_empresa in emails_encontrados:
                    try:
                        enviar_email(
                            nome_empresa_planilha,
                            email_empresa,
                            caminho_saida,
                            test=test,
                        )
                        print(
                            f"E-mail enviado para {email_empresa}")
                    except Exception as e:
                        print(
                            f"Ocorreu um erro inesperado ao processar {nome_empresa_planilha}: {e}\n")
                        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
        sys.exit(1)

    print("\n\nProcesso concluído.")


if __name__ == "__main__":
    main(test=TESTE)
