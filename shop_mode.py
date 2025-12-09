from pico2d import *
import pico2d as _pico2d # set_color를 사용하기 위해 유지
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u, SDLK_RETURN

import game_framework
import game_world
import server

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
from NPC import NPC
import inventory
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

tiled_map: TiledMap = None
ui = None
npc_water = None
se_check = None  # check.wav 효과음
collision_boxes = []  # 충돌 영역 (레이어 1: Collisions)

# NPC 대화 관련 변수
show_npc_dialogue = False  # NPC 대화 표시 여부
active_npc = None  # 현재 상호작용 중인 NPC
dialogue_box_image = None
dialogue_font = None

# 상점 진입 위치 저장 변수 (마을에서 왔는지 다른 곳에서 왔는지)
came_from_village = True

shop_entrance_sound = None

def init():
    global tiled_map, collision_boxes, ui, npc_water, dialogue_box_image, dialogue_font, se_check, shop_entrance_sound

    # 다이얼로그 이미지와 폰트 로드
    dialogue_box_image = load_image('UI/7 Dialogue Box/1.png')
    dialogue_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 28)

    # 효과음은 server.init_all_sounds()에서 이미 로드됨
    # 따라서 여기서는 별도 로드 불필요

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/shop.json')

    # 2. 충돌 영역 설정 (레이어 1)
    collision_boxes = tiled_map.get_collision_boxes()

    # 3.  초기 위치 설정 (상점 입구 위치: 하단 중앙보다 약간 오른쪽)
    server.player.x = 630
    server.player.y = 10

    # 3.5 NPC 생성
    npc_water = NPC(310, 220, npc_type='water', name='water')
    npc_water.image = load_image('NPC/NPC_water.png')
    # 이미지 크기 가져오기
    img_w = npc_water.image.w
    img_h = npc_water.image.h
    npc_water.width = img_w // 6
    npc_water.height = img_h
    npc_water.composite = True
    npc_water.frame_max = 6
    npc_water.frame = 0
    npc_water.frame_time = 0
    npc_water.draw_scale = 0.9

    # 3.5 UI 생성 및 등록
    ui = UI()
    ui.set_player(server.player)
    game_world.add_object(ui, 2)

    # 4. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(server.player, 1)     # 플레이어 레이어
    game_world.add_object(npc_water, 1)  # NPC 레이어

    # 디버그 정보 출력 (유지)
    print(f"======> 로드된 충돌 상자 개수: {len(collision_boxes)}")
    print(f"맵 크기: {tiled_map.map_width_px}x{tiled_map.map_height_px} 픽셀")
    print(f"스케일: {tiled_map.scale}")
    print(f"오프셋: ({tiled_map.offset_x}, {tiled_map.offset_y})")

    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:5]):
            print(f"  박스 {i}: {box}")


    if shop_entrance_sound is None:
        shop_entrance_sound = load_wav('Sound/shop_entrance.wav')
        if hasattr(shop_entrance_sound, 'set_volume'):
            shop_entrance_sound.set_volume(20)
    shop_entrance_sound.play()


def finish():
    # 상점 나가면 UI 포함 모든 객체 제거
    game_world.clear()
    global collision_boxes, ui, shop_entrance_sound
    collision_boxes = []
    ui = None

    if shop_entrance_sound is None:
        shop_entrance_sound = load_wav('Sound/shop_entrance.wav')
        if hasattr(shop_entrance_sound, 'set_volume'):
            shop_entrance_sound.set_volume(20)
    shop_entrance_sound.play()

def handle_events():
    global show_npc_dialogue, active_npc

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_u:
                # 대화 중이 아닐 때만 인벤토리 열기
                if not show_npc_dialogue:
                    inventory.set_player(server.player)  # 플레이어 전달
                    game_framework.push_mode(inventory)
            elif event.key == SDLK_RETURN:
                # 엔터 키로 NPC와 상호작용 또는 대화 종료
                if show_npc_dialogue:
                    # 대화 중이면 거래 실행 후 대화 종료
                    if active_npc is not None and active_npc.npc_type == 'water':
                        # 물 NPC와 거래 (포션 구매)
                        if active_npc.trade_water(server.player):
                            print(f"[거래 성공] 포션 2개 구매! 현재 포션: {server.player.hp_potion_count}개")
                            # 거래 성공 시 check.wav 재생
                            try:
                                if se_check:
                                    se_check.play()
                            except Exception as e:
                                print(f"[SE] check.wav 재생 실패: {e}")
                        else:
                            print("[거래 실패] 돈이 부족합니다!")
                    print("NPC 대화 종료")
                    show_npc_dialogue = False
                elif active_npc is not None:
                    # NPC가 범위 안에 있으면 대화 시작
                    print(f"NPC와 상호작용: {active_npc.name}")
                    show_npc_dialogue = True
            else:
                # 대화 중이 아닐 때만 플레이어 이동
                if not show_npc_dialogue:
                    server.player.handle_event(event)
        else:
            # 대화 중이 아닐 때만 플레이어 이동
            if not show_npc_dialogue:
                server.player.handle_event(event)

def check_collision(x, y):
    """플레이어의 위치가 충돌 박스와 충돌하는지 확인 (실제 캐릭터 크기 사용)"""

    # 변신 상태에 따라 다른 충돌 범위 사용
    if server.player.is_transformed:
        collision_w = TRANSFORM_COLLISION_W // 2
        collision_h = TRANSFORM_COLLISION_H // 2
    else:
        collision_w = CHARACTER_COLLISION_W // 2
        collision_h = CHARACTER_COLLISION_H // 2

    for box in collision_boxes:
        left, bottom, right, top = box
        # 플레이어의 사각형 충돌 감지 (실제 캐릭터 크기 사용)
        if left - collision_w < x < right + collision_w and \
           bottom - collision_h < y < top + collision_h:
            return True
    return False

def update(dt):
    global show_npc_dialogue, active_npc

    # 대화 중이면 플레이어 업데이트 중단
    if show_npc_dialogue:
        return

    # 이전 위치 저장
    prev_x = server.player.x
    prev_y = server.player.y

    # 플레이어 업데이트
    server.player.update(dt)

    # NPC 업데이트 및 상호작용 체크
    active_npc = None  # 매 프레임마다 리셋

    if npc_water is not None:
        npc_water.update(dt, player=server.player)
        if npc_water.can_interact:
            active_npc = npc_water

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(server.player.x, server.player.y):
        server.player.x = prev_x
        server.player.y = prev_y

    # 플레이어가 y축 하단으로 나가면 village_mode로 전환
    if server.player.y < 10:
        print("======> 상점 나가기 - 마을로 이동 ======>")
        import village_mode
        village_mode.came_from_shop = True  # 상점에서 나왔다는 플래그 설정
        game_framework.change_mode(village_mode)
        return


def draw():
    clear_canvas()
    game_world.render()

    # 충돌 박스들을 하얀색 테두리로 화면에 표시
    for box in collision_boxes:
        left, bottom, right, top = box
        draw_rectangle(left, bottom, right, top)

    # NPC 대화 표시
    if show_npc_dialogue and active_npc is not None and dialogue_box_image and dialogue_font:
        # 다이얼로그 박스 그리기 (화면 중앙)
        dialogue_box_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # NPC 이름 표시
        dialogue_font.draw(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 80,
                           active_npc.name, (0, 0, 255))

        # NPC와의 대화 내용 표시 (실제 NPC 대사 사용)
        dialogue_text = active_npc.get_dialogue(server.player)
        lines = dialogue_text.split('\n')

        # 여러 줄로 표시
        y_offset = 30
        for line in lines:
            dialogue_font.draw(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + y_offset,
                               line, (0, 0, 0))
            y_offset -= 40

        # 거래 안내 또는 대화 종료 안내
        if active_npc.npc_type == 'water' and active_npc.can_trade_water(server.player):
            dialogue_font.draw(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 60,
                               "구매: 엔터", (100, 100, 100))
        else:
            dialogue_font.draw(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 60,
                               "종료: 엔터", (100, 100, 100))

    update_canvas()

def pause(): pass
def resume(): pass
