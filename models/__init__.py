from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .usuario import Usuario
from .membresia import Membresia
from .suscripcion import Suscripcion
from .pago import Pago
from .plano import Plano
from .modelo3d import Modelo3D
