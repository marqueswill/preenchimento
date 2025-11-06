from selenium import webdriver
from cryptography.fernet import Fernet
import json
import pandas as pd


from src.infrastructure.web.siggo_service import SiggoService
from src.config import *


# TODO: identificação e tratamento de erros (interface?)
class SiggoServiceMock(SiggoService):

    def start(self):
        self.setup_pandas()
        self.setup_driver()
        cpf, password = self.get_siggo_credentials()
        self.login_siggo(cpf, password)

    def setup_pandas(self):
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_colwidth", None)
        pd.set_option("display.width", 0)
        pd.set_option("display.expand_frame_repr", False)

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_experimental_option("detach", True)
        options.add_argument("--log-level=3")  # Suppress Chrome logs
        options.add_argument("--silent")

        self.driver = webdriver.Chrome(options=options)

    def get_siggo_credentials(self) -> tuple[str, str]:
        try:
            with open("secret.key", "rb") as key_file:
                key = key_file.read()

            with open("credentials.enc", "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            cipher = Fernet(key)
            decrypted_json_data = cipher.decrypt(encrypted_data).decode("utf-8")

            credentials = json.loads(decrypted_json_data)

            return credentials["cpf"], credentials["password"]

        except FileNotFoundError:
            print("Erro: Arquivo 'secret.key' ou 'credentials.enc' não encontrado.")
            print("Execute o script 'setup_credentials.py' primeiro.")
            raise
        except Exception as e:
            print(f"Erro ao descriptografar as credenciais: {e}")
            raise
