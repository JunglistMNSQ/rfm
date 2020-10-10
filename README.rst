=======
RFMIZER
=======

What this?

My first project in python/django.

This app was writen for automate a SMS messaging to customers based on a RFM matrix.
The SMS is sent when a trigger works (a customer move down on a R-axis).

How works it?

Upload your database which contain deals of customers. It must be in a CSV format.
Columns are in order bellow.
| Data Deal | Customer Name | Customer Phone | Product | Price |
At an import the app checks customers to phones.

After upload your base, heed to go into settings of created table and you need to set RFM settings. Create rules of messaging on triggers which you need. Personalize your message using {name}.

A cron compute a RFM every customer at night, and if a move on the R-axis is done, the customer get a message in the day.

Summary, your have automaton which comeback your customer to you, again, and again, and your bank account full more, and more.

Attention: All the templates are implemented in russian language.

Quick start
-----------

1. Install and config PostgreSQL, create a user and a database.

2. Install Redis from there https://redis.io/.

3. Install Django and Start a new project, config a backend use the Postgres credentials like this
::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'db_name',
            'USER': 'user_name',
            'PASSWORD': 'user_password',
            'HOST': '127.0.0.1',
            'PORT': '5432'
        }
    }

4. Run
::

    pip install django-rfmizer

5. Add next apps to your INSTALLED_APPS in settings.py
::

    INSTALLED_APPS = [
        'rfmizer.apps.RfmizerConfig', # This string must be add in a first element of a the list
        '...',
        'fixture_magic',
        'multiselectfield',
        'django_celery_beat',
        ]

6. Add into settings.py a code is below
::

    LOGIN_REDIRECT_URL = '/profile/'

7. Add import into urls.py
::

    from django.contrib.auth.views import LoginView
    from django.urls import include, path

8. Include the rfmizer URLconf in your project urls.py like this
::

    urlpatterns += [
        path('registration/', include('django.contrib.auth.urls', )),
        path('', include('rfmizer.urls')),
        path('login/', LoginView.as_view(redirect_authenticated_user=True),
             name='login')
    ]

9. Create a celery.py file in main directory and insert to it a code below, NAME_OF_DIRECTORY is a directory which contain this file and the settings.py
::

    import os
    from celery import Celery
    from celery.schedules import crontab

    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NAME_OF_DIRECTORY.settings')

    celery_app = Celery(
        'rfmzer',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0',
        include=['rfmizer.tasks'],
    )

    # If you need, it can to be changed.
    celery_app.conf.timezone = 'UTC'

    celery_app.conf.beat_schedule = {
        'run-rfmizer-at-3-am': {
            'task': 'rfmizer.tasks.schedule_run_rfmizer',
            'schedule': crontab(hour='3', day_of_week='mon-fri')
        },
        'run-sms-sending-at-10-am': {
            'task': 'rfmizer.tasks.schedule_run_sms_sending',
            'schedule': crontab(hour='10', day_of_week='mon-fri')
        },
    }

9. Run `$ python manage.py migrate` to create the rfmizer models.

10. Run in a different terminals on server, NAME_OF_DIRECTORY is a directory which contain the celery.py. It must be run from a directory where the manage.py file is.
::

    redis-sever
    celery -A NAME_OF_DIRECTORY worker -l INFO
    celery -A NAME_OF_DIRECTORY beat -l INFO
    python manage.py runserver

11. Visit http://127.0.0.1:8000/