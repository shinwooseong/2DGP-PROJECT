# main.py (Commit 1)

from pico2d import *
import time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_QUIT, SDLK_ESCAPE


SCREEN_W, SCREEN_H = 800, 600
SPRITE_W, SPRITE_H = 70, 82

class StateMachine:
    def __init__(self,start_state,transitions):
        self.next_state = None
        self.cur_state = start_state
        self.transitions = transitions
        self.cur_state.enter(None)

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        if state_event[0] in self.transitions[self.cur_state]:
            next_state_func = self.transitions[self.cur_state][state_event[0]]
            next_state = next_state_func(state_event)
            self.cur_state.exit(state_event)
            self.cur_state = next_state
            self.cur_state.enter(state_event)
            return True
        return False


class Walk:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        pass

    def exit(self,e):
        pass

    def do(self):
        pass

    def draw(self):
        pass







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

        self.sprite_info = {
            'IDLE_DOWN': {'row_idx': 1, 'frames': 10},
            'IDLE_RIGHT': {'row_idx': 2, 'frames': 10},
            'IDLE_LEFT': {'row_idx': 3, 'frames': 10},
            'IDLE_UP': {'row_idx': 4, 'frames': 10},
        }

        for key in self.sprite_info:

            info = self.sprite_info[key]
            info['row_y'] = self.image.h - info['row_idx'] * SPRITE_H

        self.IDLE = Idle(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {

            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_UP:
                self.dir = 'UP'
            elif event.key == SDLK_DOWN:
                self.dir = 'DOWN'
            elif event.key == SDLK_LEFT:
                self.dir = 'LEFT'
            elif event.key == SDLK_RIGHT:
                self.dir = 'RIGHT'


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
