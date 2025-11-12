import ipaddress

from core.models import Vm
from core.settings import IP_RANGE_START, IP_RANGE_END


async def get_free_ip() -> str:
    start_ip = ipaddress.IPv4Address(IP_RANGE_START)
    end_ip = ipaddress.IPv4Address(IP_RANGE_END)

    used_ips = {vm.ip_address for vm in await Vm.all() if vm}

    for ip_int in range(int(start_ip), int(end_ip) + 1):
        ip = str(ipaddress.IPv4Address(ip_int))
        if ip not in used_ips:
            return ip

    raise RuntimeError("No free IP addresses available in range")