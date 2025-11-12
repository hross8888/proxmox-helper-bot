from aiogram.types import Message
from loguru import logger

from bot import i18n_default
from bot.keyboards.common_kbs import close_kb
from bot.shema import CreateVmShema
from bot.utils.message_helper import temporary_message
from core.models import Vm
from core.settings import DOMAIN, DEFAULT_VM_USER, VPS_HOST
from services.manager import Manager


async def background_create_vm(*, message: Message, vm_data: CreateVmShema):
    try:
        manager = Manager(DOMAIN)
        ip, vm_id = await manager.create_vm(data=vm_data, ciuser=DEFAULT_VM_USER)

        await message.answer(
            i18n_default("M.PVE.DONE_WM").format(
                name=vm_data.name,
                id=vm_id,
                ip=ip,
                login=DEFAULT_VM_USER,
                password=vm_data.password
            ),
            reply_markup=close_kb()
        )

    except Exception as e:
        await temporary_message(message=message, text=i18n_default("M.PVE.ERROR.VM_CREATE").format(name=vm_data.name))
        logger.exception(f"Ошибка при создании VM {vm_data.name}: {e}")
        raise


async def background_create_domain(*, vm: Vm, message: Message):
    try:
        manager = Manager(DOMAIN)
        full_domain = await manager.create_domain(
            name=vm.name,
            content=VPS_HOST,
            vm_ip=vm.ip_address,
            vm_user=DEFAULT_VM_USER,
            vm_pass=vm.password
        )
        vm.domain = full_domain
        await vm.save(update_fields=["domain"])
        await temporary_message(
            message=message,
            text=i18n_default("M.PVE.DOMAIN_CREATE").format(vm_id=vm.vm_id),
            kb=close_kb(),
            delay=10
        )

    except Exception as e:
        await temporary_message(message=message, text=i18n_default("M.PVE.ERROR.VM_DELETE").format(vm_id=vm.vm_id))
        logger.exception(f"Ошибка при создании домена VM {vm.vm_id}: {e}")
        raise


async def background_delete_vm(*, vm: Vm, message: Message):
    manager = Manager(DOMAIN)
    try:
        await manager.delete_vm(name=vm.name, vmid=vm.vm_id, with_domain=bool(vm.domain))
        await vm.delete()
        await temporary_message(message=message, text=i18n_default("M.PVE.VM_DELETED").format(vm_id=vm.vm_id))
        logger.info(f"VM {vm.vm_id} удалена")

    except Exception as e:
        await temporary_message(message=message, text=i18n_default("M.PVE.ERROR.VM_DELETE").format(vm_id=vm.vm_id))
        logger.exception(f"Ошибка при удалении VM {vm.vm_id}: {e}")
        raise
