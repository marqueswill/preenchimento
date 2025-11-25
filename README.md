### Venv
`python -m venv venv`

windows:
`venv\Scripts\Activate.ps1`

### Dependências

Dev and client:
`pip install -r requirements.txt`


### Gerando executável

Acesse a pasta pelo terminal e execute conforme o exemplo:
`python -m PyInstaller --onefile --name "NOME DE EXEMPLO" .\src\adapters\controllers\arquivo.py`

se quiser ocultar o console, use
`python -m PyInstaller --onefile --noconsole --name "NOME DE EXEMPLO" .\src\adapters\controllers\arquivo.py`

