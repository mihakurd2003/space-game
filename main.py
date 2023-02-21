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
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for call_num in range(random.randint(15, 20)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for call_num in range(random.randint(1, 5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for call_num in range(random.randint(1, 5)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_NORMAL)
        for call_num in range(random.randint(1, 5)):
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
        row_moving, column_moving = read_controls(canvas)

        row = max(min(row + row_moving, row_max - row_frame_size), 0)
        column = max(min(column + column_moving, column_max - column_frame_size), 0)

        draw_frame(canvas, row, column, frame)

        await asyncio.sleep(0)

        draw_frame(canvas, row, column, frame, negative=True)


def draw(canvas):
    screen = curses.initscr()
    screen_row_max, screen_column_max = screen.getmaxyx()
    screen.nodelay(True)
    curses.curs_set(0)
    canvas.border()

    coroutines = []
    max_visible_row, max_visible_column = (screen_row_max - 2, screen_column_max - 2)
    for num in range(80):
        coroutines.append(
            blink(
                canvas,
                random.randint(1, max_visible_row),
                random.randint(1, max_visible_column),
                random.choice('+*.\''),
            )
        )

    with open('frames/rocket_frame_1.txt', 'r', encoding='UTF-8') as file:
        frame_1 = file.read()
    with open('frames/rocket_frame_2.txt', 'r', encoding='UTF-8') as file:
        frame_2 = file.read()
    frames = [frame_1, frame_1, frame_2, frame_2]

    center_row_fire, center_column_fire = 10, 80
    coroutines.append(fire(canvas, center_row_fire, center_column_fire))

    center_row_ship, center_column_ship = 4, 80
    coroutines.append(animate_spaceship(canvas, center_row_ship, center_column_ship, max_visible_row, max_visible_column, frames))

    while True:
        try:
            for coroutine in coroutines:
                coroutine.send(None)
            canvas.refresh()
            time.sleep(0.1)
        except StopIteration:
            break


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
