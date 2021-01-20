from copy import deepcopy

import pygame


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        color = [pygame.Color('black'), pygame.Color('white')]
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, 'white',
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)
                pygame.draw.rect(screen, color[self.board[y][x]],
                                 (x * self.cell_size + self.left + 1, y * self.cell_size + self.top + 1,
                                  self.cell_size - 2,
                                  self.cell_size - 2))

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        # print(cell)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        if not (x in range(self.width) and y in range(self.height)):
            return None
        else:
            return x, y

    def on_click(self, cell_coords):
        if cell_coords:
            x, y = cell_coords[0], cell_coords[1]
            self.board[y][x] = (self.board[y][x] + 1) % 2


class Life(Board):
    def __init__(self, width, height):
        super().__init__(width, height)

    def render(self, screen):
        color = [pygame.Color('black'), pygame.Color('green')]
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, 'white',
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)
                pygame.draw.rect(screen, color[self.board[y][x]],
                                 (x * self.cell_size + self.left + 1, y * self.cell_size + self.top + 1,
                                  self.cell_size - 2,
                                  self.cell_size - 2))

    def next_move(self):
        copy_board = deepcopy(self.board)
        for y in range(self.height):
            for x in range(self.width):
                s_life = 0
                for row in range(y - 1, y + 2):
                    for col in range(x - 1, x + 2):
                        if row in range(self.height) and col in range(self.width):
                            s_life += self.board[row][col]
                s_life -= self.board[y][x]
                if self.board[y][x] == 1:
                    if s_life not in [2, 3]:
                        copy_board[y][x] = 0
                else:
                    if s_life == 3:
                        copy_board[y][x] = 1
        self.board = copy_board


pygame.init()
pygame.display.set_caption('life')
n, m = 30, 30
left, top, cell_size = 15, 15, 15
size = left * 2 + cell_size * n, top * 2 + cell_size * m
screen = pygame.display.set_mode(size)
screen.fill((0, 0, 0))

# размер поля
board = Life(n, m)
board.set_view(left, top, cell_size)
time_on = False
running = True
tick = 0
v = 10

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                time_on = not time_on
            elif event.button == 1:
                board.get_click(event.pos)
            elif event.button == 4:
                v += 1
            elif event.button == 5:
                v -= 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            time_on = not time_on
    screen.fill((0, 0, 0))
    board.render(screen)
    if tick >= v:
        if time_on:
            board.next_move()
        tick = 0
    pygame.display.flip()
    tick += 1
pygame.quit()
