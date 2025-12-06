from Monster import Monster, Animator, Combat, SimpleAI
import random
import game_framework
import game_world
from boss_bees import BeeSting
from boss_honey import Honey
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

        # stun 애니메이션 이미지 수집
        stun_image_list = []
        stun_base = 'MS/boss/Head_stun'
        for i in range(1, 10):
            p = f"{stun_base}/queen_bee_spit_body_{i:04d}.png"
            if os.path.exists(p):
                stun_image_list.append(p)

        # idle 애니메이터
        frames_map = {'idle': len(idle_image_list)}
        frame_time = {'idle': 0.08}
        self.animator = Animator('', frames_map, frame_time, image_list=idle_image_list)

        # spray 애니메이터 (별도 생성)
        if spray_image_list:
            spray_frames_map = {'spray': len(spray_image_list)}
            spray_frame_time = {'spray': 0.06}
            self.spray_animator = Animator('', spray_frames_map, spray_frame_time, image_list=spray_image_list)
            print(f"[BOSS] Spray 애니메이션 로드 완료: {len(spray_image_list)}프레임")
        else:
            self.spray_animator = None
            print("[BOSS WARNING] Spray 애니메이션을 찾을 수 없습니다!")

        # stun 애니메이터 (별도 생성)
        if stun_image_list:
            stun_frames_map = {'stun': len(stun_image_list)}
            stun_frame_time = {'stun': 0.15}
            self.stun_animator = Animator('', stun_frames_map, stun_frame_time, image_list=stun_image_list)
            print(f"[BOSS] Stun 애니메이션 로드 완료: {len(stun_image_list)}프레임")
        else:
            self.stun_animator = None
            print("[BOSS WARNING] Stun 애니메이션을 찾을 수 없습니다!")

        self.combat = Combat(attack_power=30, attack_range=150, cooldown=2.0, attack_frames=1, hit_frame=0)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=0, sight_range=500)
        self.state = self.animator.state
        self.scale = 2.0

        # 공격 패턴 관련 변수
        self.attack_cooldown = 0
        self.attack_interval = 2.0  # 2초마다 공격
        self.spray_cooldown = 0
        self.spray_interval = 10.0  # 10초마다 spray 공격
        self.projectiles = []

        # 상태 관리
        self.is_spraying = False  # spray 애니메이션 중인지 여부
        self.spray_y_position = 0  # spray 애니메이션 y 위치

        # 스턴 상태 관련
        self.is_stunned = False  # 스턴 상태 여부
        self.stun_timer = 0.0  # 스턴 지속 시간
        self.stun_duration = 15.0  # 5초간 스턴
        self.is_invincible = True  # 무적 상태 (기본적으로 무적)
        self.honey_objects = []  # 생성된 꿀 오브젝트들

    def update(self, dt=0.01, frozen=False, player=None):
        if frozen or not self.alive:
            return

        # 스턴 상태일 때
        if self.is_stunned:
            if self.stun_animator:
                self.stun_animator.update(dt)
            self.stun_timer -= dt

            # 스턴 시간 종료
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.is_invincible = True  # 다시 무적 상태
                self.animator.set_state('idle')
                print("[BOSS] 스턴 종료 - 다시 무적 상태")
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

                    # 꿀 생성!
                    self.spawn_honey()
                    print("[BOSS] Spray 애니메이션 완료 - 꿀 생성!")
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
        min_y = map_h // 4
        max_y = map_h - 10

        # 왼쪽에서 오른쪽으로 3개 세트 발사
        for i in range(3):
            speed = random.randint(400, 600)
            left_sting = BeeSting(x=-50, y=random.randint(min_y, max_y), direction=1, speed=speed)
            game_world.add_object(left_sting, 1)

        # 오른쪽에서 왼쪽으로 3개 세트 발사
        for i in range(3):
            speed = random.randint(300, 500)
            right_sting = BeeSting(x=map_w + 50, y=random.randint(min_y, max_y), direction=-1, speed=speed)
            game_world.add_object(right_sting, 1)


    def spray_honey(self):
        """꿀 뿌리기 공격 - spray 애니메이션 실행"""
        if not self.spray_animator:
            print("[BOSS] Spray 애니메이터가 없습니다!")
            return

        self.is_spraying = True
        self.spray_animator.set_state('spray')

        # spray 애니메이션 위치 (화면 상단 중앙)
        map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)
        map_h = getattr(getattr(server, 'tiled_map', None), 'map_height_px', 736)
        self.spray_y_position = map_h - 100  # 상단에서 100픽셀 아래

        print("[BOSS] 꿀 뿌리기 시작!")

    def spawn_honey(self):
        map_w = getattr(getattr(server, 'tiled_map', None), 'map_width_px', 1280)
        map_h = getattr(getattr(server, 'tiled_map', None), 'map_height_px', 736)

        # 기존 꿀 제거
        for honey in self.honey_objects:
            try:
                game_world.remove_object(honey)
            except:
                pass
        self.honey_objects.clear()

        # 꿀 5개 생성
        margin = 150
        boss_exclusion_radius = 250

        attempts = 0
        max_attempts = 100

        while len(self.honey_objects) < 5 and attempts < max_attempts:
            x = random.randint(margin, map_w - margin)
            y = random.randint(margin, map_h - margin)

            # 보스 위치와의 거리 계산
            dx = x - self.x
            dy = y - self.y
            distance_to_boss = (dx * dx + dy * dy) ** 0.5

            # 보스 위치에서 충분히 멀리 떨어진 곳에만 생성
            if distance_to_boss > boss_exclusion_radius:
                honey = Honey(x, y)
                self.honey_objects.append(honey)
                game_world.add_object(honey, 0)  # Layer 0 (배경)에 추가하여 플레이어 아래 그려지게
                print(f"[BOSS] 꿀 생성 #{len(self.honey_objects)}: ({x}, {y})")

            attempts += 1

        if len(self.honey_objects) < 5:
            print(f"[BOSS WARNING] 꿀 {5 - len(self.honey_objects)}개를 생성하지 못했습니다.")

    def check_honey_collected(self):
        # 꿀이 생성되지 않았으면 체크하지 않음
        if len(self.honey_objects) == 0:
            return

        # 수집되지 않은 꿀만 필터링
        self.honey_objects = [h for h in self.honey_objects if not h.collected]

        # 모든 꿀이 수집되었으면 스턴 상태로 전환
        if len(self.honey_objects) == 0 and self.is_invincible and not self.is_stunned and not self.is_spraying:
            self.enter_stun_state()

    def enter_stun_state(self):
        self.is_stunned = True
        self.is_invincible = False  # 무적 해제
        self.stun_timer = self.stun_duration
        if self.stun_animator:
            self.stun_animator.set_state('stun')
        print("[BOSS] 스턴 상태 진입!")

    def take_damage(self, dmg):
        # 스턴상태일떄만 데미지
        if not self.alive:
            return

        # 무적 상태일 때는 데미지 무시
        if self.is_invincible:
            print(f"[BOSS] 무적 상태! 꿀을 모두 먹어야 공격 가능!")
            return

        # 스턴 상태일 때만 데미지 받음
        self.hp -= dmg
        print(f"[BOSS] 데미지 {dmg} 받음! 남은 HP: {self.hp}/{self.max_hp}")

        if self.hp <= 0:
            self.alive = False
            self.animator.set_state('death')
            print("[BOSS] 보스 처치!")

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
            self.spray_animator.draw(spray_x + cam_ox, spray_y + cam_oy, self.scale * 0.8)
        # 스턴 상태일 때는 중앙에 stun 애니메이션 그리기
        elif self.is_stunned and self.stun_animator:
            self.stun_animator.draw(self.x + cam_ox, self.y + cam_oy, self.scale)
        else:
            # 일반 상태일 때는 중앙에 idle 애니메이션 그리기
            if not self.alive and self.animator._death_done:
                return
            self.animator.draw(self.x + cam_ox, self.y + cam_oy, self.scale)
