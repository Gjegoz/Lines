import LinesGame as g

SP = ' '
SHIFT = SP * 5
NL = '\n'

game = g.LinesGame()


def print_game_state():
    info = 'Состояние игры:' + NL
    info += SP * 3 + SP + SP.join(['%0.3d' % x for x in range(0, game.get_field_size())]) + NL
    for y in range(0, game.get_field_size()):
        line = []
        for x in range(0, game.get_field_size()):
            ball = game.get_ball((x, y))
            if ball is not None:
                line.append(str(ball.get_color())[0:3])
            else:
                line.append(SP * 3)
        info += '%0.3d' % y + SP + SP.join(line) + NL
    info += 'Общий счет:' + SP + str(game.get_score()) + NL
    if game.get_is_over():
        info += 'Игра окончена' + NL
    print(info)


def print_path():
    info = SHIFT + 'Перемещение шарика:'
    path = game.get_last_move().get_path()
    ball = game.get_last_move().get_ball()
    info += SP + str(ball.get_color()) + SP + '->'.join([str(step) for step in path]) + NL
    info += SHIFT + SP * 3 + SP + SP.join(['%0.3d' % x for x in range(0, game.get_field_size())]) + NL
    for y in range(0, game.get_field_size()):
        line = []
        for x in range(0, game.get_field_size()):
            if (x, y) == game.get_last_move().get_path_from():
                line.append(SP + '*' + SP)
            elif (x, y) == game.get_last_move().get_path_to():
                line.append(str(ball.get_color())[0:3])
            elif (x, y) in path:
                line.append(SP + '*' + SP)
            else:
                line.append(SP * 3)
        info += SHIFT + '%0.3d' % y + SP + SP.join(line) + NL
    print(info)


def print_freed_lines():
    info = SHIFT + 'Линии после перемещения шарика:' + NL
    cells = game.get_last_move().get_freed_cells()
    info += SHIFT + SP * 3 + SP + SP.join(['%0.3d' % x for x in range(0, game.get_field_size())]) + NL
    for y in range(0, game.get_field_size()):
        line = []
        for x in range(0, game.get_field_size()):
            if (x, y) in cells:
                line.append(SP + 'x' + SP)
            else:
                line.append(SP * 3)
        info += SHIFT + '%0.3d' % y + SP + SP.join(line) + NL
    print(info)


def print_new_balls():
    info = SHIFT + 'Новые шарики:'
    new_balls = game.get_last_move().get_new_balls()
    info += SP + '; '.join([str(new_balls[c_id].get_color()) + '->' + str(c_id) for c_id in new_balls]) + NL
    info += SHIFT + SP * 3 + SP + SP.join(['%0.3d' % x for x in range(0, game.get_field_size())]) + NL
    for y in range(0, game.get_field_size()):
        line = []
        for x in range(0, game.get_field_size()):
            if (x, y) in new_balls:
                line.append(str(new_balls[(x, y)].get_color())[0:3])
            else:
                line.append(SP * 3)
        info += SHIFT + '%0.3d' % y + SP + SP.join(line) + NL
    print(info)


def print_freed_lines_after_new_balls():
    info = SHIFT + 'Линии после добавления новых шариков:' + NL
    cells = game.get_last_move().get_freed_cells_after_new_balls()
    info += SHIFT + SP * 3 + SP + SP.join(['%0.3d' % x for x in range(0, game.get_field_size())]) + NL
    for y in range(0, game.get_field_size()):
        line = []
        for x in range(0, game.get_field_size()):
            if (x, y) in cells:
                line.append(SP + 'x' + SP)
            else:
                line.append(SP * 3)
        info += SHIFT + '%0.3d' % y + SP + SP.join(line) + NL
    print(info)


def print_points():
    info = SHIFT + 'Набрано очков:' + SP + str(game.get_last_move().get_points()) + NL
    print(info)


if __name__ == '__main__':
    print_game_state()
    stop = False
    while not stop:
        print('Ваш ход: ', end='')
        s = input()
        if s.lower() in ['stop', 'exit']:
            stop = True
            continue
        if s.lower() in ['new', 'start']:
            game.start_game()
            print_game_state()
            continue
        try:
            s_from, s_to = s.split(' ')
            x_from, y_from = s_from.split(',')
            x_to, y_to = s_to.split(',')
            x_f = int(x_from)
            y_f = int(y_from)
            x_t = int(x_to)
            y_t = int(y_to)
        except Exception as e:
            print('Некорректный ввод')
            continue
        try:
            game.make_move((x_f, y_f), (x_t, y_t))
            print_path()
            print_freed_lines()
            print_points()
            print_new_balls()
            print_freed_lines_after_new_balls()
            print_game_state()
            if game.get_is_over():
                stop = True
        except g.InvalidParams as e:
            print(e)
        except g.GameOver as e:
            print(e)
        except g.NoPath as e:
            print(e)