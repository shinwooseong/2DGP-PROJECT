from pico2d import *
import pico2d as _pico2d
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u, SDLK_RETURN
import random

import game_framework
import game_world

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
import inventory
from Monster import Green_MS, Red_MS, Trash_Monster

player: Main_character = None
tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역
monsters = []  # 몬스터 리스트

def is_position_valid(x, y, min_distance=100):
    """위치가 충돌 박스와 겹치지 않고, 다른 몬스터와도 충분히 떨어져 있는지 확인"""
    # 충돌 박스와 겹치는지 확인
    for box in collision_boxes:
        left, bottom, right, top = box
        if left - 50 < x < right + 50 and bottom - 50 < y < top + 50:
            return False

    # 다른 몬스터와 너무 가까운지 확인
    for monster in monsters:
        distance = ((x - monster.x) ** 2 + (y - monster.y) ** 2) ** 0.5
        if distance < min_distance:
            return False

    return True

def spawn_random_monsters(count=5):
    """랜덤한 위치에 몬스터들을 배치"""
    global monsters
    monsters = []

    # 몬스터 타입 리스트
    monster_types = [Green_MS, Red_MS, Trash_Monster]

    # 맵 크기 가져오기 (던전 맵 크기 고려)
    map_width = getattr(tiled_map, 'map_width_px', 1280)
    map_height = getattr(tiled_map, 'map_height_px', 736)

    # 안전한 경계 설정 (화면 가장자리 피하기)
    margin = 100
    attempts = 0
    max_attempts = 100

    while len(monsters) < count and attempts < max_attempts:
        # 랜덤 위치 생성
        x = random.randint(margin, map_width - margin)
        y = random.randint(margin, map_height - margin)

        # 플레이어 시작 위치와 너무 가까우면 제외
        if abs(x - 640) < 150 and abs(y - 200) < 150:
            attempts += 1
            continue

        # 위치가 유효한지 확인
        if is_position_valid(x, y):
            # 랜덤하게 몬스터 타입 선택
            monster_class = random.choice(monster_types)
            monster = monster_class(x, y)
            monsters.append(monster)
            game_world.add_object(monster, 1)  # 플레이어와 같은 레이어
            print(f"몬스터 생성: {monster.name} at ({x}, {y})")

        attempts += 1

    print(f"총 {len(monsters)}마리의 몬스터 생성 완료!")

def init():
    global player, tiled_map, collision_boxes, ui

    # 1. 타일드 맵 로드 (던전 맵 사용)
    tiled_map = TiledMap('map/dungeon1.json')

    # 2. 충돌 영역 설정
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정
    player = Main_character()
    player.x = 640  # 던전 시작 X 좌표 (중앙)
    player.y = 200  # 던전 시작 Y 좌표

    # 4. UI 생성 및 등록
    ui = UI()
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 5. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어

    # 6. 몬스터들을 랜덤하게 배치
    spawn_random_monsters(count=8)  # 8마리의 몬스터 생성

    # 디버그 정보 출력
    print(f"======> 던전 모드 시작 ======>")
    print(f"로드된 충돌 상자 개수: {len(collision_boxes)}")
    print(f"맵 크기: {tiled_map.map_width_px}x{tiled_map.map_height_px} 픽셀")
    print(f"스케일: {tiled_map.scale}")
    print(f"오프셋: ({tiled_map.offset_x}, {tiled_map.offset_y})")

    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:5]):
            print(f"  박스 {i}: {box}")

def finish():
    # 던전 나가면 UI 포함 모든 객체 제거
    game_world.clear()
    global collision_boxes, ui, monsters
    collision_boxes = []
    monsters = []
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
                # ENTER 키를 누르면 shop_mode로 전환
                import shop_mode
                game_framework.change_mode(shop_mode)
            else:
                player.handle_event(event)
        else:
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

    # 몬스터 업데이트
    for monster in monsters:
        if monster.alive:
            monster.update(dt, frozen=False, player=player)
        else:
            # 죽은 몬스터는 death 애니메이션이 끝나면 제거
            if hasattr(monster, 'animator') and monster.animator.state == 'death':
                if monster.animator.is_animation_finished():
                    game_world.remove_object(monster)
                    monsters.remove(monster)

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(player.x, player.y):
        player.x = prev_x
        player.y = prev_y

def draw():
    clear_canvas()
    game_world.render()

    # 충돌 박스들을 빨간색 테두리로 화면에 표시 (던전은 빨간색으로)
    for box in collision_boxes:
        left, bottom, right, top = box
        draw_rectangle(left, bottom, right, top)

    update_canvas()

def pause(): pass
def resume(): pass
