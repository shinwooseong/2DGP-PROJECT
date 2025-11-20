from pico2d import load_image, draw_rectangle

class NPC:
    def __init__(self, x, y, npc_type='default', name='NPC'):
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.name = name

        # NPC 크기
        self.width = 32
        self.height = 48

        # 상호작용 범위 (플레이어가 이 범위 안에 있으면 상호작용 가능)
        self.interaction_range = 80

        # 상호작용 가능 여부
        self.can_interact = False

        # 대화 상태
        self.is_talking = False
        self.dialogue_index = 0

        # 그리기 스케일 (크기 조절용)
        self.draw_scale = 1.0
        self.composite =False

        # NPC 이미지 로드

        # 기본 이미지 로드 시 파일이 없으면 예외 처리 (None으로 둠)
        try:
            self.image = load_image('or_character/IDLE/player_idle.png')
        except Exception:
            self.image = None

        self.frame = 0
        self.frame_time = 0
        self.frame_max = 4  # 애니메이션 프레임 수

    # NPC 대화
    def _load_dialogues(self):
        pass

    def update(self, dt, player=None):
        # 애니메이션 프레임 업데이트
        if self.image:
            self.frame_time += dt
            if self.frame_time > 1.4:  # 프레임 전환 시간 조절
                self.frame = (self.frame + 1) % self.frame_max
                self.frame_time = 0

        # 플레이어와의 거리 계산
        if player:
            distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

            # 상호작용 범위 체크
            if distance <= self.interaction_range:
                self.can_interact = True
            else:
                self.can_interact = False
                self.is_talking = False
                self.dialogue_index = 0

    def handle_event(self, event):
        pass

    def draw(self):
        if self.image and not self.composite:
            # NPC 이미지 그리기 (프레임 애니메이션)
            self.image.clip_draw(
                self.frame * self.width, 0,  # 소스 x, y
                self.width, self.height,      # 소스 width, height
                self.x, self.y,               # 목표 x, y
                self.width * self.draw_scale, self.height * self.draw_scale  # 목표 width, height (스케일 적용)
            )
        elif self.image and self.composite:
            # composite이 True면 좌우 반전으로 그리기
            self.image.clip_composite_draw(
                self.frame * self.width, 0,  # 소스 x, y
                self.width, self.height,      # 소스 width, height
                0, 'h',                       # 회전 각도, 'h'는 수평 반전
                self.x, self.y,               # 목표 x, y
                self.width * self.draw_scale, self.height * self.draw_scale  # 목표 width, height (스케일 적용)
            )
        else:
            # 이미지가 없으면 사각형으로 표시
            draw_rectangle(
                self.x - self.width // 2,
                self.y - self.height // 2,
                self.x + self.width // 2,
                self.y + self.height // 2
            )

    # 상호작용 UI 그리기
    def draw_interaction_ui(self, font=None):
        pass

    # 충돌 박스 반환
    def get_collision_box(self):
        return (
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.x + self.width // 2,
            self.y + self.height // 2
        )

    # 플레이어와 충돌 여부 확인
    def is_colliding_with_player(self, player):
        left1, bottom1, right1, top1 = self.get_collision_box()

        # 플레이어의 충돌 박스
        player_w = 20
        player_h = 30
        left2 = player.x - player_w
        bottom2 = player.y - player_h
        right2 = player.x + player_w
        top2 = player.y + player_h

        # AABB 충돌 체크
        if left1 < right2 and right1 > left2 and bottom1 < top2 and top1 > bottom2:
            return True
        return False
