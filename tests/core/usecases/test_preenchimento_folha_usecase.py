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
    # print(dados_preenchidos["SUBSTITUICOES"]["folha"])
    # try:
    #     for template in dados_gerados.keys():
    #         nl_gerada = dados_gerados[template]["folha"]
    #         nl_preenchida = dados_preenchidos[template]["folha"]
    #         cabecalho_gerado = dados_gerados[template]["cabecalho"]
    #         cabecalho_preenchido = dados_preenchidos[template]["cabecalho"]

    #         pd_testing.assert_frame_equal(nl_gerada, nl_preenchida)
    #         pd_testing.assert_frame_equal(cabecalho_gerado, cabecalho_preenchido)

    # except AssertionError as e:
    #     pytest.fail(f"DataFrame comparison failed:\n{e}")
