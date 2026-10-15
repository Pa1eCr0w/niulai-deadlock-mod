import bpy,bmesh,numpy as np,json,math
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path('./workspace/aber-lai-v17');bpy.ops.wm.open_mainfile(filepath='./workspace/aber-lai-v15/niulai-skin-sync-v15.blend');s=bpy.context.scene
h=bpy.data.objects['Niulai_Fitted_Head'];rig=next(o for o in s.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST'
origco=np.array([v.co[:] for v in h.data.vertices]);origweights=[{h.vertex_groups[g.group].name:g.weight for g in v.groups} for v in h.data.vertices];rest={b.name:[list(r) for r in b.matrix_local] for b in rig.data.bones}
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
with bpy.data.libraries.load('./workspace/original/abrams-original.blend',link=False) as (src,dst):
 dst.objects=[n for n in src.objects if n.endswith('.abrams_face_model')]
donor=dst.objects[0];s.collection.objects.link(donor);donor.hide_render=True
world=donor.matrix_world.copy()
for v in donor.data.vertices:v.co=world@v.co
# Landmark alignment: chin, lip seam, nose, eyes and brows separately.
sourcez=np.array([2.50,2.61,2.652,2.68,2.72,2.753,2.77,2.80,2.90])
targetz=np.array([2.50,2.59,2.643,2.68,2.72,2.746,2.789,2.82,2.93])
for v in donor.data.vertices:
 x,y,z=v.co;offset=np.interp(z,[2.50,2.61,2.652,2.68,2.72,2.753,2.80,2.90],[.01,.08,.145,.145,.12,.115,.08,.01])
 v.co=(x*1.60,y*1.30-offset,float(np.interp(z,sourcez,targetz)))
donor.matrix_world.identity();donor.parent=None
for m in list(donor.modifiers):donor.modifiers.remove(m)
target=h.copy();target.data=h.data.copy();s.collection.objects.link(target);target.name='Facial_transfer_probe';target.hide_render=True
for m in list(target.modifiers):target.modifiers.remove(m)
for g in donor.vertex_groups:
 if not target.vertex_groups.get(g.name):target.vertex_groups.new(name=g.name)
active(target);dt=target.modifiers.new('Anatomical facial weight transfer','DATA_TRANSFER');dt.object=donor;dt.use_vert_data=True;dt.data_types_verts={'VGROUP_WEIGHTS'};dt.vert_mapping='POLYINTERP_NEAREST';dt.layers_vgroup_select_src='ALL';dt.layers_vgroup_select_dst='NAME';bpy.ops.object.modifier_apply(modifier=dt.name)
allowed={b.name for b in rig.data.bones if any(k in b.name for k in ['brow','forehead','cheek','lip_','jaw','aboveeye','nose','nostril','chin'])}
for name in allowed:
 if not h.vertex_groups.get(name):h.vertex_groups.new(name=name)
counts={};totals={};changed=0
for v in h.data.vertices:
 x,y,z=v.co
 # Face-only front envelope; all ears, horns, posterior skull and neck retain original binding.
 front=max(0,min(1,(-y-.065)/.055));side=max(0,min(1,(.16-abs(x))/.035));vertical=min(max(0,(z-2.575)/.045),max(0,(2.87-z)/.045),1)
 strength=.24+.21*max(0,min(1,(z-2.70)/.055))
 mix=strength*front*side*vertical
 if mix<=0:continue
 w={target.vertex_groups[g.group].name:g.weight for g in target.data.vertices[v.index].groups if target.vertex_groups[g.group].name in allowed and g.weight>.001}
 total=sum(w.values())
 if total<.001:continue
 w={k:val*mix for k,val in w.items()};out={k:val*(1-total*mix) for k,val in origweights[v.index].items()}
 for k,val in w.items():out[k]=out.get(k,0)+val
 out=dict(sorted(out.items(),key=lambda kv:kv[1],reverse=True)[:4]);norm=sum(out.values())
 for g in list(v.groups):h.vertex_groups[g.group].remove([v.index])
 for name,val in out.items():h.vertex_groups[name].add([v.index],val/norm,'REPLACE');totals[name]=totals.get(name,0)+val/norm
 changed+=1
bpy.data.objects.remove(target,do_unlink=True);bpy.data.objects.remove(donor,do_unlink=True)
active(h)
for v in h.data.vertices:v.select=(v.co.y<-.065 and 2.575<v.co.z<2.87 and abs(v.co.x)<.16)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.object.vertex_group_smooth(group_select_mode='ALL',factor=.65,repeat=100);bpy.ops.object.mode_set(mode='OBJECT');bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
assert np.array_equal(origco,np.array([v.co[:] for v in h.data.vertices]))
assert rest=={b.name:[list(r) for r in b.matrix_local] for b in rig.data.bones}
weights=[sum(g.weight for g in v.groups) for v in h.data.vertices];assert min(weights)>.999 and max(weights)<1.001
report={'base':'approved v15','geometry_unchanged':True,'skeleton_rest_unchanged':True,'bones':len(rig.data.bones),'transfer':'native nearest-face interpolated from anatomically aligned stock face','face_vertices_bound':changed,'facial_weight_totals':{k:v for k,v in totals.items() if k in allowed},'weight_range':[min(weights),max(weights)],'installed':False,'limitation':'closed sculpted mouth and painted eyes; subtle face deformation, not a rebuilt opening mouth/eyeball system'}
(R/'facial-binding.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(R/'niulai-facial-v17.blend'),compress=True)
print('BINDING_OK',json.dumps(report),flush=True)
