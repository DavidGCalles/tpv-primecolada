from enum import Enum

class VentaState(Enum):
    ERROR = 0
    IMPRIMIENDO = 1
    EN_COLA = 2
    LAVANDO = 3
    PTE_RECOGIDA = 4
    RECOGIDO = 5