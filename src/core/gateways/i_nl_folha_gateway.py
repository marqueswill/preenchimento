class INLFolhaGateway: 
    """_summary_ Gera uma NL para folha de pagamento a partir de um fundo e um template
    de preenchimento 
    """
    
    def __init__(self):
        pass

# 1. Obter o nome do fundo e do template selecionado
# 2. Carregar template 
# 3. Carregar cabecalho do template
# 4. Fazer cálculo usando saldos e instruções do template
#   Obter saldos -> controller irá passar como argumento na hora de fazer o cálculo, 
#   transferir método/lógica pro ConferenciaGateway
# 5. Retornar dataframe do template com valores calculados