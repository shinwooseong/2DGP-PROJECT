from pico2d import load_image

SPRITE_W, SPRITE_H = 96, 80

class PlayerLoader:
    def __init__(self):
        # 이미지 로드
        try:
            self.idle_images = {
                'DOWN': load_image('or_character/IDLE/idle_down.png'),
                'UP': load_image('or_character/IDLE/idle_up.png'),
                'LEFT': load_image('or_character/IDLE/idle_left.png'),
                'RIGHT': load_image('or_character/IDLE/idle_right.png'),
            }
        except Exception:
            self.idle_images = {d: load_image('Maid Idle.png') for d in ('DOWN','UP','LEFT','RIGHT')}

        try:
            self.run_images = {
                'DOWN': load_image('or_character/RUN/run_down.png'),
                'UP': load_image('or_character/RUN/run_up.png'),
                'LEFT': load_image('or_character/RUN/run_left.png'),
                'RIGHT': load_image('or_character/RUN/run_right.png'),
            }
        except Exception:
            self.run_images = {d: load_image('Maid Run.png') for d in ('DOWN','UP','LEFT','RIGHT')}

        try:
            self.attack_images = {
                1: {d: load_image(f'or_character/ATTACK 1/attack1_{d.lower()}.png') for d in ('DOWN','UP','LEFT','RIGHT')},
                2: {d: load_image(f'or_character/ATTACK 2/attack2_{d.lower()}.png') for d in ('DOWN','UP','LEFT','RIGHT')}
            }
        except Exception:
            self.attack_images = {1: {d: load_image('Maid Idle.png') for d in ('DOWN','UP','LEFT','RIGHT')},
                                  2: {d: load_image('Maid Idle.png') for d in ('DOWN','UP','LEFT','RIGHT')}}

        # 프레임 수
        self.idle_frames = {d: 8 for d in ('DOWN','UP','LEFT','RIGHT')}
        self.run_frames = {d: 8 for d in ('DOWN','UP','LEFT','RIGHT')}
        self.attack_frames = {1: {d: 8 for d in ('DOWN','UP','LEFT','RIGHT')}, 2: {d: 8 for d in ('DOWN','UP','LEFT','RIGHT')}}

        # Y 오프셋 자동 계산
        self.idle_y_offsets = {}
        self.run_y_offsets = {}
        self.attack_y_offsets = {1: {}, 2: {}}
        try:
            from PIL import Image
            import numpy as np
            # idle
            for d in ('DOWN','UP','LEFT','RIGHT'):
                p = f'or_character/IDLE/idle_{d.lower()}.png'
                pil = Image.open(p).convert('RGBA')
                arr = np.array(pil)
                alpha = arr[:,:,3]
                rows = np.where(alpha.any(axis=1))[0]
                self.idle_y_offsets[d] = int(rows[0]) if len(rows)>0 else 0
            # run
            for d in ('DOWN','UP','LEFT','RIGHT'):
                p = f'or_character/RUN/run_{d.lower()}.png'
                pil = Image.open(p).convert('RGBA')
                arr = np.array(pil)
                alpha = arr[:,:,3]
                rows = np.where(alpha.any(axis=1))[0]
                self.run_y_offsets[d] = int(rows[0]) if len(rows)>0 else 0
            # attack
            for stage in (1,2):
                for d in ('DOWN','UP','LEFT','RIGHT'):
                    p = f'or_character/ATTACK {stage}/attack{stage}_{d.lower()}.png'
                    pil = Image.open(p).convert('RGBA')
                    arr = np.array(pil)
                    alpha = arr[:,:,3]
                    rows = np.where(alpha.any(axis=1))[0]
                    self.attack_y_offsets[stage][d] = int(rows[0]) if len(rows)>0 else 0
        except Exception:
            print("경고: PIL/Numpy Y-offset 계산 실패. 기본값(0)을 사용합니다.")
            for d in ('DOWN','UP','LEFT','RIGHT'):
                self.idle_y_offsets[d] = 0
                self.run_y_offsets[d] = 0
            for stage in (1,2):
                for d in ('DOWN','UP','LEFT','RIGHT'):
                    self.attack_y_offsets[stage][d] = 0