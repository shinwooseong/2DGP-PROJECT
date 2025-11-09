# UI.py
from pico2d import load_font, load_image, draw_rectangle
import main_chracter


class UI:
    """Simple HUD: left-top coin + money, HP bar with decor, right-top item icons.
    Designed to be readable and easy to tweak.
    """

    def __init__(self, font_path='UI/use_font/MaruBuri-Regular.ttf', font_size=20):
        # 1. Font
        self.font = None
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
                print("경고: UI 폰트를 로드할 수 없습니다.")

        # 2. Player reference
        self.player = None
        self.money = 0

        # 3. Layout Configuration (모든 "매직 넘버"를 여기로)
        self.margin = 8
        self.icon_scale = 1.12

        # (좌측 상단: 코인/HP)
        self.coin_offset_x = 24  # 코인 아이콘 중심 X (좌측 여백 기준)
        self.coin_offset_y = 24  # 코인 아이콘 중심 Y (상단 여백 기준)
        self.hp_coin_spacing = 60  # 코인 아이콘과 HP 바 사이의 거리
        self.money_text_x_offset = 8  # 코인 아이콘 우측 텍스트 오프셋
        self.money_text_y_offset = 8  # 코인 아이콘 하단 텍스트 오프셋
        self.hp_bar_width = 180
        self.hp_bar_height = 35
        self.hp_text_x_offset = 8  # HP 바 우측 텍스트 오프셋

        # (우측 상단: 아이콘)
        self.icon_anchor_y = 24  # 아이콘 중심 Y (상단 여백 기준)
        self.icon_spacing = 56  # 아이콘들 사이의 X 간격
        self.icon_text_x_offset = 40  # 아이콘 위 텍스트 X 오프셋 ('U')
        self.icon_text_y_offset = 32  # 아이콘 위 텍스트 Y 오프셋 ('U')

        # 4. Images
        def _load(path, fallback=None):
            try:
                return load_image(path)
            except Exception:
                try:
                    return load_image(fallback) if fallback else None
                except Exception:
                    return None

        self.coin_img = _load('UI/have_money.png')
        self.potion_img = _load('Maid Run.png')
        self.backpack_img = _load('UI/backpack_in.png')
        self.transform_img = _load('Maid Idle.png')

        # hp 변화에 따른 변수 추가
        self.hp_part_left = _load('UI/hp_image/1.png')
        self.hp_part_mid = _load('UI/hp_image/2.png')
        self.hp_part_right = _load('UI/hp_image/3.png')
        self.hp_extra_part_left = _load('UI/hp_image/4.png')
        self.hp_extra_part_mid = _load('UI/hp_image/5.png')
        self.hp_extra_part_right = _load('UI/hp_image/6.png')
        self.hp_0_part_left = _load('UI/hp_image/7.png')
        self.hp_0_part_mid = _load('UI/hp_image/8.png')
        self.hp_0_part_right = _load('UI/hp_image/9.png')
        self.hp_decor = _load('UI/hp_image/13.png')

    def set_player(self, player):
        self.player = player

    def set_money(self, amount):
        try:
            self.money = int(amount)
        except Exception:
            pass

    def add_money(self, delta):
        try:
            self.money += int(delta)
        except Exception:
            pass

    def update(self, dt):
        if self.player is not None:
            try:
                self.money = getattr(self.player, 'money', self.money)
            except Exception:
                pass

    def _icon_size(self):
        base_w = getattr(main_chracter, 'SPRITE_W', 96)
        base_h = getattr(main_chracter, 'SPRITE_H', 80)
        return int(base_w * self.icon_scale), int(base_h * self.icon_scale)

    def _draw_hp_bar(self, cx, cy):
        bar_w = self.hp_bar_width
        draw_h = int(self.hp_bar_height)

        if self.player is not None:
            hp = max(0, getattr(self.player, 'health', 0))
            max_hp = max(1, getattr(self.player, 'max_health', getattr(self.player, 'health', 100)))
        else:
            hp, max_hp = 100, 100
        ratio = float(hp) / float(max_hp) if max_hp > 0 else 0.0

        left_edge = float(cx) - float(bar_w) / 2.0

        if self.hp_decor:
            orig_w = float(getattr(self.hp_decor, 'w', draw_h))
            orig_h = float(getattr(self.hp_decor, 'h', draw_h)) or float(draw_h)
            decor_h = draw_h
            decor_w = int(orig_w * (decor_h / orig_h))
            decor_center_x = int(left_edge - (decor_w / 2.0))
            self.hp_decor.draw(decor_center_x, cy, decor_w, decor_h)


        if self.hp_part_left and self.hp_part_mid and self.hp_part_right:
            lw = getattr(self.hp_part_left, 'w', draw_h)
            rw = getattr(self.hp_part_right, 'w', draw_h)
            mid_total = max(0, bar_w - lw - rw)


            self.hp_part_left.draw(int(left_edge + lw / 2), cy, lw, draw_h)
            if mid_total > 0:
                self.hp_part_mid.draw(int(left_edge + lw + mid_total / 2), cy, mid_total, draw_h)
            self.hp_part_right.draw(int(left_edge + lw + mid_total + rw / 2), cy, rw, draw_h)


            filled_mid = int(mid_total * ratio)
            if filled_mid > 0:
                self.hp_part_mid.draw(int(left_edge + lw + filled_mid / 2), cy, filled_mid, draw_h)

        else:
            # Fallback: simple rectangle
            filled_w = int(bar_w * ratio)
            if filled_w > 0:
                draw_rectangle(int(cx - bar_w / 2), int(cy - draw_h / 2), int(cx - bar_w / 2 + filled_w),
                               int(cy + draw_h / 2))
            draw_rectangle(int(cx - bar_w / 2), int(cy - draw_h / 2), int(cx + bar_w / 2), int(cy + draw_h / 2))

        # Numeric HP text
        if self.font:
            text_x = int(cx + bar_w / 2) + self.hp_text_x_offset
            text_y = int(cy - draw_h / 4)
            self.font.draw(text_x, text_y, f"{hp}/{max_hp}", (255, 255, 255))

    def _draw_icons_right(self, screen_w, screen_h):
        right_x = screen_w - self.margin
        top_y = screen_h - self.margin - self.icon_anchor_y
        spacing = self.icon_spacing

        if self.transform_img:
            self.transform_img.draw(right_x - 0 * spacing - 24, top_y)
        if self.potion_img:
            self.potion_img.draw(right_x - 1 * spacing - 24, top_y)
        if self.backpack_img:
            self.backpack_img.draw(right_x - 2 * spacing - 24, top_y)

        if self.font:
            text_y = top_y - self.icon_text_y_offset
            self.font.draw(right_x - 2 * spacing - self.icon_text_x_offset, text_y, 'U', (255, 255, 255))
            self.font.draw(right_x - 0 * spacing - self.icon_text_x_offset, text_y, 'X', (255, 255, 255))

    def draw(self):
        SCREEN_W = main_chracter.SCREEN_W
        SCREEN_H = main_chracter.SCREEN_H

        # 1. Calculate positions based on layout config
        coin_x = self.margin + self.coin_offset_x
        coin_y = SCREEN_H - self.margin - self.coin_offset_y
        icon_w, icon_h = self._icon_size()

        hp_cx = coin_x + icon_w + self.hp_coin_spacing
        hp_cy = int(coin_y)

        # 2. Draw HP bar (background)
        self._draw_hp_bar(hp_cx, hp_cy)

        # 3. Draw coin and money (foreground)
        if self.coin_img:
            self.coin_img.draw(coin_x, coin_y, icon_w, icon_h)

        if self.font:
            text_x = coin_x + icon_w // 2 + self.money_text_x_offset
            text_y = coin_y - icon_h // 2 - self.money_text_y_offset
            self.font.draw(text_x, text_y, f"{self.money}", (255, 255, 255))

        # 4. Draw Right-top icons
        self._draw_icons_right(SCREEN_W, SCREEN_H)