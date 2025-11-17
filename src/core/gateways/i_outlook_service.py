from abc import ABC, abstractmethod

from src.infrastructure.web.web_driver import WebDriver


class IOutlookService(WebDriver):

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
    ): ...
