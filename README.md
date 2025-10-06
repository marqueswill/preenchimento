### Dependências

Dev and client:
`pip install selenium pandas openpyxl PyPDF2 pyinstaller pywin32`


### Gerando executável

Acesse a pasta pelo terminal e execute conforme o exemplo:
`python -m PyInstaller --onefile --name "APP FOLHA DE PAGAMENTO" .\drivers\pagamento\controller.py`

se quiser ocultar o console, use
`python -m PyInstaller --onefile --noconsole --name "APP FOLHA DE PAGAMENTO" .\drivers\pagamento\controller.py`

Ou execute o comando na pasta raiz (deprecated, but useful?):
`./build_rgps.bat`

