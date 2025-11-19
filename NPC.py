from pico2d import load_image, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_e

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



        # NPC 이미지 로드

        # 기본 이미지 (임시)
        self.image = load_image('or_character/IDLE/player_idle.png')
        self.frame = 0
        self.frame_time = 0
        self.frame_max = 4  # 애니메이션 프레임 수

    # NPC 대화
    def _load_dialogues(self):
        pass

    def update(self, dt, player):
        # 애니메이션 프레임 업데이트
        if self.image:
            self.frame_time += dt
            if self.frame_time > 0.2:  # 0.2초마다 프레임 변경
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
        if self.image:
            # NPC 이미지 그리기 (임시로 단일 프레임)
            self.image.clip_draw(
                self.frame * self.width, 0,  # 소스 x, y
                self.width, self.height,      # 소스 width, height
                self.x, self.y,               # 목표 x, y
                self.width * 2, self.height * 2  # 목표 width, height (2배 확대)
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

