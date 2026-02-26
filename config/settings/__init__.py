import os

# Variable de entorno que define el entorno: 'development' o 'production'
# Si no se define, por defecto usamos 'development' para seguridad en desarrollo
DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .production import *
else:
    from .development import *