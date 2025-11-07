import sys

from drivers.nl_automatica import PreenchimentoTemplates


try:
    driver = PreenchimentoTemplates(test=True, run=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
