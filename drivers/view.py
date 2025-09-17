import os
import sys
import time


class ConsoleView:
    """
    Responsável por toda a interação com o usuário via console.
    Agrupa funções de exibição de menus, obtenção de entrada e mensagens.
    """

    def display_menu(self,opcoes: list[str], mensagem="Selecione uma opção:", selecionar_todos=False, permitir_voltar=False):
        """Exibe um menu de opções no console."""
        self.clear_console()
        print(mensagem)
        if selecionar_todos:
            print("0. TODOS")
        for i, opcao in enumerate(opcoes, start=1):
            print(f"{i}. {opcao}")

        print()
        if permitir_voltar:
            print("V. VOLTAR")
        print("X. SAIR\n")

    def get_user_input(self, opcoes: list[str], selecionar_todos=False, permitir_voltar=False):
        """Obtém e valida a entrada do usuário a partir do menu exibido."""
        while True:
            escolha = input("Digite o número correspondente: ").strip().upper()

            if escolha == 'X':
                sys.exit()
            elif permitir_voltar and escolha == 'V':
                return None
            elif selecionar_todos and escolha == '0':
                return opcoes
            elif escolha.isdigit() and int(escolha) in range(1, len(opcoes) + 1):
                return [opcoes[int(escolha) - 1]]
            else:
                input("Opção inválida. Pressione ENTER para tentar novamente.")
                self.clear_console()
                self.display_menu(opcoes, selecionar_todos=selecionar_todos,
                            permitir_voltar=permitir_voltar)

    def show_processing_message(self, message: str):
        """Exibe uma mensagem de processamento com uma animação de pontinhos."""
        print(f"\n{message}", end='', flush=True)
        for _ in range(3):
            print(".", end='', flush=True)
            time.sleep(0.5)

    #TODO: ConsoleView
    def clear_console(self):
        """Limpa a tela do console."""
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')

    def show_message(self, message: str):
        """Exibe uma mensagem e espera que o usuário pressione ENTER."""
        input(f"\n{message}\nPressione ENTER para sair.")

    @staticmethod
    def color_text(text, color=None, style=None, background=None):
        # ANSI color codes
        colors = {
            "black": 30, "red": 31, "green": 32, "yellow": 33,
            "blue": 34, "magenta": 35, "cyan": 36, "white": 37
        }
        styles = {
            "normal": 0, "bold": 1, "underline": 4
        }
        backgrounds = {
            "black": 40, "red": 41, "green": 42, "yellow": 43,
            "blue": 44, "magenta": 45, "cyan": 46, "white": 47
        }

        codes = []

        if style in styles:
            codes.append(str(styles[style]))
        if color in colors:
            codes.append(str(colors[color]))
        if background in backgrounds:
            codes.append(str(backgrounds[background]))

        prefix = f"\033[{';'.join(codes)}m" if codes else ""
        suffix = "\033[0m" if codes else ""

        return f"{prefix}{text}{suffix}"


    @staticmethod
    def color_print(*args, color=None, style=None, background=None, sep=" ", end="\n"):
        colored_args = [ConsoleView.color_text(
            str(arg), color=color, style=style, background=background) for arg in args]
        print(*colored_args, sep=sep, end=end)

# TODO: ExcelExporter
# TODO: Logger para isolar prints de debug