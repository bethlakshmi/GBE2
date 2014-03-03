GBE2
====

Total rewrite of GBE original PHP into Python with Django


Until we have a better build process, here's how to get up to scratch:

navigate to the directory in which you want to drop this project
clone into this repo
cd into the newly-created GBE2 directory and delete the expo directory (!)
$ django-admin.py startproject expo
$ cd expo
$ python manage.py startapp gbe
$ cd ..
$ git checkout

(this should make sure that django-admin and manage.py take all necessary steps to create the project and the app correctly)
