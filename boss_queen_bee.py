from Monster import Monster, Animator, Combat, SimpleAI


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

