import bpy,json,numpy as np
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='./workspace/aber-lai-v15/niulai-skin-sync-v15.blend')
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');h=bpy.data.objects['Niulai_Fitted_Head'];sums={g.name:0.0 for g in h.vertex_groups}
for v in h.data.vertices:
 for g in v.groups:sums[h.vertex_groups[g.group].name]+=g.weight
r={'rig':rig.name,'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones],'active_head_weights':{k:v for k,v in sums.items() if v>.01},'actions':[{'name':a.name,'frames':list(a.frame_range)} for a in bpy.data.actions],'meshes':[o.name for o in bpy.data.objects if o.type=='MESH']}
Path('./workspace/aber-lai-v17/rig-audit.json').write_text(json.dumps(r,indent=2));print('AUDIT_OK')
