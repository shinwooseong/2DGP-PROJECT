from pico2d import load_image
import time
import math

class Monster:
    def __init__(self,name='monster',image_path='assets/monsters/monster.png', x=100, y=100, hp=10, speed=0, attack=0, attack_range=0):
        self.name = name
        self.image = image_path
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
        self.image.draw(self.x, self.y)

    def update(self,dt):
        # 몬스터의 상태 업데이트 로직 추가
        if not self.alive:
            return
        self.x += self.speed * self.dir * dt

    # target = 주인공
    def attack(self, target = None):
        # 몬스터 공격 로직 추가:
        now = time.time()
        if now - self.last_attack_time < self.attack_cooldown:
            return False
        self.last_attack_time = now

        if target is None:
            return True

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

    def move(self,dx, dy):
        self.x += dx
        self.y += dy


    def range_of_attack(self, target):
        dx = target.x - self.x
        dy = target.y - self.y
        return dx * dx + dy * dy <= self.attack_range * self.attack_range

