import bpy,json,numpy as np
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='./workspace/aber-lai-v15/niulai-skin-sync-v15.blend')
h=bpy.data.objects['Niulai_Fitted_Head'];p=np.array([v.co[:] for v in h.data.vertices]);c=np.array([x.color[:] for x in h.data.color_attributes['NiulaiColor'].data]);r={}
for name,mask in [('white',(c[:,0]>.6)&(c[:,1]>.6)&(c[:,2]>.6)&(p[:,1]<-.08)),('pink',(c[:,0]>c[:,2]*1.1)&(c[:,0]>.2)&(abs(p[:,0])<.12)),('brow',(c[:,0]>c[:,1]*1.5)&(p[:,2]>2.72)&(p[:,1]<-.05))]:
 a=p[mask];r[name]={'n':len(a),'min':a.min(0).tolist(),'max':a.max(0).tolist(),'median':np.median(a,0).tolist()} if len(a) else {}
with bpy.data.libraries.load('./workspace/original/abrams-original.blend',link=False) as (src,dst):
 r['original_objects']=list(src.objects)
print(json.dumps(r),flush=True)
