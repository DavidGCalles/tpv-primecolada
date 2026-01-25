from enum import Enum

class VentaState(Enum):
    ERROR = 0
    EN_COLA = 1
    LAVANDO = 2
    PTE_RECOGIDA = 3
    RECOGIDO = 4