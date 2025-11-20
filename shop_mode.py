from pico2d import *
import pico2d as _pico2d # set_color를 사용하기 위해 유지
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u, SDLK_RETURN

import game_framework
import game_world

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
from NPC import NPC
import inventory
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H

player: Main_character = None
tiled_map: TiledMap = None
ui = None
npc_water = None
collision_boxes = []  # 충돌 영역 (레이어 1: Collisions)

# 상점 진입 위치 저장 변수 (마을에서 왔는지 다른 곳에서 왔는지)
came_from_village = True

def init():
    global player, tiled_map, collision_boxes, ui, npc_water

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/shop.json')

    # 2. 충돌 영역 설정 (레이어 1)
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정 (상점 입구 위치: 하단 중앙보다 약간 오른쪽)
    player = Main_character()
    player.x = 630
    player.y = 10

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
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 4. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어
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

def finish():
    # 상점 나가면 UI 포함 모든 객체 제거
    game_world.clear()
    global collision_boxes, ui
    collision_boxes = []
    ui = None

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_u:
                game_framework.push_mode(inventory)
            elif event.key == SDLK_RETURN:
                # ENTER 키를 누르면 dungeon_mode로 전환
                import dungeon_mode
                game_framework.change_mode(dungeon_mode)
            else:
                player.handle_event(event)
        else:
            player.handle_event(event)

def check_collision(x, y, player):
    """플레이어의 위치가 충돌 박스와 충돌하는지 확인 (실제 캐릭터 크기 사용)"""

    # 변신 상태에 따라 다른 충돌 범위 사용
    if player.is_transformed:
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
    # 이전 위치 저장
    prev_x = player.x
    prev_y = player.y

    # 플레이어 업데이트
    player.update(dt)

    # UI 업데이트 (try...except 제거)
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(player.x, player.y, player):
        player.x = prev_x
        player.y = prev_y
    # NPC 업데이트
    if npc_water is not None:
        npc_water.update(dt, player)


    # 플레이어가 y축 하단으로 나가면 village_mode로 전환
    if player.y < 10:
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


    update_canvas()

def pause(): pass
def resume(): pass