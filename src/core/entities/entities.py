from pandas import DataFrame
from dataclasses import dataclass


@dataclass
class NotaLancamento:
    _dados: DataFrame


    def __post_init__(self):
        self._sanitizar_dados()
        self._checar_formato()
    
    def _sanitizar_dados(self):
        self._dados.replace(["nan", ""], ".", inplace=True)

        if "CLASS. ORC" in self._dados.columns:
            self._dados["CLASS. ORC"] = (
                self._dados["CLASS. ORC"]
                .apply(lambda x: str(x)[1:] if len(str(x)) == 9 else str(x))
                .astype(str)
            )


    def _checar_formato(self):
        colunas_obrigatorias = {
            "EVENTO", "INSCRIÇÃO", "CLASS. CONT", "CLASS. ORC", 
            "FONTE", "VALOR"
        }
        
        if not colunas_obrigatorias.issubset(self._dados.columns):
            faltantes = colunas_obrigatorias - set(self._dados.columns)
            raise ValueError(f"O DataFrame não possui as colunas obrigatórias. Faltando: {faltantes}")



        evento = self._dados["CLASS. CONT"].astype(str).str.strip()
        if not evento.str.match(r'(^\d{9}$|^\.$)').all():
            raise ValueError("O evento deve conter 8 dígitos.")


        class_cont = self._dados["CLASS. CONT"].astype(str).str.strip()
        if not class_cont.str.match(r'(^\d{9}$|^\.$)').all():
            raise ValueError("A classificação contábil, caso existir, deve conter 9 dígitos.")

        class_orc = self._dados["CLASS. ORC"].astype(str).str.strip()
        if not class_orc.str.match(r'(^\d{8}$|^\.$)').all():
            raise ValueError("A classificação oraçamentária, caso existir, deve conter 8 dígitos.")

    @property
    def cabecalhos(self):
        return self._dados.columns

    def esta_vazia(self) -> bool:
        return self._dados.empty

class TemplateNotaLancamento(NotaLancamento):
    def _checar_formato(self):
        colunas_obrigatorias = {
            "EVENTO", "INSCRIÇÃO", "CLASS. CONT", "CLASS. ORC", 
            "FONTE", "VALOR","SOMAR", "SUBTRAIR", "TIPO"
        }

        if not colunas_obrigatorias.issubset(self._dados.columns):
            faltantes = colunas_obrigatorias - set(self._dados.columns)
            raise ValueError(f"O DataFrame não possui as colunas obrigatórias. Faltando: {faltantes}")

        return super()._checar_formato()

@dataclass
class CabecalhoNL:
    _dados: dict


@dataclass
class DadosPreenchimento:
    _dados_lancamento: NotaLancamento
    _dados_cabecalho: CabecalhoNL
