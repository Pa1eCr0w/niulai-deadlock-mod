import bpy,bmesh,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('./workspace/aber-lai-build-v19');R.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='./workspace/aber-lai-v17/niulai-facial-v17.blend')
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST'
for b in rig.pose.bones:b.matrix_basis.identity()
bpy.context.view_layer.update()
h=bpy.data.objects['Niulai_Fitted_Head'];body=bpy.data.objects['Abrams_Original_Body'];neck=bpy.data.objects['Abrams_Original_Neck_Fitted']
def active(o):
 bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o
active(h)
tri=sum(len(p.vertices)-2 for p in h.data.polygons)
m=h.modifiers.new('Game resolution','DECIMATE');m.ratio=min(1,220000/tri);m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name)
original=np.array([v.co[:] for v in h.data.vertices]);active(h)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.003);bpy.ops.object.mode_set(mode='OBJECT')
im=bpy.data.images.new('Niulai_Albedo',width=2048,height=2048,alpha=False)
for mat in h.data.materials:
 n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF');out=next(x for x in n if x.type=='OUTPUT_MATERIAL');em=n.new('ShaderNodeEmission');l.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs[0]);l.new(em.outputs[0],out.inputs['Surface']);t=n.new('ShaderNodeTexImage');t.image=im;n.active=t
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.bake.margin=8
p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';bpy.ops.object.bake(type='EMIT');im.filepath_raw=str(R/'head_albedo.png');im.file_format='PNG';im.save()
mat=bpy.data.materials.new('materials/models/niulai_v19/head.vmat');mat.use_nodes=True;t=mat.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;mat.node_tree.links.new(t.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1.0;h.data.materials.clear();h.data.materials.append(mat)
for poly in h.data.polygons:poly.material_index=0
# Give the concealed closure the same atlas color as the lower throat.
neck.data.materials.clear();neck.data.materials.append(mat)
if not neck.data.uv_layers:neck.data.uv_layers.new(name='UVMap')
poly=min(h.data.polygons,key=lambda p:(p.center.x-.08)**2+(p.center.y-.01)**2+(p.center.z-2.47)**2)
uv=sum((h.data.uv_layers.active.data[i].uv.copy() for i in poly.loop_indices),Vector((0,0)))/len(poly.loop_indices)
for loop in neck.data.uv_layers.active.data:loop.uv=uv
for p in neck.data.polygons:p.material_index=0
for o in [body,neck]:
 for mat in o.data.materials:
  if mat and not mat.name.endswith('.vmat'):mat.name='models/heroes_wip/abrams/materials/'+mat.name.split('.')[0]+'.vmat'
assert np.array_equal(original,np.array([v.co[:] for v in h.data.vertices]))
report={'bakePreservedPreparedGeometry':True,'bones':len(rig.data.bones),'materials':{o.name:[m.name for m in o.data.materials if m] for o in [h,body,neck]},'lods':[]}
bpy.ops.wm.save_as_mainfile(filepath=str(R/'game-source.blend'),compress=True)
# Export only replacement main mesh and face mesh; stock weapons and attachments remain in ModelDoc.
for lod in range(4):
 for tag,objects in [('body',[body,h]),('face',[neck])]:
  for o in objects:
   active(o)
   if lod and o==h:
    m=o.modifiers.new('Distance detail','DECIMATE');m.ratio=.5;m.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=m.name)
   bpy.ops.object.vertex_group_limit_total(limit=4);bpy.ops.object.vertex_group_normalize_all(lock_active=False)
  active(rig)
  for o in objects:o.select_set(True)
  bpy.ops.export_scene.fbx(filepath=str(R/f'{tag}_lod{lod}.fbx'),global_scale=1/2.54,use_selection=True,object_types={'ARMATURE','MESH'},add_leaf_bones=False,bake_anim=False,use_armature_deform_only=False,axis_forward='-Z',axis_up='Y')
  if tag=='body':
   bm=bmesh.new();bm.from_mesh(h.data);boundary=sum(e.is_boundary for e in bm.edges);bm.free();assert boundary==0,(lod,boundary)
  report['lods'].append({'headNeckBoundaryEdges':0,'part':tag,'lod':lod,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)})
(R/'export-report.json').write_text(json.dumps(report,indent=2));print('EXPORT_OK',report,flush=True)
