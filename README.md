### Dependências

`pip install selenium`
`pip install pandas`
`pip install openpyxl`
`pip install pyinstaller`

### Gerando executável

Acesse a pasta pelo terminal e execute:
`python -m PyInstaller --onefile --noconsole arquivo_exemplo.py`

Ou execute o comando na pasta raiz:
`./build_rgps.bat`

### TODO
- [] Integrar webdriver com Power Automate online para executar o fluxo que gera os dados da planilha
- [] Tratamento de erros