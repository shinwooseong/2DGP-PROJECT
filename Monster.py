from pico2d import load_image

class Monster:
    def __init__(self,name='monster',image_path='assets/monsters/monster.png', x=100, y=100, hp=10, speed=0, attack=0):
        self.name = name
        self.image_path = image_path
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.attack = attack
        self.alive = True

    def draw(self):
        self.image.draw(self.x, self.y)

    def update(self):
        # 몬스터의 상태 업데이트 로직 추가
        pass

    def attack(self)
        # 몬스터 공격 로직 추가:
        pass

    def move(self):
        # 몬스터 이동 로직 추가
        pass

    def range_of_attack(self, target):
        # 공격 범위 내에 있는지 확인하는 로직 추가
        pass

