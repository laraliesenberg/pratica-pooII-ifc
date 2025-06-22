import pygame

class Carro:
    def __init__(self, x, y, largura, altura, cor, velocidade):
        #Posição inicial e tamanho do carro
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.cor = cor
        self.velocidade = velocidade

    def mover(self, direcao):
        #O canto superior esquerdo da tela é (0,0), isso nos mostra que o eixo X cresce da esquerda para a direita,
        #e o eixo Y de cima para baixo. O Pygame usa um sistema de coordenadas invertido no eixo Y comparado à matemática
        if direcao == 'LEFT': self.x -= self.velocidade
        elif direcao == 'RIGHT': self.x += self.velocidade
        elif direcao == 'UP': self.y -= self.velocidade
        elif direcao == 'DOWN': self.y += self.velocidade

    def desenhar(self, tela):
        #Desenha o carro na tela
        pygame.draw.rect(tela, self.cor, (self.x, self.y, self.largura, self.altura))

    def posicao(self):
        #Retorna a posição atual do carro
        return (self.x, self.y)