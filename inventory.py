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
    pass


def draw():
    clear_canvas()
    game_world.render()

    # 그 위에 배낭 UI 그리기
    if backpack_image:
        center_x = SCREEN_W // 2
        center_y = SCREEN_H // 2

        # 배낭 이미지의 원본 크기
        img_w = backpack_image.w
        img_h = backpack_image.h

        # 화면에 맞게 스케일 계산 (여백을 위해 0.9 배율 적용)
        scale_w = (SCREEN_W * 0.9) / img_w
        scale_h = (SCREEN_H * 0.9) / img_h
        scale = min(scale_w, scale_h)  # 작은 쪽에 맞춤

        # 스케일된 크기로 그리기
        draw_w = int(img_w * scale)
        draw_h = int(img_h * scale)
        backpack_image.draw(center_x, center_y, draw_w, draw_h)

    update_canvas()


def pause():
    pass


def resume():
    pass