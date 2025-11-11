import os
import re
import PyPDF2
import pandas as pd
from datetime import datetime
from pandas import DataFrame

from src.factories import UseCaseFactory
from src.infrastructure.cli.console_service import ConsoleService
from src.config import *


def ExportarValoresPagosController():
    app_view = ConsoleService()
    factory = UseCaseFactory()
    use_case = factory.create_extrair_dados_r2000_usecase()
    use_case.exportar_valores_pagos()

