from core.settings import *
from services.pve.api import ProxmoxAPI

proxmox = ProxmoxAPI(
        api_url=PVE_URL,
        token=PVE_TOKEN,
        node=PVE_NODE,
        default_gw=DEFAULT_GW,
        default_dns=DEFAULT_DNS,
    )