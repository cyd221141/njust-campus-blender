import bpy,os,sys,json
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene
for key,ambient in [('DAY',.65),('GOLDEN_HOUR',.34),('NIGHT',.055)]:
 w=bpy.data.worlds.get('WORLD_'+key)
 if not w:
  w=bpy.data.worlds['WORLD_GOLDEN_HOUR'].copy();w.name='WORLD_'+key
 w.use_fake_user=True;nt=w.node_tree;bg=nt.nodes.get('Background');bg.inputs[1].default_value=ambient
 if key=='NIGHT':
  tex=next(n for n in nt.nodes if n.type=='TEX_ENVIRONMENT');mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.28,.42,.78,1);nt.links.new(tex.outputs[0],mix.inputs[1]);nt.links.new(mix.outputs[0],bg.inputs[0])
for f in ['lighting.py','campus_controls.py']:
 old=bpy.data.texts.get(f)
 if old:bpy.data.texts.remove(old)
 bpy.data.texts.load(os.path.join(ROOT,'scripts',f))
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod()
s['RendererProfiles']='Cycles GPU OptiX 128 samples final stills; Eevee 32 samples animation preview.'
s.cycles.samples=128
save('NJUST_v06_Delivery')
