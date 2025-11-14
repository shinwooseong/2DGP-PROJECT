import time
from pico2d import load_image
from transform_loader import TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H, TRANSFORM_FOOT_OFFSET_Y

# 실제 충돌 범위 import (순환 import 방지를 위해 character_constants에서 가져옴)
from character_constants import (
    SCREEN_W, SCREEN_H,
    TRANSFORM_COLLISION_W, TRANSFORM_COLLISION_H
)

# 몸집이 작아서 속도가 더 빠름
WALK_SPEED = 180.0
ROLL_SPEED = 360.0
ROLL_DISTANCE = 80.0

class TransformIdle:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self, dt):
        loader = self.character.transform_loader
        frames = loader.idle_frames

        self.character.frame_time_acc += dt
        frame_time = 0.1
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        if any(self.character.key_map.values()):
            self.character.state_machine.handle_state_event(('MOVE', None))

    def draw(self):
        loader = self.character.transform_loader
        image = loader.idle_image
        frames = loader.idle_frames
        frame_idx = int(self.character.frame) % frames

        # 실제 프레임 크기 사용
        x_offset = frame_idx * TRANSFORM_SPRITE_W
        img_height = image.h

        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (TRANSFORM_SPRITE_H // 2) - TRANSFORM_FOOT_OFFSET_Y

        # 왼쪽 방향이면 이미지 좌우 반전
        if self.character.dir == 'LEFT':
            image.clip_composite_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                0, 'h', self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )
        else:  # RIGHT
            image.clip_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )


class TransformWalk:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0

    def exit(self, e):
        pass

    def do(self, dt):
        loader = self.character.transform_loader
        frames = loader.run_frames

        self.character.frame_time_acc += dt
        frame_time = 0.08
        while self.character.frame_time_acc >= frame_time:
            self.character.frame_time_acc -= frame_time
            self.character.frame = (self.character.frame + 1) % frames

        dx = 0.0
        dy = 0.0
        speed = WALK_SPEED

        # 방향 키 처리 (좌우만)
        if self.character.key_map['LEFT']:
            dx -= speed * dt
            self.character.dir = 'LEFT'
        if self.character.key_map['RIGHT']:
            dx += speed * dt
            self.character.dir = 'RIGHT'
        if self.character.key_map['UP']:
            dy += speed * dt
        if self.character.key_map['DOWN']:
            dy -= speed * dt

        if dx == 0.0 and dy == 0.0:
            self.character.state_machine.handle_state_event(('STOP', None))
            return

        # 실제 충돌 범위로 화면 경계 제한 (스프라이트 크기 대신)
        collision_half_w = TRANSFORM_COLLISION_W // 2
        collision_half_h = TRANSFORM_COLLISION_H // 2

        self.character.x = max(collision_half_w, min(SCREEN_W - collision_half_w, self.character.x + dx))
        self.character.y = max(collision_half_h, min(SCREEN_H - collision_half_h, self.character.y + dy))

    def draw(self):
        loader = self.character.transform_loader
        image = loader.run_image
        frames = loader.run_frames
        frame_idx = int(self.character.frame) % frames

        # 실제 프레임 크기 사용
        x_offset = frame_idx * TRANSFORM_SPRITE_W
        img_height = image.h

        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (TRANSFORM_SPRITE_H // 2) - TRANSFORM_FOOT_OFFSET_Y

        # 왼쪽 방향이면 이미지 좌우 반전
        if self.character.dir == 'LEFT':
            image.clip_composite_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                0, 'h', self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )
        else:  # RIGHT
            image.clip_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )


class TransformRoll:
    def __init__(self, character):
        self.character = character

    def enter(self, e):
        self.character.frame = 0
        self.character.frame_time_acc = 0.0
        self.character.roll_moved = 0.0

    def exit(self, e):
        pass

    def do(self, dt):
        # 대시 방향 결정 (좌우만)
        if self.character.key_map['LEFT']:
            self.character.dir = 'LEFT'
        elif self.character.key_map['RIGHT']:
            self.character.dir = 'RIGHT'

        loader = self.character.transform_loader
        frames = loader.dash_frames

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

            # 실제 충돌 범위로 화면 경계 제한
            collision_half_w = TRANSFORM_COLLISION_W // 2
            collision_half_h = TRANSFORM_COLLISION_H // 2

            if self.character.key_map['UP']:
                self.character.y = min(SCREEN_H - collision_half_h, self.character.y + move)
            elif self.character.key_map['DOWN']:
                self.character.y = max(collision_half_h, self.character.y - move)

            if self.character.dir == 'LEFT':
                self.character.x = max(collision_half_w, self.character.x - move)
            elif self.character.dir == 'RIGHT':
                self.character.x = min(SCREEN_W - collision_half_w, self.character.x + move)

            self.character.roll_moved = getattr(self.character, 'roll_moved', 0.0) + move

    def draw(self):
        loader = self.character.transform_loader
        image = loader.dash_image
        frames = loader.dash_frames
        frame_idx = int(self.character.frame) % frames

        # 실제 프레임 크기 사용
        x_offset = frame_idx * TRANSFORM_SPRITE_W
        img_height = image.h

        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (TRANSFORM_SPRITE_H // 2) - TRANSFORM_FOOT_OFFSET_Y

        # 왼쪽 방향이면 이미지 좌우 반전
        if self.character.dir == 'LEFT':
            image.clip_composite_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                0, 'h', self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )
        else:  # RIGHT
            image.clip_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )


class TransformAttack:
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
        loader = self.character.transform_loader

        if self.stage == 1:
            frames = loader.attack1_frames
            frame_time = 0.07
        else:
            frames = loader.attack2_frames
            frame_time = 0.06

        hit_frame = max(0, frames // 2)

        self.frame_time_acc += dt

        # 공격 중 이동 (느리게)
        dx = 0.0
        dy = 0.0
        move_speed = 70.0

        if self.character.key_map['LEFT']:
            dx -= move_speed * dt
            self.character.dir = 'LEFT'
        if self.character.key_map['RIGHT']:
            dx += move_speed * dt
            self.character.dir = 'RIGHT'
        if self.character.key_map['UP']:
            dy += move_speed * dt
        if self.character.key_map['DOWN']:
            dy -= move_speed * dt

        if dx != 0.0 or dy != 0.0:
            # 실제 충돌 범위로 화면 경계 제한
            collision_half_w = TRANSFORM_COLLISION_W // 2
            collision_half_h = TRANSFORM_COLLISION_H // 2

            self.character.x = max(collision_half_w, min(SCREEN_W - collision_half_w, self.character.x + dx))
            self.character.y = max(collision_half_h, min(SCREEN_H - collision_half_h, self.character.y + dy))

        while self.frame_time_acc >= frame_time:
            self.frame_time_acc -= frame_time
            self.frame += 1

            if not self._hit_done and self.frame >= hit_frame:
                self._hit_done = True
                self.character.attack_hit_pending = True

            if self.frame >= frames:
                self.animation_ended = True
                if self.stage == 1 and self.character.next_attack_request:
                    # 2단 공격으로 전환
                    self.stage = 2
                    self.character.attack_stage = 2
                    self.frame = 0
                    self.frame_time_acc = 0.0
                    self.animation_ended = False
                    self.character.next_attack_request = False
                    self._hit_done = False
                    self.character.attack_hit_pending = False
                    frames = loader.attack2_frames
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
        loader = self.character.transform_loader

        if self.stage == 1:
            img = loader.attack1_image
            frames = loader.attack1_frames
        else:
            img = loader.attack2_image
            frames = loader.attack2_frames

        frame_idx = int(self.frame) % frames
        # 실제 프레임 크기 사용
        x_offset = frame_idx * TRANSFORM_SPRITE_W
        img_height = img.h

        # 발(실제 발 위치)을 원점으로 하기 위해 y 좌표 조정
        draw_y = self.character.y + (TRANSFORM_SPRITE_H // 2) - TRANSFORM_FOOT_OFFSET_Y

        # 왼쪽 방향이면 이미지 좌우 반전
        if self.character.dir == 'LEFT':
            img.clip_composite_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                0, 'h', self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )
        else:  # RIGHT
            img.clip_draw(
                x_offset, 0, TRANSFORM_SPRITE_W, img_height,
                self.character.x, draw_y, TRANSFORM_SPRITE_W, TRANSFORM_SPRITE_H
            )
