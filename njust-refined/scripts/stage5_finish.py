import os,sys,bpy,random,math,json,bmesh
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene
# Add a continuous but porous crown to the existing branch-and-leaf assets.
for o in list(bpy.data.objects):
 if not (o.name.startswith(('Broadleaf_','Metasequoia_')) and o.name.endswith(('LOD1','LOD2'))):continue
 idx=int(o.name.split('_')[1]);lod=int(o.name[-1]);rr=random.Random(705+idx);b=Build();h=8+idx*.25 if idx<5 else 11+(idx-5)*1.1
 for j in range(1900 if lod==1 else 4300):
  z=rr.uniform(h*.43,h*.96);ang=rr.uniform(0,2*pi)
  if idx<5:rmax=2.5*math.sqrt(max(.01,1-((z-h*.70)/(h*.29))**2))
  else:rmax=(1-z/h)*4.8+.12
  r=rr.random()**.4*rmax
  b.leaf((r*cos(ang),r*sin(ang),z),rr.uniform(.3,.48) if lod==1 else rr.uniform(.19,.32),rr.uniform(.15,.25),rr.randrange(1,6),(ang,rr.uniform(-pi,pi),rr.uniform(-pi,pi)))
 temp=b.finish('Crown_fill_temp',list(o.data.materials),coll('LOD_Assets'))
 bm=bmesh.new();bm.from_mesh(o.data);bm.from_mesh(temp.data);bm.to_mesh(o.data);bm.free();bpy.data.objects.remove(temp,do_unlink=True)
for o in bpy.data.objects:
 if o.name.startswith(('Broadleaf_','Metasequoia_')) and o.name.endswith('LOD0'):
  for md in o.modifiers:
   if md.type=='DECIMATE':md.ratio=.78
# A slightly lower aerial viewpoint provides a more legible full-campus composition.
c=bpy.data.objects['Camera_Master_Aerial'];c.location=(260,-330,260);c.rotation_euler=(Vector((0,0,4))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=48
# Keep model, lighting and reusable controls in the saved file.
for f in ['lighting.py','campus_controls.py']:
 path=os.path.join(ROOT,'scripts',f)
 if os.path.exists(path):
  old=bpy.data.texts.get(f)
  if old:bpy.data.texts.remove(old)
  bpy.data.texts.load(path)
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod()
s.render.resolution_x=2400;s.render.resolution_y=1500
save('NJUST_v05_Final')
