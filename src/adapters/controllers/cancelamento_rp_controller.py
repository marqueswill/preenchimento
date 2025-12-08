from src.factories import UseCaseFactory


def CancelamentoRPController(run=True, test=False):
    factory = UseCaseFactory()
    use_case = factory.create_cancelamento_rp_usecase()
    use_case.executar()


if __name__ == "__main__":
    CancelamentoRPController()
