from pico2d import *
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDL_KEYUP, SDLK_ESCAPE, SDLK_u, SDLK_RETURN, SDLK_SPACE, SDLK_y, SDLK_n

import game_framework
import game_world
import server

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
import inventory
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H
from NPC import NPC

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역
npc = None
npc_item: NPC = None

# 던전 출구 영역 (타일 좌표 x 37~41, y 5) 우상단 길 있는 곳
exit_zone_dungeon = None
# 상점 출구 영역 - 삭제됨 (이제 NPC를 통해 상점 갈 수 있음)
exit_zone_shop = None

# 다이얼로그 관련 변수
dialogue_box_image = None
npc_dialogue_box_image = None  # NPC 대화용 이미지 추가
dialogue_font = None
show_dungeon_warning = False  # 던전 경고 다이얼로그 표시 여부
player_at_dungeon_exit = False  # 플레이어가 던전 출구 영역에 있는지
player_at_shop_exit = False  # 플레이어가 상점 출구 영역에 있는지
show_npc_dialogue = False  # NPC 대화 표시 여부
active_npc = None  # 현재 상호작용 중인 NPC

# 상점에서 나왔는지 확인하는 플래그
came_from_shop = False

def init():
    global tiled_map, collision_boxes, ui, exit_zone_dungeon, exit_zone_shop, dialogue_box_image, dialogue_font, came_from_shop
    global npc, npc_item, npc_dialogue_box_image

    # 다이얼로그 이미지와 폰트 로드
    dialogue_box_image = load_image('UI/7 Dialogue Box/1.png')  # 던전 입구용
    npc_dialogue_box_image = load_image('UI/NPC_text.png')  # NPC 대화용
    dialogue_font = load_font('UI/use_font/MaruBuri-Bold.ttf', 28)

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/village.json', use_camera=False)

    # 2. 충돌 영역 설정
    collision_boxes = tiled_map.get_collision_boxes()


    # NPC 생성
    # 요정
    npc = NPC(250, 78, npc_type='fairy', name='요정')
    npc.image = load_image('NPC/NPC_fairy.png')
    # 이미지 크기 가져오기
    img_w = npc.image.w
    img_h = npc.image.h
    npc.width = img_w // 2
    npc.height = img_h
    npc.composite = True
    npc.frame_max = 2
    npc.frame = 0
    npc.frame_time = 0
    npc.draw_scale = 1.0

    # 아이템
    npc_item = NPC(1000, 350, npc_type='item', name='박사')
    npc_item.image = load_image('NPC/NPC_item.png')
    # 이미지 크기 가져오기
    img_w = npc_item.image.w
    img_h = npc_item.image.h
    npc_item.width = img_w // 2
    npc_item.height = img_h
    npc_item.composite = False
    npc_item.frame_max = 2
    npc_item.frame = 0
    npc_item.frame_time = 0
    npc_item.draw_scale = 1.0

    # 상점에서 나왔다면 상점 입구 앞에 배치
    if came_from_shop:
        # 상점 입구 앞 위치 (상점 출구 영역 바로 아래)
        tile_size = 10
        scale = tiled_map.scale
        offset_x = tiled_map.offset_x
        offset_y = tiled_map.offset_y
        map_height_px = tiled_map.map_height_px

        # 상점 입구 중앙
        shop_entrance_x = 77.5 * tile_size * scale + offset_x
        shop_entrance_y = (map_height_px - 22 * tile_size) * scale + offset_y

        server.player.x = shop_entrance_x
        server.player.y = shop_entrance_y
        came_from_shop = False  # 플래그 리셋
    else:
        # 기본 시작 위치
        server.player.x = 640  # 시작 X 좌표
        server.player.y = 400  # 시작 Y 좌표

    # 4. UI 생성 및 등록
    ui = UI()
    ui.set_player(server.player)
    game_world.add_object(ui, 2)

    # 5. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    # NPC를 플레이어보다 먼저 추가하여 플레이어가 앞에 보이도록 함
    if npc:
        game_world.add_object(npc, 1)
    if npc_item:  # 추가: npc_item을 월드에 등록
        game_world.add_object(npc_item, 1)
    game_world.add_object(server.player, 1)  # 플레이어 레이어

    # 6. 출구 영역 설정
    # village 타일 크기: 10x10 픽셀
    tile_size = 10
    scale = tiled_map.scale
    offset_x = tiled_map.offset_x
    offset_y = tiled_map.offset_y
    map_height_px = tiled_map.map_height_px

    # 던전 출구
    tile_left = 37 * tile_size
    tile_right = 41 * tile_size
    tile_bottom = 3 * tile_size
    tile_top = 6 * tile_size
    pico2d_bottom = map_height_px - tile_top
    pico2d_top = map_height_px - tile_bottom
    exit_zone_dungeon = (
        tile_left * scale + offset_x,
        pico2d_bottom * scale + offset_y,
        tile_right * scale + offset_x,
        pico2d_top * scale + offset_y
    )

    # 상점 출구
    tile_left = 76 * tile_size
    tile_right = 79 * tile_size
    tile_bottom = 19 * tile_size
    tile_top = 21 * tile_size
    pico2d_bottom = map_height_px - tile_top
    pico2d_top = map_height_px - tile_bottom
    exit_zone_shop = (
        tile_left * scale + offset_x,
        pico2d_bottom * scale + offset_y,
        tile_right * scale + offset_x,
        pico2d_top * scale + offset_y
    )

    # 디버그 정보 출력
    print(f"======> Village 모드 시작 ======>")
    print(f"로드된 충돌 상자 개수: {len(collision_boxes)}")
    print(f"맵 크기: {tiled_map.map_width_px}x{tiled_map.map_height_px} 픽셀")
    print(f"스케일: {tiled_map.scale}")
    print(f"출구 영역 (던전): {exit_zone_dungeon}")
    print(f"출구 영역 (상점): {exit_zone_shop}")

    if collision_boxes:
        print(f"첫 번째 충돌 박스: {collision_boxes[0]}")
        for i, box in enumerate(collision_boxes[:5]):
            print(f"  박스 {i}: {box}")

def finish():
    # Village 나가면 UI 포함 모든 객체 제거
    game_world.clear()
    global collision_boxes, ui
    collision_boxes = []
    ui = None
    global npc
    npc = None
    npc_item = None

def handle_events():
    global show_dungeon_warning, player_at_dungeon_exit, show_npc_dialogue, active_npc

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                # 다이얼로그 표시 중이면 다이얼로그 닫기
                if show_dungeon_warning:
                    show_dungeon_warning = False
                    player_at_dungeon_exit = False  # 출구 영역 상태 리셋

                    # 플레이어 키 입력 상태 초기화 (계속 직진 방지)
                    server.player.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

                    # 플레이어를 출구 영역 밖으로 이동 (아래쪽으로 50픽셀)
                    server.player.y -= 50

                    print("던전 진입 취소 - 플레이어를 입구 밖으로 이동")
                elif show_npc_dialogue:
                    # NPC 대화 중 ESC를 누르면 대화 종료
                    print("NPC 대화 종료")
                    show_npc_dialogue = False
                else:
                    game_framework.quit()
            elif event.key == SDLK_u:
                # 다이얼로그 표시 중이 아닐 때만 인벤토리 열기
                if not show_dungeon_warning and not show_npc_dialogue:
                    inventory.set_player(server.player)  # 플레이어 전달
                    game_framework.push_mode(inventory)
            elif event.key == SDLK_y:
                # Y 키: 요정 NPC와 거래 실행
                if show_npc_dialogue and active_npc is not None and active_npc.npc_type == 'fairy':
                    if active_npc.can_trade_fairy(server.player):
                        # 거래 실행
                        if active_npc.trade_fairy(server.player):
                            print(f"[거래 성공] 최대 체력: {server.player.max_health}, 현재 체력: {server.player.health}")
                            print(f"남은 전리품: loot1={server.player.loot_inventory.get('loot1', 0)}, "
                                  f"loot2={server.player.loot_inventory.get('loot2', 0)}, "
                                  f"loot3={server.player.loot_inventory.get('loot3', 0)}, "
                                  f"loot4={server.player.loot_inventory.get('loot4', 0)}")
                        # 거래 후에도 대화창은 유지 (업데이트된 전리품 개수 확인 가능)
                # Y 키: 아이템 NPC와 거래 실행
                elif show_npc_dialogue and active_npc is not None and active_npc.npc_type == 'item':
                    if active_npc.can_trade_item(server.player):
                        # 거래 실행
                        if active_npc.trade_item(server.player):
                            print(f"[거래 성공] 현재 소지금: {server.player.money}골드")
                        # 거래 후에도 대화창은 유지
            elif event.key == SDLK_n:
                # N 키: 거래 취소 (대화 종료)
                if show_npc_dialogue and active_npc is not None:
                    if (active_npc.npc_type == 'fairy' and active_npc.can_trade_fairy(server.player)) or \
                       (active_npc.npc_type == 'item' and active_npc.can_trade_item(server.player)):
                        print("거래 취소")
                        show_npc_dialogue = False
            elif event.key == SDLK_RETURN:
                # 던전 다이얼로그 표시 중이면 던전 진입
                if show_dungeon_warning:
                    print("던전 진입 확인")
                    show_dungeon_warning = False

                    # 플레이어 키 입력 상태 초기화 (던전 진입 전)
                    server.player.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

                    import dungeon_mode
                    game_framework.change_mode(dungeon_mode)
                # NPC 대화 표시 중이면 대화 종료
                elif show_npc_dialogue:
                    # 거래 가능한 상태가 아니면 대화 종료
                    if active_npc is None:
                        print("NPC 대화 종료")
                        show_npc_dialogue = False
                    elif active_npc.npc_type == 'fairy' and not active_npc.can_trade_fairy(server.player):
                        print("NPC 대화 종료")
                        show_npc_dialogue = False
                    elif active_npc.npc_type == 'item' and not active_npc.can_trade_item(server.player):
                        print("NPC 대화 종료")
                        show_npc_dialogue = False
                    # 거래 가능한 상태면 Y/N을 기다림 (엔터로는 종료 안됨)
                # NPC가 범위 안에 있으면 대화 시작
                elif active_npc is not None:
                    print(f"NPC와 상호작용: {active_npc.name}")
                    show_npc_dialogue = True
            else:
                # 다이얼로그 표시 중이 아닐 때만 플레이어 이동
                if not show_dungeon_warning and not show_npc_dialogue:
                    server.player.handle_event(event)
        elif event.type == SDL_KEYUP:
            # 다이얼로그 표시 중이 아닐 때만 플레이어 이동
            if not show_dungeon_warning and not show_npc_dialogue:
                server.player.handle_event(event)
        else:
            # 다이얼로그 표시 중이 아닐 때만 플레이어 이동
            if not show_dungeon_warning and not show_npc_dialogue:
                server.player.handle_event(event)

def check_collision(x, y, player):
    # 변신 상태에 따라 다른 충돌 범위 사용
    if player.is_transformed:
        collision_w = TRANSFORM_COLLISION_W // 2
        collision_h = TRANSFORM_COLLISION_H // 2
    else:
        collision_w = CHARACTER_COLLISION_W // 2
        collision_h = CHARACTER_COLLISION_H // 2

    for box in collision_boxes:
        left, bottom, right, top = box
        # 플레이어의 사각형 충돌 감지
        if left - collision_w < x < right + collision_w and \
           bottom - collision_h < y < top + collision_h:
            return True
    return False

def check_exit_zone(player_x, player_y, exit_zone):
    """플레이어가 출구 영역에 들어갔는지 확인"""
    if exit_zone is None:
        return False

    left, bottom, right, top = exit_zone
    return left <= player_x <= right and bottom <= player_y <= top

def update(dt):
    global show_dungeon_warning, player_at_dungeon_exit, player_at_shop_exit, active_npc, show_npc_dialogue

    # 다이얼로그 표시 중이면 플레이어 업데이트 중단
    if show_dungeon_warning or show_npc_dialogue:
        return

    # 이전 위치 저장
    prev_x = server.player.x
    prev_y = server.player.y

    # 플레이어 업데이트
    server.player.update(dt)

    # NPC 업데이트 및 상호작용 체크
    active_npc = None  # 매 프레임마다 리셋

    if npc is not None:
        npc.update(dt, player=server.player)
        if npc.can_interact:
            active_npc = npc

    if npc_item is not None:
        npc_item.update(dt, player=server.player)
        if npc_item.can_interact and active_npc is None:  # 하나의 NPC만 활성화
            active_npc = npc_item

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(server.player.x, server.player.y, server.player):
        server.player.x = prev_x
        server.player.y = prev_y

    # 맵 경계 제한
    map_width = tiled_map.map_width_px
    map_height = tiled_map.map_height_px

    # 플레이어 충돌 박스 크기 고려
    if server.player.is_transformed:
        collision_w = TRANSFORM_COLLISION_W // 2
        collision_h = TRANSFORM_COLLISION_H // 2
    else:
        collision_w = CHARACTER_COLLISION_W // 2
        collision_h = CHARACTER_COLLISION_H // 2

    # 플레이어가 맵 밖으로 나가지 않도록 제한
    if server.player.x < collision_w:
        server.player.x = collision_w
    elif server.player.x > map_width - collision_w:
        server.player.x = map_width - collision_w

    if server.player.y < collision_h:
        server.player.y = collision_h
    elif server.player.y > map_height - collision_h:
        server.player.y = map_height - collision_h

    # 던전 출구 영역 체크
    at_dungeon_exit = check_exit_zone(server.player.x, server.player.y, exit_zone_dungeon)

    # 플레이어가 던전 출구 영역에 처음 진입했을 때만 다이얼로그 표시
    if at_dungeon_exit and not player_at_dungeon_exit:
        print("======> 던전 입구 도착! 경고 다이얼로그 표시 ======>")
        show_dungeon_warning = True
        player_at_dungeon_exit = True
    elif not at_dungeon_exit:
        # 플레이어가 던전 출구 영역을 벗어나면 상태 리셋
        player_at_dungeon_exit = False

    # 상점 출구 영역 체크 (경고 없이 바로 진입)
    at_shop_exit = check_exit_zone(server.player.x, server.player.y, exit_zone_shop)

    if at_shop_exit and not player_at_shop_exit:
        print("======> 상점 입구 진입! ======>")
        player_at_shop_exit = True
        import shop_mode
        game_framework.change_mode(shop_mode)
        return
    elif not at_shop_exit:
        player_at_shop_exit = False

def draw():
    clear_canvas()
    game_world.render()

    # 충돌 박스들을 화면에 표시 (디버그용)
    for box in collision_boxes:
        left, bottom, right, top = box
        draw_rectangle(left, bottom, right, top)

    # 던전 출구 영역 표시 (디버그용 - 노란색)
    if exit_zone_dungeon:
        left, bottom, right, top = exit_zone_dungeon
        for i in range(3):
            draw_rectangle(left - i, bottom - i, right + i, top + i)

    # 상점 출구 영역 표시 (디버그용 - 초록색처럼)
    if exit_zone_shop:
        left, bottom, right, top = exit_zone_shop
        for i in range(5):  # 더 두꺼운 선으로 구분
            draw_rectangle(left - i, bottom - i, right + i, top + i)

    # 던전 경고 다이얼로그 표시
    if show_dungeon_warning and dialogue_box_image and dialogue_font:
        # 다이얼로그 박스 그리기 (화면 중앙)
        dialogue_box_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # 텍스트 그리기 (중앙 정렬)
        # 첫 번째 줄: 경고 메시지
        dialogue_font.draw(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 30,
                           "던전입니다.", (255, 0, 0))

        # 두 번째 줄: 확인 질문
        dialogue_font.draw(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 10,
                           "정말 들어가겠습니까?", (0, 0, 0))

        # 세 번째 줄: 선택 안내
        dialogue_font.draw(SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 50,
                           "네(Enter)    아니요(ESC)", (15, 15, 15))

    # NPC 대화 표시
    if show_npc_dialogue and active_npc is not None and npc_dialogue_box_image and dialogue_font:
        # 다이얼로그 박스 그리기 (화면 중앙) - NPC 전용 이미지 사용
        npc_dialogue_box_image.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # 시작 Y 위치를 위쪽으로 조정
        start_y = SCREEN_HEIGHT // 2 + 180

        # NPC 이름 표시
        dialogue_font.draw(SCREEN_WIDTH // 2 - 50, start_y,
                           active_npc.name, (0, 0, 255))

        # NPC별 대화 내용 표시
        dialogue_text = active_npc.get_dialogue(server.player)

        # 줄바꿈 처리 (\n으로 구분)
        lines = dialogue_text.split('\n')
        y_offset = 0
        for line in lines:
            dialogue_font.draw(SCREEN_WIDTH // 2 - 150, start_y - 40 - y_offset,  # 이름 아래 40픽셀
                               line, (0, 0, 0))
            y_offset += 35  # 줄 간격

        # 요정 NPC인 경우 전리품 개수 표시
        if active_npc.npc_type == 'fairy':
            # 전리품 개수 표시 (대화 내용 아래)
            loot_y_position = start_y - 40 - y_offset - 20  # 대화 내용과 간격

            dialogue_font.draw(SCREEN_WIDTH // 2 - 150, loot_y_position,
                               "보유 전리품:", (50, 50, 50))

            # 각 전리품 개수 표시 (세로로 나열)
            loot_names = ['loot1', 'loot2', 'loot3', 'loot4']
            loot_display_names = ['전리품1', '전리품2', '전리품3', '전리품4']

            for i, (loot_key, display_name) in enumerate(zip(loot_names, loot_display_names)):
                loot_count = server.player.loot_inventory.get(loot_key, 0)
                # 3개 이상이면 빨간색, 아니면 검은색
                color = (255, 0, 0) if loot_count >= 3 else (0, 0, 0)

                loot_text = f"{display_name}: {loot_count}/3"
                # 세로로 배치 (각 줄마다 35픽셀 간격)
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, loot_y_position - 35 - (i * 35),
                                   loot_text, color)

            # 거래 가능 여부에 따라 안내 메시지 변경 (전리품 4개 아래)
            button_y_position = loot_y_position - 35 - (4 * 35) - 10  # 전리품 목록 아래
            if active_npc.can_trade_fairy(server.player):
                # 거래 가능하면 Y/N 선택 표시
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, button_y_position,
                                   "거래하시겠습니까?", (50, 50, 50))
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, button_y_position - 35,
                                   "거래: Y     거래 취소: N", (125, 215, 12))
            else:
                dialogue_font.draw(SCREEN_WIDTH // 2 - 100, button_y_position,
                                   "종료: Enter 또는 ESC", (15, 15, 15))
        # 아이템 NPC인 경우 전리품 개수와 가격 표시
        elif active_npc.npc_type == 'item':
            from loot import Loot

            # 전리품 개수 표시 (대화 내용 아래)
            loot_y_position = start_y - 40 - y_offset - 20

            dialogue_font.draw(SCREEN_WIDTH // 2 - 150, loot_y_position,
                               "보유 전리품:", (50, 50, 50))

            # 각 전리품 개수와 가격 표시 (세로로 나열)
            loot_names = ['loot1', 'loot2', 'loot3', 'loot4']
            loot_display_names = ['전리품1', '전리품2', '전리품3', '전리품4']

            total_value = 0
            for i, (loot_key, display_name) in enumerate(zip(loot_names, loot_display_names)):
                loot_count = server.player.loot_inventory.get(loot_key, 0)
                price = Loot.LOOT_PRICES.get(loot_key, 0)
                item_total = loot_count * price
                total_value += item_total

                # 1개 이상이면 초록색, 없으면 검은색
                color = (0, 150, 0) if loot_count > 0 else (100, 100, 100)

                loot_text = f"{display_name}: {loot_count}개 (개당 {price}G)"
                # 세로로 배치 (각 줄마다 35픽셀 간격)
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, loot_y_position - 35 - (i * 35),
                                   loot_text, color)

            # 총 판매 금액 표시
            total_y_position = loot_y_position - 35 - (4 * 35) - 10
            dialogue_font.draw(SCREEN_WIDTH // 2 - 150, total_y_position,
                               f"총 판매 금액: {total_value}G", (255, 100, 0))

            # 거래 가능 여부에 따라 안내 메시지 변경
            button_y_position = total_y_position - 40
            if active_npc.can_trade_item(server.player):
                # 거래 가능하면 Y/N 선택 표시
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, button_y_position,
                                   "전리품을 판매하시겠습니까?", (50, 50, 50))
                dialogue_font.draw(SCREEN_WIDTH // 2 - 150, button_y_position - 35,
                                   "판매: Y     취소: N", (125, 215, 12))
            else:
                dialogue_font.draw(SCREEN_WIDTH // 2 - 100, button_y_position,
                                   "종료: Enter 또는 ESC", (15, 15, 15))
        else:
            dialogue_font.draw(SCREEN_WIDTH // 2 - 100, start_y - 40 - y_offset - 20,
                               "종료: Enter 또는 ESC", (15, 15, 15))

    update_canvas()

def pause(): pass
def resume(): pass
