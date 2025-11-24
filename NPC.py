from pico2d import load_image, draw_rectangle
from loot import Loot

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
        self.composite = False

        # NPC 이미지 로드
        # 기본 이미지 로드 시 파일이 없으면 예외 처리 (None으로 둠)
        try:
            self.image = load_image('or_character/IDLE/player_idle.png')
        except Exception:
            self.image = None

        # 상호작용 UI 이미지 로드
        self.interaction_ui_image = load_image('UI/NPC_close.png')


        self.frame = 0
        self.frame_time = 0
        self.frame_max = 4  # 애니메이션 프레임 수

    # 요정 NPC 거래 확인
    def can_trade_fairy(self, player):
        # 요정 NPC는 전리품 각각을 3개씩 받아서
        # 최대 체력을 늘려주는 역할을 한다.
        if self.npc_type != 'fairy':
            return False

        # 최대 체력이 이미 200이면 거래 불가
        if player.max_health >= 200:
            return False

        # 전리품 각각 3개씩 있는지 확인
        for loot_key in ['loot1', 'loot2', 'loot3', 'loot4']:
            if player.loot_inventory.get(loot_key, 0) < 3:
                return False

        return True

    # 요정 NPC 거래 실행
    def trade_fairy(self, player):
        if not self.can_trade_fairy(player):
            return False

        # 전리품 소모 (각각 3개씩)
        for loot_key in ['loot1', 'loot2', 'loot3', 'loot4']:
            player.loot_inventory[loot_key] -= 3

        # 최대 체력 증가 (최대 200까지)
        player.max_health = min(player.max_health + 50, 200)
        # 현재 체력도 증가된 최대 체력만큼 회복
        player.health = min(player.health + 50, player.max_health)

        print(f"[요정 거래] 최대 체력 증가! 현재 최대 체력: {player.max_health}")
        return True

    # 아이템 NPC 거래 확인 (전리품 판매)
    def can_trade_item(self, player):
        # item NPC는 플레이어가 가진 전리품을 돈으로 바꿔준다
        if self.npc_type != 'item':
            return False

        # 전리품이 하나라도 있으면 거래 가능 -> 수정 할 것임. 개별 판매 기능으로
        for loot_key in ['loot1', 'loot2', 'loot3', 'loot4']:
            if player.loot_inventory.get(loot_key, 0) > 0:
                return True

        return False

    # 아이템 NPC 거래 실행 (전리품 판매)
    def trade_item(self, player):
        if not self.can_trade_item(player):
            return False

        total_earned = 0

        # 모든 전리품을 팔아서 돈으로 변환
        for loot_key in ['loot1', 'loot2', 'loot3', 'loot4']:
            count = player.loot_inventory.get(loot_key, 0)
            if count > 0:
                price = Loot.LOOT_PRICES.get(loot_key, 0)
                earned = price * count
                total_earned += earned
                player.loot_inventory[loot_key] = 0
                print(f"[아이템 거래] {loot_key} {count}개 판매: {earned}골드")

        player.money += total_earned
        print(f"[아이템 거래] 총 획득 금액: {total_earned}골드, 현재 소지금: {player.money}골드")
        return True

    # 대화 메시지 가져오기
    def get_dialogue(self, player):
        # NPC 따라서 다른 대화를 하게 함
        if self.npc_type == 'fairy':
            if player.max_health >= 200:
                return "이미 최대 체력이 200입니다!"
            elif self.can_trade_fairy(player):
                return "전리품을 가져왔군요!\n최대 체력을 50 증가시켜드릴게요!"
            else:
                return "전리품 각각 3개씩 가져오면\n최대 체력을 50 올려드려요!"
        elif self.npc_type == 'item':
            if self.can_trade_item(player):
                return "전리품을 가져왔군요!\n전리품을 팔아드릴게요!"
            else:
                return "전리품을 가져오면\n돈으로 바꿔드려요!"
        elif self.npc_type == 'water':
            return "어서오세요!"
        else:
            return "안녕하세요!"

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

        # 상호작용 가능할 때 UI 표시
        if self.can_interact:
            self.draw_interaction_ui()

    # 상호작용 UI 그리기
    def draw_interaction_ui(self, font=None):
        if self.interaction_ui_image:
            ui_scale = 0.8
            ui_width = self.interaction_ui_image.w * ui_scale
            ui_height = self.interaction_ui_image.h * ui_scale
            # NPC 오른쪽 옆에 표시
            ui_x = self.x + self.width * self.draw_scale // 2 + ui_width // 2 + 10
            ui_y = self.y + self.height * self.draw_scale // 4
            self.interaction_ui_image.draw(ui_x, ui_y, ui_width, ui_height)

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
