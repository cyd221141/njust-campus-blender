import bpy,os,sys,random,math
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene;rr=random.Random(935)
old=next(o for o in s.objects if o.get('SourceName','').startswith('二月兰'))
pts=[];vs=old.data.vertices
for i in range(0,len(vs),32):
 group=vs[i:i+16]
 if len(group)<16:continue
 center=sum((old.matrix_world@v.co for v in group),Vector())/16
 pts.append((center.x,center.y,.97))
archive(old,'Overscaled original petals replaced by metric four-petal flower clusters using Geometry Nodes')
obj=bpy.data.objects['GN_Close_Flowerbeds'];me=bpy.data.meshes.new('Metric_Flower_Carpet_Points');me.from_pydata(pts,[],[]);obj.data=me;obj['SourcePointCount']=len(pts)
for md in obj.modifiers:
 if md.type=='NODES':
  for sock in md.node_group.interface.items_tree:
   if sock.item_type=='SOCKET' and sock.in_out=='INPUT' and sock.name=='Density':md[sock.identifier]=.9
# Broad basal leaves create green ground cover under the restrained violet blooms.
for idx in range(3):
 o=bpy.data.objects['Flower_Variant_'+str(idx)];b=Build()
 for j in range(16):
  a=rr.random()*2*pi;r=rr.uniform(.02,.19)
  b.leaf((r*cos(a),r*sin(a),rr.uniform(.04,.13)),.15,.06,0,(a,.3,rr.uniform(-.4,.4)))
 temp=b.finish('Plant_leaf_addition',list(o.data.materials),coll('LOD_Assets'))
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bm.from_mesh(temp.data);bm.to_mesh(o.data);bm.free();bpy.data.objects.remove(temp,do_unlink=True)
# Reduce elevated paint marks inherited from the miniature, keeping original road topology.
for o in s.objects:
 if o.get('SourceName','').startswith('Fine details') and any('Roads' in c.name for c in o.users_collection) and o.type=='MESH':
  if o.data.materials and o.data.materials[0].name=='Wall_White':
   for v in o.data.vertices:v.co.z=.902+(v.co.z-.92)*.025
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod();s.cycles.samples=128
save('NJUST_Final')
