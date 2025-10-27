import time
from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE

from state_machine import StateMachine

SCREEN_W, SCREEN_H = 1000, 1000
SPRITE_W, SPRITE_H = 70, 82

# 이동 속도(px/sec)
WALK_SPEED = 140.0
ROLL_SPEED = 420.0


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
        key = f'IDLE_{self.character.dir}'
        info = self.character.sprite_info[key]
        self.character.frame_time_acc += self.character.dt
        ft = info['frame_time']
        while self.character.frame_time_acc >= ft:
            self.character.frame_time_acc -= ft
            self.character.frame = (self.character.frame + 1) % info['frames']

        # 입력이 있으면 걷기 상태로
        if any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('MOVE', None))

    def draw(self):
        key = f'IDLE_{self.character.dir}'
        info = self.character.sprite_info[key]
        ox = info.get('offset_x', 0)
        oy = info.get('offset_y', 0)
        self.character.image.clip_draw(
            int(self.character.frame) * SPRITE_W,
            info['row_y'],
            SPRITE_W, SPRITE_H,
            self.character.x + ox,
            self.character.y + oy,
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
        key = f'WALK_{self.character.dir}'
        info = self.character.sprite_info[key]
        # 시간 기반 프레임 증가
        self.character.frame_time_acc += self.character.dt
        ft = info['frame_time']
        while self.character.frame_time_acc >= ft:
            self.character.frame_time_acc -= ft
            self.character.frame = (self.character.frame + 1) % info['frames']

        # 이동 처리
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
            self.character.x = min(SCREEN_W - SPRITE_W // 2, self.character.x + move_dist)

    def draw(self):
        key = f'WALK_{self.character.dir}'
        info = self.character.sprite_info[key]
        ox = info.get('offset_x', 0)
        oy = info.get('offset_y', 0)
        self.character.image.clip_draw(
            int(self.character.frame) * SPRITE_W,
            info['row_y'],
            SPRITE_W, SPRITE_H,
            self.character.x + ox,
            self.character.y + oy,
        )


class Roll:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0
        # 구르는 동안 키 입력 영향 차단
        for k in self.character.key_map:
            self.character.key_map[k] = False

    def exit(self, e):
        pass

    def do(self):
        key = f'ROLL_{self.character.dir}'
        # Up에 대한 별도 이미지가 없으면 Down 사용
        if key == 'ROLL_UP':
            key = 'ROLL_DOWN'
        info = self.character.sprite_info[key]

        # 시간 기반 프레임 진행 (마지막 프레임에서 STOP)
        self.character.frame_time_acc += self.character.dt
        ft = info['frame_time']
        while self.character.frame_time_acc >= ft:
            self.character.frame_time_acc -= ft
            if self.character.frame < info['frames'] - 1:
                self.character.frame += 1
            else:
                self.character.state_machine.handle_state_event(('STOP', None))
                break

        # 구르기 이동
        roll_dist = 10
        if self.character.dir == 'UP':
            self.character.y = min(SCREEN_H - SPRITE_H // 2, self.character.y + roll_dist)
        elif self.character.dir == 'DOWN':
            self.character.y = max(SPRITE_H // 2, self.character.y - roll_dist)
        elif self.character.dir == 'LEFT':
            self.character.x = max(SPRITE_W // 2, self.character.x - roll_dist)
        elif self.character.dir == 'RIGHT':
            self.character.x = min(SCREEN_W - SPRITE_W // 2, self.character.x + roll_dist)

    def draw(self):
        key = f'ROLL_{self.character.dir}'
        if key == 'ROLL_UP':
            key = 'ROLL_DOWN'
        info = self.character.sprite_info[key]
        ox = info.get('offset_x', 0)
        oy = info.get('offset_y', 0)
        self.character.image.clip_draw(
            int(self.character.frame) * SPRITE_W,
            info['row_y'],
            SPRITE_W, SPRITE_H,
            self.character.x + ox,
            self.character.y + oy,
        )


class Main_character:
    def __init__(self):
        self.x = SCREEN_W // 2
        self.y = SCREEN_H // 2
        self.image = load_image('Main_character_move.png')
        self.dir = 'DOWN'
        self.frame = 0

        self.health = 100
        self.key_map = {'UP': False, 'DOWN': False, 'LEFT': False, 'RIGHT': False}

        # 시간 관련
        self.prev_time = time.time()
        self.dt = 0.0
        self.frame_time_acc = 0.0

        # sprite_info: row order per user's Main_character_move2 mapping (1..12)
        # 1: 앞 Idle, 2: 오른 Idle, 3: 왼 Idle, 4: 위 Idle
        # 5: 앞 걷기, 6: 왼 걷기, 7: 오른 걷기, 8: 위 걷기
        # 9: 앞 구르기, 10: 왼 구르기, 11: 오른 구르기, 12: 뒤 구르기
        self.sprite_info = {
            'IDLE_DOWN': {'row_idx': 1},
            'IDLE_RIGHT': {'row_idx': 2},
            'IDLE_LEFT': {'row_idx': 3},
            'IDLE_UP': {'row_idx': 4},

            'WALK_DOWN': {'row_idx': 5},
            'WALK_LEFT': {'row_idx': 6},
            'WALK_RIGHT': {'row_idx': 7},
            'WALK_UP': {'row_idx': 8},

            'ROLL_DOWN': {'row_idx': 9},
            'ROLL_LEFT': {'row_idx': 10},
            'ROLL_RIGHT': {'row_idx': 11},
            'ROLL_UP': {'row_idx': 12},
        }

        # 시트 픽셀 데이터로 프레임별 오프셋 계산 (프레임 간 중심 차이 보정)
        try:
            from PIL import Image
            import numpy as np
            pil_img = Image.open('Main_character_move.png').convert('RGBA')
            arr = np.array(pil_img)
            H = pil_img.height
            # anchor: IDLE_DOWN frame 0 center
            anchor_x = None
            anchor_y = None
            # 먼저 compute frames, row_y
            for key in self.sprite_info:
                info = self.sprite_info[key]
                info['frames'] = 10 if info['row_idx'] <= 4 else 8
                info['row_y'] = H - info['row_idx'] * SPRITE_H
            # get anchor center
            ad = self.sprite_info['IDLE_DOWN']
            x0 = 0
            y0 = ad['row_y']
            frame = arr[y0:y0+SPRITE_H, x0:x0+SPRITE_W]
            alpha = frame[:, :, 3]
            ys, xs = np.where(alpha > 0)
            if len(xs) == 0:
                anchor_x = SPRITE_W // 2
                anchor_y = SPRITE_H // 2
            else:
                anchor_x = xs.mean()
                anchor_y = ys.mean()

            # compute per-frame offsets
            for key in self.sprite_info:
                info = self.sprite_info[key]
                fr = info['frames']
                r_y = info['row_y']
                offsets = []
                for f in range(fr):
                    x0 = f * SPRITE_W
                    y0 = r_y
                    frame = arr[y0:y0+SPRITE_H, x0:x0+SPRITE_W]
                    alpha = frame[:, :, 3]
                    ys, xs = np.where(alpha > 0)
                    if len(xs) == 0:
                        cx = SPRITE_W / 2
                        cy = SPRITE_H / 2
                    else:
                        cx = xs.mean()
                        cy = ys.mean()
                    ox = int(round(anchor_x - cx))
                    oy = int(round(anchor_y - cy))
                    offsets.append((ox, oy))
                info['frame_offsets'] = offsets
                info['frame_time'] = 0.35 if info['frames'] == 10 else 0.28
        except Exception:
            # PIL/numpy 없거나 실패 시: 기본값 채움
            for key in self.sprite_info:
                info = self.sprite_info[key]
                info['frames'] = 10 if info['row_idx'] <= 4 else 8
                info['row_y'] = self.image.h - info['row_idx'] * SPRITE_H
                info.setdefault('offset_x', 0)
                info.setdefault('offset_y', 0)
                info['frame_offsets'] = [(info.get('offset_x', 0), info.get('offset_y', 0))] * info['frames']
                info['frame_time'] = 0.35 if info['frames'] == 10 else 0.28

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
