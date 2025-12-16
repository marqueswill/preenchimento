# src/core/exceptions.py


class DomainError(Exception):
    """Classe base para erros de negócio."""

    pass


# ==========================================
# ERROS DO SIGGO (WEB AUTOMATION)
# ==========================================


class ErroPreenchimentoSiggoError(DomainError):
    def __init__(self, detalhes):
        super().__init__(f"Falha ao preencher dados no SIGGO: {detalhes}")


class ConexaoSiggoError(DomainError):
    def __init__(self, msg="A conexão com o Siggo foi interrompida ou está instável."):
        super().__init__(f"Erro de Conexão: {msg}")


class LoginSiggoError(DomainError):
    def __init__(self, usuario=None):
        msg = "Não foi possível realizar o login no Siggo."
        if usuario:
            msg += f" Usuário tentado: {usuario}."
        msg += " Verifique se as credenciais estão corretas ou se a senha expirou."
        super().__init__(msg)


class SiggoIndisponivelError(DomainError):
    def __init__(self):
        super().__init__(
            "O site do Siggo parece estar indisponível ou não carregou a tempo (Timeout)."
        )


# ==========================================
# ERROS DE EXCEL E ARQUIVOS
# ==========================================


class PlanilhaNaoEncontradaError(DomainError):
    def __init__(self, caminho_ou_nome):
        super().__init__(
            f"A planilha não foi encontrada no caminho esperado: '{caminho_ou_nome}'"
        )


class PlanilhaEmUsoError(DomainError):
    def __init__(self, caminho):
        super().__init__(
            f"O arquivo parece estar aberto em outro programa.\n"
            f"Por favor, FECHE o arquivo e tente novamente.\n"
            f"Arquivo: {caminho}"
        )


class TemplateInvalidoError(DomainError):
    def __init__(self, motivo):
        super().__init__(
            f"O template da planilha selecionada é inválido. Motivo: {motivo}"
        )


class FormatoPlanilhaInvalidoError(DomainError):
    def __init__(self, colunas_faltantes):
        colunas_str = ", ".join(colunas_faltantes)
        super().__init__(
            f"A planilha não possui as colunas obrigatórias: [{colunas_str}]"
        )


class DadosAusentesError(DomainError):
    def __init__(self, coluna, linha=None):
        msg = f"Dados obrigatórios estão faltando na coluna '{coluna}'."
        if linha:
            msg += f" (Linha aprox: {linha})"
        super().__init__(msg)


class PdfIllegivelError(DomainError):
    def __init__(self, caminho):
        super().__init__(
            f"O sistema não conseguiu ler o texto do PDF. Verifique se é um arquivo escaneado (imagem) sem OCR: {caminho}"
        )


# ==========================================
# ERROS DE INFRAESTRUTURA E SISTEMA
# ==========================================


class CaminhoRedeNaoEncontradoError(DomainError):
    def __init__(self, caminho):
        super().__init__(
            f"Não foi possível acessar o caminho de rede: '{caminho}'.\n"
            "Verifique sua conexão com a VPN, Internet ou se a pasta foi movida."
        )


class OutlookNaoConfiguradoError(DomainError):
    def __init__(self):
        super().__init__(
            "Não foi possível conectar ao Outlook.\n"
            "Verifique se o aplicativo Outlook Desktop está instalado e com o login realizado."
        )
