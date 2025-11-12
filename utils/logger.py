from loguru import logger
import sys

from core.settings import DEBUG


def setup_logger():
    logger.remove()

    if DEBUG:
        logger.add(
            sys.stdout,
            level="DEBUG",  # Уровень логирования
            format="<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> | <level>{level}</level> | {message}")  # Формат
    else:
        logger.add(f"log/app.log",
                   enqueue=True,
                   mode="a",
                   rotation="100 MB",  # Ротация файла по размеру
                   retention="10 days",  # Сохранение логов за последние 10 дней
                   compression="zip",  # Архивация старых логов
                   level="DEBUG",  # Уровень логирования
                   format="{time:YYYY-MM-DD HH:mm:ss:SSS} | {level} | {message}")  # Формат вывода
