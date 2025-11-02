from pico2d import load_image
import time

class Monster:
    def __init__(self,name='monster',image_path='assets/monsters/monster.png', x=100, y=100, hp=10, speed=0, attack_power=0, attack_range=0):
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
        self.attack_power = attack_power
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
                target.take_damage(self.attack_power)
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



# 몬스터 만들기!!
class Green_MS(Monster):
    def __init__(self, x=200, y=140):
        super().__init__(name='green_ms',
                         image_path='MS/green_ms/idle.png',
                         x=x, y=y,
                         hp=80, speed=30, attack_power=12, attack_range=48)

        # 패트롤 설정
        self._patrol_origin_x = x
        self.patrol_width = 120
        self.dir = 1

        # 애니메이션 로드 (폴더 구조: MS/green_ms/idle.png 등)
        self.anim_images = {}
        self.anim_frames = {}
        # 프레임 수 고정 매핑
        frames_map = {
            'idle': 5,
            'attack': 11,
            'damaged': 2,
            'death': 5,
        }
        for state, fname in (('idle', 'idle.png'),
                             ('attack', 'attack.png'),
                             ('damaged', 'damaged.png'),
                             ('death', 'death.png')):
            path = f"MS/green_ms/{fname}"
            try:
                img = load_image(path)
                self.anim_images[state] = img
                # 프레임 수는 고정값 사용 (스프라이트 시트에 맞춤)
                self.anim_frames[state] = frames_map.get(state, 1)
            except Exception:
                self.anim_images[state] = None
                self.anim_frames[state] = 1

        # 애니메이션 상태
        self.state = 'idle'  # 'idle','attack','damaged','death'
        self.frame = 0
        self.frame_time_acc = 0.0

        # 각 상태별 프레임 시간
        self.frame_time = {
            'idle': 0.12,
            'attack': 0.07,
            'damaged': 0.08,
            'death': 0.10,
        }

        self._death_done = False

    def update(self, dt=0.01, frozen=False):
        # 정지(예: 인벤토리) 또는 이미 사망 후 처리
        if frozen:
            return
        if self.state == 'death' and self._death_done:
            return

        # 이동: 패트롤
        if self.patrol_width > 0 and self.speed != 0 and self.state != 'death':
            self.x += self.speed * self.dir * dt
            left = self._patrol_origin_x - self.patrol_width / 2
            right = self._patrol_origin_x + self.patrol_width / 2
            if self.x < left:
                self.x = left
                self.dir = 1
            elif self.x > right:
                self.x = right
                self.dir = -1

        # 애니메이션 진행
        img = self.anim_images.get(self.state)
        frames = self.anim_frames.get(self.state, 1)
        self.frame_time_acc += dt
        ft = self.frame_time.get(self.state, 0.1)
        while self.frame_time_acc >= ft:
            self.frame_time_acc -= ft
            self.frame += 1
            # death는 끝나면 고정, 나머지는 루프
            if self.state == 'death':
                if self.frame >= frames:
                    self.frame = frames - 1
                    self._death_done = True
                    self.alive = False
                    break
            else:
                self.frame %= frames

    def draw(self):
        img = self.anim_images.get(self.state)
        frames = self.anim_frames.get(self.state, 1)
        if img:
            fw = max(1, img.w // frames)
            fh = img.h
            idx = int(self.frame) % frames
            x_offset = idx * fw
            # pico2d image.clip_draw(x, y, w, h, cx, cy)
            img.clip_draw(x_offset, 0, fw, fh, self.x, self.y)
        else:
            # 이미지 없을 때는 기본 draw (사각형)
            left = self.x - self.w // 2
            bottom = self.y - self.h // 2
            right = self.x + self.w // 2
            top = self.y + self.h // 2
            try:
                from pico2d import draw_rectangle
                draw_rectangle(left, bottom, right, top)
            except Exception:
                pass

    def take_damage(self, damage):
        # 데미지 적용 및 피격 애니 시작
        if self.state == 'death':
            return
        super().take_damage(damage)
        if self.alive:
            self.state = 'damaged'
            self.frame = 0
            self.frame_time_acc = 0.0
        else:
            # 사망 상태로 진입
            self.state = 'death'
            self.frame = 0
            self.frame_time_acc = 0.0
            self._death_done = False

    def attack(self, target=None):
        # 공격 시 상태 전환 후 실제 데미지는 부모 로직 사용
        if self.state == 'death':
            return False
        fired = super().attack(target)
        if fired:
            self.state = 'attack'
            self.frame = 0
            self.frame_time_acc = 0.0
        return fired
