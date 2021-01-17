import random as rnd
import itertools as itt
import networkx as nx
import enum


class Color(enum.Enum):
    BLACK = 0
    BLUE = 1
    GREEN = 2
    RED = 3
    PURPLE = 4
    BROWN = 5
    DEEP_PINK = 6
    OLIVE = 7

    def as_string(self):
        AS_STRING = {0: 'black', 1: 'blue', 2: 'green', 3: 'red', 4: 'purple',
                     5: 'brown', 6: 'pink', 7: 'olive'}
        return AS_STRING[self.value]

    def __str__(self):
        return self.as_string()

    def __int__(self):
        return self.value


PALETTE = [Color.BLACK, Color.BLUE, Color.GREEN, Color.PURPLE, Color.BROWN, Color.DEEP_PINK, Color.OLIVE]


# PALETTE = [Color.BLACK, Color.GREEN]


# Некорректные параметры хода:
class InvalidParams(Exception):
    pass


# Игра закончена:
class GameOver(Exception):
    pass


# Невозможно передвинуть шарик (отсутствует путь):
class NoPath(Exception):
    pass


class LinesGame:
    def __init__(self):
        self.field_size = 9  # размеры игрового поля
        self.line_length = 5  # минимальное длина линии
        self.new_balls_count = 3  # количество добавляемых шариков
        self.cells = dict()  # ячейки на игровом поле
        self.paths = nx.Graph()  # возможные переходы между ячейками игрового поля
        self.lanes = self.get_lanes()  # все дорожки на игровом поле
        self.start_position = dict()  # начальная позиция
        self.moves = []  # выполненные ходы
        self.score = 0  # набранные очки
        self.is_over = False  # признак окончания игры
        self.start_game()  # сразу стартуем новую игру

    # начать игру сначала (накопленный прогресс при этом сбрасывается)
    def start_game(self):
        cell_ids = self.get_cells()
        # создаем ячейки:
        self.cells.clear()
        for c_id in cell_ids:
            self.cells[c_id] = Cell(c_id)
        # переходы между ячейками на игровом поле:
        self.paths.clear()
        for c_id in cell_ids:
            for n_c_id in self.get_neighbors(c_id):
                self.paths.add_edge(c_id, n_c_id, weight=1)
        # распределяем новые шарики:
        new_balls = self.distribute_new_balls()
        self.start_position = new_balls
        # сбрасываем накопленные очки:
        self.score = 0
        # сбрасываем признак окончания игры:
        self.is_over = False
        # сбрасываем запомненные ходы:
        self.moves.clear()

    # сделать очередной ход в игре:
    def make_move(self, from_cell_id, to_cell_id):
        # сначала проверяем правильно ли заданы параметры для выполнения хода:
        if self.is_over:
            raise GameOver('Игра закончена')
        if not self.is_cell_in_field(from_cell_id) or (
                not self.is_cell_in_field(to_cell_id)):
            raise InvalidParams('Некорректно указаны номера ячеек')
        if from_cell_id == to_cell_id:
            raise InvalidParams('Совпадают исходная и целевая ячейки')
        if self.cells[from_cell_id].is_free():
            raise InvalidParams('Нет шарика в исходной ячейке')
        if not self.cells[to_cell_id].is_free():
            raise InvalidParams('Целевая ячейка занята')

        # пробуем переместить шарик на новую позицию игрового поля:
        try:
            path = self.relocate_ball(from_cell_id, to_cell_id)
        except NoPath as e:
            raise NoPath('Нет пути для перемещения шарика')

        current_move = Move()

        current_move.set_ball(self.cells[to_cell_id].get_ball())
        current_move.set_path(path)

        # находим образовавшиеся после перемещения линии:
        lines = self.get_lines()

        # убираем шарики с соответствующих позиций найденных линий:
        cell_ids = set()
        for line in lines:
            cell_ids |= set(line)
        for c_id in cell_ids:
            self.free_cell(c_id)
        current_move.set_freed_cells(cell_ids)

        # считаем очки за каждую собранную линию и добавляем их к набранным очкам:
        points = 0
        for line in lines:
            points += self.calculate_points(len(line))
        self.score += points
        current_move.set_points(points)

        # распределяем новые шарики по игровому полю:
        new_balls = self.distribute_new_balls()
        current_move.set_new_balls(new_balls)

        # находим образовавшиеся после распределения новых шариков линии
        # и убираем шарики с соответствующих позиций найденных линий:
        lines = self.get_lines()
        cell_ids = set()
        for line in lines:
            cell_ids |= set(line)
        for c_id in cell_ids:
            self.free_cell(c_id)
        current_move.set_freed_cells_after_new_balls(cell_ids)

        # запоминаем выполненный ход
        self.moves.append(current_move)

        # проверяем не закончена ли игра (все яячейки пустые)
        # и если закончена, выставляем соответствующий признак
        if not self.get_free_cells():
            self.is_over = True

        return self.get_last_move()

    # сгенерить и распределить новые шарики по игровому полю
    # возвращает распределение в виде словаря "(x,y)->ball":
    def distribute_new_balls(self):
        new_balls = dict()
        new_cells_count = min([self.new_balls_count, len(list(self.paths.nodes))])
        new_cell_ids = rnd.sample(list(self.paths.nodes), k=new_cells_count)
        for c_id in new_cell_ids:
            new_ball = Ball(rnd.choice(PALETTE))
            self.fill_cell(c_id, new_ball)
            new_balls[c_id] = new_ball
        return new_balls

    # переместить шарик из одной ячейки в другую:
    def relocate_ball(self, from_cell_id, to_cell_id):
        try:
            for n_c_id in self.get_free_neighbors(from_cell_id):
                self.paths.add_edge(from_cell_id, n_c_id, weight=1)
            path = (nx.shortest_path(self.paths, from_cell_id, to_cell_id, weight='weight'))
        except nx.exception.NetworkXNoPath as e:  # если пути нет, надо восстановить граф
            self.paths.remove_node(from_cell_id)
            raise NoPath('Нет пути для перемещания шарика')
        ball = self.cells[from_cell_id].get_ball()
        self.free_cell(from_cell_id)
        self.fill_cell(to_cell_id, ball)
        return path

    # очистить указанную ячейку:
    def free_cell(self, cell_id):
        # убираем шарик из указанной ячейки:
        self.cells[cell_id].pull_ball()
        # добавляем пути к очищенной ячейке:
        for n_c_id in self.get_free_neighbors(cell_id):
            self.paths.add_edge(cell_id, n_c_id, weight=1)

    # поместить шарик в указанную ячейку:
    def fill_cell(self, cell_id, ball):
        if ball is not None:
            # добавляем шарик в указанную ячейку:
            self.cells[cell_id].put_ball(ball)
            # удаляем пути к вновь заполненной ячейке:
            self.paths.remove_node(cell_id)

    # вычисляет количество полученных очков за собранную линию указанной длины
    def calculate_points(self, line_len):
        return line_len * (1 + line_len - self.line_length)

    # найти все линии из одинаковых шариков, имеющиеся на игровом поле:
    def get_lines(self):
        lines = []
        for lane in self.lanes:
            lane_len = len(lane)
            lane_cells = [self.cells[c_id] for c_id in lane]
            line_in_lane_was_founded = False
            for line_len in reversed(range(self.line_length, lane_len + 1)):
                for shift in range(0, lane_len - line_len + 1):
                    cells = lane_cells[shift:(line_len + shift)]
                    if any([c.is_free() for c in cells]):
                        continue
                    colors = [c.get_ball().get_color() for c in cells]
                    if all([color == colors[0] for color in colors[1:]]):
                        lines.append(sorted([c.get_cell_id() for c in cells]))
                        line_in_lane_was_founded = True
                        break
                if line_in_lane_was_founded:
                    break
        return lines

    #  получить все дорожки на игровом поле:
    def get_lanes(self):
        lanes = []
        #  горизонтальные дорожки:
        for i in range(0, self.field_size):
            lane = list(itt.product(range(0, self.field_size), [i]))
            lanes.append(lane)
        #  вертикальные дорожки:
        for i in range(0, self.field_size):
            lane = list(itt.product([i], range(0, self.field_size)))
            lanes.append(lane)
        #  диагональные дорожки слева направо:
        for i in range(1 - self.field_size, self.field_size):
            y_range = range(0, self.field_size)
            x_range = [x + i for x in range(0, self.field_size)]
            lane = list(filter(lambda c_id: self.is_cell_in_field(c_id), zip(x_range, y_range)))
            if len(lane) >= self.line_length:
                lanes.append(lane)
        #  диагональные дорожки справа налево:
        for i in range(1 - self.field_size, self.field_size):
            y_range = reversed(range(0, self.field_size))
            x_range = [x - i for x in range(0, self.field_size)]
            lane = list(filter(lambda c_id: self.is_cell_in_field(c_id), zip(x_range, y_range)))
            if len(lane) >= self.line_length:
                lanes.append(lane)
        return lanes

    # найти все пустые соседние ячейки (c которыми возможны переходы):
    def get_free_neighbors(self, cell_id):
        if not self.is_cell_in_field(cell_id):
            return []
        empty_neighbors = list(filter(lambda c_id: self.cells[c_id].is_free(),
                                      self.get_neighbors(cell_id)))
        return empty_neighbors

    # найти все соседние ячейки:
    def get_neighbors(self, cell_id):
        if not self.is_cell_in_field(cell_id):
            return []
        x, y = cell_id
        neighbors = list(filter(lambda c_id: self.is_cell_in_field(c_id),
                                [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]))
        return neighbors

    # проверить принадлежность ячейки игровому полю:
    def is_cell_in_field(self, cell_id):
        x, y = cell_id
        return (0 <= x <= self.field_size - 1) and (0 <= y <= self.field_size - 1)

    # получить размер игрового поля:
    def get_field_size(self):
        return self.field_size

    # получить общее количество набранных очков
    def get_score(self):
        return self.score

    # получить все ячейки на игровом поле:
    def get_cells(self):
        return list(itt.product(range(0, self.field_size), range(0, self.field_size)))

    # получить признак окончания игры:
    def get_is_over(self):
        return self.is_over

    # найти все свободные ячейки на игровом поле:
    def get_free_cells(self):
        free_cells = []
        for c_id in self.cells:
            if self.cells[c_id].is_free():
                free_cells.append(c_id)
        return free_cells

    # найти все заполненные ячейки на игровом поле:
    def get_filled_cells(self):
        filled_cells = []
        for c_id in self.cells:
            if not self.cells[c_id].is_free():
                filled_cells.append(c_id)
        return filled_cells

    # получить шарик из указанной ячейки:
    def get_ball(self, cell_id):
        ball = None
        if self.is_cell_in_field(cell_id):
            if not self.cells[cell_id].is_free():
                ball = self.cells[cell_id].get_ball()
        return ball

    # получить стартовую позицию
    def get_start_position(self):
        position = dict()
        for cell_id in self.start_position:
            position[cell_id] = self.start_position[cell_id].copy()
        return position

    # получить список всех выполненных ходов:
    def get_moves(self):
        moves = []
        for move in self.moves:
            moves.append(move.copy())
        return moves

    # получить последний выполненный ход:
    def get_last_move(self):
        if not self.moves:
            return None
        return self.moves[-1].copy()

    def __str__(self):
        # строковое представление игры для печати
        SPACE = ' '
        NEWLINE = '\n'
        full_info = ''  # NEWLINE
        full_info += '**************** Lines *****************'
        full_info += NEWLINE
        full_info += 'Игровое поле:'
        full_info += NEWLINE
        full_info += SPACE * 3 + SPACE + SPACE.join(['%0.3d' % x for x in range(0, self.field_size)])
        full_info += NEWLINE
        for y in range(0, self.field_size):
            line = []
            for x in range(0, self.field_size):
                cell = self.cells[(x, y)]
                if not cell.is_free():
                    line.append(str(cell.get_ball().get_color())[0:3])
                else:
                    line.append(SPACE * 3)
            full_info += '%0.3d' % y + SPACE + SPACE.join(line)
            full_info += NEWLINE
        full_info += '****************************************'
        full_info += NEWLINE
        return full_info


# Выполненный игровой ход:
class Move:
    def __init__(self):
        self.ball = None  # шарик, который был перемещен
        self.path = []  # маршрут перемещения шарика, список ячеек
        self.freed_cells = set()  # освобожденные ячейки после перемещения шарика
        self.points = 0  # полученные очки
        self.new_balls = dict()  # распределение новых шариков по ячейкам
        self.freed_cells_after_new_balls = set()  # освобожденные ячейки после распределения новых шариков

    def set_ball(self, ball):
        self.ball = ball.copy()

    def get_ball(self):
        return self.ball.copy()

    def set_path(self, path):
        self.path = path.copy()

    def get_path(self):
        return self.path.copy()

    def get_path_from(self):
        if not self.path:
            return None
        return self.path[0]

    def get_path_to(self):
        if not self.path:
            return None
        return self.path[-1]

    def set_freed_cells(self, cell_ids):
        self.freed_cells.clear()
        self.freed_cells |= cell_ids

    def get_freed_cells(self):
        return self.freed_cells.copy()

    def set_points(self, points):
        self.points = points

    def get_points(self):
        return self.points

    def set_new_balls(self, balls_distribution):
        self.new_balls.clear()
        for c_id in balls_distribution:
            self.new_balls[c_id] = balls_distribution[c_id].copy()

    def get_new_balls(self):
        new_balls = dict()
        if self.new_balls is None:
            return new_balls
        for c_id in self.new_balls:
            new_balls[c_id] = self.new_balls[c_id].copy()
        return new_balls

    def set_freed_cells_after_new_balls(self, cell_ids):
        self.freed_cells_after_new_balls.clear()
        self.freed_cells_after_new_balls |= cell_ids

    def get_freed_cells_after_new_balls(self):
        return self.freed_cells_after_new_balls.copy()

    def copy(self):
        move_copy = Move()
        move_copy.set_ball(self.get_ball())
        move_copy.set_path(self.get_path())
        move_copy.set_freed_cells(self.get_freed_cells())
        move_copy.set_points(self.get_points())
        move_copy.set_new_balls(self.get_new_balls())
        move_copy.set_freed_cells_after_new_balls(self.get_freed_cells_after_new_balls())
        return move_copy


class Cell:
    def __init__(self, cell_id):
        self.cell_id = cell_id
        self.ball = None

    def get_cell_id(self):
        return self.cell_id

    # проверить есть ли шарик в ячейке
    def is_free(self):
        return self.ball is None

    # положить шарик в ячейку;
    # если шарик там уже был, он заменяется новым;
    # None игнорируется
    def put_ball(self, ball):
        if ball is not None:
            self.ball = ball.copy()

    # извлечь шарик из ячейки, ячейка становится пустой;
    # извлеченный шарик возвращается;
    # если в ячейке шарика не было, то возвращается None
    def pull_ball(self):
        if not self.is_free():
            ball = self.ball.copy()
        else:
            ball = None
        self.ball = None
        return ball

    # просто посмотреть какой шарик находится в ячейке, не извлекая его
    def get_ball(self):
        if self.is_free():
            return None
        else:
            return self.ball.copy()


class Ball:
    def __init__(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def copy(self):
        return Ball(self.color)


if __name__ == '__main__':
    g = LinesGame()  # новая игра
    print(g)
