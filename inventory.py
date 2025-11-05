from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u

import game_framework
import game_world  # play_mode의 월드를 그리기 위해 임포트

# 스크린 크기는 main_chracter에서 가져옴
import main_chracter

SCREEN_W, SCREEN_H = main_chracter.SCREEN_W, main_chracter.SCREEN_H

backpack_image = None


def init():
    global backpack_image
    try:
        backpack_image = load_image('UI/backpack_in.png')
    except Exception as e:
        print(f"배낭 이미지 로드 오류: {e}")
        backpack_image = None


def finish():
    global backpack_image
    del backpack_image


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_u or event.key == SDLK_ESCAPE:
                # U 또는 ESC 키로 인벤토리를 닫음 (pop)
                game_framework.pop_mode()


def update(dt):
    pass  # 인벤토리는 정적이므로 업데이트할 내용 없음


def draw():
    # LEC11 (page 43) [cite: 553] 처럼, item_mode는
    # 뒤의 game_world를 먼저 그리고 그 위에 UI를 그립니다.
    clear_canvas()
    game_world.render()  # play_mode의 객체들을 그대로 그림

    # 그 위에 배낭 UI 그리기
    if backpack_image:
        center_x = SCREEN_W // 2
        center_y = SCREEN_H // 2
        backpack_image.draw(center_x, center_y)

    update_canvas()


def pause():
    pass


def resume():
    pass