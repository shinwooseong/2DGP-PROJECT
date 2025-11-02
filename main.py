# main.py
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import main_chracter
import inventory
from Monster import Green_MS
import time

# 디버그 출력 켜면 콘솔로 상태 출력
DEBUG_MONSTERS = True
_last_dbg = 0.0



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
]





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

    # 디버그 상태 출력 (0.5초 간격)
    if DEBUG_MONSTERS:
        now = time.time()
        if now - _last_dbg >= 0.5:
            _last_dbg = now
            print(f"Player @ ({Main_player.x:.1f},{Main_player.y:.1f})")
            for i, m in enumerate(monsters):
                dx = Main_player.x - m.x
                dy = Main_player.y - m.y
                dist = (dx*dx+dy*dy)**0.5
                print(f"  M{i}: {m.__class__.__name__} state={getattr(m,'state',None)} pos=({m.x:.1f},{m.y:.1f}) dist={dist:.1f}")

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
