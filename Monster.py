from pico2d import load_image
import time
import math

# 디버그 출력 기본값
DEBUG_MONSTER = False



# 몬스터 추가할거면, Red_MS 복사해서 수정해서 사용하면 된다.
# 그리고 play_mode.py에서 import하고 추가해주면 됨.

class Animator:
    """Animation loader and frame manager.
    Supports per-state images (horizontal) and single-sheet modes:
      - vertical: frames stacked vertically (states in order idle,attack,damaged,death)
      - grid: states are rows (frames_map order), each row has given columns
    Computes per-frame bboxes using PIL when available.
    """
    def __init__(self, folder, frames_map, frame_time, layout='horizontal', single_image_path=None, single_frame_height=None):
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
                    max_cols = max(1, max(int(v) for k, v in items))
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
                    # vertical stacked frames: try to detect precise frame height using PIL+numpy
                    fw = getattr(sheet, 'w', 1)
                    H = getattr(sheet, 'h', 1)
                    # default total frames from frames_map sum
                    expected_total = max(1, sum(int(v) for v in self.frames_map.values()))
                    frame_h = None
                    pil = None
                    try:
                        from PIL import Image
                        import numpy as np
                        pil = Image.open(single_image_path).convert('RGBA')
                        arr = np.array(pil)
                        alpha = arr[:, :, 3]
                        rows = np.where(alpha.any(axis=1))[0]
                        # ensure starts/dists are always defined to avoid debug-time reference issues
                        starts = []
                        dists = []
                        if len(rows) > 0:
                            # collect start rows of visible blocks
                            prev = None
                            for r in rows:
                                if prev is None or r != prev + 1:
                                    starts.append(r)
                                prev = r
                            if len(starts) > 1:
                                dists = [starts[i+1] - starts[i] for i in range(len(starts)-1)]
                                # filter out tiny distances (noise like single-pixel artifacts)
                                dists_filtered = [int(d) for d in dists if int(d) > 5]
                                if dists_filtered:
                                    try:
                                        from statistics import mode
                                        frame_h = int(mode(dists_filtered))
                                    except Exception:
                                        # fallback to median-like selection
                                        dists_filtered.sort()
                                        frame_h = int(dists_filtered[len(dists_filtered)//2])
                                else:
                                    # no large gaps found -> fall back to min of raw dists
                                    frame_h = int(max(1, min(dists)))
                            else:
                                # single block: estimate by contiguous segment length
                                segs = []
                                prev = rows[0]
                                seg_start = prev
                                for r in rows[1:]:
                                    if r == prev + 1:
                                        prev = r
                                    else:
                                        segs.append(prev - seg_start + 1)
                                        seg_start = r
                                        prev = r
                                segs.append(prev - seg_start + 1)
                                frame_h = int(segs[0]) if segs else max(1, H // expected_total)
                        # debug output to help diagnose incorrect frame height detection
                        if DEBUG_MONSTER:
                            try:
                                s = starts if 'starts' in locals() else []
                                d = dists if 'dists' in locals() else []
                                print(f"Animator vertical-detect: file={single_image_path} H={H} expected_total={expected_total}")
                                print(f"  rows_count={len(rows)} starts={s[:10]}{'...' if len(s)>10 else ''}")
                                if d:
                                    print(f"  dists sample={d[:10]}{'...' if len(d)>10 else ''} -> frame_h(candidate)={frame_h}")
                                else:
                                    print(f"  single-block segs sample, chosen frame_h={frame_h}")
                            except Exception:
                                pass
                    except Exception:
                        pil = None
                    forced_fh = int(single_frame_height) if single_frame_height is not None else None
                    if forced_fh is not None and forced_fh > 0:
                        frame_h = forced_fh
                    elif not frame_h or frame_h <= 0:
                        # fallback to equal division
                        frame_h = max(1, int(H // expected_total))
                    # remember computed/forced frame height
                    self._sheet_frame_h = int(frame_h)
                    total_frames = max(1, int(H // frame_h))
                    # if detected total smaller than expected, force equal division
                    if total_frames < expected_total:
                        frame_h = max(1, int(H // expected_total))
                        total_frames = expected_total
                    # build bboxes per state using ordered frames_map keys
                    idx = 0
                    for state, fcount in list(self.frames_map.items()):
                        fcount = int(fcount)
                        self.sheet_state_offsets[state] = (idx, fcount)
                        bboxes = []
                        for i in range(fcount):
                            if pil is not None:
                                top = (idx + i) * frame_h
                                frame_img = pil.crop((0, top, fw, top + frame_h))
                                bbox = frame_img.getbbox()
                                if bbox is None:
                                    bboxes.append((0, 0, fw, frame_h))
                                else:
                                    l, u, r, d = bbox
                                    bl = l
                                    bb = frame_h - d
                                    br = r
                                    bt = frame_h - u
                                    bboxes.append((bl, bb, br, bt))
                            else:
                                bboxes.append((0, 0, fw, frame_h))
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
            elif self.state == 'damaged':
                # damaged 애니메이션이 끝나면 idle로 돌아감
                if self.frame >= frames:
                    self.frame = 0
                    self.state = 'idle'
                    break
            elif self.state == 'attack':
                # attack 애니메이션이 끝나면 idle로 돌아감
                if self.frame >= frames:
                    self.frame = 0
                    self.state = 'idle'
                    break
            else:
                self.frame %= frames

    # 'death' 애니메이션 끝나야지만, 죽음 처리되게
    def is_animation_finished(self):
        return self.state == 'death' and self._death_done

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
                # use computed/forced frame height if available
                fh = int(getattr(self, '_sheet_frame_h', max(1, int(getattr(sheet, 'h', 1) // max(1, sum(int(v) for v in self.frames_map.values()))))))
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

            # vertical stacked fallback: use computed/forced frame height when available
            fw = getattr(sheet, 'w', 1)
            fh = int(getattr(self, '_sheet_frame_h', max(1, int(getattr(sheet, 'h', 1) // max(1, sum(int(v) for v in self.frames_map.values()))))))
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

        # 공격 범위 표시 플래그
        self.show_attack_range = True

    def update(self, dt=0.01, frozen=False, player=None):
        # death 애니메이션 중일 때는 계속 업데이트
        if frozen and self.alive:
            return

        # alive 상태일 때만 AI 업데이트
        if self.alive:
            chased = False
            # 공격 중이 아닐 때만 AI로 이동
            if self.animator.state != 'attack':
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

        # 항상 애니메이터 업데이트 (death 애니메이션도 진행되어야 함)
        self.animator.update(dt)
        self.state = self.animator.state
        frames = int(self.animator.frames_map.get(self.animator.state, 1))
        prev = int(self.animator.frame - 1)
        if prev < 0:
            prev = 0
        new = int(self.animator.frame)
        if self.animator.state == 'attack':
            self.combat.apply_hit_if_needed(prev, new, self)


    def draw(self):
        # death 애니메이션이 완전히 끝난 후에만 화면에서 제거
        if not self.alive and self.animator._death_done:
            return

        # alive이거나, death 애니메이션 진행 중이면 계속 그리기
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

    # 몬스터 공격범위 설정
    def get_attack_bb(self):
        # 공격 상태가 아니면 None 반환
        if self.animator.state != 'attack':
            return None

        # 공격 범위 -> 수정해야함( 그림범위로 되어있어서 너무 큼 )
        attack_range = self.combat.attack_range
        left = self.x - attack_range
        right = self.x + attack_range
        bottom = self.y - attack_range
        top = self.y + attack_range

        return (left, bottom, right, top)

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
        frame_time = {'idle': 0.12, 'attack': 0.07, 'damaged': 0.08, 'death': 0.15}
        self.animator = Animator('MS/green_ms', frames_map, frame_time)
        self.combat = Combat(attack_power=15, attack_range=120, cooldown=1.0, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=120, sight_range=400)
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
        frame_time = {'idle': 0.1, 'sleep': 0.1, 'damaged1': 0.08, 'damaged2': 0.08, 'attack': 0.07, 'death': 0.2}
        self.animator = Animator('', frames_map, frame_time, layout='grid', single_image_path=sheet_path)
        self.combat = Combat(attack_power=10, attack_range=50, cooldown=1.5, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
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


class Red_MS(Monster):
    def __init__(self, x=500, y=150):
        super().__init__(name='red_ms', x=x, y=y, hp=100, speed=35)
        # per-state images are in MS/red_magic_ms/{idle,attack,damaged,death}.png
        # each state's image has frames stacked vertically
        frames_map = {'idle': 5, 'attack': 8, 'damaged': 2, 'death': 5}
        frame_time = {'idle': 0.11, 'attack': 0.06, 'damaged': 0.09, 'death': 0.15}
        # use vertical layout so each state's PNG is interpreted as vertically stacked frames
        self.animator = Animator('MS/red_magic_ms', frames_map, frame_time, layout='vertical')
        self.combat = Combat(attack_power=15, attack_range=90, cooldown=1.0, attack_frames=frames_map['attack'], hit_frame=frames_map['attack']//2)
        # give it a patrol so it moves a bit
        self.ai = SimpleAI(patrol_origin_x=x, patrol_width=150, sight_range=450)
        self.state = self.animator.state

# EOF