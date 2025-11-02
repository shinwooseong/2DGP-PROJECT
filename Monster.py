from pico2d import load_image
import time
import math

# 디버그 출력 켜려면 True
DEBUG_MONSTER = True


class Animator:
    """애니메이션 로드/프레임 관리 컴포넌트
    폴더에 idle.png, attack.png, damaged.png, death.png 가로로 프레임이 이어진 시트라고 가정.
    frames_map: {'idle':n, 'attack':n, ...}
    frame_time: 상태별 프레임 시간
    """
    def __init__(self, folder, frames_map, frame_time):
        self.folder = folder
        self.frames_map = frames_map.copy()
        self.frame_time_map = frame_time.copy()
        self.images = {}
        # per-frame bboxes in bottom-left origin: {state: [(minx,miny,maxx,maxy), ...]}
        self.frame_bboxes = {}
        for state in ('idle', 'attack', 'damaged', 'death'):
            path = f"{folder}/{state}.png"
            try:
                img = load_image(path)
                self.images[state] = img
                # attempt to compute per-frame bbox using PIL for pixel-accurate hitbox
                try:
                    from PIL import Image
                    pil = Image.open(path).convert('RGBA')
                    fw = max(1, getattr(img, 'w', 1) // max(1, self.frames_map.get(state, 1)))
                    fh = getattr(img, 'h', 1)
                    frames = self.frames_map.get(state, 1)
                    bboxes = []
                    for i in range(frames):
                        left = i * fw
                        upper = 0
                        right = left + fw
                        lower = fh
                        frame_img = pil.crop((left, upper, right, lower))
                        bbox = frame_img.getbbox()  # (l,u,r,d) or None
                        if bbox is None:
                            # no pixels -> empty bbox
                            bboxes.append((0, 0, 0, 0))
                        else:
                            l, u, r, d = bbox
                            # convert to bottom-left origin: y_bottom = fh - d, y_top = fh - u
                            bl = l
                            bb = fh - d
                            br = r
                            bt = fh - u
                            bboxes.append((bl, bb, br, bt))
                    self.frame_bboxes[state] = bboxes
                except Exception:
                    # PIL not available or failed -> default full-frame bboxes
                    frames = self.frames_map.get(state, 1)
                    fw = max(1, getattr(img, 'w', 1) // frames)
                    fh = getattr(img, 'h', 1)
                    self.frame_bboxes[state] = [(0, 0, fw, fh) for _ in range(frames)]
            except Exception:
                self.images[state] = None
                self.frame_bboxes[state] = []
        self.state = 'idle'
        self.frame = 0
        self.acc = 0.0
        self._death_done = False

    def set_state(self, state):
        if state == self.state:
            return
        self.state = state
        self.frame = 0
        self.acc = 0.0
        if state == 'death':
            self._death_done = False

    def update(self, dt):
        if self.state == 'death' and self._death_done:
            return
        frames = self.frames_map.get(self.state, 1)
        ft = self.frame_time_map.get(self.state, 0.1)
        self.acc += dt
        while self.acc >= ft:
            self.acc -= ft
            self.frame += 1
            if self.state == 'death':
                if self.frame >= frames:
                    self.frame = frames - 1
                    self._death_done = True
                    break
            else:
                self.frame %= frames

    def draw(self, x, y):
        img = self.images.get(self.state)
        frames = self.frames_map.get(self.state, 1)
        if img:
            fw = max(1, img.w // frames)
            fh = img.h
            idx = int(self.frame) % frames
            x_offset = idx * fw
            img.clip_draw(x_offset, 0, fw, fh, x, y)
        else:
            # 이미지 없을 때는 그려지지 않음
            pass

    def current_frame_index(self):
        return int(self.frame)

    def get_world_hit_bbox(self, state, frame_idx, cx, cy):
        """Return world-space bbox for given state/frame index based on precomputed frame bbox.
        Returns (lx,by,rx,ty) or None if no bbox.
        """
        img = self.images.get(state)
        frames = self.frames_map.get(state, 1)
        if img is None:
            return None
        fw = max(1, img.w // frames)
        fh = img.h
        bboxes = self.frame_bboxes.get(state, [])
        if not bboxes or frame_idx < 0 or frame_idx >= len(bboxes):
            # default full frame
            minx, miny, maxx, maxy = 0, 0, fw, fh
        else:
            minx, miny, maxx, maxy = bboxes[frame_idx]
            # if bbox empty
            if minx == maxx == 0 and miny == maxy == 0:
                return None
        # frame origin is centered at (cx,cy) with frame width fw and height fh
        world_left = cx - fw / 2 + minx
        world_bottom = cy - fh / 2 + miny
        world_right = cx - fw / 2 + maxx
        world_top = cy - fh / 2 + maxy
        return (world_left, world_bottom, world_right, world_top)


class Combat:
    """공격/히트 처리 컴포넌트
    공격 시작(try_attack) -> 타겟 저장. 실제 피해는 hit_frame에서 적용하도록 함.
    """
    def __init__(self, attack_power=10, attack_range=48, cooldown=0.5, attack_frames=1, hit_frame=None):
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.last_attack_time = 0.0
        self.attack_target = None
        self.attack_frames = attack_frames
        # 히트 프레임 인덱스(없으면 중간 프레임)
        self.hit_frame = hit_frame if hit_frame is not None else max(0, attack_frames // 2)
        self.hit_done = False

    def try_attack(self, target):
        now = time.time()
        if now - self.last_attack_time < self.cooldown:
            return False
        self.last_attack_time = now
        self.attack_target = target
        self.hit_done = False
        return True

    def apply_hit_if_needed(self, prev_frame, new_frame, monster):
        """Apply hit only if attack hit-frame reached AND target's position lies within attack-frame non-transparent bbox."""
        if self.attack_target is None or self.hit_done:
            return False
        hf = self.hit_frame
        if not (prev_frame <= hf < new_frame + 1):
            return False
        target = self.attack_target
        try:
            # get world bbox for attack frame
            bbox = monster.animator.get_world_hit_bbox('attack', hf, monster.x, monster.y)
            if bbox is None:
                # no visible pixels in that frame -> no hit
                return False
            lx, by, rx, ty = bbox
            tx = getattr(target, 'x', None)
            ty_pos = getattr(target, 'y', None)
            if tx is None or ty_pos is None:
                return False
            # check if target center point inside bbox
            if lx <= tx <= rx and by <= ty_pos <= ty:
                if hasattr(target, 'take_damage'):
                    target.take_damage(self.attack_power)
                    if DEBUG_MONSTER:
                        print(f"Combat applied {self.attack_power} dmg to target via pixel bbox")
                self.hit_done = True
                return True
        except Exception:
            pass
        return False

    def clear(self):
        self.attack_target = None
        self.hit_done = False


class SimpleAI:
    """기본 AI: 패트롤, 플레이어 감지/추적, 공격 호출
    설정: patrol_origin_x, patrol_width, sight_range
    """
    def __init__(self, patrol_origin_x=0, patrol_width=0, sight_range=300):
        self.patrol_origin_x = patrol_origin_x
        self.patrol_width = patrol_width
        self.sight_range = sight_range

    def update(self, monster, dt, player=None):
        # 반환: chased(bool) - 추적/공격 중이면 True
        if player is None or not monster.alive:
            return False
        dx = player.x - monster.x
        dy = player.y - monster.y
        dist2 = dx * dx + dy * dy
        # 공격 범위
        if dist2 <= (monster.combat.attack_range * monster.combat.attack_range):
            if DEBUG_MONSTER:
                print(f"{monster.name} detected player in attack range dist={math.sqrt(dist2):.1f}")
            fired = monster.combat.try_attack(player)
            if fired:
                # set animator state to attack
                monster.animator.set_state('attack')
                # 방향 업데이트
                monster.dir = 1 if dx >= 0 else -1
                return True
        # 추적
        elif dist2 <= (self.sight_range * self.sight_range):
            if DEBUG_MONSTER:
                print(f"{monster.name} chasing player dist={math.sqrt(dist2):.1f}")
            dist = math.sqrt(dist2) if dist2 > 0 else 1.0
            vx = (dx / dist) * monster.speed
            vy = (dy / dist) * monster.speed
            monster.x += vx * dt
            monster.y += vy * dt
            monster.dir = 1 if vx >= 0 else -1
            monster.animator.set_state('idle')
            return True
        return False


class Monster:
    def __init__(self, name='monster', x=100, y=100, hp=10, speed=0):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.alive = True
        self.dir = 1

        # 컴포넌트 placeholders
        self.animator = Animator('', {'idle': 1, 'attack': 1, 'damaged': 1, 'death': 1}, {'idle': 0.1, 'attack': 0.1, 'damaged': 0.1, 'death': 0.1})
        self.combat = Combat()
        self.ai = SimpleAI()

        # 외부에서 적절히 설정될 수 있게 기본 state 노출
        self.state = self.animator.state

    def update(self, dt=0.01, frozen=False, player=None):
        if frozen or not self.alive:
            return
        # AI 처리
        chased = False
        try:
            chased = self.ai.update(self, dt, player)
        except Exception:
            chased = False
        # 패트롤(단순)
        if not chased and getattr(self.ai, 'patrol_width', 0) > 0 and self.speed != 0:
            self.x += self.speed * self.dir * dt
            left = self.ai.patrol_origin_x - self.ai.patrol_width / 2
            right = self.ai.patrol_origin_x + self.ai.patrol_width / 2
            if self.x < left:
                self.x = left
                self.dir = 1
            elif self.x > right:
                self.x = right
                self.dir = -1
        # 애니메이터 업데이트
        self.animator.update(dt)
        self.state = self.animator.state
        # Combat 히트 처리: animator 프레임 변화 체크
        frames = self.animator.frames_map.get(self.animator.state, 1)
        prev = int(self.animator.frame - 1)
        if prev < 0:
            prev = 0
        new = int(self.animator.frame)
        # 만약 공격 상태이면 combat에 의해 히트 적용
        if self.animator.state == 'attack':
            # pass monster reference so combat can get precise attack-frame bbox
            self.combat.apply_hit_if_needed(prev, new, self)
            # 공격 애니 종료시 초기화
            if new >= frames:
                self.combat.clear()

    def draw(self):
        self.animator.draw(self.x, self.y)

    def take_damage(self, dmg):
        if not self.alive:
            return
        self.hp -= dmg
        if DEBUG_MONSTER:
            print(f"{self.name} took {dmg} dmg. HP={self.hp}")
        if self.hp <= 0:
            self.alive = False
            self.animator.set_state('death')
        else:
            self.animator.set_state('damaged')

    def _in_attack_range(self, target):
        try:
            dx = target.x - self.x
            dy = target.y - self.y
            return dx * dx + dy * dy <= (self.combat.attack_range * self.combat.attack_range)
        except Exception:
            return False


class Green_MS(Monster):
    def __init__(self, x=200, y=140):
        super().__init__(name='green_ms', x=x, y=y, hp=80, speed=30)
        # Animator 세팅: MS/green_ms 폴더 안의 idle.png 등 사용
        frames_map = {'idle': 5, 'attack': 11, 'damaged': 2, 'death': 5}
        frame_time = {'idle': 0.12, 'attack': 0.07, 'damaged': 0.08, 'death': 0.10}
        self.animator = Animator('MS/green_ms', frames_map, frame_time)
        # Combat 세팅
        self.combat = Combat(attack_power=15, attack_range=80, cooldown=0.5, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        # AI 세팅
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=120, sight_range=400)
        # 이름/state 동기화
        self.state = self.animator.state

    # 필요하면 추가 오버라이드 가능


# EOF
