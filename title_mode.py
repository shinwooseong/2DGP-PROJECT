from pico2d import *
from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_SPACE, SDLK_k, SDLK_h

import game_framework
import village_mode
import opening_mode
import main_chracter
import shop_mode

image = None
dialogue_box_image = None
dialogue_font = None
show_tutorial = False  # 튜토리얼 표시 여부
bgm = None  # 타이틀 BGM

def init():
    global image, dialogue_box_image, dialogue_font, bgm
    image = load_image('UI/moonlighter_logo.png')

    # 튜토리얼 이미지와 폰트 로드
    dialogue_box_image = load_image('UI/NPC_text.png')
    dialogue_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 24)

    # 타이틀 BGM 로드 및 재생
    if bgm is None:
        try:
            bgm = load_music('Sound/title.mp3')
            if hasattr(bgm, 'set_volume'):
                bgm.set_volume(64)
            bgm.repeat_play()
            print("[BGM] title.mp3 재생 시작")
        except Exception as e:
            print(f"[BGM] 로드 실패: {e}")
            bgm = None

def finish():
    global image, dialogue_box_image, dialogue_font, bgm
    del image
    del dialogue_box_image
    del dialogue_font

    # 타이틀 BGM 정지
    if bgm:
        bgm.stop()


def update(dt):
    pass # 타이틀은 정적이므로 update에서 할 일이 없음

def draw():
    clear_canvas()
    if image:
        image.draw(main_chracter.SCREEN_W // 2, main_chracter.SCREEN_H // 2)

    # 튜토리얼 표시
    if show_tutorial and dialogue_box_image and dialogue_font:
        # 다이얼로그 박스 그리기 (화면 중앙)
        dialogue_box_image.draw(main_chracter.SCREEN_W // 2, main_chracter.SCREEN_H // 2)

        # 튜토리얼 텍스트 그리기
        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 + 150,
                           "【 조작법 】", (255, 255, 255))

        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 + 100,
                           "이동: ↑↓←→ 방향키", (0, 0, 0))
        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 + 60,
                           "상호작용: Enter", (0, 0, 0))
        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 + 20,
                           "인벤토리: U", (0, 0, 0))
        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 - 20,
                           "거래/선택: Y(네) / N(아니오)", (0, 0, 0))
        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 - 60,
                           "취소/대화 종료: ESC", (0, 0, 0))

        dialogue_font.draw(main_chracter.SCREEN_W // 2 - 150, main_chracter.SCREEN_H // 2 - 120,
                           "닫기: ESC 또는 H", (255, 100, 0))
    else:
        # 타이틀 화면에서 항상 표시되는 키 설명
        dialogue_font.draw(50, main_chracter.SCREEN_H - 50,
                           "H: 조작법 보기", (255, 255, 255))
        dialogue_font.draw(50, main_chracter.SCREEN_H - 90,
                           "K: 게임 시작", (240, 25, 215))

    update_canvas()

def handle_events():
    global show_tutorial

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if show_tutorial:
                    show_tutorial = False
                else:
                    game_framework.quit()
            elif event.key == SDLK_h:
                # H 키: 튜토리얼 토글
                show_tutorial = not show_tutorial
            elif event.key == SDLK_k:
                # K 키: 오프닝 모드로 이동
                game_framework.change_mode(opening_mode)

def pause(): pass
def resume(): pass