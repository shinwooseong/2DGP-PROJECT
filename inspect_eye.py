from PIL import Image
import numpy as np
p='MS/EyeBall Monster-Sheet.png'
try:
    im=Image.open(p).convert('RGBA')
    W,H=im.size
    arr=np.array(im)
    alpha=arr[:,:,3]
    rows=np.where(alpha.any(axis=1))[0]
    starts=[]
    prev=None
    for r in rows:
        if prev is None or r!=prev+1:
            starts.append(r)
        prev=r
    dists=[starts[i+1]-starts[i] for i in range(len(starts)-1)] if len(starts)>1 else []
    print('SIZE',W,H)
    print('rows_count',len(rows))
    print('starts_count',len(starts))
    print('starts_sample',starts[:40])
    print('dists_sample',dists[:40])
    candidates=[]
    for fh in range(6,401):
        if H%fh==0:
            candidates.append((fh,H//fh))
    print('candidates(fh,total_frames) sample', candidates[:40])
except Exception as e:
    print('ERR',e)

