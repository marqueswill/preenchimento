from core.gateways.i_pathing_gateway import IPathingGateway
from infrastructure.services.pathing_gateway import PathingGateway


pathing_gw: IPathingGateway = PathingGateway()

ROOT_PATH = pathing_gw.get_root_path()
