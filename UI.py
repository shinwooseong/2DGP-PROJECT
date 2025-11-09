from pico2d import load_font, load_image, draw_rectangle


# 간단한 HUD 클래스: 좌측 상단에 코인 이미지 + 금액, 옆에 HP바, 우측 상단에 아이템 아이콘들
class UI:
    def __init__(self, font_path='UI/use_font/MaruBuri-Regular.ttf', font_size=20):
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

        # 플레이어 참조는 play_mode에서 set_player로 전달받음
        self.player = None

        # 돈
        self.money = 0

        # 이미지 플래이스홀더들
        try:
            # 변경: 좌측 상단 코인 이미지는 UI 폴더의 have_money.png 사용
            self.coin_img = load_image('UI/have_money.png')
        except Exception:
            try:
                self.coin_img = load_image('Maid Idle.png')
            except Exception:
                self.coin_img = None
        try:
            self.potion_img = load_image('Maid Run.png')
        except Exception:
            self.potion_img = None
        try:
            self.backpack_img = load_image('UI/backpack_in.png')
        except Exception:
            self.backpack_img = None
        try:
            self.transform_img = load_image('Maid Idle.png')
        except Exception:
            self.transform_img = None

        # 레이아웃 관련
        self.margin = 16
        self.hp_bar_width = 200
        self.hp_bar_height = 36
        # HP 바 이미지를 부분별로 로드
        try:
            self.hp_part_left = load_image('UI/hp_image/1.png')
        except Exception:
            self.hp_part_left = None
        try:
            self.hp_part_mid = load_image('UI/hp_image/2.png')
        except Exception:
            self.hp_part_mid = None
        try:
            self.hp_part_right = load_image('UI/hp_image/3.png')
        except Exception:
            self.hp_part_right = None

    def set_player(self, player):
        self.player = player

    def update(self, dt):
        # 플레이어의 돈을 동기화할 수도 있음
        if self.player is not None:
            self.money = getattr(self.player, 'money', getattr(self.player, 'attack', 0))

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
        # 캔버스 크기는 main_chracter 모듈에서 가져옵니다.
        try:
            import main_chracter
            SCREEN_W = main_chracter.SCREEN_W
            SCREEN_H = main_chracter.SCREEN_H
        except Exception:
            SCREEN_W, SCREEN_H = 1280, 720

        # 좌측 상단 기본 위치
        left = self.margin
        top = SCREEN_H - self.margin

        # 코인 이미지 그리기 (아이콘) - 플레이어보다 살짝 크게 표시
        coin_x = left + 24
        coin_y = top - 24
        # 플레이어 스프라이트 크기를 참고해 아이콘 크기 결정
        try:
            import main_chracter
            base_w = getattr(main_chracter, 'SPRITE_W', 96)
            base_h = getattr(main_chracter, 'SPRITE_H', 80)
        except Exception:
            base_w, base_h = 96, 80
        icon_scale = 1.12  # 플레이어보다 12% 크게
        icon_w = int(base_w * icon_scale)
        icon_h = int(base_h * icon_scale)
        if self.coin_img:
            try:
                self.coin_img.draw(coin_x, coin_y, icon_w, icon_h)
            except Exception:
                try:
                    self.coin_img.draw(coin_x, coin_y)
                except Exception:
                    pass

        # 금액 텍스트: 코인 이미지 아래 (아이콘 크기에 맞춰 위치 조정)
        amount_text = f"{self.money}"
        if self.font:
            try:
                # 텍스트를 아이콘 오른쪽 또는 아래에 표시하도록 위치 계산
                text_x = coin_x + icon_w // 2 + 8
                text_y = coin_y - icon_h // 2 - 8
                self.font.draw(text_x, text_y, amount_text, (255, 255, 255))
            except Exception:
                try:
                    self.font.draw(coin_x - 8, coin_y - 40, amount_text, (255, 255, 255))
                except Exception:
                    pass

        # HP 바: 코인 오른쪽에 배치
        # 코인 아이콘 오른쪽에서 여유를 두고 시작
        hp_x = coin_x + icon_w + 40
        hp_y = coin_y
        bar_w = self.hp_bar_width
        bar_h = self.hp_bar_height
        # 배경과 채워진 부분을 그림
        try:
            if self.player is not None:
                hp = max(0, getattr(self.player, 'health', 0))
                max_hp = max(1, getattr(self.player, 'max_health', getattr(self.player, 'health', 100)))
            else:
                hp = 100
                max_hp = 100
            ratio = float(hp) / float(max_hp) if max_hp > 0 else 0.0
            filled_w = int(bar_w * ratio)

            # Compose HP bar from three images (left, mid, right) if available
            if self.hp_part_left is not None and self.hp_part_mid is not None and self.hp_part_right is not None:
                try:
                    lw = getattr(self.hp_part_left, 'w', int(bar_h))
                    lh = getattr(self.hp_part_left, 'h', int(bar_h))
                    rw = getattr(self.hp_part_right, 'w', int(bar_h))
                    rh = getattr(self.hp_part_right, 'h', int(bar_h))
                    # mid area width
                    mid_total = max(0, bar_w - lw - rw)
                    # draw background (left, mid full, right)
                    self.hp_part_left.draw(hp_x - bar_w//2 + lw//2, hp_y, lw, bar_h)
                    if mid_total > 0:
                        try:
                            self.hp_part_mid.draw(hp_x - bar_w//2 + lw + mid_total//2, hp_y, mid_total, bar_h)
                        except Exception:
                            self.hp_part_mid.draw(hp_x, hp_y)
                    self.hp_part_right.draw(hp_x + bar_w//2 - rw//2, hp_y, rw, bar_h)

                    # draw filled portion based on ratio: fill the mid area
                    filled_mid = int(mid_total * ratio)
                    if filled_mid > 0:
                        try:
                            # draw filled mid using same mid image scaled to filled_mid width
                            self.hp_part_mid.draw(hp_x - bar_w//2 + lw + filled_mid//2, hp_y, filled_mid, bar_h)
                        except Exception:
                            pass
                except Exception:
                    try:
                        draw_rectangle(hp_x - bar_w//2, hp_y - bar_h//2, hp_x + bar_w//2, hp_y + bar_h//2)
                    except Exception:
                        pass
            else:
                try:
                    # draw filled rectangle then outline
                    filled_w = int(bar_w * ratio)
                    if filled_w > 0:
                        draw_rectangle(hp_x - bar_w//2, hp_y - bar_h//2, hp_x - bar_w//2 + filled_w, hp_y + bar_h//2)
                    draw_rectangle(hp_x - bar_w//2, hp_y - bar_h//2, hp_x + bar_w//2, hp_y + bar_h//2)
                except Exception:
                    pass

            # 숫자 HP 표시 (항상 보이도록)
            if self.font:
                try:
                    self.font.draw(hp_x + bar_w//2 + 8, hp_y - bar_h//4, f"{hp}/{max_hp}", (255,255,255))
                except Exception:
                    pass
        except Exception:
            pass

        # 우측상단: 물약, 배낭(U), 변신(X) 아이콘
        right_x = SCREEN_W - self.margin
        top_y = SCREEN_H - self.margin - 24
        # 그리기 순서: transform, potion, backpack (오른쪽에서 왼쪽)
        spacing = 56
        try:
            if self.transform_img:
                self.transform_img.draw(right_x - 0 * spacing - 24, top_y)
        except Exception:
            pass
        try:
            if self.potion_img:
                self.potion_img.draw(right_x - 1 * spacing - 24, top_y)
        except Exception:
            pass
        try:
            if self.backpack_img:
                self.backpack_img.draw(right_x - 2 * spacing - 24, top_y)
        except Exception:
            pass

        # 아이콘 위에 키 텍스트(간단 표시)
        if self.font:
            try:
                # backpack -> U, transform -> X
                self.font.draw(right_x - 2 * spacing - 40, top_y - 32, 'U', (255,255,255))
                self.font.draw(right_x - 0 * spacing - 40, top_y - 32, 'X', (255,255,255))
            except Exception:
                pass
