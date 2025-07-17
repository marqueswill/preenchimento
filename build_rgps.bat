@echo off
set SCRIPTS="RGPS_COMPLETO.py" "RGPS_BENEFICIOS.py" "RGPS_CONFERENCIA.py" "RGPS_DEA_BENEFICIOS.py" "RGPS_INDENIZACOES_PESSOAL.py" "RGPS_INDENIZACOES_RESTITUICOES.py" "RGPS_PRINCIPAL.py" "RGPS_SUBSTITUICOES.py"

for %%s in (%SCRIPTS%) do (
    echo Building %%~ns...
    python -m PyInstaller --onefile drivers\pagamento\rgps\%%~s
)
