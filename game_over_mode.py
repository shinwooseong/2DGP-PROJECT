from pico2d import *
import game_framework
import server
import village_mode

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

# 폰트
title_font = None
message_font = None

# 반투명 오버레이를 위한 변수
overlay_alpha = 0.0
fade_speed = 1.5  # 페이드 인 속도

def init():
    global title_font, message_font, overlay_alpha

    # 폰트 로드
    title_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 60)
    message_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)

    # 오버레이 알파값 초기화
    overlay_alpha = 0.0

    print("======> 게임 오버! ======>")

def finish():
    global title_font, message_font
    # 폰트 해제는 pico2d가 자동으로 처리

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_RETURN:
                # 다시 시작: 플레이어 상태 초기화 후 마을로 이동
                if server.player is not None:
                    server.player.is_dead = False
                    server.player.health = server.player.max_health
                    server.player.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

                # 던전/상점 플래그 초기화 (완전 초기 시작)
                village_mode.came_from_shop = False
                village_mode.came_from_dungeon = False

                game_framework.change_mode(village_mode)

def update(dt):
    global overlay_alpha

    # 오버레이 페이드 인 효과
    if overlay_alpha < 0.7:
        overlay_alpha += fade_speed * dt
        if overlay_alpha > 0.7:
            overlay_alpha = 0.7

def draw():
    clear_canvas()

    # 검은색 반투명 배경
    if overlay_alpha > 0:
        # pico2d에서 사각형을 채우려면 draw_rectangle 대신 Canvas의 draw_rectangle 사용
        # 또는 검은색 이미지 사용
        # 여기서는 간단하게 작은 사각형들로 화면을 채움
        from pico2d import draw_rectangle

        # 검은색으로 화면 전체를 덮기
        # draw_rectangle은 테두리만 그리므로, 여러 겹으로 그려서 채우기
        for i in range(0, SCREEN_HEIGHT, 2):
            draw_rectangle(0, i, SCREEN_WIDTH, i + 2)

    # "당신은 죽었습니다" 메시지
    if title_font:
        title_font.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                       "당신은 죽었습니다", (255, 50, 50))

    # "전리품과 돈을 잃었습니다" 메시지
    if message_font:
        message_font.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20,
                         "전리품과 돈을 잃었습니다", (255, 200, 200))

    # "ENTER를 눌러 마을에서 부활하세요" 메시지
    if message_font:
        message_font.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60,
                         "ENTER를 눌러 마을에서 부활하세요", (255, 255, 255))

    update_canvas()

def pause():
    pass

def resume():
    pass
