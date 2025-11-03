from pico2d import load_image
import time
import math

# 디버그 출력 끄기
DEBUG_MONSTER = False


class Animator:
    """Animation loader and frame manager.
    Supports per-state images (horizontal) and single-sheet modes:
      - vertical: frames stacked vertically (states in order idle,attack,damaged,death)
      - grid: states are rows (frames_map order), each row has given columns
    Computes per-frame bboxes using PIL when available.
    """
    def __init__(self, folder, frames_map, frame_time, layout='horizontal', single_image_path=None):
        self.folder = folder
        self.frames_map = dict(frames_map)
        self.frame_time_map = dict(frame_time)
        self.images = {}
        self.frame_bboxes = {}
        self.layout = layout
        self.sheet_image = None
        self.sheet_state_offsets = {}
        self._sheet_grid_mode = False
        self._grid_info = {}

        if single_image_path:
            try:
                sheet = load_image(single_image_path)
                self.sheet_image = sheet
                if layout == 'grid':
                    # rows = frames_map keys order
                    items = list(self.frames_map.items())
                    num_rows = len(items)
                    max_cols = max(1, max(v for k, v in items))
                    fw = max(1, int(getattr(sheet, 'w', 1) // max_cols))
                    fh = max(1, int(getattr(sheet, 'h', 1) // num_rows))
                    # try PIL for bbox extraction
                    try:
                        from PIL import Image
                        pil = Image.open(single_image_path).convert('RGBA')
                    except Exception:
                        pil = None
                    for row_idx, (state, fcount) in enumerate(items):
                        self.sheet_state_offsets[state] = (row_idx, int(fcount))
                        bboxes = []
                        for col in range(int(fcount)):
                            if pil is not None:
                                left = col * fw
                                top = row_idx * fh
                                frame_img = pil.crop((left, top, left + fw, top + fh))
                                bbox = frame_img.getbbox()
                                if bbox is None:
                                    bboxes.append((0, 0, fw, fh))
                                else:
                                    l, u, r, d = bbox
                                    bl = l
                                    bb = fh - d
                                    br = r
                                    bt = fh - u
                                    bboxes.append((bl, bb, br, bt))
                            else:
                                bboxes.append((0, 0, fw, fh))
                        self.frame_bboxes[state] = bboxes
                    self._sheet_grid_mode = True
                    self._grid_info = {'fw': fw, 'fh': fh, 'rows': num_rows, 'cols': max_cols}
                else:
                    # vertical stacked frames (states order idle,attack,damaged,death)
                    total_frames = max(1, sum(int(self.frames_map.get(s, 1)) for s in self.frames_map))
                    fw = getattr(sheet, 'w', 1)
                    fh = max(1, int(getattr(sheet, 'h', 1) // total_frames))
                    try:
                        from PIL import Image
                        pil = Image.open(single_image_path).convert('RGBA')
                    except Exception:
                        pil = None
                    idx = 0
                    for state in ('idle', 'attack', 'damaged', 'death'):
                        fcount = int(self.frames_map.get(state, 1))
                        self.sheet_state_offsets[state] = (idx, fcount)
                        bboxes = []
                        for i in range(fcount):
                            if pil is not None:
                                top = (idx + i) * fh
                                frame_img = pil.crop((0, top, fw, top + fh))
                                bbox = frame_img.getbbox()
                                if bbox is None:
                                    bboxes.append((0, 0, fw, fh))
                                else:
                                    l, u, r, d = bbox
                                    bl = l
                                    bb = fh - d
                                    br = r
                                    bt = fh - u
                                    bboxes.append((bl, bb, br, bt))
                            else:
                                bboxes.append((0, 0, fw, fh))
                        self.frame_bboxes[state] = bboxes
                        idx += fcount
                    self._sheet_grid_mode = False
            except Exception as e:
                if DEBUG_MONSTER:
                    print(f"Animator: failed to load single sheet '{single_image_path}': {e}")
                self.sheet_image = None
                for state in self.frames_map:
                    self.images[state] = None
                    self.frame_bboxes[state] = []
            self.state = 'idle'
            self.frame = 0
            self.acc = 0.0
            self._death_done = False
            return

        # folder-based per-state images
        for state in self.frames_map:
            path = f"{folder}/{state}.png"
            try:
                img = load_image(path)
                self.images[state] = img
                try:
                    from PIL import Image
                    pil = Image.open(path).convert('RGBA')
                except Exception:
                    pil = None
                frames = int(self.frames_map.get(state, 1))
                bboxes = []
                if pil is not None:
                    if layout == 'horizontal':
                        fw = max(1, int(getattr(img, 'w', 1) // max(1, frames)))
                        fh = getattr(img, 'h', 1)
                        for i in range(frames):
                            left = i * fw
                            frame_img = pil.crop((left, 0, left + fw, fh))
                            bbox = frame_img.getbbox()
                            if bbox is None:
                                bboxes.append((0, 0, fw, fh))
                            else:
                                l, u, r, d = bbox
                                bl = l
                                bb = fh - d
                                br = r
                                bt = fh - u
                                bboxes.append((bl, bb, br, bt))
                    else:
                        fh = max(1, int(getattr(img, 'h', 1) // max(1, frames)))
                        fw = getattr(img, 'w', 1)
                        for i in range(frames):
                            top = i * fh
                            frame_img = pil.crop((0, top, fw, top + fh))
                            bbox = frame_img.getbbox()
                            if bbox is None:
                                bboxes.append((0, 0, fw, fh))
                            else:
                                l, u, r, d = bbox
                                bl = l
                                bb = fh - d
                                br = r
                                bt = fh - u
                                bboxes.append((bl, bb, br, bt))
                else:
                    if layout == 'horizontal':
                        fw = max(1, int(getattr(img, 'w', 1) // frames))
                        fh = getattr(img, 'h', 1)
                    else:
                        fw = getattr(img, 'w', 1)
                        fh = max(1, int(getattr(img, 'h', 1) // frames))
                    bboxes = [(0, 0, fw, fh) for _ in range(frames)]
                self.frame_bboxes[state] = bboxes
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
        frames = int(self.frames_map.get(self.state, 1))
        ft = float(self.frame_time_map.get(self.state, 0.1))
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

    def draw(self, x, y, scale=1.0):
        frames = int(self.frames_map.get(self.state, 1))
        if self.sheet_image is not None:
            sheet = self.sheet_image
            if getattr(self, '_sheet_grid_mode', False):
                gi = getattr(self, '_grid_info', {})
                fw = int(gi.get('fw', max(1, getattr(sheet, 'w', 1))))
                fh = int(gi.get('fh', max(1, getattr(sheet, 'h', 1))))
                start_row, cnt = self.sheet_state_offsets.get(self.state, (0, 1))
                col = int(self.frame) % int(cnt)
                left = col * fw
                bottom = max(0, getattr(sheet, 'h', 1) - (start_row + 1) * fh)
                dw = int(fw * scale)
                dh = int(fh * scale)
                try:
                    sheet.clip_draw(left, bottom, fw, fh, x, y, dw, dh)
                except Exception:
                    sheet.clip_draw(left, bottom, fw, fh, x, y)
            else:
                fw = getattr(sheet, 'w', 1)
                start, cnt = self.sheet_state_offsets.get(self.state, (0, 1))
                idx = start + (int(self.frame) % cnt)
                total_frames = sum(int(self.frames_map.get(s, 1)) for s in self.frames_map)
                fh = max(1, int(getattr(sheet, 'h', 1) // total_frames))
                bottom = max(0, getattr(sheet, 'h', 1) - (idx + 1) * fh)
                dw = int(fw * scale)
                dh = int(fh * scale)
                try:
                    sheet.clip_draw(0, bottom, fw, fh, x, y, dw, dh)
                except Exception:
                    sheet.clip_draw(0, bottom, fw, fh, x, y)
            return

        img = self.images.get(self.state)
        if not img:
            return
        if self.layout == 'horizontal':
            fw = max(1, int(img.w // frames))
            fh = img.h
            idx = int(self.frame) % frames
            x_offset = idx * fw
            try:
                dw = int(fw * scale)
                dh = int(fh * scale)
                img.clip_draw(x_offset, 0, fw, fh, x, y, dw, dh)
            except Exception:
                img.clip_draw(x_offset, 0, fw, fh, x, y)
        else:
            fh = max(1, int(img.h // frames))
            fw = img.w
            idx = int(self.frame) % frames
            top = idx * fh
            try:
                dw = int(fw * scale)
                dh = int(fh * scale)
                img.clip_draw(0, top, fw, fh, x, y, dw, dh)
            except Exception:
                img.clip_draw(0, top, fw, fh, x, y)

    def current_frame_index(self):
        return int(self.frame)

    def get_world_hit_bbox(self, state, frame_idx, cx, cy, scale=1.0):
        # returns (left,bottom,right,top) in world coords or None
        if self.sheet_image is not None:
            sheet = self.sheet_image
            if getattr(self, '_sheet_grid_mode', False):
                gi = getattr(self, '_grid_info', {})
                fw = int(gi.get('fw', getattr(sheet, 'w', 1)))
                fh = int(gi.get('fh', getattr(sheet, 'h', 1)))
                row, cnt = self.sheet_state_offsets.get(state, (0, 1))
                if frame_idx < 0 or frame_idx >= cnt:
                    return None
                bboxes = self.frame_bboxes.get(state, [])
                if not bboxes:
                    minx, miny, maxx, maxy = 0, 0, fw, fh
                else:
                    minx, miny, maxx, maxy = bboxes[frame_idx]
                    if minx == maxx == 0 and miny == maxy == 0:
                        return None
                fw_s = fw * scale
                fh_s = fh * scale
                world_left = cx - fw_s / 2 + minx * scale
                world_bottom = cy - fh_s / 2 + miny * scale
                world_right = cx - fw_s / 2 + maxx * scale
                world_top = cy - fh_s / 2 + maxy * scale
                return (world_left, world_bottom, world_right, world_top)

            # vertical stacked fallback
            total_frames = sum(int(self.frames_map.get(s, 1)) for s in self.frames_map)
            fw = getattr(sheet, 'w', 1)
            fh = max(1, int(getattr(sheet, 'h', 1) // total_frames))
            start, cnt = self.sheet_state_offsets.get(state, (0, 1))
            if frame_idx < 0 or frame_idx >= cnt:
                return None
            bboxes = self.frame_bboxes.get(state, [])
            if not bboxes:
                minx, miny, maxx, maxy = 0, 0, fw, fh
            else:
                minx, miny, maxx, maxy = bboxes[frame_idx]
                if minx == maxx == 0 and miny == maxy == 0:
                    return None
            fw_s = fw * scale
            fh_s = fh * scale
            world_left = cx - fw_s / 2 + minx * scale
            world_bottom = cy - fh_s / 2 + miny * scale
            world_right = cx - fw_s / 2 + maxx * scale
            world_top = cy - fh_s / 2 + maxy * scale
            return (world_left, world_bottom, world_right, world_top)

        img = self.images.get(state)
        if img is None:
            return None
        frames = int(self.frames_map.get(state, 1))
        if self.layout == 'horizontal':
            fw = max(1, int(img.w // frames))
            fh = img.h
        else:
            fh = max(1, int(img.h // frames))
            fw = img.w
        bboxes = self.frame_bboxes.get(state, [])
        if not bboxes or frame_idx < 0 or frame_idx >= len(bboxes):
            minx, miny, maxx, maxy = 0, 0, fw, fh
        else:
            minx, miny, maxx, maxy = bboxes[frame_idx]
            if minx == maxx == 0 and miny == maxy == 0:
                return None
        fw_s = fw * scale
        fh_s = fh * scale
        world_left = cx - fw_s / 2 + minx * scale
        world_bottom = cy - fh_s / 2 + miny * scale
        world_right = cx - fw_s / 2 + maxx * scale
        world_top = cy - fh_s / 2 + maxy * scale
        return (world_left, world_bottom, world_right, world_top)


class Combat:
    def __init__(self, attack_power=10, attack_range=48, cooldown=0.5, attack_frames=1, hit_frame=None):
        self.attack_power = attack_power
        self.attack_range = attack_range
        self.cooldown = cooldown
        self.last_attack_time = 0.0
        self.attack_target = None
        self.attack_frames = attack_frames
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
        if self.attack_target is None or self.hit_done:
            return False
        hf = self.hit_frame
        if not (prev_frame <= hf < new_frame + 1):
            return False
        target = self.attack_target
        try:
            bbox = monster.animator.get_world_hit_bbox('attack', hf, monster.x, monster.y, getattr(monster, 'scale', 1.0))
            if bbox is None:
                return False
            lx, by, rx, ty = bbox
            tx = getattr(target, 'x', None)
            ty_pos = getattr(target, 'y', None)
            if tx is None or ty_pos is None:
                return False
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
    def __init__(self, patrol_origin_x=0, patrol_width=0, sight_range=300):
        self.patrol_origin_x = patrol_origin_x
        self.patrol_width = patrol_width
        self.sight_range = sight_range

    def update(self, monster, dt, player=None):
        if player is None or not monster.alive:
            return False
        dx = player.x - monster.x
        dy = player.y - monster.y
        dist2 = dx * dx + dy * dy
        if dist2 <= (monster.combat.attack_range * monster.combat.attack_range):
            fired = monster.combat.try_attack(player)
            if fired:
                monster.animator.set_state('attack')
                monster.dir = 1 if dx >= 0 else -1
                return True
        elif dist2 <= (self.sight_range * self.sight_range):
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
        self.scale = 2.0
        self.animator = Animator('', {'idle': 1}, {'idle': 0.1})
        self.combat = Combat()
        self.ai = SimpleAI()
        self.state = self.animator.state

    def update(self, dt=0.01, frozen=False, player=None):
        if frozen or not self.alive:
            return
        chased = False
        try:
            chased = self.ai.update(self, dt, player)
        except Exception:
            chased = False
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
        self.animator.update(dt)
        self.state = self.animator.state
        frames = int(self.animator.frames_map.get(self.animator.state, 1))
        prev = int(self.animator.frame - 1)
        if prev < 0:
            prev = 0
        new = int(self.animator.frame)
        if self.animator.state == 'attack':
            self.combat.apply_hit_if_needed(prev, new, self)
            if new >= frames:
                self.combat.clear()

    def draw(self):
        self.animator.draw(self.x, self.y, getattr(self, 'scale', 1.0))

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
            # generic damaged state if exists
            if 'damaged' in self.animator.frames_map:
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
        frames_map = {'idle': 5, 'attack': 11, 'damaged': 2, 'death': 5}
        frame_time = {'idle': 0.12, 'attack': 0.07, 'damaged': 0.08, 'death': 0.10}
        self.animator = Animator('MS/green_ms', frames_map, frame_time)
        self.combat = Combat(attack_power=15, attack_range=80, cooldown=0.5, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=120, sight_range=400)
        self.state = self.animator.state


class EyeBall(Monster):
    def __init__(self, x=400, y=400):
        super().__init__(name='eyeball', x=x, y=y, hp=60, speed=20)
        sheet_path = 'MS/EyeBall Monster-Sheet.png'
        idle_count = 10
        attack_count = 17
        damaged_count = 2
        frames_map = {'idle': idle_count, 'attack': attack_count, 'damaged': damaged_count, 'death': 5}
        frame_time = {'idle': 0.12, 'attack': 0.08, 'damaged': 0.09, 'death': 0.12}
        self.animator = Animator('', frames_map, frame_time, layout='vertical', single_image_path=sheet_path)
        self.combat = Combat(attack_power=12, attack_range=40, cooldown=0.6, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=0, sight_range=300)
        self.state = self.animator.state


class Trash_Monster(Monster):
    def __init__(self, x=300, y=300):
        super().__init__(name='trash_monster', x=x, y=y, hp=50, speed=25)
        sheet_path = 'MS/Trash Monster-Sheet.png'
        # rows top-to-bottom: idle(6), sleep(6), damaged1(6), damaged2(6), attack(6), death(3)
        frames_map = {
            'idle': 6,
            'sleep': 6,
            'damaged1': 6,
            'damaged2': 6,
            'attack': 6,
            'death': 3,
        }
        frame_time = {'idle': 0.1, 'sleep': 0.1, 'damaged1': 0.08, 'damaged2': 0.08, 'attack': 0.07, 'death': 0.1}
        self.animator = Animator('', frames_map, frame_time, layout='grid', single_image_path=sheet_path)
        self.combat = Combat(attack_power=10, attack_range=50, cooldown=0.6, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=0, sight_range=300)
        # start sleeping until player detected
        self.animator.set_state('sleep')
        self.state = self.animator.state

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
            # start damaged sequence: damaged1 -> damaged2 -> idle
            self.animator.set_state('damaged1')

    def update(self, dt=0.01, frozen=False, player=None):
        super().update(dt, frozen=frozen, player=player)
        try:
            cur = self.animator.state
            if cur == 'damaged1':
                frames = int(self.animator.frames_map.get('damaged1', 1))
                if int(self.animator.frame) >= frames - 1:
                    self.animator.set_state('damaged2')
            elif cur == 'damaged2':
                frames = int(self.animator.frames_map.get('damaged2', 1))
                if int(self.animator.frame) >= frames - 1:
                    self.animator.set_state('idle')
        except Exception:
            pass


# EOF
