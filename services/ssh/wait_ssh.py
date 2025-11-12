import asyncio

from loguru import logger


async def wait_for_ssh(ip: str, timeout: int = 120):
    """Дождаться, пока сервер поднимет SSH (port 22)."""
    start = asyncio.get_event_loop().time()
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, 22)
            writer.close()
            await writer.wait_closed()
            logger.info(f"SSH доступен на {ip}")
            return True
        except (OSError, ConnectionRefusedError):
            if asyncio.get_event_loop().time() - start > timeout:
                raise TimeoutError(f"SSH недоступен на {ip} в течение {timeout} секунд")
            await asyncio.sleep(2)