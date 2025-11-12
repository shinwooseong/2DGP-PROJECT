from pico2d import load_image

SPRITE_W, SPRITE_H = 96, 80


class PlayerLoader:
    def __init__(self):
        # 1. 이미지 로드
        self.idle_images = {
            'DOWN': load_image('or_character/IDLE/idle_down.png'),
            'UP': load_image('or_character/IDLE/idle_up.png'),
            'LEFT': load_image('or_character/IDLE/idle_left.png'),
            'RIGHT': load_image('or_character/IDLE/idle_right.png'),
        }

        self.run_images = {
            'DOWN': load_image('or_character/RUN/run_down.png'),
            'UP': load_image('or_character/RUN/run_up.png'),
            'LEFT': load_image('or_character/RUN/run_left.png'),
            'RIGHT': load_image('or_character/RUN/run_right.png'),
        }

        self.attack_images = {
            1: {d: load_image(f'or_character/ATTACK 1/attack1_{d.lower()}.png') for d in
                ('DOWN', 'UP', 'LEFT', 'RIGHT')},
            2: {d: load_image(f'or_character/ATTACK 2/attack2_{d.lower()}.png') for d in
                ('DOWN', 'UP', 'LEFT', 'RIGHT')}
        }

        # 2. 프레임 수
        self.idle_frames = {d: 8 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}
        self.run_frames = {d: 8 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}
        self.attack_frames = {1: {d: 8 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')},
                              2: {d: 8 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}}

        # 3. Y 오프셋 (x축 정렬이므로 모두 0)
        self.idle_y_offsets = {d: 0 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}
        self.run_y_offsets = {d: 0 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}
        self.attack_y_offsets = {1: {d: 0 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')},
                                 2: {d: 0 for d in ('DOWN', 'UP', 'LEFT', 'RIGHT')}}
