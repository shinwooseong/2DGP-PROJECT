# main.py (Commit 1)
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import main_chracter




def handle_events(player):
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            player.handle_event(event)


running = True
open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H)
Main_player = main_chracter.Main_character()

while running:

    # 이벤트 처리
    handle_events(Main_player)

    # 객체 업데이트
    Main_player.update()

    # 그리기
    clear_canvas()
    Main_player.draw()
    update_canvas()

    delay(0.01)

close_canvas()
