PYTHONPATH=/home/my_username/webapps/bip/lib:/home/my_username/webapps/bip/lib/python2.7:/home/my_username/webapps/bip/bip:/home/my_username/webapps/bip/bip/project
DJANGO_SETTINGS_MODULE=project.settings

/usr/local/bin/python2.7 ~/webapps/gbelive/expo/manage.py shell < ~/webapps/gbelive/expo/transaction_cron_job.py &>> ~/logs/user/transaction_cron_job.log

