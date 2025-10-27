from PIL import Image

SPRITE_W, SPRITE_H = 70, 82

# mapping similar to main_chracter
keys = [
    ('IDLE_DOWN', 1, 10),
    ('IDLE_RIGHT', 2, 10),
    ('IDLE_LEFT', 3, 10),
    ('IDLE_UP', 4, 10),
    ('WALK_DOWN', 5, 8),
    ('WALK_RIGHT', 6, 8),
    ('WALK_LEFT', 7, 8),
    ('WALK_UP', 8, 8),
    ('ROLL_DOWN', 9, 8),
    ('ROLL_LEFT', 10, 8),
    ('ROLL_RIGHT', 11, 8),
]

img_path = 'Main_character_move.png'
img = Image.open(img_path).convert('RGBA')
W, H = img.size

results = {}

# helper to get bbox center of non-transparent pixels
import numpy as np
arr = np.array(img)

for name, row_idx, frames in keys:
    centers = []
    row_y = H - row_idx * SPRITE_H
    for f in range(frames):
        x0 = f * SPRITE_W
        y0 = row_y
        frame = arr[y0:y0+SPRITE_H, x0:x0+SPRITE_W]
        alpha = frame[:, :, 3]
        ys, xs = np.where(alpha > 0)
        if len(xs) == 0:
            cx = SPRITE_W // 2
            cy = SPRITE_H // 2
        else:
            cx = xs.mean()
            cy = ys.mean()
        centers.append((cx, cy))
    avg_x = sum(c[0] for c in centers) / len(centers)
    avg_y = sum(c[1] for c in centers) / len(centers)
    results[name] = {'row_idx': row_idx, 'frames': frames, 'avg_center': (avg_x, avg_y)}

# choose anchor as IDLE_DOWN center
anchor = results['IDLE_DOWN']['avg_center']

print('anchor (IDLE_DOWN) center:', anchor)
print('\nOffsets (ox = anchor_x - center_x, oy = anchor_y - center_y)')
for k in results:
    cx, cy = results[k]['avg_center']
    ox = round(anchor[0] - cx)
    oy = round(anchor[1] - cy)
    print(f"{k}: offset_x={ox}, offset_y={oy}  (center={cx:.2f},{cy:.2f})")

# Print suggested mapping if left/right seems swapped: compare expected facing by x center
print('\nSuggested row order check:')
for k in results:
    print(f"{k} row {results[k]['row_idx']} center_x={results[k]['avg_center'][0]:.2f}")

