import pygame
import random
import heapq
import networkx as nx
import matplotlib.pyplot as plt

# Configurações do jogo
TAMANHO_GRADE = 20
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)

# Direções
CIMA = (0, -1)
BAIXO = (0, 1)
ESQUERDA = (-1, 0)
DIREITA = (1, 0)
posicao_comida = 0
posicao_cobra = (0, 0)

class Cobra:
    def __init__(self, largura_grade, altura_grade):
        self.largura_grade = largura_grade
        self.altura_grade = altura_grade
        self.corpo = [(0, 0), (0, 1)]  
        self.direcao = random.choice([BAIXO, DIREITA, CIMA, ESQUERDA])
        self.pontuacao = 0
        self.caminhos_astar = []  # Lista para armazenar os caminhos calculados pela função A*

    def mover(self):
        x, y = self.corpo[0]
        dx, dy = self.direcao
        nova_cabeca = ((x + dx) % self.largura_grade, (y + dy) % self.altura_grade)

        # Manter apenas os dois primeiros segmentos do corpo
        self.corpo = [nova_cabeca] + self.corpo[:1]

        # Verificar se a cabeça alcançou a comida
        if nova_cabeca == self.comida.posicao:
            self.pontuacao += 1

        # Movimento A*
        astar = AStar(self.corpo[0], self.comida.posicao, self.largura_grade, self.altura_grade)
        caminho = astar.buscar()
        if len(caminho) > 1:  # Garantir que há um próximo ponto no caminho
            proxima_celula = caminho[1]
            x, y = self.corpo[0]
            dx = proxima_celula[0] - x
            dy = proxima_celula[1] - y
            if dx == 1:
                self.direcao = DIREITA
            elif dx == -1:
                self.direcao = ESQUERDA
            elif dy == 1:
                self.direcao = BAIXO
            elif dy == -1:
                self.direcao = CIMA

        # Salvar o caminho calculado
        self.caminhos_astar.append(caminho)

    def mudar_direcao(self, direcao):
        if (direcao[0] * -1, direcao[1] * -1) != self.direcao:
            self.direcao = direcao

    def desenhar(self, superficie):
        for segmento in self.corpo:
            pygame.draw.rect(superficie, BRANCO, (segmento[0] * TAMANHO_GRADE, segmento[1] * TAMANHO_GRADE, TAMANHO_GRADE, TAMANHO_GRADE))

    def definir_comida(self, comida):
        self.comida = comida

class Comida:
    def __init__(self, largura_grade, altura_grade):
        self.largura_grade = largura_grade
        self.altura_grade = altura_grade
        self.posicao = (random.randint(0, largura_grade - 1), random.randint(0, altura_grade - 1))
        self.comida_consumida = True  # Inicialmente, a comida não foi comida

    def desenhar(self, superficie):
        pygame.draw.rect(superficie, VERMELHO, (self.posicao[0] * TAMANHO_GRADE, self.posicao[1] * TAMANHO_GRADE, TAMANHO_GRADE, TAMANHO_GRADE))


class AStar:
    def __init__(self, inicio, objetivo, largura_grade, altura_grade):
        self.inicio = inicio
        self.objetivo = objetivo
        self.largura_grade = largura_grade
        self.altura_grade = altura_grade

    def heuristica(self, no):
        x1, y1 = no
        x2, y2 = self.objetivo
        return abs(x1 - x2) + abs(y1 - y2)

    def obter_vizinhos(self, no):
        x, y = no
        vizinhos = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        vizinhos = [(x, y) for x, y in vizinhos if 0 <= x < self.largura_grade and 0 <= y < self.altura_grade]
        return vizinhos

    def reconstruir_caminho(self, veio_de):
        atual = self.objetivo
        caminho = [atual]
        while atual != self.inicio:
            atual = veio_de[atual]
            caminho.append(atual)
        caminho.reverse()
        return caminho

    def buscar(self):
        fronteira = []
        heapq.heappush(fronteira, (0, self.inicio))
        veio_de = {}
        custo_ate_agora = {self.inicio: 0}

        while fronteira:
            custo_atual, no_atual = heapq.heappop(fronteira)

            if no_atual == self.objetivo:
                break

            for vizinho in self.obter_vizinhos(no_atual):
                novo_custo = custo_ate_agora[no_atual] + 1
                if vizinho not in custo_ate_agora or novo_custo < custo_ate_agora[vizinho]:
                    custo_ate_agora[vizinho] = novo_custo
                    prioridade = novo_custo + self.heuristica(vizinho)
                    heapq.heappush(fronteira, (prioridade, vizinho))
                    veio_de[vizinho] = no_atual

        return self.reconstruir_caminho(veio_de)

def desenhar_grafico_final(largura_grade, altura_grade, caminhos_astar, posicao_inicial_cobra, posicao_comida):
    # Criando um grafo vazio
    G = nx.Graph()

    # Adicionando nós ao grafo com as coordenadas corretas
    for x in range(largura_grade):
        for y in range(altura_grade):
            G.add_node((x, y))

    # Adicionando arestas ao grafo com base nos caminhos A*
    for caminho in caminhos_astar:
        for i in range(len(caminho) - 1):
            G.add_edge(caminho[i], caminho[i + 1])

    # Plotando o grafo
    plt.figure(figsize=(10, 10))

    # Definindo a posição dos nós no gráfico
    pos = {}
    for x in range(largura_grade):
        for y in range(altura_grade):
            pos[(x, y)] = (x, altura_grade - y - 1)

    nx.draw(G, pos, with_labels=True, node_size=700, font_size=8, node_color='lightblue')

    # Desenhar ponto inicial (cobra)
    nx.draw_networkx_nodes(G, pos, nodelist=[posicao_inicial_cobra], node_color='green', node_size=200)

    # Desenhar ponto final (comida)
    nx.draw_networkx_nodes(G, pos, nodelist=[posicao_comida], node_color='red', node_size=200)

    plt.legend()
    plt.show()

def main():
    largura_grade = 20  # Largura da grade
    altura_grade = 10  # Altura da grade

    pygame.init()

    LARGURA_TELA = largura_grade * TAMANHO_GRADE  # Atualiza a largura da tela
    ALTURA_TELA = altura_grade * TAMANHO_GRADE  # Atualiza a altura da tela

    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Jogo da Cobra")
    relogio = pygame.time.Clock()

    cobra = Cobra(largura_grade, altura_grade)
    comida = Comida(largura_grade, altura_grade)
    posicao_cobra = cobra.corpo[0]
    cobra.definir_comida(comida)

    comida_consumida = False  

    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    cobra.mudar_direcao(CIMA)
                elif evento.key == pygame.K_DOWN:
                    cobra.mudar_direcao(BAIXO)
                elif evento.key == pygame.K_LEFT:
                    cobra.mudar_direcao(ESQUERDA)
                elif evento.key == pygame.K_RIGHT:
                    cobra.mudar_direcao(DIREITA)

        cobra.mover()

        if cobra.corpo[0] == comida.posicao:
            if not comida_consumida:  
                cobra.corpo.append(cobra.corpo[-1])
        else:
            comida_consumida = False

        tela.fill(PRETO)
        cobra.desenhar(tela)
        comida.desenhar(tela)

        pygame.display.flip()
        relogio.tick(3)
        if cobra.pontuacao == 1:
            break

    posicao_comida = comida.posicao

    # Desenhar o gráfico final com os caminhos A*
    desenhar_grafico_final(largura_grade, altura_grade, cobra.caminhos_astar, posicao_cobra, posicao_comida)

if __name__ == "__main__":
    main()
