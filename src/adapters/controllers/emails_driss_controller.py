from src.factories import UseCaseFactory


def EmailsDrissController(run=True, test=False):
    factory = UseCaseFactory()
    use_case = factory.create_emails_driss_usecase()
    use_case.executar()
