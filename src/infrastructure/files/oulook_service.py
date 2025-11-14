class OutlookService(IOutlookService):
    
    def enviar_email()
            # acessar a aba "https://outlook.office.com/mail/secon.gab@tc.df.gov.br/"
        # clicar no botão '//*[@id="588"]/button[1]'
        # preencher mail_from em '//*[@id="docking_InitVisiblePart_0"]/div/div[3]/div[1]/div/div[3]/div/span/span[2]'
        # preencher body em '//*[@id="editorParent_1"]/div'
        # preencher subject em '//*[@id="docking_InitVisiblePart_0"]/div/div[3]/div[2]/span/input'

        # try:
        #     outlook = win32.Dispatch("outlook.application")
        #     mail = outlook.CreateItem(0)

        #     mail.SentOnBehalfOfName = mail_from

        #     mail.To = mail_to
        #     mail.Subject = subject
        #     mail.Body = body
        #     mail.HTMLBody = html

        #     for att in attachments:
        #         mail.Attachments.Add(att)

        #     if display:
        #         mail.Display()

        #     if send:
        #         mail.Send()

        # except Exception as e:
        #     raise (f"Ocorreu um erro inesperado ao enviar o email: {e}\n")
