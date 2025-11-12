import win32com.client as win32

from src.core.gateways.i_email_service import IEmailService


class EmailService(IEmailService):

    def send_email(
        mail_from,
        mail_to,
        subject,
        body,
        html,
        attachments,
        send=True,
        display=False,
    ):
        return

        # TODO: enviar emails usando selenium
        try:
            outlook = win32.Dispatch("outlook.application")
            mail = outlook.CreateItem(0)

            mail.SentOnBehalfOfName = mail_from

            mail.To = mail_to
            mail.Subject = subject
            mail.Body = body
            mail.HTMLBody = html

            for att in attachments:
                mail.Attachments.Add(att)

            if display:
                mail.Display()

            if send:
                mail.Send()

        except Exception as e:
            raise (f"Ocorreu um erro inesperado ao enviar o email: {e}\n")
