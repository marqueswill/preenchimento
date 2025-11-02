import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest.mock import MagicMock
import os

# Importações das suas classes
from src.infrastructure.services.conferencia_gateway import ConferenciaGateway
from src.core.gateways.i_pathing_gateway import IPathingGateway
from src.core.gateways.i_excel_service import IExcelService
from tests.mocks.pathing_gateway_mock import PathingGatewayMock


@pytest.fixture
def gateway_com_mocks(mocker) -> tuple[ConferenciaGateway, IPathingGateway, MagicMock]:
    """
    Cria uma instância real do ConferenciaGateway, 
    injetando mocks para suas dependências de construtor.
    """
    # 1. Cria os mocks para as interfaces
    # pathing_gw_mock = mocker.MagicMock(spec=IPathingGateway)
    pathing_gw_mock = PathingGatewayMock()
    excel_svc_mock = mocker.MagicMock(spec=IExcelService)

    # 2. Cria a instância real do Gateway com os mocks injetados
    gateway = ConferenciaGateway(
        pathing_gw=pathing_gw_mock, 
        excel_svc=excel_svc_mock
    )

    return gateway, pathing_gw_mock, excel_svc_mock


def test_get_tabela_demofin_deve_ler_excel_corretamente(gateway_com_mocks):
    """
    Testa (Integração) se o gateway consegue ler um arquivo Excel real
    e se os cabeçalhos (headers) estão corretos.
    """
    
    gateway, _, _ = gateway_com_mocks


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


def test_parse_relatorio_deve_ler_pdf_corretamente(gateway_com_mocks):
    """
    Testa (Integração) se o gateway consegue ler um arquivo PDF real.
    """
    # Arrange
    gateway, pathing_gw, _ = gateway_com_mocks

    caminho_gabarito = os.path.join(
        pathing_gw.get_secon_root_path(),"relatorio_extraido.txt")

    expected_text = ""
    try:
        with open(caminho_gabarito, "r", encoding="utf-8") as f:
            expected_text = f.read()
    except FileNotFoundError:
        pytest.fail(f"Arquivo de gabarito não encontrado em: {caminho_gabarito}")
    except Exception as e:
        pytest.fail(f"Erro ao ler arquivo de gabarito: {e}")

    result_text = gateway.parse_relatorio()

    assert expected_text == result_text
