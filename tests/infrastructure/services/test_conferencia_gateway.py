import pytest
import os


from tests.mock_factories import GatewayFactoryMock


def test_get_tabela_demofin_deve_ler_excel_corretamente(mocker):
    """
    Testa (Integração) se o gateway consegue ler um arquivo Excel real
    e se os cabeçalhos (headers) estão corretos.
    """

    factory = GatewayFactoryMock(mocker)
    gateway = factory.create_conferecia_gateway()

    expected_headers = [
        "CDG_FUNDO",
        "NME_FUNDO",
        "CDG_NAT_DESPESA",
        "NME_NAT_DESPESA",
        "CDG_PROVDESC",
        "NME_PROVDESC",
        "VALOR",
        "QTD",
        "RUBRICA",
        "VALOR_AUXILIAR",
    ]

    result_df = gateway.get_tabela_demofin()

    actual_headers = result_df.columns.tolist()

    assert actual_headers == expected_headers


def test_parse_relatorio_deve_ler_pdf_corretamente(mocker):
    """
    Testa (Integração) se o gateway consegue ler um arquivo PDF real.
    """
    # Arrange
    factory = GatewayFactoryMock(mocker)
    conferencia_gw = factory.create_conferecia_gateway()
    pathing_gw = factory.create_pathing_gateway()

    caminho_gabarito = os.path.join(
        pathing_gw.get_secon_root_path(), "expected","relatorio_extraido.txt"
    )

    expected_text = ""
    try:
        with open(caminho_gabarito, "r", encoding="utf-8") as f:
            expected_text = f.read()
    except FileNotFoundError:
        pytest.fail(f"Arquivo de gabarito não encontrado em: {caminho_gabarito}")
    except Exception as e:
        pytest.fail(f"Erro ao ler arquivo de gabarito: {e}")

    result_text = conferencia_gw.parse_relatorio()

    assert expected_text == result_text
