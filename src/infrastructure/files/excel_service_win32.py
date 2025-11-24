from typing import Any, List, Optional
import pandas as pd
import os
import win32com.client as win32
from win32com.client import CDispatch

from pandas import DataFrame


# Assumindo que esta é a nova estrutura para usar o win32com
class ExcelServiceWin32:
    excel: Optional[CDispatch] = None
    workbook: Optional[CDispatch] = None

    def __init__(self, caminho_arquivo: str):
        self.caminho_arquivo = caminho_arquivo
        self.__enter__()

    def __enter__(self):
        """Inicializa e abre o Excel e o Workbook."""
        try:
            # 1. Abre a Aplicação Excel (invisível para o usuário)
            self.excel = win32.Dispatch("Excel.Application")
            self.excel.Visible = False  # Defina como True para ver a mágica
            self.excel.DisplayAlerts = False  # Não exibe pop-ups de alerta

            # 2. Abre o Workbook
            if not os.path.exists(self.caminho_arquivo):
                # Cria um novo se não existir (se o excel.Application estiver aberto)
                self.workbook = self.excel.Workbooks.Add()
                self.workbook.SaveAs(self.caminho_arquivo)
            else:
                self.workbook = self.excel.Workbooks.Open(self.caminho_arquivo)

            return self
        except Exception as e:
            if self.excel:
                self.excel.Quit()
            raise Exception(f"Erro ao inicializar Excel via win32com: {e}")

    def __exit__(self):
        """Salva e fecha o Workbook e a Aplicação Excel."""
        if self.workbook:
            try:
                # O save preserva conexões e outros objetos complexos
                self.workbook.Save()
            except Exception as e:
                print(f"Erro ao salvar o arquivo: {e}")
            finally:
                self.workbook.Close(SaveChanges=True)
        if self.excel:
            self.excel.Quit()

    def exportar_para_planilha(
        self,
        table: DataFrame,
        sheet_name: str,
        start_column="A",
        start_line="1",
        clear=False,
        sum_numeric=False,
        fit_columns=True,
        write_headers=True,
    ):
        """
        Exporta o DataFrame para uma planilha usando win32com, preservando conexões.
        """

        try:
            sheet = self.workbook.Sheets(sheet_name)
        except:
            sheet = self.workbook.Sheets.Add()
            sheet.Name = sheet_name

        if write_headers:
            data_to_write = [table.columns.tolist()] + table.values.tolist()
        else:
            data_to_write = table.values.tolist()

        if not data_to_write:
            if write_headers and not table.columns.empty:
                data_to_write = [table.columns.tolist()]
            else:
                print(f"DataFrame vazio. Nada exportado para a aba '{sheet_name}'.")
                return

        # 3. Define o intervalo de destino no Excel
        n_rows = len(data_to_write)
        n_cols = len(data_to_write[0])

        start_cell = f"{start_column}{start_line}"

        end_column_index = sheet.Range(start_column + "1").Column + n_cols - 1
        end_column = self.get_column_letter(end_column_index)
        end_row = int(start_line) + n_rows - 1
        end_cell = f"{end_column}{end_row}"

        target_range = sheet.Range(f"{start_cell}:{end_cell}")

        if clear:
            sheet.Range("A1", sheet.UsedRange.SpecialCells(11)).ClearContents()

        if fit_columns:
            target_range.EntireColumn.AutoFit()

        target_range.Value = data_to_write

    def get_column_letter(self, index):
        result = ""
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = chr(65 + remainder) + result
        return result

    def get_sheet(
        self, sheet_name: str, as_dataframe=False, header_row=1, columns=None
    ) -> CDispatch | DataFrame:
        """
        Retorna uma aba específica do arquivo Excel.
        Se as_dataframe=True, retorna como pandas DataFrame.
        """

        try:
            sheet = self.workbook.Sheets(sheet_name)
        except Exception:
            raise ValueError(f"Aba '{sheet_name}' não encontrada.")

        if not as_dataframe:
            return sheet

        data_range = sheet.UsedRange
        data_values = data_range.Value

        if not data_values:
            return pd.DataFrame()

        data_list = [list(row) for row in data_values]
        try:
            headers = data_list[header_row - 1]
            rows = data_list[header_row:]
        except IndexError:
            return pd.DataFrame()

        df = pd.DataFrame(rows, columns=headers)

        return df

    def delete_sheet(self, sheet_name: str) -> None:
        """
        Deleta uma aba (Worksheet) específica do Workbook pelo nome.
        """
        if not self.workbook:
            raise Exception("Workbook não está aberto.")

        # Desabilita o DisplayAlerts para suprimir o pop-up de confirmação de exclusão
        self.excel.DisplayAlerts = False
        try:
            # 1. Acessa a planilha pelo nome
            sheet = self.workbook.Sheets(sheet_name)
            # 2. Chama o método Delete()
            sheet.Delete()
            print(f"Aba '{sheet_name}' deletada com sucesso.")
        except Exception as e:
            print(f"Erro ao tentar deletar a aba '{sheet_name}': {e}")
            # Não lança o erro, apenas o imprime, pois a sheet pode não existir
        finally:
            # Restaura o DisplayAlerts
            self.excel.DisplayAlerts = True

    def delete_rows(
        self, sheet_name: str, start_row: int = 1, end_row: Optional[int] = None
    ):
        """
        Deleta linhas a partir de uma linha de início em uma planilha específica.
        Se end_row não for fornecido, deleta apenas a linha de início.
        """
        if not self.workbook:
            raise Exception("Workbook não está aberto.")

        try:
            sheet = self.workbook.Sheets(sheet_name)
        except Exception:
            print(f"Aba '{sheet_name}' não encontrada. Nenhuma linha deletada.")
            return

        # 1. Define o intervalo de linhas a ser deletado
        if end_row is None:
            # Deleta apenas a linha de início
            range_to_delete = sheet.Rows(start_row)
            msg = f"Linha {start_row}"
        else:
            # Deleta um intervalo de linhas (ex: 5:10)
            range_to_delete = sheet.Range(f"{start_row}:{end_row}")
            msg = f"Linhas {start_row} até {end_row}"

        # 2. Chama o método Delete (o valor padrão 'Shift' é xlShiftUp)
        try:
            range_to_delete.Delete()
            print(f"{msg} deletadas da aba '{sheet_name}'.")
        except Exception as e:
            print(f"Erro ao deletar {msg} da aba '{sheet_name}': {e}")

    def move_to_first(self, sheet_name: str) -> None:
        """
        Move a aba especificada para a primeira posição no Workbook.
        """
        if not self.workbook:
            raise Exception("Workbook não está aberto.")

        try:
            # 1. Acessa a aba que será movida
            sheet_to_move = self.workbook.Sheets(sheet_name)
            # 2. Acessa a primeira aba, que será o destino (Before)
            first_sheet = self.workbook.Sheets(1)

            # 3. Chama o método Move, especificando o destino (Before)
            sheet_to_move.Move(Before=first_sheet)
            print(f"Aba '{sheet_name}' movida para a primeira posição.")
        except Exception:
            raise ValueError(f"Aba '{sheet_name}' não encontrada ou erro ao mover.")

    def destacar_linhas(
        self,
        sheet_name: str,
        cor_fundo: str = "FFFF00",  # Cor amarela em Hex (BGR)
        negrito: bool = False,
        coluna_alvo: str = None,
        valor_alvo: Any = None,
        header_row: int = 1,
    ) -> None:
        """
        Aplica formatação condicional simples (destaca linhas) na aba.
        Se coluna_alvo e valor_alvo forem fornecidos, destaca apenas as linhas onde
        a coluna_alvo corresponde ao valor_alvo.
        Se forem None, destaca o cabeçalho.
        """
        if not self.workbook:
            raise Exception("Workbook não está aberto.")

        # Converte a cor HEX (RGB, ex: FF0000 para vermelho) para o formato BGR esperado pelo Excel (ex: 0000FF para vermelho)
        try:
            # Inverte os bytes: RRGGBB -> BBGGRR (o win32com espera um inteiro BGR)
            bgr_color = int(cor_fundo[4:6] + cor_fundo[2:4] + cor_fundo[0:2], 16)
        except ValueError:
            print(f"Cor '{cor_fundo}' inválida. Usando amarelo padrão.")
            bgr_color = int("00FFFF", 16)  # Amarelo padrão (BGR)

        try:
            sheet = self.workbook.Sheets(sheet_name)
        except Exception:
            raise ValueError(f"Aba '{sheet_name}' não encontrada.")

        # 1. Destacar Cabeçalho (Comportamento Padrão ou se coluna_alvo for None)
        if coluna_alvo is None and valor_alvo is None:
            # Intervalo de Cabeçalho (Linha inteira)
            header_range = sheet.Rows(header_row)
            header_range.Interior.Color = bgr_color
            if negrito:
                header_range.Font.Bold = True
            print(f"Cabeçalho (Linha {header_row}) da aba '{sheet_name}' destacado.")
            return

        # 2. Destacar Linhas Condicionalmente
        if coluna_alvo and valor_alvo is not None:
            # Lendo os dados para aplicar a formatação condicional no Python
            data_range = sheet.UsedRange
            data_values = data_range.Value

            if not data_values:
                print("Planilha vazia. Nenhuma formatação aplicada.")
                return

            # Cria lista de cabeçalhos para encontrar o índice da coluna alvo
            # Data_values é 1-indexado, então o cabeçalho é o elemento [header_row - 1]
            headers = data_values[header_row - 1]
            try:
                # O Excel/win32com é 1-indexado, então adicionamos 1
                col_index = headers.index(coluna_alvo) + 1
            except ValueError:
                print(
                    f"Coluna alvo '{coluna_alvo}' não encontrada. Nenhuma formatação aplicada."
                )
                return

            # Itera sobre os dados (começando após o cabeçalho)
            for i, row in enumerate(data_values):
                # O índice 'i' aqui é 0-based a partir da tupla 'data_values',
                # mas queremos pular o cabeçalho e usar o número da linha do Excel.
                excel_row = i + 1

                # Pula as linhas de cabeçalho
                if excel_row <= header_row:
                    continue

                # Acessa o valor na coluna alvo (col_index - 1 é o índice Python)
                current_value = row[col_index - 1]

                if current_value == valor_alvo:
                    # Aplica a formatação em toda a linha
                    target_row_range = sheet.Rows(excel_row)
                    target_row_range.Interior.Color = bgr_color
                    if negrito:
                        target_row_range.Font.Bold = True

            print(
                f"Formatação condicional aplicada na aba '{sheet_name}' para linhas onde '{coluna_alvo}' é igual a '{valor_alvo}'."
            )
