from cryptography.fernet import Fernet
import json
import getpass

# 1. Gerar uma chave e salvá-la em um arquivo
key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)

print("Chave de criptografia salva em 'secret.key'")

# 2. Obter as credenciais do usuário
cpf = input("Digite o CPF: ").strip()
cpf_formatado = f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
password = getpass.getpass("Digite a senha: ").strip()  # getpass esconde a senha

# 3. Preparar os dados para criptografar (usando JSON)
data_to_encrypt = {"cpf": cpf_formatado, "password": password}
json_data = json.dumps(data_to_encrypt)

# 4. Criptografar os dados e salvar no arquivo
cipher = Fernet(key)
encrypted_data = cipher.encrypt(json_data.encode("utf-8"))

with open("credentials.enc", "wb") as encrypted_file:
    encrypted_file.write(encrypted_data)

print("Credenciais salvas e criptografadas em 'credentials.enc'")
