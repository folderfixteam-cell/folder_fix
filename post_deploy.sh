#!/bin/bash
workon env
cd /home/folderfix/folder_fix
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/folderfix_com_wsgi.py
