from pony.orm import Required, Set
from entidades.trajeto import db, Trajeto

class Viagem(db.Entity):
    nome = Required(str)
    trajetos = Set(Trajeto)