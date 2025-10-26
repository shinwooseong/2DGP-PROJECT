from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDL_KEYUP

from main import SCREEN_H, SPRITE_H, SPRITE_W, SCREEN_W
from state_machine import StateMachine


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


class Roll:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0

    def exit(self,e):
        pass

    def do(self):
        # Up 일 때는 Down 이미지 사용하기
        # Up 구르기 이미지 없음..
        key = f'ROLL_{self.character.dir}'
        if key == 'ROLL_UP':
            key = 'ROLL_DOWN'
        info = self.character.sprite_info[key]

        # 구르기는 8프레임만 있음, 따라서 6번째까지만 1증가하고
        # 7프레임에서는 애니메이션 종료하기!
        if self.character.frame < info['frames'] - 1:
            self.character.frame += 1
        else:
            self.character.state_machine.handle_state_event(('STOP', None))

        move_dist = 10

        if self.character.dir == 'UP':
            self.character.y = min(SCREEN_H - SPRITE_H // 2, self.character.y + move_dist)
        elif self.character.dir == 'DOWN':
            self.character.y = max(SPRITE_H // 2, self.character.y - move_dist)
        elif self.character.dir == 'LEFT':
            self.character.x = max(SPRITE_W // 2, self.character.x - move_dist)
        elif self.character.dir == 'RIGHT':
            self.character.x = min(SCREEN_W - SPRITE_W // 2, self.character.x + move_dist)

    def draw(self):
        key = f'ROLL_{self.character.dir}'
        if key == 'ROLL_UP':
            key = 'ROLL_DOWN'
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

            'ROLL_DOWN': {'row_idx': 9, 'frames': 8},
            'ROLL_LEFT': {'row_idx': 10, 'frames': 8},
            'ROLL_RIGHT': {'row_idx': 11, 'frames': 8},

        }

        for key in self.sprite_info:
            info = self.sprite_info[key]
            info['row_y'] = self.image.h - info['row_idx'] * SPRITE_H

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ROLL = Roll(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    'MOVE': lambda e: self.WALK,
                    'SPACE': lambda e: self.ROLL  # 스페이스 누르면 Roll
                },
                self.WALK: {
                    'STOP': lambda e: self.IDLE,
                    'SPACE': lambda e: self.ROLL  # 스페이스 누르면 Roll
                },
                self.ROLL: {
                    'STOP': lambda e: self.IDLE  # 구르기 끝나면 Idle
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
                self.key_map['UP'] = True;
                self.dir = 'UP'
            elif event.key == SDLK_DOWN:
                self.key_map['DOWN'] = True;
                self.dir = 'DOWN'
            elif event.key == SDLK_LEFT:
                self.key_map['LEFT'] = True;
                self.dir = 'LEFT'
            elif event.key == SDLK_RIGHT:
                self.key_map['RIGHT'] = True;
                self.dir = 'RIGHT'
            elif event.key == SDLK_SPACE:
                # [추가] 스페이스바가 눌리면 'SPACE' 이벤트를 FSM에 전달
                self.state_machine.handle_state_event(('SPACE', None))

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_UP:
                self.key_map['UP'] = False
            elif event.key == SDLK_DOWN:
                self.key_map['DOWN'] = False
            elif event.key == SDLK_LEFT:
                self.key_map['LEFT'] = False
            elif event.key == SDLK_RIGHT:
                self.key_map['RIGHT'] = False
