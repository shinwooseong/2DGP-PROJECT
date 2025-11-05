# play_mode.py
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_u

import game_framework
import game_world
import inventory
import title_mode

import main_chracter
from Monster import Green_MS, EyeBall, Trash_Monster, Red_MS

# UI import (simple direct import)
from UI import UI

# 디버그 설정
DEBUG_MONSTERS = True
_last_hp = None

player = None
monsters = []
ui = None


def init():
    global player, monsters, _last_hp, ui

    player = main_chracter.Main_character()
    game_world.add_object(player, 1)  # layer 1

    monsters = [
        Green_MS(300, 200),
        Green_MS(600, 200),
        Trash_Monster(100, 100),
        EyeBall(400, 400),
        Red_MS(500, 150),
    ]
    game_world.add_objects(monsters, 1)  # layer 1

    _last_hp = None

    # UI 생성 및 등록 (layer 2)
    if UI is not None:
        try:
            ui = UI()
            game_world.add_object(ui, 2)
        except Exception:
            ui = None

    if DEBUG_MONSTERS:
        print("Monsters summary (play_mode init):")
        for i, m in enumerate(monsters):
            try:
                sheet = getattr(m.animator, 'sheet_image', None)
                sheet_info = None
                if sheet is not None:
                    sheet_info = (getattr(sheet, 'w', None), getattr(sheet, 'h', None))
                print(f"  M{i}: {m.__class__.__name__} pos=({m.x},{m.y}) sheet={sheet_info}")
            except Exception as e:
                print(f"  M{i}: {m.__class__.__name__} - debug error: {e}")


def finish():
    global ui
    # UI 제거
    if ui is not None:
        try:
            game_world.remove_object(ui)
        except Exception:
            pass
        ui = None

    game_world.clear()  # game_world의 모든 객체 삭제


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.change_mode(title_mode)
            elif event.key == SDLK_u:
                game_framework.push_mode(inventory)
            else:
                player.handle_event(event)


def update(dt):
    # 플레이어 업데이트
    player.update(dt)

    # UI 동기화 (player.money가 없으면 0 사용)
    if ui is not None:
        try:
            ui.set_money(getattr(player, 'money', 0))
        except Exception:
            pass

    for m in monsters:
        # play_mode가 실행 중이라는 것은 인벤토리가 닫힌 상태
        m.update(dt, frozen=False, player=player)

    # 플레이어 공격 히트 처리
    if getattr(player, 'attack_hit_pending', False):
        pr = getattr(player, 'attack_range', 80)
        for m in monsters:
            if not m.alive: continue
            dx = m.x - player.x
            dy = m.y - player.y
            if dx * dx + dy * dy <= pr * pr:
                m.take_damage(getattr(player, 'attack', 10))
                if DEBUG_MONSTERS:
                    print(f"Player hit M at ({m.x:.1f},{m.y:.1f}) hp_left={m.hp}")
        player.attack_hit_pending = False

    dead_monsters = []
    for m in monsters:
        # m.alive가 False이고, m.animator의 _death_done 플래그가 True이면
        if not m.alive and getattr(m.animator, '_death_done', False):
            dead_monsters.append(m)

    for m in dead_monsters:
        game_world.remove_object(m)
        monsters.remove(m)


def draw():
    global _last_hp
    clear_canvas()
    game_world.render()  # game_world의 모든 객체 그리기
    update_canvas()

    # 디버그용 HP 출력
    try:
        hp = int(max(0, getattr(player, 'health', 0)))
        if hp != _last_hp:
            print(f"HP: {hp}")
            _last_hp = hp
    except Exception:
        pass


def pause():
    pass


def resume():
    pass