from src.infrastructure.files.excel_service import ExcelService


class ExcelServiceMock(ExcelService):
    def __init__(self, caminho_arquivo):
        super().__init__(caminho_arquivo)
