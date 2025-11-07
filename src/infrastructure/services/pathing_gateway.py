import re
import sys
from src.config import *
from src.core.gateways.i_pathing_gateway import IPathingGateway


class PathingGateway(IPathingGateway):

    def get_secon_root_path(self) -> str:
        """
        Determina o caminho correto para o arquivo de template,
        verificando se o usuário está usando o caminho base ou o do OneDrive.
        """
        username = os.getlogin().strip()
        caminho_base = (
            f"C:\\Users\\{username}\\Tribunal de Contas do Distrito Federal\\"
        )
        caminho_onedrive = f"C:\\Users\\{username}\\OneDrive - Tribunal de Contas do Distrito Federal\\"
        if os.path.exists(caminho_base + "SECON - General\\"):
            caminho_raiz = caminho_base
        elif os.path.exists(caminho_onedrive + "SECON - General\\"):
            caminho_raiz = caminho_onedrive
        else:
            raise FileNotFoundError(
                f"Não foi possível encontrar o caminho base ou do OneDrive para o usuário {username}."
            )
        return caminho_raiz

    def get_caminho_template(self, tipo_folha: str) -> str:
        return (
            self.get_secon_root_path()
            + f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\TEMPLATES\\TEMPLATES_NL_{tipo_folha.upper()}.xlsx"
        )

    def get_caminho_conferencia(self, fundo: str):
        return (
            self.get_secon_root_path()
            + f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{PASTA_MES_ATUAL}\\CONFERÊNCIA_{fundo}.xlsx"
        )

    def get_caminho_pasta_folha(self):
        return (
            self.get_secon_root_path()
            + f"SECON - General\\ANO_ATUAL\\FOLHA_DE_PAGAMENTO_{ANO_ATUAL}\\{PASTA_MES_ATUAL}"
        )

    def get_caminho_tabela_demofin(self):
        # Crie o caminho para a pasta onde o arquivo está

        caminho_pasta = self.get_caminho_pasta_folha()

        # Defina o padrão para o nome do arquivo (DEMOFIN_TABELA)
        # 're.IGNORECASE' ignora maiúsculas/minúsculas
        # '\\' é usado para escapar o caractere especial '-'
        # '*' torna o traço opcional
        padrao_nome = re.compile(r"demofin\s*[-_]?\s*tabela\.xlsx", re.IGNORECASE)

        # Itere sobre os arquivos na pasta e encontre o que corresponde ao padrão
        caminho_completo = None
        for nome_arquivo in os.listdir(caminho_pasta):
            if padrao_nome.search(nome_arquivo):
                caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
                break

        # Verifique se o arquivo foi encontrado antes de prosseguir
        if caminho_completo:
            return caminho_completo
        else:
            raise FileNotFoundError("Nenhum arquivo DEMOFIN_TABELA foi encontrado.")

    def get_caminho_pdf_relatorio(self):
        diretorio_alvo = os.path.join(
            self.get_secon_root_path(),
            "SECON - General",
            "ANO_ATUAL",
            f"FOLHA_DE_PAGAMENTO_{ANO_ATUAL}",
            PASTA_MES_ATUAL,
        )

        caminho_pdf_relatorio = None

        if os.path.exists(diretorio_alvo):
            for nome_arquivo in os.listdir(diretorio_alvo):
                # Converte para minúsculas para ignorar caixa alta/baixa
                nome_lower = nome_arquivo.lower()
                if nome_lower.startswith("relatórios") and nome_lower.endswith(".pdf"):
                    caminho_pdf_relatorio = os.path.join(diretorio_alvo, nome_arquivo)
                    return caminho_pdf_relatorio
        else:
            raise FileNotFoundError(
                f"Atenção: O diretório '{diretorio_alvo}' não foi encontrado."
            )

        if not caminho_pdf_relatorio:
            raise FileNotFoundError(
                "Nenhum arquivo PDF começando com 'RELATÓRIOS' foi encontrado."
            )

    def get_current_file_path(self) -> str:
        diretorio_atual = os.path.dirname(os.path.abspath(sys.argv[0]))
        return diretorio_atual

    def listar_arquivos(self, caminho: str) -> list[str]:
        try:
            arquivos = os.listdir(caminho)
            return arquivos
        except FileNotFoundError:
            raise FileNotFoundError(f"O caminho especificado '{caminho}' não foi encontrado.")
