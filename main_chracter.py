import time
from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE

from state_machine import StateMachine

SCREEN_W, SCREEN_H = 1000, 1000
SPRITE_W, SPRITE_H = 70, 82

# 이동 속도(px/sec)
WALK_SPEED = 140.0
ROLL_SPEED = 420.0
# 구르기 총 이동 거리(픽셀)
ROLL_DISTANCE = 160.0


class Idle:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self):
        # 시간 기반 프레임 진행
        image = self.character.idle_images[self.character.dir]
        frames = self.character.idle_frames[self.character.dir]

        self.character.frame_time_acc += self.character.dt
        frame_time = 0.1  # idle 프레임 시간
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        # 입력이 있으면 걷기 상태로
        if any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('MOVE', None))

    def draw(self):
        image = self.character.idle_images[self.character.dir]
        frames = self.character.idle_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        # 각 프레임이 가로로 배열되어 있음
        x_offset = frame_idx * SPRITE_W
        image.clip_draw(
            x_offset, 0,
            SPRITE_W, SPRITE_H,
            self.character.x,
            self.character.y,
        )


class Walk:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self):
        # 시간 기반 프레임 증가
        image = self.character.run_images[self.character.dir]
        frames = self.character.run_frames[self.character.dir]

        self.character.frame_time_acc += self.character.dt
        frame_time = 0.08  # run 프레임 시간 (walk보다 약간 빠름)
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        # 시간 기반으로 이동 (px/sec)
        dx = 0.0
        dy = 0.0
        speed = WALK_SPEED
        if self.character.key_map['UP']:
            dy += speed * self.character.dt
        if self.character.key_map['DOWN']:
            dy -= speed * self.character.dt
        if self.character.key_map['LEFT']:
            dx -= speed * self.character.dt
        if self.character.key_map['RIGHT']:
            dx += speed * self.character.dt

        if dx == 0.0 and dy == 0.0:
            self.character.state_machine.handle_state_event(('STOP', None))
            return

        # 적용 및 화면 경계
        self.character.x = max(SPRITE_W // 2, min(SCREEN_W - SPRITE_W // 2, self.character.x + dx))
        self.character.y = max(SPRITE_H // 2, min(SCREEN_H - SPRITE_H // 2, self.character.y + dy))

    def draw(self):
        image = self.character.run_images[self.character.dir]
        frames = self.character.run_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        x_offset = frame_idx * SPRITE_W
        image.clip_draw(
            x_offset, 0,
            SPRITE_W, SPRITE_H,
            self.character.x,
            self.character.y,
        )


class Roll:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0
        self.character.roll_moved = 0.0

    def exit(self, e):
        pass

    def do(self):
        # 구르기 중에도 방향 키 입력을 받아서 방향 업데이트
        if self.character.key_map['UP']:
            self.character.dir = 'UP'
        elif self.character.key_map['DOWN']:
            self.character.dir = 'DOWN'
        elif self.character.key_map['LEFT']:
            self.character.dir = 'LEFT'
        elif self.character.key_map['RIGHT']:
            self.character.dir = 'RIGHT'

        image = self.character.run_images[self.character.dir]
        frames = self.character.run_frames[self.character.dir]

        # 시간 기반 프레임 진행 (마지막 프레임에서 STOP)
        self.character.frame_time_acc += self.character.dt
        frame_time = 0.06  # roll은 더 빠르게
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            if self.character.frame < frames - 1:
                self.character.frame += 1
            else:
                # 마지막 프레임에 도달하면 상태 전환
                self.character.state_machine.handle_state_event(('STOP', None))
                break

        # 구르기 이동
        remaining = max(0.0, ROLL_DISTANCE - getattr(self.character, 'roll_moved', 0.0))
        if remaining > 0.0:
            move = min(ROLL_SPEED * self.character.dt, remaining)
            if self.character.dir == 'UP':
                self.character.y = min(SCREEN_H - SPRITE_H // 2, self.character.y + move)
            elif self.character.dir == 'DOWN':
                self.character.y = max(SPRITE_H // 2, self.character.y - move)
            elif self.character.dir == 'LEFT':
                self.character.x = max(SPRITE_W // 2, self.character.x - move)
            elif self.character.dir == 'RIGHT':
                self.character.x = min(SCREEN_W - SPRITE_W // 2, self.character.x + move)
            self.character.roll_moved = getattr(self.character, 'roll_moved', 0.0) + move

    def draw(self):
        image = self.character.run_images[self.character.dir]
        frames = self.character.run_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        x_offset = frame_idx * SPRITE_W
        image.clip_draw(
            x_offset, 0,
            SPRITE_W, SPRITE_H,
            self.character.x,
            self.character.y,
        )


class Main_character:
    def __init__(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.dir = 'DOWN'
        self.frame = 0

        self.health = 100
        self.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

        # 시간 관련
        self.prev_time = time.time()
        self.dt = 0.0
        self.frame_time_acc = 0.0
        self.roll_moved = 0.0

        # IDLE 이미지 로드 (각 방향별)
        self.idle_images = {
            'DOWN': load_image('IDLE/idle_down.png'),
            'UP': load_image('IDLE/idle_up.png'),
            'LEFT': load_image('IDLE/idle_left.png'),
            'RIGHT': load_image('IDLE/idle_right.png'),
        }

        # RUN 이미지 로드 (각 방향별)
        self.run_images = {
            'DOWN': load_image('RUN/run_down.png'),
            'UP': load_image('RUN/run_up.png'),
            'LEFT': load_image('RUN/run_left.png'),
            'RIGHT': load_image('RUN/run_right.png'),
        }

        # 각 방향별 프레임 수 (이미지 로드 후 계산)
        self.idle_frames = {}
        self.run_frames = {}

        for direction in ['DOWN', 'UP', 'LEFT', 'RIGHT']:
            # idle과 run 모두 8프레임 고정
            self.idle_frames[direction] = 8
            self.run_frames[direction] = 8

        # 상태 인스턴스
        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ROLL = Roll(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    'MOVE': lambda e: self.WALK,
                    'SPACE': lambda e: self.ROLL
                },
                self.WALK: {
                    'STOP': lambda e: self.IDLE,
                    'SPACE': lambda e: self.ROLL
                },
                self.ROLL: {
                    'STOP': lambda e: self.IDLE
                }
            }
        )

    def update(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now
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
            elif event.key == SDLK_SPACE:
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

