# main.py
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import main_chracter
import inventory
from Monster import Green_MS, EyeBall, Trash_Monster

# 디버그 출력 켜면 콘솔로 상태 출력
DEBUG_MONSTERS = True
_last_dbg = 0.0
_last_hp = None



def handle_events(player, inv):
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            player.handle_event(event)
            inv.handle_event(event)


running = True
open_canvas(main_chracter.SCREEN_W, main_chracter.SCREEN_H)
Main_player = main_chracter.Main_character()
Main_inventory = inventory.Inventory()

# 몬스터 리스트 생성 (예시 위치)
monsters = [
    Green_MS(300, 200),
    Green_MS(600, 200),
    Trash_Monster(100, 100),
    EyeBall(400, 400),
]


# 디버그: 생성된 몬스터와 애니메이터 시트 로드 상태 출력
if DEBUG_MONSTERS:
    print("Monsters summary:")
    for i, m in enumerate(monsters):
        try:
            sheet = getattr(m.animator, 'sheet_image', None)
            sheet_info = None
            if sheet is not None:
                sheet_info = (getattr(sheet, 'w', None), getattr(sheet, 'h', None))
            print(f"  M{i}: {m.__class__.__name__} pos=({m.x},{m.y}) animator_sheet={sheet_info} frames_map={getattr(m.animator,'frames_map',None)}")
        except Exception as e:
            print(f"  M{i}: {m.__class__.__name__} - debug error: {e}")


while running:

    # 이벤트 처리
    handle_events(Main_player, Main_inventory)

    # 플레이어 업데이트 (dt 계산은 플레이어 내부에서 함)
    if not Main_inventory.is_open:
        Main_player.update()

    # 몬스터 업데이트: 인벤토리 열려있으면 frozen=True로 정지
    for m in monsters:
        m.update(getattr(Main_player, 'dt', 0.01), frozen=Main_inventory.is_open, player=Main_player)

    # 플레이어 공격 히트 처리 (Attack 상태의 히트 프레임에서 메인 루프가 적용)
    if getattr(Main_player, 'attack_hit_pending', False):
        # 플레이어 공격 범위
        pr = getattr(Main_player, 'attack_range', 80)
        for m in monsters:
            dx = m.x - Main_player.x
            dy = m.y - Main_player.y
            if dx*dx + dy*dy <= pr * pr:
                m.take_damage(getattr(Main_player, 'attack', 10))
                if DEBUG_MONSTERS:
                    print(f"Player hit M at ({m.x:.1f},{m.y:.1f}) dmg={Main_player.attack} hp_left={m.hp}")
        Main_player.attack_hit_pending = False


    # 그리기
    clear_canvas()
    # 콘솔 출력용: 플레이어 HP가 변할 때마다 콘솔에 출력
    try:
        hp = int(max(0, getattr(Main_player, 'health', 0)))
        if hp != _last_hp:
            print(f"HP: {hp}")
            _last_hp = hp
    except Exception:
        try:
            print(f"HP: {getattr(Main_player, 'health', 0)}")
        except Exception:
            pass
    # 배경이 있으면 먼저 그리고
    for m in monsters:
        m.draw()
    Main_player.draw()
    Main_inventory.draw()
    update_canvas()

    delay(0.01)

close_canvas()
