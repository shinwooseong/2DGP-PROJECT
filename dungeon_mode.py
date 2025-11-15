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
from loot import Loot
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H

player: Main_character = None
tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역
monsters = []  # 몬스터 리스트
loots = []  # 떨어진 전리품 리스트

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

    # 0. 인벤토리 초기화 (이미지 로드)
    #inventory.init()

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

def check_collision(x, y, player):
    # 실제 캐릭터 크기를 지정해서 충돌박스 만들기!
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
    global loots

    # 이전 위치 저장
    prev_x = player.x
    prev_y = player.y

    # 플레이어 업데이트
    player.update(dt)

    # 몬스터 업데이트
    for monster in monsters[:]:  # 복사본으로 순회하여 안전하게 제거
        # 살아있거나 death 애니메이션 중이면 업데이트
        monster.update(dt, frozen=False, player=player)

        # death 애니메이션이 완전히 끝난 몬스터만 제거하고 전리품 생성
        if not monster.alive and monster.animator.is_animation_finished():
            # 전리품 생성
            loot = Loot(monster.x, monster.y, 'coin', random.randint(1, 5))
            loots.append(loot)
            game_world.add_object(loot, 1)  # 플레이어와 같은 레이어

            game_world.remove_object(monster)
            monsters.remove(monster)
            print(f"{monster.name} 제거 완료 - 전리품 생성!")

    # 플레이어 공격 충돌 처리
    player_attack_bb = player.get_bb()
    if player_attack_bb is not None and hasattr(player, 'attack_hit_pending') and player.attack_hit_pending:
        left, bottom, right, top = player_attack_bb
        for monster in monsters[:]:  # 복사본으로 순회
            if not monster.alive:
                continue

            # 몬스터의 충돌 범위 계산
            # 몬스터 크기는 스프라이트 크기에 따라 가정해서 일단 구함 -> 수정할 것
            monster_size = monster.scale * 25  # 반지름
            monster_left = monster.x - monster_size
            monster_right = monster.x + monster_size
            monster_bottom = monster.y - monster_size
            monster_top = monster.y + monster_size

            # 사각형 충돌 감지
            if not (left > monster_right or right < monster_left or
                    bottom > monster_top or top < monster_bottom):
                monster.take_damage(player.attack)
                print(f"플레이어가 {monster.name}에게 {player.attack} 데미지!")

        # 한 번만 데미지 주기
        player.attack_hit_pending = False

    # 전리품 업데이트 및 수집 처리
    collected_loots = []
    for loot in loots:
        # 전리품 업데이트
        should_remove = loot.update(dt)

        # 플레이어가 수집 범위에 있는지 확인
        if loot.check_collection(player.x, player.y):
            item_info = loot.get_item_info()
            # 배낭에 추가
            inventory.add_item(item_info['type'], item_info['quantity'])
            print(f"[COLLECT] 수집: {item_info['type']} x{item_info['quantity']}")

        # 수집 완료되거나 제거 대상이면 표시
        if should_remove or loot.collected:
            collected_loots.append(loot)

    # 완료된 전리품 제거
    for loot in collected_loots:
        try:
            game_world.remove_object(loot)
        except Exception:
            pass
        loots.remove(loot)

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    # 즉, 벽에 닿으면 벽 앞에서만 움직이는 효과
    if check_collision(player.x, player.y, player):
        player.x = prev_x
        player.y = prev_y

def draw():
    clear_canvas()
    game_world.render()

    # 충돌 박스들을 빨간색 테두리로 화면에 표시 (던전은 빨간색으로)
    for box in collision_boxes:
        left, bottom, right, top = box
        draw_rectangle(left, bottom, right, top)

    # 몬스터들의 공격 범위 표시
    for monster in monsters:
        if monster.alive and monster.show_attack_range:
            attack_bb = monster.get_attack_bb()
            if attack_bb is not None:
                left, bottom, right, top = attack_bb
                draw_rectangle(left, bottom, right, top)

    update_canvas()

def pause(): pass
def resume(): pass
