# main.py (Commit 1)
from pico2d import *
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_QUIT, SDLK_ESCAPE

from state_machine import StateMachine

SCREEN_W, SCREEN_H = 800, 600
SPRITE_W, SPRITE_H = 70, 82


class Walk:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame =0

    def exit(self,e):
        pass

    def do(self):
        key = f'WALK_{self.character.dir}'
        info = self.character.sprite_info[key]
        self.character.frame = (self.character.frame + 1) % info['frames']


        if not any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('STOP', None))
            return

        move_dist = 5

        if self.character.key_map['UP']:
            self.character.y = min(SCREEN_H - SPRITE_H // 2, self.character.y + move_dist)
        if self.character.key_map['DOWN']:
            self.character.y = max(SPRITE_H // 2, self.character.y - move_dist)
        if self.character.key_map['LEFT']:
            self.character.x = max(SPRITE_W // 2, self.character.x - move_dist)
        if self.character.key_map['RIGHT']:
            self.character.x = min(SCREEN_W - SPRITE_H // 2, self.character.x + move_dist)

    def draw(self):
        key = f'WALK_{self.character.dir}'
        info = self.character.sprite_info[key]
        self.character.image.clip_draw(
            self.character.frame * SPRITE_W,
            info['row_y'],
            SPRITE_W, SPRITE_H,
            self.character.x, self.character.y
        )







class Idle:
    def __init__(self, character):
      self.character = character

    def enter(self, e):
        self.character.frame = 0

    def exit(self,e):
        pass

    def do(self):
        key = f'IDLE_{self.character.dir}'
        info = self.character.sprite_info[key]

        self.character.frame = (self.character.frame + 1) % info['frames']

        if any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('MOVE', None))

    def draw(self):
        key = f'IDLE_{self.character.dir}'
        info = self.character.sprite_info[key]
        self.character.image.clip_draw(
            self.character.frame * SPRITE_W,
            info['row_y'],
            SPRITE_W, SPRITE_H,
            self.character.x, self.character.y
        )


class Main_character:
    def __init__(self):
        self.x, self.y = SCREEN_W // 2, SCREEN_H // 2
        self.image = load_image('Main_character_move.png')
        self.dir = 'DOWN'
        self.frame = 0

        self.key_map = {'UP' : False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

        self.sprite_info = {
            'IDLE_DOWN': {'row_idx': 1, 'frames': 10},
            'IDLE_RIGHT': {'row_idx': 2, 'frames': 10},
            'IDLE_LEFT': {'row_idx': 3, 'frames': 10},
            'IDLE_UP': {'row_idx': 4, 'frames': 10},

            'WALK_DOWN': {'row_idx': 5, 'frames': 10},
            'WALK_RIGHT': {'row_idx': 6, 'frames': 10},
            'WALK_LEFT': {'row_idx': 7, 'frames': 10},
            'WALK_UP': {'row_idx': 8, 'frames': 10},

        }

        for key in self.sprite_info:
            info = self.sprite_info[key]
            info['row_y'] = self.image.h - info['row_idx'] * SPRITE_H

        self.IDLE = Idle(self)
        self.WALK = Walk(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    'MOVE': lambda e: self.WALK
                },
                self.WALK: {
                    'STOP': lambda e: self.IDLE
                }
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_UP:
                self.key_map['UP'] = True
                self.dir = 'UP'
            elif event.key == SDLK_DOWN:
                self.key_map['DOWN'] = True
                self.dir = 'DOWN'
            elif event.key == SDLK_LEFT:
                self.key_map['LEFT'] = True
                self.dir = 'LEFT'
            elif event.key == SDLK_RIGHT:
                self.key_map['RIGHT'] = True
                self.dir = 'RIGHT'

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_UP:
                self.key_map['UP'] = False
            elif event.key == SDLK_DOWN:
                self.key_map['DOWN'] = False
            elif event.key == SDLK_LEFT:
                self.key_map['LEFT'] = False
            elif event.key == SDLK_RIGHT:
                self.key_map['RIGHT'] = False


def handle_events(player):
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            player.handle_event(event)


running = True
open_canvas(SCREEN_W, SCREEN_H)
Main_player = Main_character()

while running:

    # 이벤트 처리
    handle_events(Main_player)

    # 객체 업데이트
    Main_player.update()

    # 그리기
    clear_canvas()
    Main_player.draw()
    update_canvas()

    delay(0.01)

close_canvas()
