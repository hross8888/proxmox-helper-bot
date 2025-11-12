import asyncio
import httpx
from typing import Optional
from loguru import logger

from services.pve.dto import PveCloneDTO
from services.pve.shema import VmInfo


class ProxmoxAPI:
    """Асинхронный клиент для работы с Proxmox VE API."""

    def __init__(self, api_url: str, token: str, node: str, *, default_gw: str, default_dns: str):
        self.api_url = api_url.rstrip("/")
        self.node = node
        self.headers = {"Authorization": f"PVEAPIToken={token}"}
        self.client = httpx.AsyncClient(verify=False, timeout=30)
        self.default_gw = default_gw
        self.default_dns = default_dns

    async def close(self):
        await self.client.aclose()

    # =============================================================
    # === ОСНОВНЫЕ ОПЕРАЦИИ ===
    # =============================================================

    async def get_vm_list(self, templates_only: bool = False) -> list[VmInfo]:
        """Получить список VM"""
        r = await self.client.get(f"{self.api_url}/nodes/{self.node}/qemu", headers=self.headers)
        r.raise_for_status()
        data = r.json()["data"]
        return [VmInfo(**vm) for vm in data if bool(vm.get("template")) == templates_only]

    async def _next_id(self) -> int:
        """Получить следующий свободный VMID."""
        r = await self.client.get(f"{self.api_url}/cluster/nextid", headers=self.headers)
        r.raise_for_status()
        return int(r.json()["data"])

    async def _wait_for_task(self, upid: str):
        """Дождаться завершения задачи в Proxmox."""
        while True:
            r = await self._get(f"/nodes/{self.node}/tasks/{upid}/status")
            data = r["data"]
            if data["status"] == "stopped":
                exitstatus = data.get("exitstatus")
                if exitstatus == "OK":
                    logger.debug(f"Task {upid} completed successfully")
                    return
                raise RuntimeError(f"Task {upid} failed: {data}")
            await asyncio.sleep(1)

    async def clone_vm(self, template_id: int, vmid: int, name: str):
        """Клонировать шаблон и дождаться завершения операции."""
        dto = PveCloneDTO(newid=vmid, name=name, full=1)
        resp = await self._post(f"/nodes/{self.node}/qemu/{template_id}/clone", dto.model_dump())
        upid = resp.get("data")
        if upid:
            await self._wait_for_task(upid)
        logger.info(f"VM {vmid} успешно клонирована из шаблона {template_id}")

    async def set_config(
        self,
        vmid: int,
        ip: str,
        *,
        password: str,
        ciuser: str = "root",
        memory: int = 2048,
        cores: int = 2,
    ):
        """Настроить сеть и Cloud-Init-параметры без сниппетов."""
        data = {
            "ipconfig0": f"ip={ip}/24,gw={self.default_gw}",
            "nameserver": self.default_dns,
            "memory": memory,
            "cores": cores,
            "ciuser": ciuser,
            "cipassword": password,
            "sshkeys": "",  # сбрасываем ключи, чтобы гарантировать применение пароля
        }
        await self._post(f"/nodes/{self.node}/qemu/{vmid}/config", data)
        logger.debug(f"Cloud-init config applied for VM {vmid}")

    async def start_vm(self, vmid: int):
        """Запустить VM и дождаться старта."""
        resp = await self._post(f"/nodes/{self.node}/qemu/{vmid}/status/start")
        upid = resp.get("data")
        if upid:
            await self._wait_for_task(upid)
        logger.info(f"VM {vmid} запущена")

    async def create_vm(
        self,
        *,
        name: str,
        ip: str,
        password: str,
        template_id: int,
        ciuser: str,
        memory: int,
        cores: int,
        disk_gb: int,
    ) -> int:
        """Полный цикл создания VM (clone → config → resize disk → start)."""
        vmid = await self._next_id()
        logger.info(f"Создание новой VM {vmid} ({name}) на основе шаблона {template_id}")

        # 1. Клонирование
        await self.clone_vm(template_id, vmid, name)

        # 2. Применение конфигурации cloud-init

        await self._wait_until_unlocked(vmid)

        await self.set_config(
            vmid,
            ip,
            password=password,
            ciuser=ciuser,
            memory=memory,
            cores=cores,
        )

        # 4. Легкая пауза (Proxmox иногда пишет user-data чуть отложенно)
        await asyncio.sleep(4)

        # 3. Ресайз диска
        if disk_gb:
            resp = await self._put(f"/nodes/{self.node}/qemu/{vmid}/resize", {"disk": "scsi0", "size": f"+{disk_gb}G"})
            upid = resp.get("data")
            if upid:
                await self._wait_for_task(upid)
            logger.debug(f"Disk resized for VM {vmid}: +{disk_gb}G")

        # 4. Запуск
        await self.start_vm(vmid)
        return vmid

    # =============================================================
    # === УПРАВЛЕНИЕ ВМ ===
    # =============================================================

    async def stop_vm(self, vmid: int):
        await self._post(f"/nodes/{self.node}/qemu/{vmid}/status/stop")
        logger.info(f"VM {vmid} остановлена")

    async def reboot_vm(self, vmid: int):
        await self._post(f"/nodes/{self.node}/qemu/{vmid}/status/reboot")
        logger.info(f"VM {vmid} перезапущена")

    async def reset_vm(self, vmid: int):
        await self._post(f"/nodes/{self.node}/qemu/{vmid}/status/reset")
        logger.info(f"VM {vmid} сброшена")

    async def delete_vm(self, vmid: int):
        resp = await self._delete(f"/nodes/{self.node}/qemu/{vmid}")
        upid = resp.get("data")
        if upid:
            await self._wait_for_task(upid)
        logger.info(f"VM {vmid} удалена")

    async def update_resources(self, vmid: int, *, memory: Optional[int] = None, cores: Optional[int] = None):
        data = {}
        if memory:
            data["memory"] = memory
        if cores:
            data["cores"] = cores
        await self._post(f"/nodes/{self.node}/qemu/{vmid}/config", data)
        logger.debug(f"Обновлены ресурсы VM {vmid}: {data}")

    async def resize_disk(self, vmid: int, size_gb: int, disk: str = "scsi0"):
        resp = await self._put(f"/nodes/{self.node}/qemu/{vmid}/resize", {"disk": disk, "size": f"+{size_gb}G"})
        upid = resp.get("data")
        if upid:
            await self._wait_for_task(upid)
        logger.debug(f"VM {vmid}: диск {disk} увеличен на {size_gb}G")

    async def vm_info(self, vmid: int) -> VmInfo:
        base = f"/nodes/{self.node}/qemu/{vmid}"
        status = (await self._get(f"{base}/status/current")).get("data", {})
        config = (await self._get(f"{base}/config")).get("data", {})

        ip_addresses = []
        try:
            res = await self._post(f"{base}/agent/network-get-interfaces")
            for iface in res.get("result", []):
                for addr in iface.get("ip-addresses", []):
                    ip = addr.get("ip-address")
                    if ip and not ip.startswith("127."):
                        ip_addresses.append(ip)
        except Exception:
            pass

        return VmInfo(
            vmid=vmid,
            name=config.get("name"),
            status=status.get("status"),
            cpus=status.get("cpus") or config.get("cores") or 1,
            cpu=status.get("cpu", 0.0),
            mem=status.get("mem", 0),
            maxmem=status.get("maxmem", 0),
            disk=status.get("disk", 0),
            maxdisk=status.get("maxdisk", 0),
            diskwrite=status.get("diskwrite", 0),
            diskread=status.get("diskread", 0),
            netin=status.get("netin", 0),
            netout=status.get("netout", 0),
            uptime=status.get("uptime", 0),
            serial=status.get("serial"),
            template=status.get("template"),
            pid=status.get("pid"),
        )

    async def _wait_until_unlocked(self, vmid: int):
        while True:
            cfg = await self._get(f"/nodes/{self.node}/qemu/{vmid}/config")
            if "lock" not in cfg.get("data", {}):
                return
            await asyncio.sleep(1)

    # =============================================================
    # === ВСПОМОГАТЕЛЬНЫЕ ===
    # =============================================================

    async def _get(self, path: str):
        r = await self.client.get(f"{self.api_url}{path}", headers=self.headers)
        r.raise_for_status()
        return r.json()

    async def _post(self, path: str, data: Optional[dict] = None):
        r = await self.client.post(f"{self.api_url}{path}", headers=self.headers, json=data or {})
        r.raise_for_status()
        return r.json()

    async def _put(self, path: str, data: Optional[dict] = None):
        r = await self.client.put(f"{self.api_url}{path}", headers=self.headers, json=data or {})
        r.raise_for_status()
        return r.json()

    async def _delete(self, path: str):
        r = await self.client.delete(f"{self.api_url}{path}", headers=self.headers)
        r.raise_for_status()
        return r.json()
