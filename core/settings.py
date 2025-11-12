import os

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST=os.getenv("REDIS_HOST")
BOT_TOKEN=os.getenv("BOT_TOKEN")
PVE_HOST=os.getenv("PVE_HOST")
PVE_PORT=os.getenv("PVE_PORT")
PVE_NODE=os.getenv("PVE_NODE")
PVE_TOKEN=os.getenv("PVE_TOKEN")
CF_TOKEN=os.getenv("CF_TOKEN")
DOMAIN=os.getenv("DOMAIN")
DEFAULT_GW=os.getenv("DEFAULT_GW")
DEFAULT_DNS=os.getenv("DEFAULT_DNS")
IP_RANGE_START=os.getenv("IP_RANGE_START")
IP_RANGE_END=os.getenv("IP_RANGE_END")
DEFAULT_VM_USER=os.getenv("DEFAULT_VM_USER")
VPS_HOST=os.getenv("VPS_HOST")
VPS_USER=os.getenv("VPS_USER")
VPS_PASS=os.getenv("VPS_PASS")
DEBUG=os.getenv("DEBUG") is not None


PVE_URL=f"https://{PVE_HOST}:{PVE_PORT}/api2/json"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(";") if x]

REDIS_URL = f"redis://{REDIS_HOST}:6379/0"