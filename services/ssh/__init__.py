from core.settings import VPS_HOST, VPS_USER, VPS_PASS
from services.ssh.nginx_manager import NginxManager

nginx_manager = NginxManager(
    ssh_host=VPS_HOST,
    ssh_user=VPS_USER,
    ssh_pass=VPS_PASS,
)
