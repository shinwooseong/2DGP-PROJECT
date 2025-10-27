# main.py
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import main_chracter
import inventory




def handle_events(player, inv):
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            player.handle_event(event)
            inv.handle_event(event)


running = True
open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H)
Main_player = main_chracter.Main_character()
Main_inventory = inventory.Inventory()

while running:

    # 이벤트 처리
    handle_events(Main_player, Main_inventory)

    # 배낭이 열려있지 않을 때만 객체 업데이트 (캐릭터, 배경 움직이지 않음)
    if not Main_inventory.is_open:
        Main_player.update()

    # 그리기
    clear_canvas()
    Main_player.draw()
    Main_inventory.draw()
    update_canvas()

    delay(0.01)

close_canvas()
