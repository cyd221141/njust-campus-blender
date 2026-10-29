import bpy,sys,os,json,math
from mathutils import Vector
s=bpy.context.scene;root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def bbox(o):
 return [list(o.matrix_world@Vector(v)) for v in o.bound_box]
cores=[o for o in s.objects if o.get('CoreBuilding')];errs=[]
for o in cores:
 err=(o.location/2.2-Vector(o['SourcePosition'])).length
 if err>1e-4:errs.append([o.name,err])
nodes=[]
for o in s.objects:
 for md in o.modifiers:
  if md.type=='NODES':nodes.append({'object':o.name,'points':len(o.data.vertices),'inputs':[k.name for k in md.node_group.interface.items_tree if k.item_type=='SOCKET' and k.in_out=='INPUT']})
assets=[c.name for c in bpy.data.collections if c.asset_data]
cam=bpy.data.objects['Camera_Cinematic'];collisions=[];minimum_z=1e5
for f in range(1,433):
 s.frame_set(f);p=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation;minimum_z=min(minimum_z,p.z)
 for o in cores:
  q=o.matrix_world.inverted()@p;bb=[Vector(v) for v in o.bound_box]
  if all(min(v[i] for v in bb)-.3<q[i]<max(v[i] for v in bb)+.3 for i in range(3)):collisions.append({'frame':f,'object':o.name})
report={'blender':bpy.app.version_string,'scenes':[x.name for x in bpy.data.scenes],'core_buildings':len(cores),'core_position_errors':errs,'objects':len(s.objects),'mesh_datablocks_used':len({o.data.name for o in s.objects if o.type=='MESH'}),'collection_instances':sum(o.instance_type=='COLLECTION' for o in s.objects),'assets':assets,'geometry_nodes':nodes,'cameras':[o.name for o in s.objects if o.type=='CAMERA' and not o.get('SupersededReason')],'lights':{p:len(bpy.data.collections['LIGHTING_'+p].objects) for p in ['DAY','GOLDEN_HOUR','NIGHT']},'worlds':[{'name':w.name,'saved':w.use_fake_user} for w in bpy.data.worlds if w.name.startswith('WORLD_')],'materials':sorted({m.name for o in s.objects if hasattr(o.data,'materials') for m in o.data.materials if m}),'images':[{'name':i.name,'packed':bool(i.packed_file),'filepath':i.filepath} for i in bpy.data.images if i.source=='FILE' and i.users],'fonts':[{'name':f.name,'packed':bool(f.packed_file)} for f in bpy.data.fonts if f.users and f.filepath!='<builtin>'],'animation_frames':432,'fps':24,'camera_building_collisions':collisions,'camera_minimum_height':minimum_z,'window_count':s['WindowCount'],'lit_fraction':s['NightLitWindowFraction'],'metric_scale':s.unit_settings.scale_length}
open(os.path.join(root,'reports','delivery_audit.json'),'w',encoding='utf-8').write(json.dumps(report,ensure_ascii=False,indent=2))
print('AUDIT_COMPLETE',len(cores),len(errs),len(collisions),len(nodes),flush=True)
