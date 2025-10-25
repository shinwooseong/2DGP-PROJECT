# main.py (Commit 1)

from pico2d import *
import time

SCREEN_W, SCREEN_H = 800, 600
SPRITE_W, SPRITE_H = 60, 72

class Idle:
    def __init__(self):
        pass

    def enter(self, e):
        pass


class Main_character:
    def __init__(self):
        self.x, self.y = SCREEN_W // 2, SCREEN_H // 2
        self.image = load_image('Main_character_move.png')
        self.dir = 'DOWN'
        self.frame = 0

    def update(self):
        pass

    def draw(self):
        sprite_y = self.image.h - 1 * SPRITE_H
        sprite_x = 0 * SPRITE_W
        self.image.clip_draw(sprite_x, sprite_y, SPRITE_W, SPRITE_H, self.x, self.y, 200, 200)

    def handle_event(self, event):
        pass


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
