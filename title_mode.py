from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_SPACE

import game_framework
import play_mode # 다음 모드인 play_mode를 임포트합니다.
import main_chracter

image = None

def init():
    global image
    try:
        # (타이틀 이미지 경로를 수정하세요)
        image = load_image('title.png')
    except Exception as e:
        print(f"타이틀 이미지 로드 오류: {e}. 임시 이미지를 사용합니다.")
        image = load_image('UI/backpack_in.png') # 임시 이미지

def finish():
    global image
    del image

def update(dt):
    pass # 타이틀은 정적이므로 update에서 할 일이 없음

def draw():
    clear_canvas()
    if image:
        image.draw(main_chracter.SCREEN_W // 2, main_chracter.SCREEN_H // 2)
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_k:
                game_framework.change_mode(play_mode)

def pause(): pass
def resume(): pass