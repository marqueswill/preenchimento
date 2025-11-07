import pandas.testing as pd_testing
import pytest

from tests.mock_factories import GatewayFactoryMock, UseCaseFactoryMock

FUNDOS_TO_TEST = [
    "RGPS",
    "FINANCEIRO",
    "CAPITALIZADO",
]


@pytest.mark.parametrize("nome_fundo", FUNDOS_TO_TEST)
def test_preenchimento_folha_usecase(mocker, nome_fundo):
    factory = UseCaseFactoryMock(mocker)
    preenchimento_uc = factory.create_preenchimento_folha_use_case(nome_fundo)

    # templates = preenchimento_uc.get_nomes_templates(nome_fundo)
    templates = ["PRINCIPAL"]
    dados_gerados = preenchimento_uc.executar(nome_fundo, templates)
    dados_preenchidos = preenchimento_uc.get_dados_preenchidos()

    for d1, d2 in zip(dados_gerados, dados_preenchidos):
        print("\n\n", d1["folha"])
        print("\n", d2["folha"])
        pd_testing.assert_frame_equal(d1["folha"], d2["folha"])
