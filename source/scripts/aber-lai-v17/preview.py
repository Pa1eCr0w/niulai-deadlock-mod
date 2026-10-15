import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path('./workspace/aber-lai-v17');bpy.ops.wm.open_mainfile(filepath=str(R/'niulai-facial-v17.blend'));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');h=bpy.data.objects['Niulai_Fitted_Head'];rig.data.pose_position='POSE'
with bpy.data.libraries.load('./workspace/original/abrams-original.blend',link=False) as (src,dst):
 dst.actions=[n for n in src.actions if n in ['ui_pose','primary_stand_idle','models/heroes_wip/abrams/clips/ui_hero_select']]
actions=list(dst.actions)
s.render.resolution_x=700;s.render.resolution_y=700;s.render.resolution_percentage=100;s.cycles.samples=16
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU'
cam=s.camera;cam.location=(0,-2.5,2.76);cam.rotation_euler=(Vector((0,0,2.64))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.70
report={'native_actions':[],'manual_tests':[]}
def evaluate(label,render=True):
 bpy.context.view_layer.update();ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());co=np.array([ev.matrix_world@v.co for v in ev.data.vertices]);assert np.isfinite(co).all()
 if render:s.render.filepath=str(R/(label+'.png'));bpy.ops.render.render(write_still=True)
 return co
rig.animation_data_clear()
for b in rig.pose.bones:b.matrix_basis.identity()
base=evaluate('neutral')
for label,kind in [('brow-lift','brow'),('jaw-motion','jaw'),('head-turn','head')]:
 for b in rig.pose.bones:b.matrix_basis.identity()
 if kind=='brow':
  for name in ['brow_inner_L','brow_mid_L','brow_outer_L','brow_inner_R','brow_mid_R','brow_outer_R']:
   b=rig.pose.bones[name];b.location=b.bone.matrix_local.to_3x3().inverted()@Vector((0,0,.012))
 if kind=='jaw':
  b=rig.pose.bones['jaw'];axis=b.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(axis,math.radians(7))
 if kind=='head':
  b=rig.pose.bones['head'];axis=b.bone.matrix_local.to_3x3().inverted()@Vector((0,0,1));b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(axis,math.radians(35))
 co=evaluate(label);report['manual_tests'].append({'name':label,'max_displacement':float(np.linalg.norm(co-base,axis=1).max()),'finite':True})
for b in rig.pose.bones:b.matrix_basis.identity()
rig.animation_data_create()
for a in actions:
 rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 frames=np.linspace(a.frame_range[0],a.frame_range[1],5)
 rec={'name':a.name,'range':list(a.frame_range),'samples':[]}
 for i,frame in enumerate(frames):
  s.frame_set(int(frame));bpy.context.view_layer.update();target=rig.matrix_world@rig.pose.bones['head'].head;target.z-=.03;cam.location=target+Vector((0,-2.5,.10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();co=evaluate('native-'+a.name.split('/')[-1]+'-'+str(i),render=(i==2));rec['samples'].append({'frame':int(frame),'finite':True,'active_face_bones':[b.name for b in rig.pose.bones if any(k in b.name for k in ['brow','lip_','jaw','cheek','aboveeye']) and np.max(np.abs(np.array(b.matrix_basis)-np.eye(4)))>1e-5],'bounds':[co.min(0).tolist(),co.max(0).tolist()]})
 report['native_actions'].append(rec)
# Short original idle motion preview, head framing follows original head bone.
a=next(a for a in actions if 'primary_stand_idle' in a.name);rig.animation_data.action=a
if a.slots:rig.animation_data.action_slot=a.slots[0]
frames=np.linspace(a.frame_range[0],a.frame_range[1],48)
for i,frame in enumerate(frames):
 s.frame_set(int(frame));bpy.context.view_layer.update();target=rig.matrix_world@rig.pose.bones['head'].head;target.z-=.03
 cam.location=target+Vector((0,-2.5,.10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'frames'/('%03d.png'%i));bpy.ops.render.render(write_still=True)
(R/'animation-checks.json').write_text(json.dumps(report,indent=2));print('ANIMATION_CHECK_OK',flush=True)
