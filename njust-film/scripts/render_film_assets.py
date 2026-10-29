import bpy,sys,os,math,time,json
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(os.path.dirname(ROOT),'njust-refined','NJUST_Final.blend')
sys.path.insert(0,os.path.join(os.path.dirname(ROOT),'njust-refined','scripts'))
from lighting import set_lighting,set_engine,set_camera,update_lod

def setup(w=1920,h=1080):
 s=bpy.context.scene;s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.fps=30
 s.render.film_transparent=False;s.frame_set(1);set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('EEVEE','FINAL');update_lod()
 return s
def look(c,pos,target,lens=48):
 c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
def render(s,path):
 s.render.filepath=path;bpy.ops.render.render(write_still=True)

mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'all'
stats=[]
for name in ['wire','assembly','hero','grove','night','portrait']:
 if mode not in ['all',name]:continue
 bpy.ops.wm.open_mainfile(filepath=SRC);s=setup();cam=s.camera;out=os.path.join(ROOT,'process',name);os.makedirs(out,exist_ok=True);start=time.time()
 if name=='wire':
  core=[o for o in s.objects if o.get('CoreBuilding')]
  for o in s.objects:o.hide_render=True
  mat=bpy.data.materials.new('FILM_Blueprint_Emission');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.03,.4,.8,1);p.inputs['Emission Color'].default_value=(.04,.65,1,1);p.inputs['Emission Strength'].default_value=3
  cu=bpy.data.curves.new('Measured_Core_Edges','CURVE');cu.dimensions='3D';cu.bevel_depth=.07;cu.bevel_resolution=1
  for o in core:
   corners=[o.matrix_world@Vector(v) for v in o.bound_box]
   for i,j in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
    sp=cu.splines.new('POLY');sp.points.add(1)
    for p,co in zip(sp.points,[corners[i],corners[j]]):p.co=(*co,1)
  ob=bpy.data.objects.new('Core_Wireframe',cu);s.collection.objects.link(ob);cu.materials.append(mat)
  w=bpy.data.worlds.new('FILM_Black');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[0].default_value=(.001,.003,.008,1);s.world=w
  s.view_settings.exposure=0;s.render.film_transparent=True;s.render.image_settings.color_mode='RGBA'
  render(s,os.path.join(ROOT,'public','media','wire.png'))
 elif name=='assembly':
  for o in s.objects:
   keep=o.get('CoreBuilding') or o.get('SourceName') in ['Campus ground'] or o.get('SourceName','').startswith(('Campus avenue','Cross avenue'))
   o.hide_render=not keep
  s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.4;s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.58,.65,.7);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.012,.02,.04)
  core=sorted([o for o in s.objects if o.get('CoreBuilding')],key=lambda o:o.location.y+o.location.x*.4)
  originals={o.name:(o.location.copy(),o.scale.copy(),min(v[2] for v in o.bound_box)) for o in core}
  for f in range(120):
   for i,o in enumerate(core):
    pos,scale,zmin=originals[o.name];q=max(.003,min(1,(f-i*2.3)/35));q=1-(1-q)**3;o.scale.z=scale.z*q;o.location.z=pos.z+zmin*scale.z*(1-q)
   a=(f/119-.5)*.10;pos=Vector((260,-330,260));look(cam,(pos.x*math.cos(a)-pos.y*math.sin(a),pos.x*math.sin(a)+pos.y*math.cos(a),pos.z),(0,0,3),48)
   render(s,os.path.join(out,f'{f:04}.png'))
   if f%30==0:print(name,f,flush=True)
  render(s,os.path.join(ROOT,'public','media','clay.png'))
 elif name=='portrait':
  s=setup(1080,1920);cam=s.camera
  for preset in ['DAY','GOLDEN_HOUR','NIGHT']:
   set_lighting(preset);look(cam,(340,-410,355),(0,0,4),37);update_lod();render(s,os.path.join(ROOT,'public','media','portrait_'+preset+'.png'))
 else:
  n=120 if name=='hero' else 90
  if name=='night':set_lighting('NIGHT')
  if name=='grove':set_lighting('DAY')
  for f in range(n):
   u=f/(n-1)
   if name in ['hero','night']:
    a=-.075+.15*u;pos=Vector((260,-330,245));look(cam,(pos.x*math.cos(a)-pos.y*math.sin(a),pos.x*math.sin(a)+pos.y*math.cos(a),pos.z-8*u),(0,0,5),49)
   else:look(cam,(48+u*4,58-u*2,2.85),(65,75,3.4),28)
   update_lod();render(s,os.path.join(out,f'{f:04}.png'))
   if f%30==0:print(name,f,flush=True)
 stats.append({'shot':name,'seconds':round(time.time()-start,2)});print('DONE',stats[-1],flush=True)
open(os.path.join(ROOT,'reports','blender_'+mode+'.json'),'w').write(json.dumps(stats,indent=2))
