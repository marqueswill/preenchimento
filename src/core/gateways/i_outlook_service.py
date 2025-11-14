from abc import ABC, abstractmethod

from src.infrastructure.web.web_driver import WebDriver


class IOutlookService(WebDriver):
    def send_email(
        mail_from, mail_to, subject, body, html, attachments, send=True, display=False
    ): ...
