import sys

from drivers.template_nls.preenchimento_template import PreenchimentoTemplates


try:
    driver = PreenchimentoTemplates(test=True, run=True)
    driver.executar()
except Exception as e:
    print(e)
    sys.exit()
