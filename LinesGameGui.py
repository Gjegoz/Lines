import LinesGame as g
import pygame
import random

class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[''] * width for _ in range(height)]

        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

        size = width * self.cell_size * 2 + 2 * self.left, height * self.cell_size * 2 + 2 * self.top
        self.screen = pygame.display.set_mode(size)
        self.screen.fill((0, 0, 0))

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        # print(self.board)
        for y in range(self.height):
            for x in range(self.width):
                # рисуем границу ячейки
                pygame.draw.rect(self.screen, 'grey80',
                                 (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                                  self.cell_size), 1)
                # рисуем фон ячейки
                pygame.draw.rect(self.screen, 'grey20',
                                 (x * self.cell_size + self.left + 1, y * self.cell_size + self.top + 1, self.cell_size - 2,
                                  self.cell_size - 2))
                # рисуем шарик в ячейке
                if self.board[x][y] != '':
                    ball_x = x * self.cell_size + self.cell_size / 2 + self.left
                    ball_y = y * self.cell_size + self.cell_size / 2 + self.top
                    pygame.draw.circle(self.screen, self.board[x][y], [ball_x, ball_y], 22, 100)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        print(cell)
        return self.on_click(cell)

    def get_cell(self, mouse_pos):
        x = (mouse_pos[0] - self.left) // self.cell_size
        y = (mouse_pos[1] - self.top) // self.cell_size
        if not (x in range(self.width) and y in range(self.height)):
            return None
        else:
            return x, y

    def on_click(self, cell_coords):
        x, y = cell_coords[0], cell_coords[1]
        self.delete_ball(x, y)
        return x, y

    def draw_ball(self, x, y, color):   # координаты в клетках
        self.board[x][y] = color

    def delete_ball(self, x, y):
        self.board[x][y] = ''


# class new_ball:
#     def __init__(self, x, y, color):    # координаты в пикслях
#         self.color = color
#         self.x = x
#         self.y = y
#
#     def render(self, screen):
#         r = 22
#         zap = 100
#         coords = [self.x, self.y]
#         pygame.draw.circle(screen, self.color, coords, r, zap)


pygame.init()

game = g.LinesGame()

board = Board(game.get_field_size(), game.get_field_size())
board.set_view(10, 10, 60)

running = True

move_coordinates = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = board.get_click(event.pos)
            move_coordinates.append((x, y))

            if len(move_coordinates) == 2:
                try:
                    game.make_move(move_coordinates[0], move_coordinates[1])
                except g.InvalidParams as e:
                    pass
                except g.GameOver as e:
                    pass
                except g.NoPath as e:
                    pass
                finally:
                    move_coordinates.clear()

    for x in range(0, board.width):
        for y in range(0, board.height):
            ball = game.get_ball((x, y))
            if ball is not None:
                board.draw_ball(x, y, str(ball.get_color()))
            else:
                board.delete_ball(x, y)

    board.render()
    pygame.display.flip()


# отлавливание клика мышки в опр. клетке
# нарисовать Шарик в заданной клетке:
#
# -стирание его
# -считать цвет, в какой клетке шарик.
# перемещение шарика
# создание 3х шариков
# стирание сделанных линий
# очки
