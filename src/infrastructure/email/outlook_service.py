import win32com.client as win32

from src.core.gateways.i_outlook_service import IOutlookService


class OutlookService(IOutlookService):

    def send_email(
        self,
        mail_from,
        mail_to,
        inbox,
        subject,
        body,
        html,
        attachments,
        send=True,
        display=False,
    ):
        try:
            outlook = win32.Dispatch("outlook.application")
            mail = outlook.CreateItem(0)

            mail.SentOnBehalfOfName = inbox

            mail.To = mail_to
            mail.Subject = subject
            mail.Body = body
            mail.HTMLBody = html

            for att in attachments:
                mail.Attachments.Add(att)

            if display:
                mail.Display()

            if send:
                pass
                # mail.Send()

        except Exception as e:
            raise (f"Ocorreu um erro inesperado ao enviar o email: {e}\n")
