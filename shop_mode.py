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