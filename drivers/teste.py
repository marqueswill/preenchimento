import sys

from drivers.preenchimento_template import PreenchimentoTemplates


try:
    driver = PreenchimentoTemplates(test=True, run=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
