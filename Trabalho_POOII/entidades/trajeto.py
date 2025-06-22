from pony.orm import Database, Required, Set

# Banco de dados
db = Database()
db.bind(provider='sqlite', filename='simulacao.db', create_db=True)

#Classe trajeto (sequência de pontos, coordenadas)
class Trajeto(db.Entity):
    nome = Required(str, unique=True)
    pontos = Required(str)  #Armazena os pontos como string "x1,y1;x2,y2;..."
    viagem = Set('Viagem')