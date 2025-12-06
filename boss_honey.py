from pico2d import *
import game_world
import server

# 보스 뿌린 꿀
class Honey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = load_image('MS/boss/honey.png')
        self.width = 40
        self.height = 40
        self.collected = False
        self.scale = 0.1

    def update(self, dt):
        if self.collected:
            return

        # 플레이어와 충돌 체크
        if self.check_collection():
            self.collected = True
            try:
                game_world.remove_object(self)
            except:
                pass

    def check_collection(self):
        try:
            player = server.player
            dx = self.x - player.x
            dy = self.y - player.y
            distance = (dx * dx + dy * dy) ** 0.5

            # 수집 범위: 50픽셀
            if distance < 50:
                print(f"[HONEY] 꿀 수집! 위치: ({self.x}, {self.y})")
                return True
            return False
        except:
            return False

    def draw(self):
        if self.collected:
            return

        # 카메라 오프셋 적용
        try:
            cam = getattr(server, 'tiled_map', None)
            use_cam = bool(cam and getattr(cam, 'use_camera', False))
            cam_ox = cam.cam_offset_x if use_cam else 0
            cam_oy = cam.cam_offset_y if use_cam else 0
        except:
            cam_ox = 0
            cam_oy = 0

        screen_x = self.x + cam_ox
        screen_y = self.y + cam_oy

        dw = int(self.image.w * self.scale)
        dh = int(self.image.h * self.scale)
        self.image.draw(screen_x, screen_y, dw, dh)

    def get_bb(self):
        return (self.x - self.width // 2, self.y - self.height // 2,
                self.x + self.width // 2, self.y + self.height // 2)

