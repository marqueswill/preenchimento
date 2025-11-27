class DomainError(Exception):
    """Classe base para erros de negócio."""

    pass


class PlanilhaNaoEncontradaError(DomainError):
    def __init__(self, nome_planilha):
        super().__init__(
            f"A planilha '{nome_planilha}' não foi encontrada ou está aberta."
        )


class ErroPreenchimentoSiggoError(DomainError):
    def __init__(self, detalhes):
        super().__init__(f"Falha ao preencher dados no SIGGO: {detalhes}")


class TemplateInvalidoError(DomainError):
    pass
