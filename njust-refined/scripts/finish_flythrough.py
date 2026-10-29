import bpy,os,sys,json
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
s=bpy.context.scene;cam=bpy.data.objects['Camera_Cinematic'];route=bpy.data.objects['Cinematic_Bezier_Route'];target=bpy.data.objects['Cinematic_LookAt']
first=route.data.splines[0].bezier_points[0];first.co=(0,-155,13.2)
for i in range(5,11):route.data.splines[0].bezier_points[i].co.z=max(26,route.data.splines[0].bezier_points[i].co.z)
for c in target.constraints:c.mute=True
cam.animation_data_clear();target.animation_data_clear();con=next(c for c in cam.constraints if c.type=='FOLLOW_PATH')
points=[Vector(p.co) for p in route.data.splines[0].bezier_points];candidates=[]
for i in range(1001):
 con.offset_factor=i/1000;bpy.context.view_layer.update();pos=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy();candidates.append((i/1000,pos))
offsets=[min(candidates,key=lambda t:(t[1]-p).length)[0] for p in points]
frames=[1,40,70,100,130,160,190,220,250,280,310,335,355,397,432]
targets=[(0,-46,2),(0,-18,7),(18,12,5),(0,15,8),(0,15,9),(25,34,3),(31,36,2),(0,30,4),(-28,31,2),(-28,31,2),(-35,8,3),(-39,5,2),(0,6,5),(0,0,4),(0,0,5)]
for frame,off,co in zip(frames,offsets,targets):
 con.offset_factor=off;con.keyframe_insert('offset_factor',frame=frame)
 target.location=Vector(co)*S;target.keyframe_insert('location',frame=frame)
for o in [cam,target]:
 for slot in o.animation_data.action.slots:
  for layer in o.animation_data.action.layers:
   for strip in layer.strips:
    bag=strip.channelbag(slot)
    if bag:
     for fcu in bag.fcurves:
      for k in fcu.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
cam.data.lens=34;cam.data.keyframe_insert('lens',frame=1);cam.data.keyframe_insert('lens',frame=335);cam.data.lens=47;cam.data.keyframe_insert('lens',frame=432)
s.frame_set(1);set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod();s.cycles.samples=128
s['CinematicTiming']='18 s / 432 frames / 24 fps; matched path and look-at keyframes; entrance, avenue, Zhiyuan, woodland, lake, sport, final aerial'
open(os.path.join(ROOT,'reports','flythrough_keyframes.json'),'w').write(json.dumps({'frames':frames,'path_offsets':offsets,'targets':targets},indent=2))
save('NJUST_Final')
