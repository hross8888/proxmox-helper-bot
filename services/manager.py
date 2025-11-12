import asyncio

from loguru import logger

from bot.shema import CreateVmShema
from core.models import Vm
from services.cloudflare import cloudflare
from services.pve import proxmox
from services.pve.utils.free_ip import get_free_ip
from services.ssh import nginx_manager
from services.ssh.wait_ssh import wait_for_ssh


class Manager:
    """Оркестратор, объединяющий работу Proxmox, Cloudflare и Nginx."""

    def __init__(self, domain: str):
        self.proxmox = proxmox
        self.cloudflare = cloudflare
        self.nginx = nginx_manager
        self.domain = domain

    async def start_vm(self, *, vmid: int):
        await self.proxmox.start_vm(vmid=vmid)

    async def stop_vm(self, *, vmid: int):
        await self.proxmox.stop_vm(vmid=vmid)

    async def reboot_vm(self, *, vmid: int):
        await self.proxmox.reboot_vm(vmid=vmid)

    async def create_vm(self, *, data: CreateVmShema, ciuser) -> tuple[str, int]:
        """Создает VM"""
        ip = await get_free_ip()
        vm_id = await self.proxmox.create_vm(ciuser=ciuser, ip=ip, **data.model_dump())
        await wait_for_ssh(ip)
        await Vm.create(vm_id=vm_id, name=data.name, ip_address=ip, password=data.password)
        return ip, vm_id

    async def create_domain(self, *, name: str, content: str, vm_ip: str, vm_user: str, vm_pass: str) -> str:
        """Создает домен на клауде и вирт хост на vps."""
        full_domain = f"{name}.{self.domain}"
        await self.cloudflare.create_record(name=full_domain, content=content)
        await self.nginx.full_setup(domain=full_domain, target_ip=vm_ip, vm_user=vm_user, vm_pass=vm_pass)
        return full_domain

    async def delete_vm(self, *, name: str, vmid: int, with_domain=True):
        """Удаляет VM, DNS и nginx-прокси."""
        if with_domain:
            full_domain = f"{name}.{self.domain}"
            logger.info(f"Удаление VM {vmid} ({full_domain})")

            # Удалить nginx-прокси
            try:
                await self.nginx.remove_vhost(full_domain)
            except Exception as e:
                logger.warning(f"Ошибка при удалении vhost: {e}")

            # Удалить DNS-запись
            try:
                await self.cloudflare.delete_record(full_domain)
            except Exception as e:
                logger.warning(f"Ошибка при удалении DNS: {e}")

        # Удалить VM
        try:
            vm_info = await self.proxmox.vm_info(vmid)
            if vm_info.status == "running":
                logger.debug(f"VM {vmid} запущена, останавливаю...")
                await self.proxmox.stop_vm(vmid)

                # ждём до 30 секунд пока реально остановится
                for _ in range(30):
                    vm_info = await self.proxmox.vm_info(vmid)
                    if vm_info.status != "running":
                        break
                    await asyncio.sleep(1)
                else:
                    logger.warning(f"VM {vmid} не остановилась вовремя — удаляю принудительно")

            # 4. Удаляем VM
            await self.proxmox.delete_vm(vmid)
            logger.info(f"VM {vmid} полностью удалена")

        except Exception as e:
            logger.error(f"Ошибка при удалении VM {vmid}: {e}")

        await Vm.filter(vm_id=vmid).delete()

    async def reload_nginx(self, *, vm_ip: str, vm_user: str, vm_pass: str):
        await self.nginx.reload(vm_ip=vm_ip, vm_user=vm_user, vm_pass=vm_pass)

    async def set_config_nginx(self, *, vm_ip: str, vm_user: str, vm_pass: str, config: str):
        await self.nginx.set_config(vm_ip=vm_ip, vm_user=vm_user, vm_pass=vm_pass, config=config)

    async def get_config_nginx(self, *, vm_ip: str, vm_user: str, vm_pass: str) -> str:
        return await self.nginx.get_config(vm_ip=vm_ip, vm_user=vm_user, vm_pass=vm_pass)