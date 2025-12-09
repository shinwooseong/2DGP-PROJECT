from pico2d import *
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_RETURN

import game_framework
import village_mode
from NPC import NPC

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

# 엔딩 씬 관련 변수
dialogue_box_image = None
dialogue_font = None
npcs = []  # NPC 리스트
show_ending = False

def init():
    global dialogue_box_image, dialogue_font, npcs, show_ending

    # 이미지와 폰트 로드
    dialogue_box_image = load_image('UI/NPC_text.png')
    dialogue_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)

    # 엔딩 시작
    show_ending = True

    # NPC들 생성 (화면 양 옆에 배치)
    npcs = []

    # 왼쪽 NPC들
    npc_left_1 = NPC(150, 300, npc_type='fairy', name='요정')
    npc_left_1.image = load_image('NPC/NPC_fairy.png')
    npc_left_1.width = npc_left_1.image.w // 2
    npc_left_1.height = npc_left_1.image.h
    npc_left_1.composite = True
    npc_left_1.draw_scale = 1.5
    npcs.append(npc_left_1)

    npc_left_2 = NPC(250, 500, npc_type='item', name='박사')
    npc_left_2.image = load_image('NPC/NPC_item.png')
    npc_left_2.width = npc_left_2.image.w // 2
    npc_left_2.height = npc_left_2.image.h
    npc_left_2.composite = False
    npc_left_2.draw_scale = 1.5
    npcs.append(npc_left_2)

    # 오른쪽 NPC들
    npc_right_1 = NPC(SCREEN_WIDTH - 150, 300, npc_type='water', name='물의 정령')
    npc_right_1.image = load_image('NPC/NPC_fairy.png')  # NPC_water.png 대신 NPC_fairy.png 사용
    npc_right_1.width = npc_right_1.image.w // 2
    npc_right_1.height = npc_right_1.image.h
    npc_right_1.composite = True
    npc_right_1.draw_scale = 1.5
    npcs.append(npc_right_1)

    npc_right_2 = NPC(SCREEN_WIDTH - 250, 500, npc_type='fairy', name='요정2')
    npc_right_2.image = load_image('NPC/NPC_fairy.png')
    npc_right_2.width = npc_right_2.image.w // 2
    npc_right_2.height = npc_right_2.image.h
    npc_right_2.composite = True
    npc_right_2.draw_scale = 1.5
    npcs.append(npc_right_2)

def finish():
    global npcs
    npcs = []

def update(dt):
    # NPC 애니메이션 업데이트
    for npc in npcs:
        if npc.image:
            npc.frame_time += dt
            if npc.frame_time > 0.15:
                npc.frame = (npc.frame + 1) % npc.frame_max
                npc.frame_time = 0

def draw():
    clear_canvas()

    # NPC 그리기 (오른쪽부터 역순으로 그리기 - 좌우 균형)
    for i, npc in enumerate(npcs):
        if npc.image and not npc.composite:
            npc.image.clip_draw(
                npc.frame * npc.width, 0,
                npc.width, npc.height,
                npc.x, npc.y,
                npc.width * npc.draw_scale, npc.height * npc.draw_scale
            )
        elif npc.image and npc.composite:
            npc.image.clip_composite_draw(
                npc.frame * npc.width, 0,
                npc.width, npc.height,
                0, 'h',
                npc.x, npc.y,
                npc.width * npc.draw_scale, npc.height * npc.draw_scale
            )

    # 엔딩 메시지 표시 (다이얼로그 박스)
    if show_ending and dialogue_box_image and dialogue_font:
        dialogue_box_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # 메시지 텍스트
        dialogue_font.draw(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 80,
                          "던전의 여왕을 물리쳤습니다!", (255, 215, 0))

        dialogue_font.draw(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2,
                          "당신이 영웅입니다!", (255, 255, 255))

        # 엔터 안내
        dialogue_font.draw(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 80,
                          "ENTER를 눌러 계속하세요.", (200, 200, 200))

    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_RETURN:
                # 엔터 키를 누르면 마을로 돌아가기
                village_mode.came_from_dungeon = False
                game_framework.change_mode(village_mode)

def pause(): pass
def resume(): pass
