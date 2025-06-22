import sys
sys.dont_write_bytecode = True

from entidades.trajeto import db, Trajeto 
from entidades import trajeto, viagem  # Apenas para garantir o mapeamento completo

db.generate_mapping(create_tables=True)

from simulacao import Simulacao
import pygame

pygame.init()
s = Simulacao()
s.executar()