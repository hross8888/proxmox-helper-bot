import yaml
import os

def build_cloud_init_yaml(ciuser: str, password: str) -> str:
    data = {
        "ssh_pwauth": True,
        "disable_root": False,
        "chpasswd": {
            "list": f"{ciuser}:{password}",
            "expire": False,
        },
        "runcmd": [
            "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
            "systemctl restart ssh",
        ],
    }
    return yaml.safe_dump(data, sort_keys=False)