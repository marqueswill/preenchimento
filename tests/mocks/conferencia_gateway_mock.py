from src.infrastructure.services.conferencia_gateway import ConferenciaGateway


class ConferenciaGatewayMock(ConferenciaGateway):
    def __init__(self, pathing_gw, excel_svc):
        super().__init__(pathing_gw, excel_svc)
