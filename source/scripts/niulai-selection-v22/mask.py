from PIL import Image
import numpy as np,base64,json
from pathlib import Path
r=Path('outputs/niulai-selection-v22');a=np.array(Image.open('work/niulai-successor/card-refs/bull.png').convert('RGBA')).astype(float)
# Recover only the original flat-color background, never the old hero silhouette.
color=np.array([159,140,69]);d=np.max(abs(a[:,:,:3]-color),axis=2)
mask=(d<=6)&(a[:,:,3]>0)
rects=[]
for y in range(200):
 x=0
 while x<120:
  if not mask[y,x]:x+=1;continue
  start=x;alpha=int(a[y,x,3]);x+=1
  while x<120 and mask[y,x] and int(a[y,x,3])==alpha:x+=1
  rects.append(f'<rect x="{start}" y="{y}" width="{x-start}" height="1" fill="#2092AE" opacity="{alpha/255:.7f}"/>')
fg=Path('outputs/niulai-successor/selection-foreground.png').read_bytes()
svg='<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="120" height="200" viewBox="0 0 120 200">'+''.join(rects)+'<image width="120" height="200" preserveAspectRatio="none" xlink:href="data:image/png;base64,'+base64.b64encode(fg).decode()+'"/></svg>'
(r/'selection-layout.svg').write_text(svg)
(r/'mask-source.json').write_text(json.dumps({'source':'retail panorama/images/heroes/bull_vertical_psd.vtex_c','backgroundColor':'#2092AE','originalVisibleBackgroundPixels':int(mask.sum()),'canvasPixels':24000,'method':'original flat-background coverage and alpha mapped to blue vector layer, character unchanged'},indent=2))
