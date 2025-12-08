# App Automação de Processos SECON
## Arquitetura
A arquitetura foi feita com base no **clean arquitecture** para unificar e organizizar os vários scripts que existiam. 

## Guia de Desenvolvimento
### Criando um usecase

Caso você queira implementar uma nova _feature_, você deve criar um novo **Use Case**. Isso implica também que será necessária uma nova **Controller** para executar esse caso de uso.

O processo de implementação é direto:

1.   **Crie o arquivo:** Crie um novo arquivo para o seu _usecase_.
    
2.   **Análise de dependências:** Decida quais _Services_ ou _Gateways_ serão usados.
 > **Exemplo:** O `CancelamentoRPUseCase` precisa ler dados de uma planilha (`ExcelService`), processar esses dados e então preencher páginas no Siggo (`PreenchimentoGateway`). _Nota: Se precisar implementar novos services/gateways, confira a seção: [Implementando Gateways]()._
    
3. **Defina o método `executar`:** Este método deve conter a lógica principal, dividida em passos claros e modulares. Veja o exemplo do `CancelamentoRPUseCase`:
```python
def executar(self):
    # 1. Obter os dados da planilha
    dados_planilha = self.obter_dados_cancelamento()

    # 2. Preparar os dados para o preenchimento (gerar NLs)
    dados_preenchimento = self.preparar_dados_preenchimento(dados_planilha)

    # 3. Preencher NLs no siggo
    self.preencher_dados_siggo(dados_preenchimento)
```
4. **Implemente os sub-métodos:**
- Métodos simples como `obter_dados_cancelamento` e `preencher_dados_siggo` geralmente apenas chamam os _services/gateways_ para importar ou exportar dados.
- Métodos de processamento, como `preparar_dados_preenchimento`, conterão a lógica mais robusta e serão o "coração" do Use Case.

## 🚀 Executando o Projeto
1. Inicialize o ambiente virtual (venv)-
- **Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```
- **Windows (PowerShell):**
```PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
2. Instale as dependências
```bash
pip install -r requirements.txt
```
3. Execute o Main
```bash
python -m src.main
```

## 📦 Gerando Executáveis
Existem duas formas de gerar os executáveis das controllers:
### Opção A: Script Automático (Windows)

Para gerar executáveis para cada controller automaticamente, execute:

Aqui está uma versão formatada, com correções de digitação ("precesso", "cacelamento"), melhor hierarquia visual e destaque para os comandos de código.

----------

# 📘 Guia de Desenvolvimento

## Criando um Use Case

Caso você queira implementar uma nova _feature_, você deve criar um novo **Use Case**. Isso implica também que será necessária uma nova **Controller** para executar esse caso de uso.

O processo de implementação é direto:

1.  **Crie o arquivo:** Crie um novo arquivo para o seu _usecase_.
    
2.  **Análise de dependências:** Decida quais _Services_ ou _Gateways_ serão usados.
    
    > **Exemplo:** O `CancelamentoRPUseCase` precisa ler dados de uma planilha (`ExcelService`), processar esses dados e então preencher páginas no Siggo (`PreenchimentoGateway`). _Nota: Se precisar implementar novos services/gateways, confira a seção: [Implementando Gateways](https://www.google.com/search?q=%23)._
    
3.  **Defina o método `executar`:** Este método deve conter a lógica principal, dividida em passos claros e modulares. Veja o exemplo do `CancelamentoRPUseCase`:
    

Python

```
def executar(self):
    # 1. Obter os dados da planilha
    dados_planilha = self.obter_dados_cancelamento()

    # 2. Montar os dados para o preenchimento
    dados_preenchimento = self.preparar_dados_preenchimento(dados_planilha)

    # 3. Preencher no navegador
    self.preencher_dados_siggo(dados_preenchimento)

```

4.  **Implemente os sub-métodos:**
    
    -   Métodos simples como `obter_dados_cancelamento` e `preencher_dados_siggo` geralmente apenas chamam os _services/gateways_ para importar ou exportar dados.
        
    -   Métodos de processamento, como `preparar_dados_preenchimento`, conterão a lógica mais robusta e serão o "coração" do Use Case.
        

----------

## 🚀 Executando o Projeto

### 1. Inicialize o ambiente virtual (venv)

-   **Linux/Mac:**
    
    Bash
    

-   ```
    python -m venv venv
    source venv/bin/activate
    
    ```
    
-   **Windows (PowerShell):**
    
    PowerShell
    

-   ```
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    ```
    

### 2. Instale as dependências

Bash

```
pip install -r requirements.txt

```

### 3. Execute o Main
```Bash
python -m src.main
```


## 📦 Gerando Executáveis
Existem duas formas de gerar os executáveis das controllers:
### Opção A: Script Automático (Windows)
Esse script utiliza o pyinstaller para gerar executáveis para cada controller automaticamente:
```PowerShell
./build.bat
```

### Opção B: Manualmente (PyInstaller)
Caso você queira gerar apenas parau uma controller específica,acesse a pasta raiz pelo terminal e execute o comando abaixo, substituindo os caminhos conforme necessário:
**Com console (padrão):**
```Bash
python -m PyInstaller --onefile --name "NOME_DO_EXECUTAVEL" .\src\adapters\controllers\arquivo.py
```

**Sem console (modo silencioso):** Use a flag `--noconsole` se não quiser que a janela preta do terminal apareça:
```Bash
python -m PyInstaller --onefile --noconsole --name "NOME_DO_EXECUTAVEL" .\src\adapters\controllers\arquivo.py
```
