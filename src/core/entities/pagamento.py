from dataclasses import dataclass
from decimal import Decimal
from datetime import date


@dataclass
class Lancamento:
    evento: str
    inscricao: str
    class_cont: str
    class_orc: str
    fonte: str
    valor: Decimal


@dataclass
class CabecalhoNL:
    prioridade: str
    tipo_credor: str
    gestao: str
    processo: str
    observacao_template: str


@dataclass
class FolhaPagamento:
    cabecalho: CabecalhoNL
    lancamentos: list[Lancamento]


@dataclass
class DadosDemofin:
    cdg_provdesc: int
    nme_nat_despesa: str
    cdg_nat_despesa: str
    valor_auxiliar: Decimal
    nme_provdesc: str
    cdg_fundo: int


# TODO: definir o resto das entidades
