from .base import *

DEBUG = False

ADMINS = admin_list

ALLOWED_HOSTS = ['ketabedamavand.com', 'www.ketabedamavand.com',  'localhost',]

CSRF_TRUSTED_ORIGINS = ['https://*.ketabedamavand.com']

SERVER_EMAIL = 'noreply@ketabedamavand.com'
