import time
import curses
import asyncio
from random import randint
from itertools import cycle
from environs import Env
from curses_tools import draw_frame, get_frame_size, stars_generator, get_arts_from_folder
from fire_animation import fire

env = Env()
env.read_env()


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


async def animate_spaceship(canvas, row, column, frames):
    frames_cycle = cycle(frames)

    while True:
        current_frame = next(frames_cycle)

        frame_size_y, frame_size_x = get_frame_size(current_frame)
        frame_pos_x = round(column) - round(frame_size_x / 2)
        frame_pos_y = round(row) - round(frame_size_y / 2)

        draw_frame(canvas, frame_pos_y, frame_pos_x, current_frame)
        canvas.refresh()

        for tic in range(1):
            await asyncio.sleep(0)

        draw_frame(
            canvas,
            frame_pos_y,
            frame_pos_x,
            current_frame,
            negative=True
        )

        
def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    canvas_heigth, canvas_width = canvas.getmaxyx()

    coroutines = [
        blink(canvas, row, column, symbol)
        for row, column, symbol in stars_generator(canvas_heigth, canvas_width)
    ]

    gunshot = fire(canvas, canvas_heigth - 1, canvas_width / 2)
    coroutines.append(gunshot)

    arts = get_arts_from_folder(env('ANIMATIONS_PATH'))
    coro_rocket_anim = animate_spaceship(
        canvas,
        canvas_heigth / 2,
        canvas_width / 2,
        arts
    )
    coroutines.append(coro_rocket_anim)

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        if len(coroutines) == 0:
            break

        time.sleep(env.float('TIC_TIMEOUT'))


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)


