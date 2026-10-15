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

rig.animation_data_clear();(R/'face-frames').mkdir(exist_ok=True)
for frame in range(36):
 for b in rig.pose.bones:b.matrix_basis.identity()
 phase=frame/35*2*math.pi;brow=max(0,math.sin(phase));jaw=max(0,-math.sin(phase))
 for name in ['brow_inner_L','brow_mid_L','brow_outer_L','brow_inner_R','brow_mid_R','brow_outer_R']:
  b=rig.pose.bones[name];b.location=b.bone.matrix_local.to_3x3().inverted()@Vector((0,0,.012*brow))
 b=rig.pose.bones['jaw'];axis=b.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0));b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(axis,math.radians(5*jaw))
 b=rig.pose.bones['head'];axis=b.bone.matrix_local.to_3x3().inverted()@Vector((0,0,1));b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion(axis,math.radians(8*math.sin(phase)))
 bpy.context.view_layer.update();ev=h.evaluated_get(bpy.context.evaluated_depsgraph_get());co=np.array([v.co[:] for v in ev.data.vertices]);assert np.isfinite(co).all()
 s.render.filepath=str(R/'face-frames'/('%03d.png'%frame));bpy.ops.render.render(write_still=True)
print('FACE_DEMO_OK',flush=True)
