import bpy,json
from mathutils import Vector
s=bpy.context.scene;out=[]
for o in s.objects:
 sn=o.get('SourceName','')
 if (sn.startswith('Fine details') and any('Facilities' in c.name for c in o.users_collection)) or any(w in o.name for w in ['Water','lake','river','canal','stone edge']):
  out.append({'name':o.name,'source':sn,'location':list(o.location),'scale':list(o.scale),'dimensions':list(o.dimensions),'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'hidden':o.hide_render,'lod':o.get('LOD'),'collections':[c.name for c in o.users_collection]})
print('QA_OBJECTS',json.dumps(out))
cam=bpy.data.objects['Camera_Cinematic'];hits=[];samples=[]
cores=[o for o in s.objects if o.get('CoreBuilding')]
for f in range(1,433):
 s.frame_set(f);p=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
 for o in cores:
  q=o.matrix_world.inverted()@p;bb=[Vector(v) for v in o.bound_box]
  if all(min(v[i] for v in bb)-.5<q[i]<max(v[i] for v in bb)+.5 for i in range(3)):hits.append([f,o.name])
 if f%48==1:samples.append([f,list(p)])
print('CAMERA_COLLISIONS',json.dumps(hits));print('PATH_SAMPLES',json.dumps(samples))
