Обеспечение работы нового сайта
================================
## Необходимые пакеты:
* nginx
* Python 3.11
* venv + pip
* Git

например, в Ubuntu:

    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get install nginx git python3.11 python3.11-venv

## Конфигурация виртуального узлов Nginx

* см. nginx.template.conf
* заменить SITENAME, например, на staging.my-domain.com

## Служба Systemd

* см. gunicorn-systemd.template.service
* заменить SITENAME, например, на staging.my-domain.com

## Структура папок:
Если допустить, что есть учетная запись пользователя в /home/username

/home/username
|___ sites
    |___ SITENAME
        |--- database
        |--- source
        |--- static
        |___ venv