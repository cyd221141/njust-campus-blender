import bpy,os,sys,time,json
sys.path.insert(0,os.path.dirname(__file__))
from lighting import *
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));s=bpy.context.scene
test='--test' in sys.argv
set_camera('Camera_Cinematic');set_lighting('GOLDEN_HOUR');set_engine('EEVEE','FINAL')
s.render.resolution_x=960 if test else 1920;s.render.resolution_y=540 if test else 1080;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.fps=24
frames=[1,49,97,145,193,241,289,337,385,432] if test else range(1,433)
stats=[];started=time.time()
for f in frames:
 path=os.path.join(root,'animation','frames',('test_' if test else 'frame_')+str(f).zfill(4)+'.png')
 if not test and os.path.exists(path):continue
 s.frame_set(f);update_lod();s.render.filepath=path;t=time.time();bpy.ops.render.render(write_still=True)
 stats.append({'frame':f,'seconds':round(time.time()-t,2)})
 print('FRAME_COMPLETE',f,stats[-1]['seconds'],flush=True)
open(os.path.join(root,'reports','animation_'+('preview' if test else 'render')+'.json'),'w').write(json.dumps({'seconds':time.time()-started,'frames':stats},indent=2))
