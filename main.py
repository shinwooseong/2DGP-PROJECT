# main.py
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


def draw_inventory_ui(player):
    # 배낭 UI 그리기
    if player.inventory_open and player.backpack_image:
        # 배낭 이미지를 화면 중앙에 그리기
        center_x = main_chracter.SCREEN_W // 2
        center_y = main_chracter.SCREEN_H // 2

        player.backpack_image.draw(center_x, center_y)


running = True
open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H)
Main_player = main_chracter.Main_character()

while running:

    # 이벤트 처리
    handle_events(Main_player)

    # 배낭이 열려있지 않을 때만 객체 업데이트 (캐릭터, 배경 움직이지 않음)
    if not Main_player.inventory_open:
        Main_player.update()

    # 그리기
    clear_canvas()
    Main_player.draw()
    draw_inventory_ui(Main_player)
    update_canvas()

    delay(0.01)

close_canvas()
