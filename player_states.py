import time
from pico2d import load_image
from player_loader import FOOT_OFFSET_Y

SCREEN_W, SCREEN_H = 1280, 720
SPRITE_W, SPRITE_H = 96, 80
WALK_SPEED = 140.0
ROLL_SPEED = 360.0
ROLL_DISTANCE = 80.0

class Idle:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self, dt):
        # 캐릭터가 소유한 'loader'의 프레임 정보 사용
        frames = self.character.loader.idle_frames[self.character.dir]

        self.character.frame_time_acc += dt
        frame_time = 0.1
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        if any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('MOVE', None))

    def draw(self):
        # 캐릭터가 소유한 'loader'의 이미지/오프셋 정보 사용
        loader = self.character.loader
        image = loader.idle_images[self.character.dir]
        frames = loader.idle_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        x_offset = frame_idx * SPRITE_W
        y_offset = loader.idle_y_offsets[self.character.dir]
        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (SPRITE_H // 2) - FOOT_OFFSET_Y
        image.clip_draw(
            x_offset, y_offset,
            SPRITE_W, SPRITE_H,
            self.character.x,
            draw_y,
        )


class Walk:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self, dt):
        loader = self.character.loader
        frames = loader.run_frames[self.character.dir]

        self.character.frame_time_acc += dt
        frame_time = 0.08
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        dx = 0.0
        dy = 0.0
        speed = WALK_SPEED
        if self.character.key_map['UP']:
            dy += speed * dt
        if self.character.key_map['DOWN']:
            dy -= speed * dt
        if self.character.key_map['LEFT']:
            dx -= speed * dt
        if self.character.key_map['RIGHT']:
            dx += speed * dt

        if dx == 0.0 and dy == 0.0:
            self.character.state_machine.handle_state_event(('STOP', None))
            return

        self.character.x = max(SPRITE_W // 2, min(SCREEN_W - SPRITE_W // 2, self.character.x + dx))
        self.character.y = max(SPRITE_H // 2, min(SCREEN_H - SPRITE_H // 2, self.character.y + dy))

    def draw(self):
        loader = self.character.loader
        image = loader.run_images[self.character.dir]
        frames = loader.run_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        x_offset = frame_idx * SPRITE_W
        y_offset = loader.run_y_offsets[self.character.dir]
        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (SPRITE_H // 2) - FOOT_OFFSET_Y
        image.clip_draw(
            x_offset, y_offset,
            SPRITE_W, SPRITE_H,
            self.character.x,
            draw_y,
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

    def do(self, dt):
        if self.character.key_map['UP']:
            self.character.dir = 'UP'
        elif self.character.key_map['DOWN']:
            self.character.dir = 'DOWN'
        elif self.character.key_map['LEFT']:
            self.character.dir = 'LEFT'
        elif self.character.key_map['RIGHT']:
            self.character.dir = 'RIGHT'

        frames = self.character.loader.run_frames[self.character.dir]

        self.character.frame_time_acc += dt
        frame_time = 0.06
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            if self.character.frame < frames - 1:
                self.character.frame += 1
            else:
                self.character.state_machine.handle_state_event(('STOP', None))
                break

        remaining = max(0.0, ROLL_DISTANCE - getattr(self.character, 'roll_moved', 0.0))
        if remaining > 0.0:
            move = min(ROLL_SPEED * dt, remaining)
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
        loader = self.character.loader
        image = loader.run_images[self.character.dir]
        frames = loader.run_frames[self.character.dir]
        frame_idx = int(self.character.frame) % frames

        x_offset = frame_idx * SPRITE_W
        y_offset = loader.run_y_offsets[self.character.dir]
        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (SPRITE_H // 2) - FOOT_OFFSET_Y
        image.clip_draw(
            x_offset, y_offset,
            SPRITE_W, SPRITE_H,
            self.character.x,
            draw_y,
        )


class Attack:
    def __init__(self, character):
        self.character = character
        self.stage = 1
        self.frame = 0
        self.frame_time_acc = 0.0
        self.animation_ended = False
        self._hit_done = False

    def enter(self, e):
        self.stage = getattr(self.character, 'attack_stage', 1)
        self.character.frame = 0
        self.frame = 0
        self.frame_time_acc = 0.0
        self.animation_ended = False
        self.character.next_attack_request = False
        self._hit_done = False
        self.character.attack_hit_pending = False

    def exit(self, e):
        pass

    def do(self, dt):
        loader = self.character.loader
        frames = loader.attack_frames[self.stage][self.character.dir]
        frame_time = 0.07 if self.stage == 1 else 0.06
        hit_frame = max(0, frames // 2)

        self.frame_time_acc += dt

        dx = 0.0
        dy = 0.0
        move_speed = 70.0
        if self.character.key_map['UP']:
            dy += move_speed * dt
        if self.character.key_map['DOWN']:
            dy -= move_speed * dt
        if self.character.key_map['LEFT']:
            dx -= move_speed * dt
        if self.character.key_map['RIGHT']:
            dx += move_speed * dt

        if dx != 0.0 or dy != 0.0:
            self.character.x = max(SPRITE_W // 2, min(SCREEN_W - SPRITE_W // 2, self.character.x + dx))
            self.character.y = max(SPRITE_H // 2, min(SCREEN_H - SPRITE_H // 2, self.character.y + dy))

        while self.frame_time_acc >= frame_time:
            self.frame_time_acc -= frame_time
            self.frame += 1

            if not self._hit_done and self.frame >= hit_frame:
                self._hit_done = True
                self.character.attack_hit_pending = True

            if self.frame >= frames:
                self.animation_ended = True
                if self.stage == 1 and self.character.next_attack_request:
                    self.stage = 2
                    self.character.attack_stage = 2
                    self.frame = 0
                    self.frame_time_acc = 0.0
                    self.animation_ended = False
                    self.character.next_attack_request = False
                    self._hit_done = False
                    self.character.attack_hit_pending = False
                    frames = loader.attack_frames[self.stage][self.character.dir]
                    frame_time = 0.06
                    continue
                else:
                    self.character.last_attack_end_time = time.time()
                    self.character.next_attack_request = False
                    self._hit_done = False
                    self.character.attack_hit_pending = False
                    self.character.state_machine.handle_state_event(('STOP', None))
                    return

    def draw(self):
        loader = self.character.loader
        img = loader.attack_images[self.stage][self.character.dir]
        frames = loader.attack_frames[self.stage][self.character.dir]
        frame_idx = int(self.frame) % frames
        x_offset = frame_idx * SPRITE_W
        y_offset = loader.attack_y_offsets[self.stage][self.character.dir]
        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (SPRITE_H // 2) - FOOT_OFFSET_Y
        img.clip_draw(
            x_offset, y_offset,
            SPRITE_W, SPRITE_H,
            self.character.x, draw_y
        )