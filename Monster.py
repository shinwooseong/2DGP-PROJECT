from pico2d import load_image

class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = load_image('monster.png')  # 몬스터 이미지 로드

    def draw(self):
        self.image.draw(self.x, self.y)

    def update(self):
        # 몬스터의 상태 업데이트 로직 추가
        pass

