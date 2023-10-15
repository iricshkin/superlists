from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = "git@github.com:iricshkin/superlists.git"


def deploy():
    """Развернуть."""
    site_folder = f"/home/{env.user}/sites/{env.host}"
    source_folder = site_folder + "/source"
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_venv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    """Создать структуру каталога, если нужно."""
    for subfolder in ("database", "static", "venv", "source"):
        run(f"mkdir -p {site_folder}/{subfolder}")


def _get_latest_source(source_folder):
    """Получить самый свежий исходный код."""
    if exists(source_folder + "/.git"):
        run(f"cd {source_folder} && git fetch")
    else:
        run(f"git clone {REPO_URL} {source_folder}")
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f"cd {source_folder} && git reset --hard {current_commit}")


def _update_settings(source_folder, site_name):
    """Обновить настройки."""
    setting_path = source_folder + "/superlists/settings.py"
    sed(setting_path, "DEBUG = True", "DEBUG = False")
    sed(setting_path, "ALLOWED_HOSTS =.+$", f'ALLOWED_HOSTS = ["{site_name}"]')
    secret_key_file = source_folder + "/superlists/secret_key.py"
    if not exists(secret_key_file):
        chars = "abxdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f"SECRET_KEY = '{key}'")
    append(setting_path, "\nfrom .secret_key import SECRET_KEY")


def _update_venv(source_folder):
    """Обновить виртуальную среду."""
    venv_folder = source_folder + "/../venv"
    if not exists(venv_folder + "/bin/pip"):
        run(f"python3 -m venv {venv_folder}")
    run(f"{venv_folder}/bin/pip install -r {source_folder}/requirements.txt")


def _update_static_files(source_folder):
    """Обновить статические файлы."""
    run(f"cd {source_folder} && ../venv/bin/python3 manage.py collectstatic --noinput")


def _update_database(source_folder):
    """Обновить базу данных."""
    run(f"cd {source_folder} && ../venv/bin/python3 manage.py migrate --noinput")
