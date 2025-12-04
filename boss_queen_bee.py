from Monster import Monster, Animator, Combat, SimpleAI
import random
import game_framework
import game_world
from boss_bees import BeeSting
import server

class QueenBee_Boss(Monster):
    def __init__(self, x=640, y=368):
        super().__init__(name='QueenBee_Boss', x=x, y=y, hp=500, speed=0)
        # Head 폴더의 queen_bee_spit 이미지들을 사용 (35개 프레임)
        image_list = [
            'MS/boss/Head/queen_bee_spit_0001a.png',
            'MS/boss/Head/queen_bee_spit_0001b.png',
            'MS/boss/Head/queen_bee_spit_0001c.png',
            'MS/boss/Head/queen_bee_spit_0002.png',
            'MS/boss/Head/queen_bee_spit_0003.png',
            'MS/boss/Head/queen_bee_spit_0004.png',
            'MS/boss/Head/queen_bee_spit_0005.png',
            'MS/boss/Head/queen_bee_spit_0006.png',
            'MS/boss/Head/queen_bee_spit_0007.png',
            'MS/boss/Head/queen_bee_spit_0008.png',
            'MS/boss/Head/queen_bee_spit_0009.png',
            'MS/boss/Head/queen_bee_spit_0010.png',
            'MS/boss/Head/queen_bee_spit_0011.png',
            'MS/boss/Head/queen_bee_spit_0012.png',
            'MS/boss/Head/queen_bee_spit_0013.png',
            'MS/boss/Head/queen_bee_spit_0014.png',
            'MS/boss/Head/queen_bee_spit_0015.png',
            'MS/boss/Head/queen_bee_spit_0016.png',
            'MS/boss/Head/queen_bee_spit_0017.png',
            'MS/boss/Head/queen_bee_spit_0018.png',
            'MS/boss/Head/queen_bee_spit_0019.png',
            'MS/boss/Head/queen_bee_spit_0020.png',
            'MS/boss/Head/queen_bee_spit_0021.png',
            'MS/boss/Head/queen_bee_spit_0022.png',
            'MS/boss/Head/queen_bee_spit_0023.png',
            'MS/boss/Head/queen_bee_spit_0024.png',
            'MS/boss/Head/queen_bee_spit_0025.png',
            'MS/boss/Head/queen_bee_spit_0026.png',
            'MS/boss/Head/queen_bee_spit_0027.png',
            'MS/boss/Head/queen_bee_spit_0028.png',
            'MS/boss/Head/queen_bee_spit_0029.png',
            'MS/boss/Head/queen_bee_spit_0030.png',
            'MS/boss/Head/queen_bee_spit_0031.png',
            'MS/boss/Head/queen_bee_spit_0032.png',
            'MS/boss/Head/queen_bee_spit_0033.png',
        ]
        frames_map = {'idle': 35}  # 프레임 수는 image_list 로딩 시 자동 설정됨
        frame_time = {'idle': 0.08}
        self.animator = Animator('', frames_map, frame_time, image_list=image_list)
        self.combat = Combat(attack_power=30, attack_range=150, cooldown=2.0, attack_frames=1, hit_frame=0)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=0, sight_range=500)
        self.state = self.animator.state
        self.scale = 2.0

        # 공격 패턴 관련 변수
        self.attack_cooldown = 0
        self.attack_interval = 2.0  # 2초마다 공격
        self.projectiles = []

    def update(self, dt=0.01, frozen=False, player=None):
        # 기본 애니메이션 업데이트 (부모 클래스 호출)
        super().update(dt, frozen, player)

        if frozen or not self.alive:
            return

        # 공격 쿨타임 업데이트
        self.attack_cooldown -= dt

        # 공격 쿨타임이 끝나면 벌침 발사
        if self.attack_cooldown <= 0:
            self.attack_bees()
            self.attack_cooldown = self.attack_interval

    def attack_bees(self):

        # 맵 높이 기준으로 랜덤 y 좌표 생성
        map_h = getattr(getattr(server, 'tiled_map', None), 'map_height_px', 736)
        map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)

        # 화면 중앙 ~ 상단 영역에서 발사
        min_y = map_h // 3
        max_y = map_h - 10

        # 왼쪽에서 오른쪽으로
        left_sting = BeeSting(x=-50, y=random.randint(min_y, max_y), direction=1, speed=550)
        game_world.add_object(left_sting, 1)

        # 오른쪽에서 왼쪽으로
        right_sting = BeeSting(x=map_w + 50, y=random.randint(min_y, max_y), direction=-1, speed=350)
        game_world.add_object(right_sting, 1)

