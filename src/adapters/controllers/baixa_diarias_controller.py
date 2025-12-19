from src.factories import UseCaseFactory

def BaixaDiariasController(run=True, test=False):
    factory = UseCaseFactory()
    use_case = factory.create_baixa_diarias_usecase()
    use_case.executar()


if __name__ == "__main__":
    BaixaDiariasController()
