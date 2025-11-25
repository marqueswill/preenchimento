@echo off

set PYINSTALLER_CMD=python -m PyInstaller --hiddenimport win32timezone --onefile

echo --> 1/7: Compilando NOME DE EXEMPLO...
%PYINSTALLER_CMD% --name "NOME DE EXEMPLO" .\src\adapters\controllers\arquivo.py

echo --> 2/7: Compilando APP FOLHA DE PAGAMENTO...
%PYINSTALLER_CMD% --name "APP FOLHA DE PAGAMENTO" .\src\adapters\controllers\pagamento_controller.py

echo --> 3/7: Compilando EXTRAIR DADOS R2000...
%PYINSTALLER_CMD% --name "EXTRAIR DADOS R2000" .\src\adapters\controllers\extrair_dados_r2000_controller.py

echo --> 4/7: Compilando EMAILS DRISS...
%PYINSTALLER_CMD% --name "EMAILS DRISS" .\src\adapters\controllers\emails_driss_controller.py

echo --> 5/7: Compilando PAGAMENTO DIARIAS...
%PYINSTALLER_CMD% --name "PAGAMENTO DIARIAS" .\src\adapters\controllers\pagamento_diarias_controller.py

echo --> 6/7: Compilando NL AUTOMATICA...
%PYINSTALLER_CMD% --name "NL AUTOMATICA" .\src\adapters\controllers\nl_automatica_controller.py

echo --> 7/7: Compilando IMPORTAR VALORES PAGOS...
%PYINSTALLER_CMD% --name "IMPORTAR VALORES PAGOS" .\src\adapters\controllers\exportar_valores_pagos_controller.py

echo -----------------------------------------------------------
echo Todos os executaveis foram compilados com sucesso!
echo Os arquivos estao disponiveis no diretorio 'dist'.
echo -----------------------------------------------------------

pause