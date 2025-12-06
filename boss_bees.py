from pico2d import *
import game_world
import server
import os
from Monster import Animator
import math

# 벌침 투사체 클래스
class BeeSting:
    def __init__(self, x, y, direction, speed=300, scale=0.8, damage=20):
        self.x = x
        self.y = y
        self.direction = direction  # 1: 오른쪽, -1: 왼쪽
        self.speed = speed
        self.damage = damage
        self.active = True
        self.scale = scale

        # 프레임 경로 자동 수집
        base = 'MS/boss/The bees'
        frame_paths = []
        for i in range(1, 50):
            p = f"{base}/bullet_bee_{i:04d}.png"
            if os.path.exists(p):
                frame_paths.append(p)

        # Animator 사용: image_list 모드로 애니메이션 처리
        frames_map = {'fly': len(frame_paths)}
        frame_time = {'fly': 0.05}  # 애니메이션 속도
        self.animator = Animator('', frames_map, frame_time, image_list=frame_paths)
        self.animator.set_state('fly')


        # 크기 계산
        img = self.animator._image_list_loaded[0]
        self.width = int(img.w * self.scale)
        self.height = int(img.h * self.scale)

    def update(self, dt):
        if not self.active:
            return

        # x축 이동
        self.x += self.direction * self.speed * dt

        # 애니메이션 업데이트
        if self.animator:
            self.animator.update(dt)

        # 맵 경계 체크
        map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)
        if self.x < -100 or self.x > map_w + 100:
            self.active = False
            try:
                game_world.remove_object(self)
            except:
                pass
            return

        # 플레이어 충돌 검사
        if self.check_collision_with_player():
            server.player.take_damage(self.damage)
            print(f"[BOSS ATTACK] 벌침이 플레이어에게 {self.damage} 데미지!")

            self.active = False
            try:
                game_world.remove_object(self)
            except:
                pass

    def check_collision_with_player(self):
        try:
            player = server.player
            # 플레이어 크기 (캐릭터에 따라 다를 수 있음)
            pw = getattr(player, 'width', 40)
            ph = getattr(player, 'height', 64)

            # AABB 충돌 검사
            left1 = self.x - self.width // 2
            bottom1 = self.y - self.height // 2
            right1 = self.x + self.width // 2
            top1 = self.y + self.height // 2

            left2 = player.x - pw // 2
            bottom2 = player.y - ph // 2
            right2 = player.x + pw // 2
            top2 = player.y + ph // 2

            if right1 < left2 or left1 > right2 or top1 < bottom2 or bottom1 > top2:
                return False
            return True
        except:
            return False

    def draw(self):
        # 카메라 오프셋 적용
        cam = getattr(server, 'tiled_map', None)
        use_cam = bool(cam and getattr(cam, 'use_camera', False))
        cam_ox = cam.cam_offset_x if use_cam else 0
        cam_oy = cam.cam_offset_y if use_cam else 0


        screen_x = self.x + cam_ox
        screen_y = self.y + cam_oy

        # 애니메이션 그리기
        if self.animator and hasattr(self.animator, '_image_list_loaded') and self.animator._image_list_loaded:
            self.animator.draw(screen_x, screen_y, self.scale)

    def get_bb(self):
        return (self.x - self.width // 2 + 10, self.y - self.height // 2 +10,
                self.x + self.width // 2 - 30, self.y + self.height // 2 - 30)


# 보스의 원형 발사체 (각도 기반)
class BossBullet:
    def __init__(self, x, y, angle, speed=220, scale=0.9, damage=15):
        self.x = x
        self.y = y
        self.angle = angle
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.speed = speed
        self.damage = damage
        self.active = True
        self.scale = scale

        # Bullets 폴더의 이미지만 사용
        base = 'MS/boss/Bullets'
        frame_paths = []
        try:
            if os.path.isdir(base):
                for fname in sorted(os.listdir(base)):
                    if fname.lower().endswith('.png'):
                        frame_paths.append(f"{base}/{fname}")
        except Exception:
            pass

        # Animator 생성
        frames_map = {'fly': max(1, len(frame_paths))}
        frame_time = {'fly': 0.06}
        self.animator = Animator('', frames_map, frame_time, image_list=frame_paths if frame_paths else None)
        self.animator.set_state('fly')

        # 크기 결정
        try:
            img = self.animator._image_list_loaded[0]
            self.width = int(img.w * self.scale)
            self.height = int(img.h * self.scale)
        except Exception:
            self.width = 24
            self.height = 24

    def update(self, dt):
        if not self.active:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.animator:
            self.animator.update(dt)

        # 맵 경계에서 제거
        map_w = getattr(getattr(__import__('server'), 'tiled_map', None), 'map_width_px', 1280)
        map_h = getattr(getattr(__import__('server'), 'tiled_map', None), 'map_height_px', 736)
        if self.x < -100 or self.x > map_w + 100 or self.y < -100 or self.y > map_h + 100:
            self.active = False
            try:
                game_world.remove_object(self)
            except:
                pass
            return

        # 플레이어 충돌 검사
        if self.check_collision_with_player():
            try:
                server.player.take_damage(self.damage)
            except Exception:
                pass
            self.active = False
            try:
                game_world.remove_object(self)
            except:
                pass

    def check_collision_with_player(self):
        try:
            player = server.player
            pw = getattr(player, 'width', 40)
            ph = getattr(player, 'height', 64)

            left1 = self.x - self.width // 2
            bottom1 = self.y - self.height // 2
            right1 = self.x + self.width // 2
            top1 = self.y + self.height // 2

            left2 = player.x - pw // 2
            bottom2 = player.y - ph // 2
            right2 = player.x + pw // 2
            top2 = player.y + ph // 2

            if right1 < left2 or left1 > right2 or top1 < bottom2 or bottom1 > top2:
                return False
            return True
        except:
            return False

    def draw(self):
        cam = getattr(server, 'tiled_map', None)
        use_cam = bool(cam and getattr(cam, 'use_camera', False))
        cam_ox = cam.cam_offset_x if use_cam else 0
        cam_oy = cam.cam_offset_y if use_cam else 0
        screen_x = self.x + cam_ox
        screen_y = self.y + cam_oy
        if self.animator and hasattr(self.animator, '_image_list_loaded') and self.animator._image_list_loaded:
            self.animator.draw(screen_x, screen_y, self.scale)
        else:
            try:
                from pico2d import draw_rectangle
                draw_rectangle(screen_x - self.width/2, screen_y - self.height/2, screen_x + self.width/2, screen_y + self.height/2)
            except Exception:
                pass
