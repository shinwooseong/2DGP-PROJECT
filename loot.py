from pico2d import load_image, draw_rectangle
import math
import random

class Loot:
    # LOOT 이미지 경로 (4개 이미지 중 랜덤)
    LOOT_IMAGES = [
        'LOOT/loot1.png',
        'LOOT/loot2.png',
        'LOOT/loot3.png',
        'LOOT/loot4.png',
    ]

    def __init__(self, x, y, item_type, quantity=1):
        """
        Args:
            x, y: 전리품 위치
            item_type: 'coin', 'potion', 'key' 등
            quantity: 개수
        """
        self.x = x
        self.y = y
        self.item_type = item_type
        self.quantity = quantity
        self.collected = False
        self.collection_time = 0.0
        self.collection_duration = 0.3  # 수집 애니메이션 시간

        # 수집 딜레이 (생성 후 1초는 수집 불가)
        self.spawn_time = 0.0
        self.collection_delay = 1.0  # 1초 딜레이

        # 이미지 로드 - LOOT 폴더에서 랜덤 선택
        self.image = None
        self.sprite_w = 32
        self.sprite_h = 32

        image_path = random.choice(self.LOOT_IMAGES)
        try:
            self.image = load_image(image_path)
            self.sprite_w = self.image.w
            self.sprite_h = self.image.h
            print(f"✓ 전리품 이미지 로드 성공: {image_path} ({self.sprite_w}x{self.sprite_h})")
        except Exception as e:
            print(f"✗ 전리품 이미지 로드 오류 ({image_path}): {e}")

        # 충돌 범위 (자동 수집 거리)
        self.collect_range = 80  # 플레이어로부터 이 거리 안에서 자동 수집

        print(f"[LOOT] 생성: {item_type}x{quantity} at ({x}, {y})")

    def update(self, dt):
        # 생성 시간 증가
        self.spawn_time += dt

        if self.collected:
            # 수집 중인 경우 애니메이션
            self.collection_time += dt
            if self.collection_time >= self.collection_duration:
                # 수집 완료 - 이 객체는 제거됨
                return True
        return False  # 아직 제거되지 않음

    def draw(self):
        if self.image:

            scale = 0.8
            draw_w = int(self.sprite_w * scale)
            draw_h = int(self.sprite_h * scale)
            self.image.draw(self.x, self.y, draw_w, draw_h)


    def check_collection(self, player_x, player_y):
        # 플레이어 위치와 비교하여 수집 가능한지 확인
        if self.collected:
            return False

        # 1초 딜레이 체크
        if self.spawn_time < self.collection_delay:
            return False

        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= self.collect_range:
            self.collected = True
            self.collection_time = 0.0
            return True
        return False

    def get_item_info(self):
        # 전리품 아이템 정보 반환
        return {
            'type': self.item_type,
            'quantity': self.quantity,
        }
