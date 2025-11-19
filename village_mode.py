from pico2d import *
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDL_KEYUP, SDLK_ESCAPE, SDLK_u, SDLK_RETURN

import game_framework
import game_world

from main_chracter import Main_character
from tiled_map import TiledMap
from UI import UI
import inventory
from character_constants import CHARACTER_COLLISION_W, CHARACTER_COLLISION_H, TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H

# 화면 크기
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 736

player: Main_character = None
tiled_map: TiledMap = None
ui = None
collision_boxes = []  # 충돌 영역

# 던전 출구 영역 (타일 좌표 x 37~41, y 5) 우상단 길 있는 곳
exit_zone = None

def init():
    global player, tiled_map, collision_boxes, ui, exit_zone

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/village.json', use_camera=False)

    # 2. 충돌 영역 설정
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정
    player = Main_character()
    player.x = 640  # 시작 X 좌표
    player.y = 400  # 시작 Y 좌표

    # 4. UI 생성 및 등록
    ui = UI()
    ui.set_player(player)
    game_world.add_object(ui, 2)

    # 5. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어

    # 6. 출구 영역 설정 (타일 좌표 x 37~41, y 3를 픽셀 좌표로 변환)
    # village 타일 크기: 10x10 픽셀
    # 타일 좌표를 픽셀 좌표로 변환 후 스케일과 오프셋 적용
    tile_size = 10
    tile_left = 37 * tile_size
    tile_right = 41 * tile_size
    tile_bottom = 3 * tile_size
    tile_top = 6 * tile_size  # y 5 타일의 상단

    # 스케일과 오프셋 적용
    scale = tiled_map.scale
    offset_x = tiled_map.offset_x
    offset_y = tiled_map.offset_y

    # Tiled 좌표계를 Pico2D 좌표계로 변환
    map_height_px = tiled_map.map_height_px
    pico2d_bottom = map_height_px - tile_top
    pico2d_top = map_height_px - tile_bottom

    exit_zone = (
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
    print(f"출구 영역 (던전): {exit_zone}")

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
        elif event.type == SDL_KEYUP:
            player.handle_event(event)
        else:
            player.handle_event(event)

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

def check_exit_zone(player_x, player_y):
    if exit_zone is None:
        return False

    left, bottom, right, top = exit_zone
    return left <= player_x <= right and bottom <= player_y <= top

def update(dt):
    # 이전 위치 저장
    prev_x = player.x
    prev_y = player.y

    # 플레이어 업데이트
    player.update(dt)

    # UI 업데이트
    if ui is not None:
        ui.update(dt)

    # 충돌 처리: 플레이어가 충돌 박스에 닿으면 이전 위치로 복원
    if check_collision(player.x, player.y, player):
        player.x = prev_x
        player.y = prev_y

    # 맵 경계 제한
    map_width = tiled_map.map_width_px
    map_height = tiled_map.map_height_px

    # 플레이어 충돌 박스 크기 고려
    if player.is_transformed:
        collision_w = TRANSFORM_COLLISION_W // 2
        collision_h = TRANSFORM_COLLISION_H // 2
    else:
        collision_w = CHARACTER_COLLISION_W // 2
        collision_h = CHARACTER_COLLISION_H // 2

    # 플레이어가 맵 밖으로 나가지 않도록 제한
    if player.x < collision_w:
        player.x = collision_w
    elif player.x > map_width - collision_w:
        player.x = map_width - collision_w

    if player.y < collision_h:
        player.y = collision_h
    elif player.y > map_height - collision_h:
        player.y = map_height - collision_h

    # 출구 영역 체크: 던전으로 이동
    if check_exit_zone(player.x, player.y):
        print("======> 출구 진입: 던전으로 이동 ======>")
        import dungeon_mode
        game_framework.change_mode(dungeon_mode)
        return

def draw():
    clear_canvas()
    game_world.render()

    # 충돌 박스들을 화면에 표시 (디버그용)
    for box in collision_boxes:
        left, bottom, right, top = box
        draw_rectangle(left, bottom, right, top)

    # 출구 영역 표시 (디버그용)
    if exit_zone:
        left, bottom, right, top = exit_zone
        for i in range(3):
            draw_rectangle(left - i, bottom - i, right + i, top + i)

    update_canvas()

def pause(): pass
def resume(): pass
