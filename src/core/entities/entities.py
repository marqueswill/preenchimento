from pandas import DataFrame
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class NotaLancamento:
    dados: DataFrame
    nome: str = ""

    def __post_init__(self):
        self._checar_formato()

    def _checar_formato(self):
        colunas_obrigatorias = {
            "EVENTO",
            "INSCRIÇÃO",
            "CLASS. CONT",
            "CLASS. ORC",
            "FONTE",
            "VALOR",
        }

        if not colunas_obrigatorias.issubset(self.dados.columns):
            faltantes = colunas_obrigatorias - set(self.dados.columns)
            raise ValueError(
                f"NL-{self.nome}: O DataFrame não possui as colunas obrigatórias. Faltando: {faltantes}"
            )

        evento = self.dados["EVENTO"].astype(str).str.strip()
        if not evento.str.match(r"(^\d{6}$|^\.$)").all():
            raise ValueError(f"NL-{self.nome}: O evento deve conter 6 dígitos.")

        class_cont = self.dados["CLASS. CONT"].astype(str).str.strip()
        if not class_cont.str.match(r"(^\d{9}$|^\.$)").all():
            raise ValueError(
                f"NL-{self.nome}: A classificação contábil, caso existir, deve conter 9 dígitos."
            )

        class_orc = self.dados["CLASS. ORC"].astype(str).str.strip()
        if not class_orc.str.match(r"(^\d{8}$|^\.$)").all():
            raise ValueError(
                f"NL-{self.nome}: A classificação oraçamentária, caso existir, deve conter 8 dígitos."
            )

    @property
    def cabecalhos(self):
        return self.dados.columns

    def esta_vazia(self) -> bool:
        return self.dados.empty


@dataclass
class TemplateNL(NotaLancamento):
    def _checar_formato(self):
        colunas_obrigatorias = {
            "EVENTO",
            "INSCRIÇÃO",
            "CLASS. CONT",
            "CLASS. ORC",
            "FONTE",
            "VALOR",
            "SOMAR",
            "SUBTRAIR",
            "TIPO",
        }

        if not colunas_obrigatorias.issubset(self.dados.columns):
            faltantes = colunas_obrigatorias - set(self.dados.columns)
            raise ValueError(
                f"NL-{self.nome}: O DataFrame não possui as colunas obrigatórias. Faltando: {faltantes}"
            )

        return super()._checar_formato()


@dataclass
class CabecalhoNL:
    prioridade: str = ""
    credor: str = ""
    gestao: str = ""
    processo: str = ""
    observacao: str = ""
    contrato: str = ""

    def get_all(self) -> dict:
        return asdict(self)


@dataclass
class DadosPreenchimento:
    lancamento: NotaLancamento
    cabecalho: CabecalhoNL
