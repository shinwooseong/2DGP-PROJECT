from pico2d import *
import pico2d as _pico2d
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_ESCAPE, SDLK_u, SDLK_RETURN, SDLK_z, SDLK_y, SDLK_n, SDLK_s
import random

import game_framework
import game_world
import server

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
import inventory
from Monster import Green_MS, Red_MS, Trash_Monster
from boss_queen_bee import QueenBee_Boss
from loot import Loot
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H

# 카메라 사용 여부를 기록하는 플래그
came_from_boss_room = False

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역
monsters = []  # 몬스터 리스트
loots = []  # 떨어진 전리품 리스트
current_dungeon = 3  # 현재 던전 레벨
all_monsters_cleared = False  # 모든 몬스터 처치 여부
message_font = None  # 메시지 출력용 폰트
exit_zone = None  # 출구 영역 (문 위치에 따라 설정할 것임)

# 귀환 관련 변수
pendant_image = None  # 펜던트 이미지
show_return_prompt = False  # 귀환 확인 메시지 표시 여부
return_cost = 200  # 귀환 비용
dialogue_font = None  # 대화 폰트

# BGM 변수
bgm = None

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
    global tiled_map, collision_boxes, ui, current_dungeon, all_monsters_cleared, message_font, exit_zone, pendant_image, dialogue_font, show_return_prompt
    global came_from_boss_room, bgm

    # BGM 로드 및 재생 (한 번만)
    if bgm is None:
        bgm = load_music('Sound/dungeon.mp3')
        if hasattr(bgm, 'set_volume'):
            bgm.set_volume(64)
        bgm.repeat_play()



    # 던전1부터 시작
    current_dungeon = 3
    all_monsters_cleared = False
    show_return_prompt = False

    # 메시지 폰트 로드
    message_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 32)
    dialogue_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 28)
    pendant_image = load_image('UI/pendant_Icon.png')

    # 보스방(카메라 사용) 설정
    tiled_map = TiledMap('map/boss_room.json', use_camera=True)
    server.tiled_map = tiled_map
    came_from_boss_room = True  # 현재 보스방에서 플레이 중임을 표시

    # 충돌 영역 설정
    collision_boxes = tiled_map.get_collision_boxes()

    # 플레이어 시작 위치
    server.player.x = 950
    server.player.y = 50

    # UI 생성 및 등록
    ui = UI()
    ui.set_player(server.player)
    ui.is_in_dungeon = True
    game_world.add_object(ui, 2)

    # 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)
    game_world.add_object(server.player, 1)

    global monsters
    monsters = []
    map_center_x = tiled_map.map_width_px // 2
    map_center_y = tiled_map.map_height_px // 2
    boss = QueenBee_Boss(x=map_center_x, y=map_center_y)
    monsters.append(boss)
    game_world.add_object(boss, 1)

    # 보스의 충돌 박스를 collision_boxes에 추가 (플레이어가 통과 불가능)
    boss_bb = boss.get_bb()
    collision_boxes.append(boss_bb)
    print(f"[BOSS] 충돌 박스 추가: {boss_bb}")

    # 보스방에서는 출구 없음
    exit_zone = None

    # 던전1 출구 설정 (상단 문 위치)
    exit_zone = (580, 680, 700, 736)  # (left, bottom, right, top)

    # 디버그 정보
    print(f"======> 던전1 시작 ======>")
    print(f"로드된 충돌 상자 개수: {len(collision_boxes)}")
    print(f"맵 크기: {tiled_map.map_width_px}x{tiled_map.map_height_px} 픽셀")

def finish():
    # 던전 나가면 UI 포함 모든 객체 제거
    game_world.clear()
    global collision_boxes, ui, monsters, bgm
    collision_boxes = []
    monsters = []
    ui = None

    # BGM 정지
    if bgm:
        try:
            bgm.stop()
            print("[BGM] dungeon.mp3 정지")
        finally:
            bgm = None

def handle_events():
    global show_return_prompt, came_from_boss_room
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_u:
                inventory.set_player(server.player)  # 플레이어 전달
                game_framework.push_mode(inventory)
            elif event.key == SDLK_s:
                # S 키: 포션 사용
                server.player.use_potion()
            elif event.key == SDLK_RETURN:
                # ENTER 키를 누르면 shop_mode로 전환
                import shop_mode
                game_framework.change_mode(shop_mode)
            elif event.key == SDLK_z:
                # Z 키: 귀환 펜던트 사용
                show_return_prompt = True
                print("귀환 펜던트 사용 - 확인 메시지 표시")
            elif event.key == SDLK_y:
                # Y 키: 귀환 확인 프롬프트에서 귀환 선택
                if show_return_prompt:
                    if server.player.money >= return_cost:
                        server.player.money -= return_cost
                        print(f"[귀환] {return_cost}골드 지불, 남은 돈: {server.player.money}골드")

                        # 보스방에서 귀환할 때 카메라용 tiled_map 참조 완전히 제거
                        if came_from_boss_room and getattr(server, 'tiled_map', None) is not None:
                            try:
                                server.tiled_map.cam_offset_x = 0
                                server.tiled_map.cam_offset_y = 0
                            except Exception:
                                pass
                            server.tiled_map = None
                            came_from_boss_room = False

                        show_return_prompt = False
                        import village_mode
                        village_mode.came_from_dungeon = True
                        game_framework.change_mode(village_mode)
                        print("귀환 중...")
                    else:
                        print(f"[귀환 실패] 돈이 부족합니다. (필요: {return_cost}골드, 현재: {server.player.money}골드)")
                        show_return_prompt = False
            elif event.key == SDLK_n:
                # N 키: 귀환 확인 프롬프트에서 취소 선택
                if show_return_prompt:
                    show_return_prompt = False
                    print("귀환 취소")
            else:
                server.player.handle_event(event)
        else:
            server.player.handle_event(event)

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
    global tiled_map, collision_boxes, monsters, loots, current_dungeon, all_monsters_cleared, exit_zone

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
    server.player.x = 640
    server.player.y = 50

    # UI 다시 생성
    global ui
    ui = UI()
    ui.set_player(server.player)
    ui.is_in_dungeon = True  # 던전 모드 플래그 설정
    game_world.add_object(ui, 2)

    # 게임 월드에 다시 추가
    game_world.add_object(tiled_map, 0)
    game_world.add_object(server.player, 1)

    # 던전2 몬스터 생성
    spawn_random_monsters(count=2)

    # 던전2도 상단 문 위치에 출구 설정
    exit_zone = (580, 680, 700, 736)  # (left, bottom, right, top)

    print(f"던전2 로드 완료: 몬스터 {len(monsters)}마리")

def change_to_boss_room():
    global tiled_map, collision_boxes, monsters, loots, current_dungeon, all_monsters_cleared, exit_zone


    # 현재 객체들 제거
    game_world.clear()

    # 상태 초기화
    current_dungeon = 3  # 보스방
    all_monsters_cleared = False
    monsters = []
    loots = []

    tiled_map = TiledMap('map/boss_room.json', use_camera=True)
    server.tiled_map = tiled_map

    # 충돌 박스 업데이트
    collision_boxes = tiled_map.get_collision_boxes()

    # 플레이어 위치 설정
    server.player.x = 640
    server.player.y = 200

    # UI 다시 생성
    global ui
    ui = UI()
    ui.set_player(server.player)
    ui.is_in_dungeon = True  # 던전 모드 플래그 설정
    game_world.add_object(ui, 2)

    # 게임 월드에 다시 추가
    game_world.add_object(tiled_map, 0)
    game_world.add_object(server.player, 1)

    # 보스 몬스터 생성 (맵의 정확한 중앙에 배치)
    map_center_x = tiled_map.map_width_px // 2
    map_center_y = tiled_map.map_height_px // 2
    boss = QueenBee_Boss(x=map_center_x, y=map_center_y)
    monsters.append(boss)
    game_world.add_object(boss, 1)

    # 보스의 충돌 박스를 collision_boxes에 추가 (플레이어가 통과 불가능)
    boss_bb = boss.get_bb()
    collision_boxes.append(boss_bb)
    print(f"[BOSS] 충돌 박스 추가: {boss_bb}")

    # 보스방에서는 출구 없음
    exit_zone = None

def update(dt):
    global loots, all_monsters_cleared, came_from_boss_room, tiled_map

    # 게임 오버 체크
    if getattr(server.player, 'is_dead', False):
        print("======> 게임 오버 화면으로 전환 ======>")

        # 카메라 완전 초기화 (보스방에서 게임 오버 발생 시)
        if came_from_boss_room and getattr(server, 'tiled_map', None) is not None:
            server.tiled_map.cam_offset_x = 0
            server.tiled_map.cam_offset_y = 0
            server.tiled_map.use_camera = False

            server.tiled_map = None
            came_from_boss_room = False
            if tiled_map is not None:
                tiled_map.use_camera = False
                tiled_map.cam_offset_x = 0
                tiled_map.cam_offset_y = 0

        # 게임 오버 모드로 전환
        import game_over_mode
        game_framework.change_mode(game_over_mode)
        return
    
    # 보스 처치 확인 (던전3 - 보스방) - 보스가 죽었을 때 바로 감지
    if current_dungeon == 3:
        for monster in monsters[:]:
            if not monster.alive and all_monsters_cleared == False:
                print("======> 보스 처치 완료! 엔딩 모드로 전환 ======>")
                all_monsters_cleared = True
                
                # 보스 처치 보상: 플레이어 스탯 증가
                server.player.max_health += 100  # 최대 체력 100 증가
                server.player.health = server.player.max_health  # 체력 완전 회복
                server.player.base_attack += 40 # 공격력 40 증가
                server.player.attack = server.player.base_attack  # 현재 공격력 업데이트
                server.player.money += 10000
                server.player.hp_potion_count += 5


                # 보스방에서 카메라 참조 완전히 제거
                if came_from_boss_room and getattr(server, 'tiled_map', None) is not None:
                    try:
                        server.tiled_map.cam_offset_x = 0
                        server.tiled_map.cam_offset_y = 0
                        server.tiled_map.use_camera = False
                    except Exception as e:
                        print(f"카메라 초기화 오류: {e}")
                    server.tiled_map = None
                    came_from_boss_room = False

                # 로컬 tiled_map도 카메라 비활성화
                if tiled_map is not None:
                    try:
                        tiled_map.use_camera = False
                        tiled_map.cam_offset_x = 0
                        tiled_map.cam_offset_y = 0
                    except Exception:
                        pass

                import ending_mode
                game_framework.change_mode(ending_mode)
                return

    # 이전 위치 저장
    prev_x = server.player.x
    prev_y = server.player.y

    # 플레이어 업데이트
    server.player.update(dt)

    # 보스방(던전3)에서 맵 경계 제한 (양끝에서 15픽셀 안쪽으로 제한)
    if current_dungeon == 3 and tiled_map is not None:
        margin = 50
        map_width = tiled_map.map_width_px
        map_height = tiled_map.map_height_px

        # 플레이어가 경계를 벗어나지 못하도록 제한
        if server.player.x < margin:
            server.player.x = margin
        elif server.player.x > map_width - margin:
            server.player.x = map_width - margin

        if server.player.y < margin:
            server.player.y = margin
        elif server.player.y > map_height - margin:
            server.player.y = map_height - margin

    # 카메라 업데이트 (보스방일 때만)
    if getattr(server, 'tiled_map', None) is not None and getattr(server.tiled_map, 'use_camera', False):
        server.tiled_map.update_camera(server.player.x, server.player.y)

    # game_world의 모든 객체 업데이트 (BeeSting 포함)
    game_world.update(dt)

    # 몬스터 업데이트
    for monster in monsters[:]:
        # monster.update(dt, frozen=False, player=server.player)  # 이미 game_world.update에서 호출됨

        # 보스의 꿀 수집 확인 (QueenBee_Boss인 경우)
        if hasattr(monster, 'check_honey_collected'):
            monster.check_honey_collected()

        # death 애니메이션이 완전히 끝난 몬스터만 제거하고 전리품 생성
        if not monster.alive and monster.animator.is_animation_finished():
            loot = Loot(monster.x, monster.y, item_type=None, quantity=random.randint(1, 3))
            loots.append(loot)
            game_world.add_object(loot, 1)

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
        if left <= server.player.x <= right and bottom <= server.player.y <= top:
            change_to_dungeon2()
            return

    # 출구 영역 체크 (던전2에서 모든 몬스터 처치 후 보스방으로)
    if current_dungeon == 2 and all_monsters_cleared and exit_zone is not None:
        left, bottom, right, top = exit_zone
        if left <= server.player.x <= right and bottom <= server.player.y <= top:
            change_to_boss_room()
            return

    # 플레이어 공격 충돌 처리
    player_attack_bb = server.player.get_bb()
    if player_attack_bb is not None and hasattr(server.player, 'attack_hit_pending') and server.player.attack_hit_pending:
        left, bottom, right, top = player_attack_bb
        for monster in monsters[:]:
            if not monster.alive:
                continue

            # 보스의 get_bb() 메서드 사용 (정확한 충돌 박스)
            if hasattr(monster, 'get_bb'):
                monster_bb = monster.get_bb()
                monster_left, monster_bottom, monster_right, monster_top = monster_bb
            else:
                # 일반 몬스터는 기존 방식 사용
                monster_size = monster.scale * 25
                monster_left = monster.x - monster_size
                monster_right = monster.x + monster_size
                monster_bottom = monster.y - monster_size
                monster_top = monster.y + monster_size

            if not (left > monster_right or right < monster_left or
                    bottom > monster_top or top < monster_bottom):
                monster.take_damage(server.player.attack)
                print(f"플레이어가 {monster.name}에게 {server.player.attack} 데미지!")

        server.player.attack_hit_pending = False

    # 전리품 업데이트 및 수집 처리
    collected_loots = []
    for loot in loots:
        # should_remove = loot.update(dt)  # 이미 game_world.update에서 호출됨
        should_remove = False

        if loot.check_collection(server.player.x, server.player.y):
            item_info = loot.get_item_info()
            loot_type = item_info['type']
            quantity = item_info['quantity']

            if loot_type in server.player.loot_inventory:
                server.player.loot_inventory[loot_type] += quantity
                print(f"[COLLECT] 수집: {loot_type} x{quantity} (총: {server.player.loot_inventory[loot_type]})")
            else:
                print(f"[WARNING] 알 수 없는 전리품 타입: {loot_type}")

        if should_remove or loot.collected:
            collected_loots.append(loot)

    for loot in collected_loots:
        try:
            game_world.remove_object(loot)
        except Exception:
            pass
        loots.remove(loot)

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리
    if check_collision(server.player.x, server.player.y, server.player):
        server.player.x = prev_x
        server.player.y = prev_y

def draw():
    clear_canvas()

    # 카메라 오프셋 계산(있으면 적용) - 마을 등 카메라를 쓰지 않는 모드에서는 항상 0
    cam = getattr(server, 'tiled_map', None)
    use_cam = bool(cam and getattr(cam, 'use_camera', False))
    if use_cam:
        cam_ox = cam.cam_offset_x
        cam_oy = cam.cam_offset_y
    else:
        cam_ox = 0
        cam_oy = 0

    # 모든 던전에서 동일한 렌더링
    game_world.render()

    # 충돌 박스 표시
    for box in collision_boxes:
        left, bottom, right, top = box
        if use_cam:
            draw_rectangle(left + cam_ox, bottom + cam_oy, right + cam_ox, top + cam_oy)
        else:
            draw_rectangle(left, bottom, right, top)

    # 몬스터 공격 범위 표시
    for monster in monsters:
        if monster.alive and monster.show_attack_range:
            attack_bb = monster.get_attack_bb()
            if attack_bb is not None:
                left, bottom, right, top = attack_bb
                if use_cam:
                    draw_rectangle(left + cam_ox, bottom + cam_oy, right + cam_ox, top + cam_oy)
                else:
                    draw_rectangle(left, bottom, right, top)

    # 던전1 메시지
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

    # 귀환 펜던트 메시지
    if show_return_prompt and dialogue_font is not None:
        screen_center_x = SCREEN_WIDTH // 2
        screen_center_y = SCREEN_HEIGHT // 2
        message = "귀환 펜던트를 사용하시겠습니까?"
        dialogue_font.draw(screen_center_x - 180, screen_center_y + 50, message, (255, 255, 0))
        cost_message = f"비용: {return_cost} 골드"
        dialogue_font.draw(screen_center_x - 180, screen_center_y + 10, cost_message, (255, 255, 255))
        hint_message = "Y: 예 / N: 아니오"
        dialogue_font.draw(screen_center_x - 180, screen_center_y - 30, hint_message, (200, 200, 200))

    # 보스 체력 표시 (보스방에서만)
    if current_dungeon == 3 and len(monsters) > 0:
        boss = monsters[0]  # 보스는 항상 첫 번째 몬스터
        if boss.alive:
            # 카메라 오프셋 적용
            cam = getattr(server, 'tiled_map', None)
            use_cam = bool(cam and getattr(cam, 'use_camera', False))
            cam_ox = cam.cam_offset_x if use_cam else 0
            cam_oy = cam.cam_offset_y if use_cam else 0

            # 보스 머리 위에 체력 표시
            boss_hp_x = boss.x + cam_ox
            boss_hp_y = boss.y + 100 + cam_oy  # 보스 위쪽 100픽셀

            # 체력 바 배경 (검은색)
            draw_rectangle(boss_hp_x - 60, boss_hp_y - 10, boss_hp_x + 60, boss_hp_y + 10)

            # 체력 바 (빨간색)
            hp_ratio = max(0, boss.hp / boss.max_hp)
            draw_rectangle(boss_hp_x - 60, boss_hp_y - 10, boss_hp_x - 60 + (120 * hp_ratio), boss_hp_y + 10)

            # 체력 텍스트
            if message_font:
                hp_text = f"{boss.hp}/{boss.max_hp}"
                message_font.draw(boss_hp_x - 30, boss_hp_y - 25, hp_text, (255, 100, 100))

    update_canvas()

def pause(): pass
def resume(): pass
