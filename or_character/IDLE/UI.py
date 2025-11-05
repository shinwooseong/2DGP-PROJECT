from pico2d import load_font


SCREEN_W, SCREEN_H = 1000, 1000

# 간단한 UI: 우측 상단에 돈만 표시하는 클래스
class UI:
    def __init__(self, font_path='UI/use_font/MaruBuri-Regular.ttf', font_size=45):
        try:
            if font_path:
                self.font = load_font(font_path, font_size)
            else:
                self.font = load_font(None, font_size)
        except Exception:
            try:
                self.font = load_font(None, font_size)
            except Exception:
                self.font = None

        self.money = 10000
        self.margin = 20
        self.color = (0, 0, 0)

    def update(self, dt):
        pass

    def load_UI_image(self):
        pass

    def handle_event(self, event):
        pass

    def set_money(self, amount):
        try:
            self.money = int(amount)
        except Exception:
            self.money = 0

    def add_money(self, delta):
        try:
            self.money += int(delta)
        except Exception:
            pass

    def draw(self):
        # 우측 상단에 돈 표시 (우측 정렬)
        if not self.font:
            return
        text = f"${self.money}"
        try:
            w = self.font.get_width(text)
        except Exception:
            w = len(text) * 10 +50
        x = SCREEN_W - self.margin - w
        y = SCREEN_H - self.margin - 10  # baseline 위치 조정
        try:
            self.font.draw(x, y, text, self.color)
        except Exception:
            # 실패해도 무시
            pass
