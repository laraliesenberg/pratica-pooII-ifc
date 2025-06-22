import pygame
import sys
import tkinter as tk
from tkinter import simpledialog
from pony.orm import db_session, commit

from carro import Carro
from trajetoTemp import TrajetoTemp
from entidades.trajeto import Trajeto, db
from entidades.viagem import Viagem

# Constantes de tela e cores
largura_tela = 768
altura_tela = 785
azul = (0, 0, 255)
vermelho = (255, 0, 0)
verde = (0, 255, 0)
amarelo = (255, 255, 0)
laranja = (255, 165, 0)

tela = pygame.display.set_mode((largura_tela, altura_tela))
root = tk.Tk()
root.withdraw()

class Simulacao:
    def __init__(self):
        #Implementando o mapa
        self.mapa = pygame.image.load("mapa_timbo.png")
        self.mapa = pygame.transform.scale(self.mapa, (largura_tela, altura_tela))

        #Coordenada do batalhão da polícia militar
        self.batalhao = (393, 499)

        #Criação do carro
        self.carro = Carro(393, 499, 10, 10, vermelho, 2)

        #Trajeto sendo percorrido
        self.trajeto_atual = TrajetoTemp()
        self.trajeto_atual.adicionar_pontos(self.carro.posicao())

        #Guarda o resultado de combinação de trajetos
        self.trajeto_combinado = None

        self.viagens_para_destino = []   # Armazena todas as viagens até o destino consultado
        self.melhor_viagem_pontos = []  # Armazena a melhor viagem para destacar depois

    def desenhar_trajeto(self, pontos, cor):
        #Desenha o caminho conectando os pontos
        if len(pontos) > 1:
            pygame.draw.lines(tela, cor, False, pontos, 6)
          
    def recomecar_trajeto(self):
        #Depois do ENTER o carro volta para a posição inicial (no batalhão)
        self.carro.x, self.carro.y = self.batalhao
        self.trajeto_atual = TrajetoTemp()  #Zera o trajeto atual, pra não continuar registrando pontos antigos
        self.trajeto_atual.adicionar_pontos(self.carro.posicao())  #Começa um novo trajeto
        print("Carro voltou ao batalhão")

    #Converte uma lista de tuplas [(x1, y1), (x2, y2), ...] para uma string: "x1,y1;x2,y2;..."
    def pontos_para_string(self, pontos):
        return ';'.join([f"{x},{y}" for x, y in pontos])

    #Converte a string "x1,y1;x2,y2;..." de volta para uma lista de tuplas [(x1, y1), (x2, y2), ...] pq o banco n armazena listas diretamente
    def string_para_pontos(self, string):
        return [tuple(map(int, ponto.split(','))) for ponto in string.split(';') if ponto]

    @db_session
    def salvar_trajeto_no_banco(self, nome, trajeto_temp):
        pontos_str = self.pontos_para_string(trajeto_temp.obter_caminho())  #Converte o trajeto atual (lista de pontos) em string
        Trajeto(nome=nome, pontos=pontos_str)  #Cria um novo objeto Trajeto no banco
        commit()
        print(f"'{nome}' salvo com {len(trajeto_temp.obter_caminho())} pontos.")

    @db_session
    def carregar_trajetos(self):
        trajetos = {}
        for t in Trajeto.select():
            trajetos[t.nome] = self.string_para_pontos(t.pontos)  #Converte os pontos de string para lista de tuplas e adiciona ao dicionário
        return trajetos
    
    @db_session
    def combinar_trajetos_no_banco(self, nomes):
        trajeto_combinado = []
        viagem_nome = "Viagem_" + "_".join(nomes)

        viagem = Viagem.get(nome=viagem_nome)
        if not viagem:
            viagem = Viagem(nome=viagem_nome)

        #Percorre cada nome fornecido pelo usuário no dicionário
        for nome in nomes:
            trajeto = Trajeto.get(nome=nome)
            if trajeto:
                #Converte os pontos para lista de tuplas
                pontos = self.string_para_pontos(trajeto.pontos) 
                #Adiciona os pontos ao trajeto combinado, evitando duplicatas consecutivas 
                for ponto in pontos:
                    if not trajeto_combinado or ponto != trajeto_combinado[-1]:
                        trajeto_combinado.append(ponto)
                viagem.trajetos.add(trajeto)
            else:
                print(f"Trajeto '{nome}' não encontrado.")

        commit()
        print(f"Viagem '{viagem_nome}' criada com {len(trajeto_combinado)} pontos.")
        return trajeto_combinado
    
    @db_session
    def mostrar_melhor_viagem_ate(self, destino_final):
        viagens = Viagem.select()  #Pega todas as viagens cadastradas no BD
        viagens_para_destino = []

        for viagem in viagens:
            trajetos = list(viagem.trajetos)  #Para cada viagem, pega a lista de trajetos associados a essa viagem

            if trajetos:
                ultimo_trajeto = sorted(trajetos, key=lambda t: t.id)[-1] #Ordena os trajetos pelo id, pega o ultimo trajeto da lista ordenada
                if ultimo_trajeto.nome.endswith(destino_final):  #verifica se o nome do ultimo_trajeto termina com a string destino_final
                    pontos_totais = []   #Constroi uma lista de todos os pontos dessa viagem, cuidando pra não repetir o ponto q liga os 2 trajetos
                    for traj in sorted(trajetos, key=lambda t: t.id):
                        pts = self.string_para_pontos(traj.pontos)  #Converte a string de pontos de cada trajeto em uma lista de pontos
                        if not pontos_totais or pontos_totais[-1] != pts[0]:
                            pontos_totais.extend(pts)
                        else:
                            pontos_totais.extend(pts[1:])
                    viagens_para_destino.append((viagem.nome, pontos_totais)) #tupla: Viagem: 180

        if not viagens_para_destino:
            print(f"Nenhuma viagem termina em '{destino_final}'")
            self.viagens_para_destino = []
            self.melhor_viagem_pontos = []
            return

        #Ordena pela quantidade de pontos, ou seja, a viagem com menos pontos
        viagens_para_destino.sort(key=lambda x: len(x[1])) 

        self.viagens_para_destino = viagens_para_destino
        self.melhor_viagem_pontos = viagens_para_destino[0][1]  #Guarda os pontos da melhor viagem

        print(f"Melhor viagem até '{destino_final}': {viagens_para_destino[0][0]} com {len(self.melhor_viagem_pontos)} pontos.")
        
    def solicitar_nome_trajeto(self):
        return simpledialog.askstring("Nome do trajeto", "Digite o nome do trajeto:")
    
    def exibir_mensagem(self, texto, cor_fundo=(192, 192, 192), cor_texto=(0, 0, 0)):
        fonte = pygame.font.SysFont(None, 22)
        texto_renderizado = fonte.render(texto, True, cor_texto)

        #Define tamanho do retângulo fixo (quadrado visual), mais acima
        largura_ret = 400
        altura_ret = 40
        pos_x = 10
        pos_y = altura_tela - 100 

        #Desenha o retângulo
        pygame.draw.rect(tela, cor_fundo, (pos_x, pos_y, largura_ret, altura_ret))

        #Centraliza o texto dentro do retângulo
        ret_texto = texto_renderizado.get_rect(center=(pos_x + largura_ret // 2, pos_y + altura_ret // 2))
        tela.blit(texto_renderizado, ret_texto)

        pygame.display.update()

    def mostrar_varias_viagens(self, destinos):
        for destino in destinos:
            self.mostrar_melhor_viagem_ate(destino)

            #redesenha a tela
            tela.blit(self.mapa, (0, 0))
            pygame.draw.circle(tela, azul, self.batalhao, 10)

            #desenha todas as viagens para o destino em laranja
            for nome, pontos in self.viagens_para_destino:
                self.desenhar_trajeto(pontos, laranja)

            #desenha a melhor viagem em azul
            if self.melhor_viagem_pontos:
                self.desenhar_trajeto(self.melhor_viagem_pontos, azul)
                mensagem = f"Melhor viagem para '{destino}': {self.viagens_para_destino[0][0]} com {len(self.melhor_viagem_pontos)} pontos"
                self.exibir_mensagem(mensagem)

            #redesenha o carro (estático)
            self.carro.desenhar(tela)

            pygame.display.flip()
            pygame.time.delay(6000)  #espera 6 segundos para próximo destino

    def executar(self):
        clock = pygame.time.Clock()

        trajetos_salvos = self.carregar_trajetos()

        #Loop para verificar todos os eventos
        while True:
            movimento = False

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    #Se o evento for fechar a janela, ele sai e fecha o programa
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN: #KEYDOWN é o evento de quando uma tecla se mantem pressionada
                    if evento.key == pygame.K_RETURN: #ENTER salva o trajeto
                        nome = self.solicitar_nome_trajeto()
                        if nome:
                            self.salvar_trajeto_no_banco(nome, self.trajeto_atual) 
                            trajetos_salvos[nome] = list(self.trajeto_atual.obter_caminho())

                        #Zera o trajeto atual para começar a gravar um novo
                        self.trajeto_atual = TrajetoTemp()
                        self.trajeto_atual.adicionar_pontos(self.carro.posicao())

                    #Se apertar a tecla R volta para o batalhão
                    if evento.key == pygame.K_r:
                        self.recomecar_trajeto()

                    if evento.key == pygame.K_c:
                        nomes = simpledialog.askstring("Combinar trajetos", "Digite os nomes dos trajetos separados por vírgula:") 
                        if nomes:
                            lista = [n.strip() for n in nomes.split(",")]  #Remove os espaços em brancos e divide a string em vírgulas
                            self.trajeto_combinado = self.combinar_trajetos_no_banco(lista)  #É criada variável para depois poder desenhar o trajeto combinado

                    if evento.key == pygame.K_v:
                        destino = simpledialog.askstring("Destino final", "Digite a letra do destino final:")
                        if destino:
                            self.mostrar_melhor_viagem_ate(destino.strip().upper())

                    if evento.key == pygame.K_SPACE:
                        self.mostrar_varias_viagens(["C", "F", "I", "L"])


            tecla = pygame.key.get_pressed()
            if tecla[pygame.K_LEFT]:
                self.carro.mover('LEFT')
                movimento = True
            if tecla[pygame.K_RIGHT]:
                self.carro.mover('RIGHT')
                movimento = True
            if tecla[pygame.K_UP]:
                self.carro.mover('UP')
                movimento = True
            if tecla[pygame.K_DOWN]:
                self.carro.mover('DOWN')
                movimento = True

            #Se tiver movimento, registra no trajeto atual
            if movimento:
                self.trajeto_atual.adicionar_pontos(self.carro.posicao())

            #Atualiza a tela com o mapa
            tela.blit(self.mapa, (0, 0))

            #Desenha o batalhão da polícia
            pygame.draw.circle(tela, azul, self.batalhao, 10)

            #Desenha o trajeto atual de amarelo
            self.desenhar_trajeto(self.trajeto_atual.obter_caminho(), amarelo)

            #Desenha o trajeto combinado de verde escuro
            if self.trajeto_combinado:
                self.desenhar_trajeto(self.trajeto_combinado, verde)

            #Desenha o carro
            self.carro.desenhar(tela)

            # Desenha as viagens para o destino em laranja
            for _, pontos in self.viagens_para_destino:
                self.desenhar_trajeto(pontos, laranja)

            # Destaca a melhor viagem em azul
            if self.melhor_viagem_pontos:
                self.desenhar_trajeto(self.melhor_viagem_pontos, azul)

            #Atualiza a tela
            pygame.display.flip()

            #Determina quantas vezes a tela será atualizada por segundo
            clock.tick(30)