## Criando um usecase
Caso você queira implementar uma nova feature você deve criar um novo usecase. Isso implica
também que será necessário uma nova controller para executar esse usecase.
O precesso de implementação é bem direto:
1. Crie um novo arquivo para sua usecase0
2. Faça uma análise do seu caso de uso e decida quais services/gateways serão usados. Por exemplo, o `CancelamentoRPUseCase` precisa ler dados de uma planilha (ExcelService), processar esses dados e então preencher páginas no Siggo (PreenchimentoGateway). Sem dúvidas haverá casos que serão necessárias implementar novos services/gateways, caso isso ocorra confira (como implementar um gateway)[# Implementando Gateways]
3. Defina um método "executar" do usecase com a lógica principal. Podemos usar como exemplo o `CancelamentoRPUseCase`, pois seu executar é feito em passos claros, concisos e modulares:
```
def executar(self):
    # 1. Obter os dados da planilha
    dados_planilha = self.obter_dados_cacelamento()

    # 2. Montar os dados para o preenchimento
    dados_preenchimento = self.preparar_dados_preenchimento(dados_planilha)

    # 3. Preencher no navegador
    self.preencher_dados_siggo(dados_preenchimento)
```
4. Depois basta implementar cada um dos métodos que você definiu. Em alguns casos, como nos métodos `obter_dados_cacelamento` e `preencher_dados_siggo`, você só precisará chamar um dos services/gateways para importar/exportar dados. Em outros casos você precisa de uma lógica de processamento mais robusta e complexa `preparar_dados_preenchimento` o qual será o coração do usecase.



## Executando

### Inicialize o venv

linux:
`python -m venv venv`

windows:
`venv\Scripts\Activate.ps1`

### Instale as dependências

`pip install -r requirements.txt`

### Execute o main

`python -m src.main`

## Gerando executáveis

Para gerar executável para cada controller, execute:
windows
`./build.bat`

Acesse a pasta pelo terminal e execute conforme o exemplo:
`python -m PyInstaller --onefile --name "NOME DE EXEMPLO" .\src\adapters\controllers\arquivo.py`

Se quiser ocultar o console, use
`python -m PyInstaller --onefile --noconsole --name "NOME DE EXEMPLO" .\src\adapters\controllers\arquivo.py`
