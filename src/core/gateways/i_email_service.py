from abc import ABC, abstractmethod


class IEmailService(ABC):
    def send_email(
        mail_from, mail_to, subject, body, html, attachments, send=True, display=False
    ): ...
