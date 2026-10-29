import os,sys,bpy,time,json
sys.path.insert(0,os.path.dirname(__file__))
from lighting import *
root=os.path.dirname(os.path.dirname(__file__));s=bpy.context.scene
preview='--preview' in sys.argv
shots=[('01_Day_Aerial','Camera_Master_Aerial','DAY'),('02_Golden_Aerial','Camera_Master_Aerial','GOLDEN_HOUR'),('03_Gate','Camera_Gate','GOLDEN_HOUR'),('04_Main_Road','Camera_Main_Road','DAY'),('05_Pedestrian','Camera_Pedestrian','DAY'),('06_Sports','Camera_Sports','DAY'),('07_Campus_Plan','Camera_Campus_Plan','DAY'),('08_Night','Camera_Master_Aerial','NIGHT'),('09_Central_Building','Camera_Central_Building','GOLDEN_HOUR'),('10_Lake','Camera_Lake','DAY')]
timings=[]
for name,camera,preset in shots:
 set_camera(camera);set_lighting(preset);set_engine('CYCLES','PREVIEW' if preview else 'FINAL');s.frame_set(1);update_lod()
 s.cycles.samples=32 if preview else 128
 s.render.resolution_x=1200 if preview else 2400;s.render.resolution_y=750 if preview else 1500;s.render.resolution_percentage=100
 s.render.filepath=os.path.join(root,'renders',('test_' if preview else '')+name+'.png')
 t=time.time();bpy.ops.render.render(write_still=True);timings.append({'image':name,'seconds':round(time.time()-t,2)});print('SHOT_COMPLETE',name,timings[-1]['seconds'],flush=True)
open(os.path.join(root,'reports',('preview_' if preview else '')+'render_timings.json'),'w').write(json.dumps(timings,indent=2))
