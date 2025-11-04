import pandas.testing as pd_testing
import pytest

from tests.mock_factories import GatewayFactoryMock, UseCaseFactoryMock

# --- Test Data ---
# List of the method names you want to call and compare
DATA_METHODS_TO_TEST = [
    "get_proventos_conferencia",
    "get_descontos_conferencia",
    "get_totais_conferencia",
    "get_proventos_relatorio",
    "get_descontos_relatorio",
]

FUNDOS_TO_TEST = ["RGPS", "FINANCEIRO", "CAPITALIZADO"]

def get_data_for_comparison(excel_svc, excel_svc_gabarito, method_name):
    """
    Chama os métodos forncidos para planilha excel gerada e para a planilha
    de gabarito
    """

    get_actual_method = getattr(excel_svc, method_name)
    actual_data = get_actual_method()

    get_expected_method = getattr(excel_svc_gabarito, method_name)
    expected_data = get_expected_method()

    return actual_data, expected_data


@pytest.mark.parametrize("method_name", DATA_METHODS_TO_TEST)
@pytest.mark.parametrize("nome_fundo", FUNDOS_TO_TEST)


def test_gerar_conferencia_rgps_usecase(mocker, method_name, nome_fundo):
    factory_uc = UseCaseFactoryMock()
    factory_gw = GatewayFactoryMock()
    conferencia_uc = factory_uc.create_gerar_conferencia_use_case(nome_fundo)
    pathing_gw = factory_gw.create_pathing_gateway()

    conferencia_uc.executar(nome_fundo)

    excel_svc = factory_gw.create_excel_service(nome_fundo)
    excel_svc_gabarito = factory_gw.create_excel_service_with_path(
        pathing_gw.get_caminho_conferencia_esperada(nome_fundo)
    )

    actual_df, expected_df = get_data_for_comparison(
        excel_svc, excel_svc_gabarito, method_name
    )

    try:
        pd_testing.assert_frame_equal(actual_df, expected_df)
        
    except AssertionError as e:
        pytest.fail(f"DataFrame comparison failed for {method_name}:\n{e}")
