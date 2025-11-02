# main.py
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import main_chracter
import inventory
from Monster import Green_MS



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

# 몬스터 리스트 생성 (예시 위치)
monsters = [
    Green_MS(300, 200),
    Green_MS(600, 200),
]

while running:

    # 이벤트 처리
    handle_events(Main_player, Main_inventory)

    # 플레이어 업데이트 (dt 계산은 플레이어 내부에서 함)
    if not Main_inventory.is_open:
        Main_player.update()

    # 몬스터 업데이트: 인벤토리 열려있으면 frozen=True로 정지
    for m in monsters:
        m.update(getattr(Main_player, 'dt', 0.01), frozen=Main_inventory.is_open)

    # 그리기
    clear_canvas()
    # 배경이 있으면 먼저 그리고
    for m in monsters:
        m.draw()
    Main_player.draw()
    Main_inventory.draw()
    update_canvas()

    delay(0.01)

close_canvas()
