import time
import curses
import asyncio
from random import randint, choice

from fire_animation import fire

TIC_TIMEOUT = 0.1
STARS_DIGITS = ['+', '*', '.', ':']
STARS_COUNT = 100

async def blink(canvas, row, column, symbol):
    offset = randint(0, 3)
    while True:
        if offset == 0:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            for tic in range(20):
                await asyncio.sleep(0)
            offset+=1
        if offset == 1:
            canvas.addstr(row, column, symbol)
            for tic in range(3):
                await asyncio.sleep(0)
            offset+=1
        if offset == 2:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            for tic in range(5):
                await asyncio.sleep(0)
            offset+=1
        if offset == 3:
            canvas.addstr(row, column, symbol)
            for tic in range(3):
                await asyncio.sleep(0)
            offset = 0


def stars_generator(x, y, stars_count=STARS_COUNT):
    for _ in range(stars_count):
        row = randint(1, x - 1)
        column = randint(1, y - 1)
        symbol = choice(STARS_DIGITS)
        yield row, column, symbol


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()

    coroutines = [
        blink(canvas, row, column, symbol)
        for row, column, symbol in stars_generator(height, width)
    ]

    coroutines.append(fire(canvas, width / 2, height))

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        if len(coroutines) == 0:
            break

        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)


