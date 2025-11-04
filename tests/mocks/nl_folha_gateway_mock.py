from src.infrastructure.services.nl_folha_gateway import NLFolhaGateway


class NLFolhaGatewayMock(NLFolhaGateway):
    def __init__(self, pathing_gw):
        super().__init__(pathing_gw)
