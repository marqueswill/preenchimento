@echo off
set SCRIPTS=rgps_beneficios.py rgps_conferencia.py rgps_dea_beneficios.py rgps_indenizacoes_pessoal.py rgps_indenizacoes_restituicoes.py rgps_principal.py rgps_substituicoes.py

for %%s in (%SCRIPTS%) do (
    echo Building %%s...
    python -m PyInstaller --onefile --noconsole drivers\rgps\%%s
)
