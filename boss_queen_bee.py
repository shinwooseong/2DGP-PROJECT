from Monster import Monster, Animator, Combat, SimpleAI
import random
import game_framework
import game_world
from boss_bees import BeeSting
import server
import os

class QueenBee_Boss(Monster):
    def __init__(self, x=640, y=368):
        super().__init__(name='QueenBee_Boss', x=x, y=y, hp=500, speed=0)

        # Head 폴더의 queen_bee_spit 이미지들 (idle 상태)
        idle_image_list = [
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

        # spray 애니메이션 이미지 수집
        spray_image_list = []
        base = 'MS/boss/spray_animation'
        for i in range(1, 50):
            p = f"{base}/queen_bee_spell_cast_{i:04d}.png"
            if os.path.exists(p):
                spray_image_list.append(p)

        # idle 애니메이터
        frames_map = {'idle': len(idle_image_list)}
        frame_time = {'idle': 0.08}
        self.animator = Animator('', frames_map, frame_time, image_list=idle_image_list)

        # spray 애니메이터 (별도 생성)
        if spray_image_list:
            spray_frames_map = {'spray': len(spray_image_list)}
            spray_frame_time = {'spray': 0.1}  # 더 빠른 애니메이션
            self.spray_animator = Animator('', spray_frames_map, spray_frame_time, image_list=spray_image_list)
            print(f"[BOSS] Spray 애니메이션 로드 완료: {len(spray_image_list)}프레임")
        else:
            self.spray_animator = None
            print("[BOSS WARNING] Spray 애니메이션을 찾을 수 없습니다!")

        self.combat = Combat(attack_power=30, attack_range=150, cooldown=2.0, attack_frames=1, hit_frame=0)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=0, sight_range=500)
        self.state = self.animator.state
        self.scale = 2.0

        # 공격 패턴 관련 변수
        self.attack_cooldown = 0
        self.attack_interval = 2.0  # 2초마다 공격
        self.spray_cooldown = 0
        self.spray_interval = 30.0  # 10초마다 spray 공격
        self.projectiles = []

        # 상태 관리
        self.is_spraying = False  # spray 애니메이션 중인지 여부
        self.spray_y_position = 0  # spray 애니메이션 y 위치

    def update(self, dt=0.01, frozen=False, player=None):
        if frozen or not self.alive:
            return

        # spray 상태일 때는 spray 애니메이터만 업데이트
        if self.is_spraying:
            if self.spray_animator:
                self.spray_animator.update(dt)
                # spray 애니메이션이 끝나면 idle로 복귀
                if self.spray_animator.is_animation_finished():
                    self.is_spraying = False
                    self.animator.set_state('idle')
                    # spray 애니메이터 리셋 (다음 spray를 위해)
                    self.spray_animator.frame = 0
                    self.spray_animator.acc = 0.0
                    self.spray_animator._animation_done = False
                    print("[BOSS] Spray 애니메이션 완료 - idle로 복귀")
            return

        # 일반 상태일 때는 기본 애니메이션 업데이트
        self.animator.update(dt)

        # 공격 쿨타임 업데이트
        self.attack_cooldown -= dt
        self.spray_cooldown -= dt

        # spray 공격 (우선순위 높음)
        if self.spray_cooldown <= 0:
            self.spray_honey()
            self.spray_cooldown = self.spray_interval
        # 일반 벌침 공격
        elif self.attack_cooldown <= 0:
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


    # 꿀 뿌리기 -> 꿀을 다 먹어야만 보스에게 공격 가능
    def spray_honey(self):

        self.is_spraying = True
        self.spray_animator.set_state('spray')

        # spray 애니메이션 위치 (화면 상단 중앙)
        map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)
        map_h = getattr(getattr(server, 'tiled_map', None), 'map_height_px', 736)
        self.spray_y_position = map_h - 100  # 상단에서 100픽셀 아래

        print("[BOSS] 꿀 뿌리기 시작!")
        # 꿀 뿌리기 구현

    def draw(self):
        # 카메라 보정
        try:
            import server
            cam = getattr(server, 'tiled_map', None)
            use_cam = bool(cam and getattr(cam, 'use_camera', False))
            cam_ox = cam.cam_offset_x if use_cam else 0
            cam_oy = cam.cam_offset_y if use_cam else 0
        except Exception:
            cam_ox = 0
            cam_oy = 0

        # spray 상태일 때는 화면 상단에 spray 애니메이션 그리기
        if self.is_spraying and self.spray_animator:
            map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)
            spray_x = map_w // 2  # 화면 중앙
            spray_y = self.spray_y_position
            self.spray_animator.draw(spray_x + cam_ox, spray_y + cam_oy, self.scale * 1.5)  # 크기 줄임
        else:
            # 일반 상태일 때는 중앙에 idle 애니메이션 그리기
            if not self.alive and self.animator._death_done:
                return
            self.animator.draw(self.x + cam_ox, self.y + cam_oy, self.scale)
