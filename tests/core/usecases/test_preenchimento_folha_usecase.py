import pandas.testing as pd_testing
import pytest

from tests.mock_factories import GatewayFactoryMock, UseCaseFactoryMock

FUNDOS_TO_TEST = [
    "RGPS",
    #   "FINANCEIRO",
    #   "CAPITALIZADO"
]


@pytest.mark.parametrize("nome_fundo", FUNDOS_TO_TEST)
def test_preenchimento_folha_usecase(mocker, nome_fundo):
    templates = ["SUBSTITUICOES", "BENEFICIOS"]
    factory = UseCaseFactoryMock(mocker)
    preenchimento_uc = factory.create_preenchimento_folha_use_case(nome_fundo)

    dados_gerados = preenchimento_uc.executar(nome_fundo, templates)
    dados_preenchidos = preenchimento_uc.get_dados_preenchidos()

    try:
        for dados in dados_gerados.values():
            nl_gerada = dados["folha"]
            cabecalho_gerado = dados_gerados["cabecalho"]

            # TODO: verificar se os dataframes gerados batem com algum dos que foram preenchidos
            # Retirar da lista dos preenchidos se houver match

    except AssertionError as e:
        pytest.fail(f"DataFrame comparison failed:\n{e}")
