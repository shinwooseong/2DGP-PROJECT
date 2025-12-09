from pico2d import load_image, load_font, clear_canvas, update_canvas, get_events
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_RETURN

import game_framework

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

# 이미지와 폰트
opening_image = None
backpack_image = None
opening_font = None

def init():
    global opening_image, backpack_image, opening_font

    # opening.png 로드
    opening_image = load_image('map/opening.png')

    # backpack_in 이미지 로드
    backpack_image = load_image('UI/backpack_in.png')

    # 설명 텍스트 폰트 로드
    opening_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)

    print("======> 오프닝 모드 시작 ======>")

def finish():
    global opening_image, backpack_image, opening_font
    opening_image = None
    backpack_image = None
    opening_font = None

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_RETURN:
                # Enter 키로 마을 모드로 진입
                print("======> 마을 모드로 이동 ======>")
                import village_mode
                game_framework.change_mode(village_mode)

def update(dt):
    pass

def draw():
    clear_canvas()

    # 배경 이미지 (화면 가득 채우기)
    if opening_image:
        opening_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT)

    # backpack_in 이미지로 설명 텍스트 배경 표시
    if backpack_image:
        backpack_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # 설명 텍스트 표시
    if opening_font:
        # 제목
        opening_font.draw(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT - 140,
                         "모험을 시작하세요!", (255, 255, 0))

        # 설명 텍스트
        description_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 28)

        # 텍스트 라인들
        line1 = "당신과 동생은 마을에 의뢰를 받고 이 마을에 찾아왔습니다."
        line2 = "당신은 힘이 세지만, 몸이 느리고,"
        line3 = "동생은 힘이 약하지만, 날렵합니다."
        line4 = "이 점을 이용하여 몬스터를 잡고 강해져"
        line5 = "보스를 물리쳐 보세요!"

        y_pos = SCREEN_HEIGHT - 200
        line_spacing = 50

        description_font.draw(SCREEN_WIDTH // 2 - 350, y_pos, line1, (255, 255, 255))
        y_pos -= line_spacing
        description_font.draw(SCREEN_WIDTH // 2 - 200, y_pos, line2, (255, 255, 255))
        y_pos -= line_spacing
        description_font.draw(SCREEN_WIDTH // 2 - 200, y_pos, line3, (255, 255, 255))
        y_pos -= line_spacing
        description_font.draw(SCREEN_WIDTH // 2 - 240, y_pos, line4, (100, 200, 255))
        y_pos -= line_spacing
        description_font.draw(SCREEN_WIDTH // 2 - 150, y_pos, line5, (100, 200, 255))

        # 진행 안내
        guide_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 24)
        guide_font.draw(SCREEN_WIDTH // 2 - 150, 140, "Enter 키를 눌러 진행하세요", (200, 255, 200))

    update_canvas()

def pause(): pass
def resume(): pass
