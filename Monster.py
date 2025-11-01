from pico2d import load_image
import time
import math

class Monster:
    def __init__(self,name='monster',image_path='assets/monsters/monster.png', x=100, y=100, hp=10, speed=0, attack=0, attack_range=0):
        self.name = name
        self.image_path = image_path

        # 안전하게 이미지 로드하기!
        try:
            self.image = load_image(self.image_path)
            self.w = getattr(self.image, 'w', 32)
            self.h = getattr(self.image, 'h', 32)
        except Exception:
            self.image = None
            self.w = 32
            self.h = 32

        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.attack = attack
        self.attack_range = attack_range
        self.alive = True
        self.dir = 1

        # 공격 시간
        self.attack_cooldown = 0.5
        self.last_attack_time = 0.0


    def draw(self):
        if self.image:
            self.image.draw(self.x, self.y)

    def update(self):
        # 몬스터의 상태 업데이트 로직 추가
        if not self.alive:
            return

        dx = self.speed * self.dir * 0.1
        self.move(dx, 0)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    # target = 주인공
    def attack(self, target = None):
        # 몬스터 공격 로직 추가:
        now = time.time()
        if now - self.last_attack_time < self.attack_cooldown:
            return False
        self.last_attack_time = now

        if target is None:
            return True

        # 범위 검사 후 대미지
        if hasattr(target, 'x') and hasattr(target, 'y') and self.range_of_attack(target):
            if hasattr(target, 'take_damage'):
                target.take_damage(self.attack)
            return True
        return False

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False


    def range_of_attack(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        return dx * dx + dy * dy <= self.attack_range * self.attack_range

