import asyncssh
from textwrap import dedent
from loguru import logger


class NginxManager:

    def __init__(self, ssh_host: str, ssh_user: str, ssh_pass: str):
        """
        Основной сервер (где создаются прокси-конфиги Nginx).
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass

    @staticmethod
    async def _connect(host: str, user: str, password: str):
        return await asyncssh.connect(host, username=user, password=password, known_hosts=None)

    @staticmethod
    async def _ensure_nginx_installed(conn):
        """Проверяет и при необходимости устанавливает nginx."""
        result = await conn.run("which nginx", check=False)
        if result.exit_status == 0:
            logger.debug(f"[INFO] Nginx уже установлен на {conn._host}")
            return

        logger.debug(f"[INFO] Устанавливаю nginx на {conn._host}...")

        cmd = dedent("""
            bash -lc '
            export DEBIAN_FRONTEND=noninteractive;
            apt-get update -y;
            apt-get -o Dpkg::Lock::Timeout=60 install -y nginx;
            '
        """).strip()

        res = await conn.run(cmd, check=False)
        logger.debug(f"[STDOUT] {res.stdout}")
        logger.debug(f"[STDERR] {res.stderr}")

        if res.exit_status != 0:
            raise RuntimeError(
                f"Ошибка установки nginx (exit {res.exit_status}) на {conn._host}\n"
                f"STDERR:\n{res.stderr}"
            )

        # Запуск/включение nginx
        await conn.run(
            "if command -v systemctl >/dev/null 2>&1; then "
            "sudo systemctl enable nginx --now; "
            "else "
            "sudo service nginx start; "
            "fi",
            check=False
        )

    async def setup_vm_nginx(self, vm_ip: str, vm_user: str, vm_pass: str):
        """Устанавливает nginx на VM."""
        async with await self._connect(vm_ip, vm_user, vm_pass) as vm_conn:
            await self._ensure_nginx_installed(vm_conn)

    async def add_vhost(self, domain: str, target_ip: str):
        """Создает виртуальный хост-прокси на основном сервере."""
        conf_content = dedent(f"""
            server {{
                listen 80;
                server_name {domain};

                location / {{
                    proxy_pass http://{target_ip};
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header Upgrade $http_upgrade;
                    proxy_set_header Connection "upgrade";
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header REMOTE_ADDR $http_cf_connecting_ip;
                    proxy_set_header X-Real-IP $http_cf_connecting_ip;
                }}
            }}
        """).strip()

        async with await self._connect(self.ssh_host, self.ssh_user, self.ssh_pass) as conn:
            conf_path = f"/etc/nginx/sites-available/{domain}"

            await conn.run(f"echo '{conf_content}' | sudo tee {conf_path}", check=True)
            await conn.run(f"sudo ln -sf {conf_path} /etc/nginx/sites-enabled/{domain}", check=True)
            await conn.run("sudo nginx -t && sudo systemctl reload nginx", check=True)
            logger.debug(f"[OK] Добавлен vhost для {domain} → {target_ip}")

    async def remove_vhost(self, domain: str):
        """Удаляет виртуальный хост-прокси с основного сервера."""
        async with await self._connect(self.ssh_host, self.ssh_user, self.ssh_pass) as conn:
            conf_avail = f"/etc/nginx/sites-available/{domain}"
            conf_enabled = f"/etc/nginx/sites-enabled/{domain}"

            cmd = dedent(f"""
                sudo rm -f {conf_avail} {conf_enabled} &&
                sudo nginx -t &&
                sudo systemctl reload nginx
            """).strip()

            res = await conn.run(cmd, check=False)
            if res.exit_status == 0:
                logger.debug(f"[OK] Удалён vhost {domain}")
            else:
                logger.error(f"[ERR] Ошибка при удалении vhost {domain}: {res.stderr}")
                raise RuntimeError(f"Ошибка удаления vhost {domain}: {res.stderr}")

    async def full_setup(
        self,
        domain: str,
        target_ip: str,
        vm_user: str,
        vm_pass: str,
    ):
        """Полный цикл: установка nginx на VM + создание прокси на основном сервере."""
        await self.setup_vm_nginx(target_ip, vm_user, vm_pass)
        await self.add_vhost(domain, target_ip)
        return domain

    async def reload(self, vm_ip: str, vm_user: str, vm_pass: str):
        """Перезапускает nginx на указанной VM."""
        async with await self._connect(vm_ip, vm_user, vm_pass) as conn:
            res = await conn.run("sudo nginx -t && sudo systemctl reload nginx", check=False)
            if res.exit_status != 0:
                raise RuntimeError(
                    f"Ошибка reload nginx на {vm_ip}:\n{res.stderr or res.stdout}"
                )
            logger.debug(f"[OK] nginx перезапущен на {vm_ip}")

    async def set_config(self, vm_ip: str, vm_user: str, vm_pass: str, config: str):
        """
        Записывает конфиг на VM и перезапускает nginx.
        При ошибке проверки нового конфига — откатывает на предыдущий.
        """
        conf_path = "/etc/nginx/sites-available/default"
        backup_path = f"{conf_path}.bak"

        async with await self._connect(vm_ip, vm_user, vm_pass) as conn:
            # 1. Делаем бэкап текущего конфига
            await conn.run(f"sudo cp {conf_path} {backup_path}", check=False)

            # 2. Записываем новый конфиг
            await conn.run(f"echo '{config}' | sudo tee {conf_path}", check=True)
            await conn.run(f"sudo ln -sf {conf_path} /etc/nginx/sites-enabled/default", check=False)

            # 3. Проверяем новый конфиг
            test_res = await conn.run("sudo nginx -t", check=False)

            if test_res.exit_status != 0:
                # Ошибка — откатываемся к старому конфигу
                await conn.run(f"sudo mv {backup_path} {conf_path}", check=False)
                await conn.run("sudo nginx -t", check=False)  # повторная проверка старого
                raise RuntimeError(
                    f"Ошибка проверки нового конфига на {vm_ip}:\n"
                    f"{test_res.stderr or test_res.stdout}\n"
                    f"Конфиг откатан к предыдущей версии."
                )

            # 4. Всё ок — удаляем бэкап и перезапускаем nginx
            await conn.run(f"sudo rm -f {backup_path}", check=False)

        # Перезапуск nginx (вынесен за пределы сессии)
        await self.reload(vm_ip, vm_user, vm_pass)
        logger.debug(f"[OK] Конфиг обновлён и nginx перезапущен на {vm_ip}")


    async def get_config(self, vm_ip: str, vm_user: str, vm_pass: str) -> str:
        """Считывает текущий конфиг nginx с указанной VM."""
        async with await self._connect(vm_ip, vm_user, vm_pass) as conn:
            conf_path = "/etc/nginx/sites-available/default"
            res = await conn.run(f"sudo cat {conf_path}", check=False)

            if res.exit_status != 0:
                raise RuntimeError(
                    f"Ошибка чтения конфига nginx на {vm_ip}:\n{res.stderr or res.stdout}"
                )
            logger.debug(f"[OK] Конфиг nginx считан с {vm_ip}")
            return res.stdout