class TrajetoTemp:
    def __init__(self):
        #Lista de coordenadas do trajeto
        self.caminho = [] 

    def adicionar_pontos(self, posicao):
        #Adiciona os pontos na lista caminho se for diferente do ultimo ponto 
        if not self.caminho or posicao != self.caminho[-1]:
            self.caminho.append(posicao)

    def obter_caminho(self):
        return self.caminho