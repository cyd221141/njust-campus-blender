import sys,os,bpy,argparse,time,json
sys.path.insert(0,os.path.dirname(__file__))
from lighting import *
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser();p.add_argument('--camera',default='Camera_Master_Aerial');p.add_argument('--preset',default='GOLDEN_HOUR');p.add_argument('--engine',default='CYCLES');p.add_argument('--width',type=int,default=1800);p.add_argument('--height',type=int,default=1125);p.add_argument('--name',default='preview');p.add_argument('--samples',type=int,default=32);p.add_argument('--frame',type=int,default=1);a=p.parse_args(argv)
s=bpy.context.scene;set_camera(a.camera);set_lighting(a.preset);set_engine(a.engine,'PREVIEW');s.frame_set(a.frame);update_lod();s.cycles.samples=a.samples
s.render.resolution_x=a.width;s.render.resolution_y=a.height;s.render.resolution_percentage=100;s.render.filepath=os.path.join(root,'renders',a.name+'.png')
start=time.time();bpy.ops.render.render(write_still=True);print('RENDER_SECONDS',round(time.time()-start,2),flush=True)
