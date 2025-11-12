import json

import httpx
from loguru import logger

from services.cloudflare.error_codes import CfErrorCode


class CloudflareAPI:
    def __init__(self, api_token: str, domain: str):
        self.api_token = api_token
        self.domain = domain
        self.base_url = f"https://api.cloudflare.com/client/v4/zones"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    async def get_zone_id(self, domain: str) -> str:
        """
        Возвращает ID зоны Cloudflare по имени домена (например, 'mydomain.ru').

        Если зона не найдена — выбрасывает RuntimeError.
        """
        url = "https://api.cloudflare.com/client/v4/zones"
        params = {"name": domain}
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

        if not data.get("success"):
            raise RuntimeError(f"Cloudflare API error: {data}")

        zones = data.get("result", [])
        if not zones:
            raise RuntimeError(f"Zone '{domain}' not found in Cloudflare account")

        zone_id = zones[0]["id"]
        return zone_id

    async def create_record(self, name: str, content: str, proxied: bool = True, record_type: str = "A"):
        """
        Создаёт DNS-запись (A/AAAA/CNAME).
        name: demo  => создаст demo.mydomain.ru
        content: IP-адрес
        """
        zone_id = await self.get_zone_id(self.domain)
        url = f"{self.base_url}/{zone_id}/dns_records"
        data = {
            "type": record_type,
            "name": name,
            "content": content,
            "ttl": 120,
            "proxied": proxied,
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=self.headers, json=data)
            try:
                r.raise_for_status()
            except httpx.HTTPStatusError as e:
                try:
                    r_json = r.json()
                    if r_json.get("errors", [{}])[0].get("code") == CfErrorCode.record_already_exists:
                        return
                except json.decoder.JSONDecodeError as e:
                    pass
                logger.error(f"Cloudflare API error: {e}. >> {r.text=} | {data=}")
                raise
            return

    async def delete_record(self, name: str, record_type: str = "A"):
        """Удаляет DNS-запись по имени и типу (например, demo.mydomain.ru, type=A)."""
        zone_id = await self.get_zone_id(self.domain)
        base = f"{self.base_url}/{zone_id}/dns_records"

        async with httpx.AsyncClient() as client:
            search = await client.get(
                base, headers=self.headers, params={"type": record_type, "name": name}
            )
            search.raise_for_status()
            records = search.json().get("result", [])

            if not records:
                logger.warning(f"DNS-запись {name} ({record_type}) не найдена")
                return False

            record_id = records[0]["id"]

            r = await client.delete(f"{base}/{record_id}", headers=self.headers)
            r.raise_for_status()

        logger.info(f"Удалена DNS-запись {record_type} {name}")
        return True