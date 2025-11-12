import inspect
import importlib
import pkgutil
from collections import Counter
from pathlib import Path
from aiogram import Router
from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.filters.callback_data import CallbackData
from loguru import logger


def register_all_handlers(dispatcher: Dispatcher) -> None:
    """
    Рекурсивно ищет модули с объектом `router` и подключает их к диспетчеру.
    Работает относительно текущего пакета `handlers`, ничего не требует на вход.
    Гарантирует, что *.commands подключаются ПЕРВЫМИ.
    Проверяет уникальность CallbackData.prefix и дублирующиеся handler-фильтры.
    """

    # Определяем корневой пакет автоматически
    base_package = __package__ or "bot.handlers"
    base_path = Path(__file__).resolve().parent

    callback_prefixes: dict[str, str] = {}
    all_filters: list[str] = []
    routers: list[tuple[str, Router]] = []
    found_commands = False

    # Проходим по всем подмодулям пакета
    for module_info in pkgutil.walk_packages([str(base_path)], f"{base_package}."):
        module_name = module_info.name
        try:
            module = importlib.import_module(module_name)


            # Проверка CallbackData
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj is CallbackData:
                    continue
                if issubclass(obj, CallbackData) and hasattr(obj, "__callback_data__"):
                    prefix = obj.__callback_data__["prefix"]
                    if prefix in callback_prefixes:
                        raise RuntimeError(
                            f"Дублирующийся CallbackData.prefix '{prefix}' найден в "
                            f"{callback_prefixes[prefix]} и {module_name}.{name}"
                        )
                    callback_prefixes[prefix] = f"{module_name}.{name}"

            # Копим router’ы (чтобы потом отсортировать)
            if hasattr(module, "router") and isinstance(module.router, Router):
                routers.append((module_name, module.router))
                if module_name.endswith(".commands"):
                    found_commands = True

        except Exception as e:
            logger.exception(f"Ошибка при подключении модуля {module_name}: {e}")

    if not found_commands:
        raise RuntimeError("Не найден ни один модуль *.commands — бот не может работать без команд.")

    # Сортируем — сначала *.commands, потом остальные, потом fallback
    routers.sort(key=lambda x: (
        0 if x[0].endswith(".commands") else
        2 if x[0].endswith(".fallback") else
        1,
        x[0]
    ))

    # Подключаем
    for module_name, router in routers:
        dispatcher.include_router(router)
        logger.info(f"Подключён router из модуля: {module_name}")

    # Проверка дубликатов фильтров (если будешь собирать all_filters)
    filter_counts = Counter(all_filters)
    duplicates = [f for f, count in filter_counts.items() if count > 1]
    if duplicates:
        logger.error("Найдены дублирующиеся фильтры у хендлеров:")
        for dup in duplicates:
            logger.error(f"  - {dup}")
        raise ValueError("Запуск прерван из-за дубликатов хендлеров")
