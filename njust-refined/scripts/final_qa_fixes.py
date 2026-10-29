import bpy,os,sys,math
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene
# Archive an identified furniture batch: its terracotta slabs were oversized benches.
for o in list(s.objects):
 if o.get('SourceName','').startswith('Fine details · Roofs') and any('Facilities' in c.name for c in o.users_collection):archive(o,'Original batched 2.2x benches replaced with 460 mm seat assets')
 # Lane paint should sit only millimetres above asphalt.
 if o.get('SourceName','').startswith('Fine details · Architecture | porcelain') and any('Roads' in c.name for c in o.users_collection):
  for v in o.data.vertices:v.co.z=.904+(v.co.z-.92)*.03
lookup={o.get('SourceName'):o for o in s.objects if o.name.endswith('__REF')}
# Replace the filled shore polygons by annuli, preserving outer and inner outlines.
for outer_name,inner_name in [('Lake stone edge','Zixia lake'),('Stone canal banks','Friendship river')]:
 outer=lookup[outer_name];inner=lookup[inner_name];n=len(outer.data.vertices)
 vs=[(v.co.x,v.co.y,.94) for v in outer.data.vertices]+[(v.co.x,v.co.y,.94) for v in inner.data.vertices]
 if outer_name=='Lake stone edge':fs=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 else:fs=[(i,i+2,i+2+n,i+n) for i in range(n-2)]
 me=bpy.data.meshes.new(outer.name+'_Open_Shore');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['Stone']);outer.data=me
 so=outer.modifiers.new('Stone coping thickness','SOLIDIFY');so.thickness=.12
 # Calm shallow blue-green water with visible reflection and subtle absorption.
 for v in inner.data.vertices:v.co.z=.79
water=bpy.data.materials['Water'];p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb('527F79');p.inputs['Transmission Weight'].default_value=.42;p.inputs['Roughness'].default_value=.16
c=bpy.data.objects['Camera_Sports'];c.location=(-51,-26,25);c.rotation_euler=(Vector((-86,9,1.4))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=39
# Keep the pedestrian camera at a measured 1.78 m eye level above the path.
c=bpy.data.objects['Camera_Pedestrian'];c.location=(48,59,2.78);c.rotation_euler=(Vector((71,79,3.2))-c.location).to_track_quat('-Z','Y').to_euler()
bpy.data.worlds['WORLD_NIGHT'].node_tree.nodes.get('Background').inputs[1].default_value=.13
bpy.data.lights['NIGHT_Sun'].energy=.08
old=bpy.data.texts.get('lighting.py')
if old:bpy.data.texts.remove(old)
bpy.data.texts.load(os.path.join(ROOT,'scripts','lighting.py'))
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod();s.cycles.samples=128
save('NJUST_v07_Campus_Refined')
