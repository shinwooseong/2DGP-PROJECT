from pico2d import load_image

# 변신 캐릭터의 실제 프레임 크기
TRANSFORM_SPRITE_W = 144
TRANSFORM_SPRITE_H = 144

class TransformLoader:
    """변신 캐릭터 이미지 로더 (좌우만 지원, 상하 없음)"""
    def __init__(self):
        # 이미지 로드 (모두 오른쪽 방향, 우만 있어서 좌는 뒤집어서 사용)
        self.idle_image = load_image('or_character/change_ch/Idle.png')
        self.run_image = load_image('or_character/change_ch/Run.png')
        self.attack1_image = load_image('or_character/change_ch/Attack 1.png')
        self.attack2_image = load_image('or_character/change_ch/Attack 2.png')
        self.dash_image = load_image('or_character/change_ch/Dash.png')
        self.hurt_image = load_image('or_character/change_ch/Hurt.png')
        self.death_image = load_image('or_character/change_ch/Death.png')


        # 정확한 프레임 수
        self.idle_frames = 7
        self.run_frames = 8
        self.attack1_frames = 10
        self.attack2_frames = 15
        self.dash_frames = 12
        self.hurt_frames = 3
        self.death_frames = 10
