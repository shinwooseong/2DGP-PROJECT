from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_u

SCREEN_W, SCREEN_H = 1000, 1000


class Inventory:
    def __init__(self):
        self.is_open = False
        self.backpack_image = None
        self.load_backpack_image()

    def load_backpack_image(self):
        # 배낭 이미지 로드
        try:
            self.backpack_image = load_image('backpack_in.png')
        except Exception as e:
            print(f"배낭 이미지 로드 오류: {e}")
            self.backpack_image = None

    def toggle(self):
        # 배낭 열고 닫기
        self.is_open = not self.is_open

    def handle_event(self, event):
        # 이벤트 처리
        if event.type == SDL_KEYDOWN and event.key == SDLK_u:
            self.toggle()

    def draw(self):
        # 배낭 UI 그리기
        if self.is_open and self.backpack_image:
            center_x = SCREEN_W // 2
            center_y = SCREEN_H // 2
            self.backpack_image.draw(center_x, center_y)

