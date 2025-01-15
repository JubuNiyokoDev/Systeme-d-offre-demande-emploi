from .base import *
DEBUG = True

ALLOWED_HOSTS = ['systeme-d-offre-demande-emploi.onrender.com']  

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'job_portal_db_95xa',
        'USER': 'job_portal_user',
        'PASSWORD': '8wxiM8U6HK6Fm0ZdJELar894ADRV8DWH',
        'HOST': 'dpg-ctbmp1q3esus73f6q490-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'niyondikojoffreasjubu@gmail.com'
EMAIL_HOST_PASSWORD = 'sjsaffuyrbdsanjafhfdsa'
