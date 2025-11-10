from pico2d import *
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u

import game_framework
import game_world

from main_chracter import Main_character
from tiled_map import TiledMap

player: Main_character = None
tiled_map: TiledMap = None
collision_boxes = []  # 충돌 영역 (레이어 1: Collisions)

def init():
    global player, tiled_map, collision_boxes

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/shop.json')

    # 2. 충돌 영역 설정 (레이어 1)
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정
    player = Main_character()
    player.x = 500  # 시작 X 좌표
    player.y = 150  # 시작 Y 좌표

    # 4. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어

    # 디버그 정보 출력
    print(f"======> 로드된 충돌 상자 개수: {len(collision_boxes)}")
    print(f"맵 크기: {tiled_map.map_width_px}x{tiled_map.map_height_px} 픽셀")
    print(f"스케일: {tiled_map.scale}")
    print(f"오프셋: ({tiled_map.offset_x}, {tiled_map.offset_y})")

    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:5]):
            print(f"  박스 {i}: {box}")

def finish():
    game_world.clear() # 상점 나가서 다른 모드 진입시 모든 객체 지우기!
    global collision_boxes
    collision_boxes = []

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_u:
                from inventory import inventory_mode
                game_framework.push_mode(inventory_mode)
            else:
                # (수정) 모드가 처리하지 않은 키만 플레이어에게 전달
                player.handle_event(event)
        else:
            # (수정) 키다운이 아닌 이벤트(예: KEYUP)도 플레이어에게 전달
            player.handle_event(event)

def check_collision(x, y, player_radius=15):
    """플레이어의 위치가 충돌 박스와 충돌하는지 확인"""
    for box in collision_boxes:
        left, bottom, right, top = box
        # 플레이어의 원형 충돌 감지
        if left - player_radius < x < right + player_radius and \
           bottom - player_radius < y < top + player_radius:
            return True
    return False

def update(dt):
    # 이전 위치 저장
    prev_x = player.x
    prev_y = player.y

    # 플레이어 업데이트
    player.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(player.x, player.y):
        player.x = prev_x
        player.y = prev_y

    # (수정) 테스트용 종료 코드 (play_mode가 없으므로)
    if player.y < 10 or player.x > 1200: # (화면 가장자리로 나가면)
        game_framework.quit()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause(): pass
def resume(): pass
