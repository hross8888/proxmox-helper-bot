import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()


def read_secret_file(key: str) -> str | None:
    secret_path = os.path.join("/run/secrets", key)

    if os.path.exists(secret_path):
        try:
            with open(secret_path, 'r') as f:
                return f.read().strip()
        except Exception:
            return None
    return None

REDIS_HOST: Optional[str] = read_secret_file("REDIS_HOST") or os.getenv("REDIS_HOST")
BOT_TOKEN: Optional[str] = read_secret_file("BOT_TOKEN") or os.getenv("BOT_TOKEN")
PVE_HOST: Optional[str] = read_secret_file("PVE_HOST") or os.getenv("PVE_HOST")
PVE_PORT: Optional[str] = read_secret_file("PVE_PORT") or os.getenv("PVE_PORT")
PVE_NODE: Optional[str] = read_secret_file("PVE_NODE") or os.getenv("PVE_NODE")
PVE_TOKEN: Optional[str] = read_secret_file("PVE_TOKEN") or os.getenv("PVE_TOKEN")
CF_TOKEN: Optional[str] = read_secret_file("CF_TOKEN") or os.getenv("CF_TOKEN")
DOMAIN: Optional[str] = read_secret_file("DOMAIN") or os.getenv("DOMAIN")
DEFAULT_GW: Optional[str] = read_secret_file("DEFAULT_GW") or os.getenv("DEFAULT_GW")
DEFAULT_DNS: Optional[str] = read_secret_file("DEFAULT_DNS") or os.getenv("DEFAULT_DNS")
IP_RANGE_START: Optional[str] = read_secret_file("IP_RANGE_START") or os.getenv("IP_RANGE_START")
IP_RANGE_END: Optional[str] = read_secret_file("IP_RANGE_END") or os.getenv("IP_RANGE_END")
DEFAULT_VM_USER: Optional[str] = read_secret_file("DEFAULT_VM_USER") or os.getenv("DEFAULT_VM_USER")
VPS_HOST: Optional[str] = read_secret_file("VPS_HOST") or os.getenv("VPS_HOST")
VPS_USER: Optional[str] = read_secret_file("VPS_USER") or os.getenv("VPS_USER")
VPS_PASS: Optional[str] = read_secret_file("VPS_PASS") or os.getenv("VPS_PASS")

DEBUG: bool = (os.getenv("DEBUG") is not None)


PVE_PORT_FINAL = PVE_PORT if PVE_PORT else "8006"

PVE_URL: str = f"https://{PVE_HOST}:{PVE_PORT_FINAL}/api2/json"
REDIS_URL: str = f"redis://{REDIS_HOST}:6379/0"

ADMIN_IDS_STR: Optional[str] = read_secret_file("ADMIN_IDS") or os.getenv("ADMIN_IDS")
ADMIN_IDS: List[int] = [int(x) for x in (ADMIN_IDS_STR or "").split(";") if x]