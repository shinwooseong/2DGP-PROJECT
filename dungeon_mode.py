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

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

player: Main_character = None
tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역
monsters = []  # 몬스터 리스트
loots = []  # 떨어진 전리품 리스트
current_dungeon = 1  # 현재 던전 레벨
all_monsters_cleared = False  # 모든 몬스터 처치 여부
message_font = None  # 메시지 출력용 폰트
exit_zone = None  # 출구 영역 (문 위치에 따라 설정할 것임)

# 카메라 변수
camera_x = 0
camera_y = 0

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
    global player, tiled_map, collision_boxes, ui, current_dungeon, all_monsters_cleared, message_font, exit_zone

    # 0. 인벤토리 초기화 (이미지 로드)
    #inventory.init()

    # 던전 맵 1이 던전 시작맵임.
    current_dungeon = 1
    all_monsters_cleared = False

    # 메시지 폰트 로드
    message_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)


    # 1. 타일드 맵 로드 (던전 맵 사용 - 카메라 미사용)
    if current_dungeon == 1:
        tiled_map = TiledMap('map/dungeon1.json', use_camera=False)
    else:
        # 맵 추가 시 elif로 설정할 것임
        tiled_map = TiledMap('map/dungeon2.json', use_camera=False)

    # 2. 충돌 영역 설정
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정(맵 다 설정하면 위치 재설정 할 것임)
    player = Main_character()
    if current_dungeon == 1:
        player.x = 640  # 던전1 시작 X 좌표 (중앙)
        player.y = 200  # 던전1 시작 Y 좌표
    else:
        player.x = 640  # 던전2 시작 X 좌표
        player.y = 200  # 던전2 시작 Y 좌표

    # 4. UI 생성 및 등록
    ui = UI()
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 5. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어

    # 6. 몬스터들을 랜덤하게 배치 (던전 지날수록 몬스터 수 증가하기)
    if current_dungeon == 1:
        spawn_random_monsters(count=1)  # 8마리의 몬스터 생성
    else:
        spawn_random_monsters(count=2)  # 던전2는 더 많이

    # 7. 출구 영역 설정 (던전1 상단 문 위치)
    # 던전1 맵의 상단 중앙 문 위치
    if current_dungeon == 1:
        exit_zone = (580, 680, 700, 736)  # (left, bottom, right, top)
    else:
        # 던전2도 상단 문 위치에 출구 설정
        exit_zone = (580, 680, 700, 736)  # (left, bottom, right, top)

    # 디버그 정보 출력
    print(f"======> 던전 {current_dungeon} 모드 시작 ======>")
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

def change_to_dungeon2():
    global player, tiled_map, collision_boxes, monsters, loots, current_dungeon, all_monsters_cleared, exit_zone

    print("======> 던전2로 이동 ======>")

    # 현재 객체들 제거
    game_world.clear()

    # 상태 초기화
    current_dungeon = 2
    all_monsters_cleared = False
    monsters = []
    loots = []

    # 던전2 맵 로드 (카메라 미사용 - 화면에 맞게 스케일링)
    tiled_map = TiledMap('map/dungeon2.json', use_camera=False)

    # 충돌 박스 업데이트 (중요!)
    collision_boxes = tiled_map.get_collision_boxes()

    # 디버그 출력 추가
    print(f"던전2 충돌 박스 로드 완료: {len(collision_boxes)}개")
    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:3]):
            print(f"  박스 {i}: {box}")
    else:
        print(" 경고: 던전2에 충돌 박스가 없습니다!")

    # 플레이어 위치 설정 (던전2 시작 위치)
    player.x = 640
    player.y = 200

    # UI 다시 생성
    global ui
    ui = UI()
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 게임 월드에 다시 추가
    game_world.add_object(tiled_map, 0)
    game_world.add_object(player, 1)

    # 던전2 몬스터 생성
    spawn_random_monsters(count=1)

    # 던전2도 상단 문 위치에 출구 설정
    exit_zone = (580, 680, 700, 736)  # (left, bottom, right, top)

    print(f"던전2 로드 완료: 몬스터 {len(monsters)}마리")

def change_to_boss_room():
    global player, tiled_map, collision_boxes, monsters, loots, current_dungeon, all_monsters_cleared, exit_zone

    print("======> 보스방으로 이동 ======>")

    # 현재 객체들 제거
    game_world.clear()

    # 상태 초기화
    current_dungeon = 3  # 보스방을 던전 3으로 표시
    all_monsters_cleared = False
    monsters = []
    loots = []

    # 보스방 맵 로드 (카메라 사용) - 파일명 확인
    tiled_map = TiledMap('map/boss_room.json', use_camera=True)


    # 충돌 박스 업데이트
    collision_boxes = tiled_map.get_collision_boxes()

    # 디버그 출력
    print(f"보스방 충돌 박스 로드 완료: {len(collision_boxes)}개")
    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:3]):
            print(f"  박스 {i}: {box}")

    # 플레이어 위치 설정 (보스방 시작 위치)
    player.x = 640
    player.y = 200

    # UI 다시 생성
    global ui
    ui = UI()
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 게임 월드에 다시 추가
    game_world.add_object(tiled_map, 0)
    game_world.add_object(player, 1)

    # 보스 몬스터 생성 (보스 1마리만)
    # 나중에 보스 클래스를 만들면 여기서 생성하기
    spawn_random_monsters(count=1)  # 임시로 일반 몬스터 1마리

    # 보스방에서는 출구 없음 (아직)
    exit_zone = None

    print(f"보스방 로드 완료")

def update(dt):
    global loots, all_monsters_cleared, camera_x, camera_y

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

    # 모든 몬스터 처치 확인 (던전1에서만)
    if current_dungeon == 1 and not all_monsters_cleared and len(monsters) == 0:
        all_monsters_cleared = True
        print("======> 모든 몬스터 처치! 출구로 이동하세요! ======>")

    # 모든 몬스터 처치 확인 (던전2에서만)
    if current_dungeon == 2 and not all_monsters_cleared and len(monsters) == 0:
        all_monsters_cleared = True
        print("======> 던전2의 모든 몬스터 처치! 보스방으로 이동하세요! ======>")

    # 출구 영역 체크 (던전1에서 모든 몬스터 처치 후)
    if current_dungeon == 1 and all_monsters_cleared and exit_zone is not None:
        left, bottom, right, top = exit_zone
        if left <= player.x <= right and bottom <= player.y <= top:
            change_to_dungeon2()
            return  # update 중단

    # 출구 영역 체크 (던전2에서 모든 몬스터 처치 후 보스방으로)
    if current_dungeon == 2 and all_monsters_cleared and exit_zone is not None:
        left, bottom, right, top = exit_zone
        if left <= player.x <= right and bottom <= player.y <= top:
            change_to_boss_room()
            return  # update 중단

    # 플레이어 공격 충돌 처리
    player_attack_bb = player.get_bb()
    if player_attack_bb is not None and hasattr(player, 'attack_hit_pending') and player.attack_hit_pending:
        left, bottom, right, top = player_attack_bb
        for monster in monsters[:]:  # 복사본으로 순회
            if not monster.alive:
                continue

            # 몬스터의 충돌 범위 계산
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
    if check_collision(player.x, player.y, player):
        player.x = prev_x
        player.y = prev_y

    # 보스방에서 플레이어가 맵 경계를 넘지 않도록 제한
    if current_dungeon == 3:
        map_width = tiled_map.map_width_px  # 1280
        map_height = tiled_map.map_height_px  # 1440

        # 플레이어 충돌 박스 크기 고려
        if player.is_transformed:
            collision_w = TRANSFORM_COLLISION_W // 2
            collision_h = TRANSFORM_COLLISION_H // 2
        else:
            collision_w = CHARACTER_COLLISION_W // 2
            collision_h = CHARACTER_COLLISION_H // 2

        # 플레이어가 맵 밖으로 나가지 않도록 제한 (맵 전체 범위)
        if player.x < collision_w:
            player.x = collision_w
        elif player.x > map_width - collision_w:
            player.x = map_width - collision_w

        # Y축은 맵의 전체 높이
        if player.y < collision_h:
            player.y = collision_h
        elif player.y > map_height - collision_h :
            player.y = map_height - collision_h

    # 카메라 업데이트: 보스방(던전3)에서만 작동
    if current_dungeon == 3:
        map_width = tiled_map.map_width_px  # 1280
        map_height = tiled_map.map_height_px  # 1440

        half_screen_w = SCREEN_WIDTH // 2  # 640
        half_screen_h = SCREEN_HEIGHT // 2  # 368

        # 카메라를 플레이어 중심으로 설정
        camera_x = player.x
        camera_y = player.y

        # 카메라 X 제한 (맵 너비 = 화면 너비이므로 중앙 고정)
        camera_x = map_width // 2  # 640으로 고정

        # 카메라 Y 제한 (카메라는 368~1072 범위로 제한되지만, 플레이어는 0~1440 전체 이동 가능)
        if camera_y < half_screen_h:
            camera_y = half_screen_h  # 368
        elif camera_y > map_height - half_screen_h:
            camera_y = map_height - half_screen_h  # 1072

def draw():
    clear_canvas()

    # 보스방(던전3)에서만 카메라 사용
    if current_dungeon == 3:
        # 카메라 오프셋 계산
        cam_offset_x = SCREEN_WIDTH // 2 - camera_x
        cam_offset_y = SCREEN_HEIGHT // 2 - camera_y

        # 1. 배경 맵을 카메라 기준으로 그리기
        if tiled_map:
            tiled_map.draw_with_camera(camera_x, camera_y)

        # 2. 게임 월드의 객체들을 분류하여 처리
        game_objects = []  # 플레이어, 몬스터, 전리품 등

        for obj in game_world.all_objects():
            if obj == tiled_map or obj == ui:
                continue  # 맵과 UI는 별도 처리
            game_objects.append(obj)

        # 3. 게임 객체들을 카메라 적용하여 그리기
        for obj in game_objects:
            if hasattr(obj, 'draw') and hasattr(obj, 'x') and hasattr(obj, 'y'):
                # 원본 좌표 저장
                original_x = obj.x
                original_y = obj.y

                # 화면 좌표로 변환하여 임시 설정
                obj.x = original_x + cam_offset_x
                obj.y = original_y + cam_offset_y

                # 그리기
                obj.draw()

                # 즉시 원래 좌표로 복원
                obj.x = original_x
                obj.y = original_y

        # 4. UI는 화면 고정 위치에 그리기 (카메라 영향 없음)
        if ui:
            ui.draw()

        # 5. 충돌 박스들을 카메라 기준으로 화면에 표시 (디버그용)
        for box in collision_boxes:
            left, bottom, right, top = box
            screen_left = left + cam_offset_x
            screen_bottom = bottom + cam_offset_y
            screen_right = right + cam_offset_x
            screen_top = top + cam_offset_y
            draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)

        # 6. 몬스터들의 공격 범위 표시 (카메라 기준)
        for monster in monsters:
            if monster.alive and monster.show_attack_range:
                attack_bb = monster.get_attack_bb()
                if attack_bb is not None:
                    left, bottom, right, top = attack_bb
                    screen_left = left + cam_offset_x
                    screen_bottom = bottom + cam_offset_y
                    screen_right = right + cam_offset_x
                    screen_top = top + cam_offset_y
                    draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)
    else:
        # 던전1, 던전2는 카메라 없이 기본 렌더링
        game_world.render()

        # 충돌 박스들을 화면에 표시
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

    # 모든 몬스터 처치 시 메시지 표시 (화면 고정 위치)
    if current_dungeon == 1 and all_monsters_cleared and message_font is not None:
        screen_center_x = SCREEN_WIDTH // 2
        screen_center_y = SCREEN_HEIGHT // 2
        message = "다음 맵으로 넘어갈 수 있습니다"
        message_font.draw(screen_center_x - 180, screen_center_y + 50, message, (255, 255, 0))
        hint = "(상단 문으로 이동하세요)"
        message_font.draw(screen_center_x - 150, screen_center_y + 10, hint, (200, 200, 200))

    # 던전2 메시지
    if current_dungeon == 2 and all_monsters_cleared and message_font is not None:
        screen_center_x = SCREEN_WIDTH // 2
        screen_center_y = SCREEN_HEIGHT // 2
        message = "보스방으로 넘어갈 수 있습니다"
        message_font.draw(screen_center_x - 180, screen_center_y + 50, message, (255, 255, 0))
        hint = "(상단 문으로 이동하세요)"
        message_font.draw(screen_center_x - 150, screen_center_y + 10, hint, (200, 200, 200))

    update_canvas()

def pause(): pass
def resume(): pass
