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

    for d1, d2 in zip(dados_gerados, dados_preenchidos):
        print("\n\n", d1["folha"])
        print("\n\n", d2["folha"])
        # print("\n\n", d1["cabecalho"])
        # print("\n\n", d2["cabecalho"])
        pd_testing.assert_frame_equal(d1["folha"], d2["folha"])
        # pd_testing.assert_frame_equal(d1["cabecalho"], d2["cabecalho"])

    return
    # Copiamos a lista de preenchidos para poder remover os itens encontrados
    dados_preenchidos_restantes = dados_preenchidos.copy()
    dados_gerados_nao_encontrados = []

    for dados_ger in dados_gerados:
        try:
            nl_gerada = dados_ger["folha"]
            cabecalho_gerado = dados_ger["cabecalho"]
        except KeyError:
            pytest.fail(
                "O dicionário em 'dados_gerados' não continha as chaves 'folha' ou 'cabecalho'"
            )

        match_encontrado_idx = None

        # Procura um match na lista de preenchidos restantes
        for i, dados_pre in enumerate(dados_preenchidos_restantes):
            try:
                nl_preenchida = dados_pre["folha"]
                cabecalho_preenchido = dados_pre["cabecalho"]

                # Compara os DataFrames usando o testing do pandas
                pd_testing.assert_frame_equal(nl_gerada, nl_preenchida)
                pd_testing.assert_frame_equal(cabecalho_gerado, cabecalho_preenchido)

                # Se ambas as comparações passarem, encontramos o match
                match_encontrado_idx = i
                break  # Sai do loop interno

            except (AssertionError, KeyError):
                # AssertionError: Os DFs não são iguais.
                # KeyError: O dict 'dados_pre' não tinha 'folha' or 'cabecalho'.
                # Em ambos os casos, apenas continua para o próximo item.
                pass

        if match_encontrado_idx is not None:
            # Remove o item que deu match da lista de restantes
            dados_preenchidos_restantes.pop(match_encontrado_idx)
        else:
            # Se o loop terminar e não houver match, adiciona à lista de falhas
            dados_gerados_nao_encontrados.append(dados_ger)

    # --- Verificações Finais ---

    # 1. Verifica se todos os DFs gerados encontraram um par
    if dados_gerados_nao_encontrados:
        pytest.fail(
            f"{len(dados_gerados_nao_encontrados)} conjunto(s) de DataFrame(s) gerados "
            "não foram encontrados na lista de dados preenchidos."
        )

    # 2. Verifica se não sobrou nenhum DF preenchido (garante que as listas são idênticas)
    if dados_preenchidos_restantes:
        pytest.fail(
            f"{len(dados_preenchidos_restantes)} conjunto(s) de DataFrame(s) preenchidos "
            "não corresponderam a nenhum item gerado (dados excedentes)."
        )
