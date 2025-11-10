from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE

import game_framework
import game_world
import play_mode

import player_loader
import player_states
from main_chracter import Main_character

from tiled_map import TiledMap

player = None
tiled_map = None
collision_boxes = [] # 충돌 영역 (레이어 1: Collisions)

def init():
    global player, tiled_map, collision_boxes

    # 1. 타일드 맵 로드
    tiled_map = TiledMap('map/shop_mode.json')

    # 2. 충돌 영역 설정 (레이어 1)
    collision_boxes = tiled_map.get_collision_boxes()

    # 3. 플레이어 생성 및 초기 위치 설정
    player = Main_character()
    player.x = 100  # 시작 X 좌표
    player.y = 50  # 시작 Y 좌표

    # 4. 게임 월드에 객체 추가
    game_world.add_object(tiled_map, 0)  # 배경 레이어
    game_world.add_object(player, 1)     # 플레이어 레이어

    # 상점 npc 추가 예정

def finish():
    game_world.clear() # 상점 나가서 다른 모드 진입시 모든 객체 지우기!
    global collision_boxes
    collision_boxes = []

def handle_events():
    events =get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        else:
            player.handle_event(event)

def update(dt):
    player.update(dt)

    if player.y < 10 or player.x >300:  # 상점 문 위치에 따라 조정 필요
        game_framework.change_mode(play_mode)


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause(): pass
def resume(): pass


