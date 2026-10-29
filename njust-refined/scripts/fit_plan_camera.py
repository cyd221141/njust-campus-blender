import bpy,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene;bpy.data.objects['Camera_Campus_Plan'].data.ortho_scale=430
save('NJUST_Final')
set_camera('Camera_Campus_Plan');set_lighting('DAY');set_engine('CYCLES');update_lod();s.cycles.samples=128
s.render.resolution_x=2400;s.render.resolution_y=1500;s.render.filepath=os.path.join(ROOT,'renders','07_Campus_Plan.png')
bpy.ops.render.render(write_still=True)
