import asyncio
import curses
import time
import random
from itertools import cycle

LEFT_KEY_CODE = 452
RIGHT_KEY_CODE = 454
UP_KEY_CODE = 450
DOWN_KEY_CODE = 456


def read_controls(canvas):
    """Read keys pressed and returns tuple with controls state."""

    rows_direction = columns_direction = 0

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 2

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -2

    return rows_direction, columns_direction


async def blink(canvas, row, column, symbol='*'):
    while True:
        attributes = [
            curses.A_DIM, curses.A_NORMAL, curses.A_BOLD,
            curses.A_DIM, curses.A_NORMAL, curses.A_BOLD,
        ]
        for attribute in attributes:
            canvas.addstr(row, column, symbol, attribute)
            time.sleep(0.01)
            await asyncio.sleep(0)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def animate_spaceship(canvas, row, column, row_max, column_max, frames):
    for frame in cycle(frames):
        row_frame_size, column_frame_size = get_frame_size(frame)
        spaceship_border = {
            'left_border': column,
            'right_border': column + column_frame_size,
            'upper_border': row,
            'lower_border': row + row_frame_size,
        }

        row_moving, column_moving = read_controls(canvas)

        if spaceship_border['left_border'] + column_moving >= 0 and spaceship_border['right_border'] + column_moving <= column_max:
            column += column_moving

        if spaceship_border['upper_border'] + row_moving >= 0 and spaceship_border['lower_border'] + row_moving <= row_max:
            row += row_moving

        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas):
    screen = curses.initscr()
    row_max, column_max = screen.getmaxyx()
    screen.nodelay(True)
    curses.curs_set(0)
    canvas.border()

    coroutines = []
    for num in range(60):
        coroutines.append(
            blink(
                canvas,
                random.randint(1, row_max - 2),
                random.randint(1, column_max - 2),
                random.choice('+*.:'),
            )
        )

    with open('frames/rocket_frame_1.txt', 'r', encoding='UTF-8') as file:
        frame_1 = file.read()
    with open('frames/rocket_frame_2.txt', 'r', encoding='UTF-8') as file:
        frame_2 = file.read()
    frames = [frame_1, frame_2]

    row_fire, column_fire = 8, 80
    fire_coroutine = fire(canvas, row_fire, column_fire)

    row_ship, column_ship = 5, 80
    spaceship_coroutine = animate_spaceship(canvas, row_ship, column_ship, row_max, column_max, frames)

    while True:
        for coroutine in coroutines:
            coroutine.send(None)
            canvas.refresh()

        try:
            fire_coroutine.send(None)
            canvas.refresh()
        except StopIteration:
            break

        spaceship_coroutine.send(None)
        canvas.refresh()


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
