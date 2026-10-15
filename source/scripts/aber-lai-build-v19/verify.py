import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('./workspace/aber-lai-build-v19');bpy.ops.wm.read_factory_settings(use_empty=True);
import struct
raw=(R/'final.glb').read_bytes();n,t=struct.unpack_from('<II',raw,12);j=json.loads(raw[20:20+n]);tail=raw[20+n:];all_actions=[a['name'] for a in j.get('animations',[])];j['animations']=[a for a in j.get('animations',[]) if a['name'] in ['primary_stand_idle','primary_run_n','turn_90_l']];js=json.dumps(j,separators=(',',':')).encode();js+=b' '*(-len(js)%4);(R/'check.glb').write_bytes(struct.pack('<III',0x46546c67,2,20+len(js)+len(tail))+struct.pack('<II',len(js),0x4e4f534a)+js+tail);bpy.ops.import_scene.gltf(filepath=str(R/'check.glb'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];head=[]
for o in meshes:
 if not o.data.materials:continue
 inds={p.material_index for p in o.data.polygons if 'niulai' in o.data.materials[p.material_index].name.lower() or o.data.materials[p.material_index].name=='head'}
 vi={i for p in o.data.polygons if p.material_index in inds for i in p.vertices};head += [o.matrix_world@o.data.vertices[i].co for i in vi]
assert head,'Head material not found'
lo=np.min(np.array(head),axis=0);hi=np.max(np.array(head),axis=0)
with bpy.data.libraries.load(str(R/'game-source.blend'),link=False) as (src,dst):dst.objects=['Niulai_Fitted_Head','Abrams_Original_Neck_Fitted']
coords=[]
for ref in dst.objects:
 used={i for p in ref.data.polygons for i in p.vertices};coords.extend([ref.matrix_world@ref.data.vertices[i].co for i in used])
expected=np.ptp(np.array(coords),axis=0);actual=hi-lo
print('HEAD_NECK_BOUNDS',actual,expected,flush=True)
assert np.max(np.abs(actual-expected))<.0001,(actual,expected)
for ref in dst.objects:bpy.data.objects.remove(ref,do_unlink=True)
assert len(rig.data.bones)==499
face_weights={}
for o in meshes:
 for v in o.data.vertices:
  for gr in v.groups:
   name=o.vertex_groups[gr.group].name
   if any(k in name for k in ['brow','lip_','jaw','cheek','aboveeye']) and gr.weight>.001:face_weights[name]=face_weights.get(name,0)+gr.weight
assert len(face_weights)>20,face_weights

for o in meshes:
 for mat in o.data.materials:
  if mat and mat.use_nodes:
   bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
   if bs:bs.inputs['Roughness'].default_value=.8
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.world=bpy.data.worlds.new('World');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.055,.065,.085,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.5
for loc,power,size in [((3,-4,6),700,5),((-3,-2,4),500,4),((1,3,5),900,3)]:
 d=bpy.data.lights.new('Studio','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new('Studio',d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,2))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';s.render.resolution_x=1000;s.render.resolution_y=1100;s.render.resolution_percentage=100
for name,loc,target,scale in [('compiled-low',(0,-2,1.6),(0,0,2.57),.78),('compiled-high',(.7,-.9,4.4),(0,.04,2.58),.78)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
report={'facialBoneGroupsWithWeights':len(face_weights),'compiledRoundtrip':True,'bones':len(rig.data.bones),'headBounds':actual.tolist(),'headBoundsMaxError':float(np.max(np.abs(actual-expected))),'actions':[a.name for a in bpy.data.actions],'embeddedActionCount':len(all_actions),'meshes':len(meshes),'textureImages':[i.name for i in bpy.data.images]};(R/'compiled-validation.json').write_text(json.dumps(report,indent=2));print('COMPILED_VERIFIED',report,flush=True)
