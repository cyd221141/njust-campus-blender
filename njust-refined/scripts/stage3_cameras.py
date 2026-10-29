import sys,os,bpy,math,json
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
scene=bpy.context.scene
def light(name,kind,loc,power,color,c,target=(0,0,0),size=1):
 d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color;o=bpy.data.objects.new(name,d);c.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
 if kind=='SUN':d.angle=math.radians(1.4)
 elif kind=='AREA':d.shape='DISK';d.size=size
 elif kind=='SPOT':d.spot_size=math.radians(115);d.spot_blend=.6;d.shadow_soft_size=.35
 return o
parent=coll('Campus_Lighting')
image=bpy.data.images.load(os.path.join(ROOT,'references','kloppenheim_06_puresky_1k.hdr'),check_existing=True)
presets={'DAY':(48,1.65,.65,(1,.96,.88)),'GOLDEN_HOUR':(20,2.0,.34,(1,.78,.54)),'NIGHT':(35,.04,.055,(.6,.72,1))}
lamppts=json.loads(scene['LampPoints'])
for key,(alt,power,ambient,color) in presets.items():
 c=coll('LIGHTING_'+key,parent)
 # Sun 20 degrees above horizon for the promotional golden-hour rig.
 az=math.radians(-125);elev=math.radians(alt)
 loc=(200*cos(az)*cos(elev),200*sin(az)*cos(elev),200*sin(elev))
 light(key+'_Sun','SUN',loc,power,color,c)
 w=bpy.data.worlds.new('WORLD_'+key);w.use_nodes=True;nt=w.node_tree;n=nt.nodes;l=nt.links;bg=n.get('Background')
 tex=n.new('ShaderNodeTexEnvironment');tex.image=image;tex.name='Packed CC0 sky';l.new(tex.outputs[0],bg.inputs[0]);bg.inputs[1].default_value=ambient
 if key=='NIGHT':
  mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.28,.42,.78,1);l.new(tex.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],bg.inputs[0])
  for i,(x,y,z) in enumerate(lamppts):
   if i%2==0:light('Night_street_%02d'%i,'SPOT',(x+.63,y,z+5.57),210,(1,.74,.43),c,target=(x+.7,y,.9))
  for x,y in [(-46,-5),(-46,16),(-31,-5),(-31,16)]:light('Night_sports','AREA',(x*S,y*S,11.6),750,(.89,.95,1),c,target=(-39*S,5*S,.9),size=2)
  for x,y,z in [(0,-106,4),(0,-42,5),(0,24,7)]:light('Entry_wash','AREA',(x,y,z),230,(1,.77,.5),c,target=(x,y+6,z-1),size=4)
 else:light(key+'_Sky_Fill','AREA',(90,-100,140),13000,(.79,.86,1),c,target=(0,0,0),size=150)
cams=coll('Campus_Cameras')
def camera(name,loc,target,lens=42,ortho=None):
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);cams.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=2000;d.clip_start=.12
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 d.dof.use_dof=False;o['Target']=list(target);return o
camera('Camera_Master_Aerial',(270,-330,245),(0,0,5),46)
camera('Camera_Gate',(6,-136,5.8),(0,-78,10.5),38)
camera('Camera_Main_Road',(18*S,-39*S,3.8),(18*S,5*S,8),30)
camera('Camera_Central_Building',(70,-31,34),(0,25,18),41)
camera('Camera_Sports',(-136,-12,23),(-39*S,5*S,1.4),40)
camera('Camera_Lake',(-139,37,17),(-28*S,31*S,2),43)
camera('Camera_Pedestrian',(48,60,2.78),(71,77,3.4),32)
camera('Camera_Campus_Plan',(0,-.001,350),(0,0,0),40,280)
camera('Camera_Central_Identity',(0,-120,28),(0,0,18),43)
# Two smooth Bezier paths independently control location and look-at target.
route=[(0,-54,6),(13,-44,5),(18,-30,4),(18,-12,5),(18,7,7),(18,22,8),(18,36,5),(8,43,7),(-17,42,7),(-30,42,9),(-46,30,10),(-48,7,14),(-49,-20,24),(-70,-90,77),(-120,-155,120)]
targets=[(0,-35,4),(0,-20,7),(0,-14,9),(0,12,12),(0,15,12),(28,35,5),(32,36,4),(0,30,5),(-28,31,2),(-28,31,2),(-35,8,3),(-39,5,2),(0,6,5),(0,0,4),(0,0,5)]
def path(name,coords):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=18;d.path_duration=432;sp=d.splines.new('BEZIER');sp.bezier_points.add(len(coords)-1)
 for p,co in zip(sp.bezier_points,coords):p.co=Vector(co)*S;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);cams.objects.link(o);o.hide_render=True;return o
routeobj=path('Cinematic_Bezier_Route',route);lookpath=path('Cinematic_LookAt_Route',targets)
cam=camera('Camera_Cinematic', (0,0,0),(0,1,0),30)
target=bpy.data.objects.new('Cinematic_LookAt',None);cams.objects.link(target)
for o,pa in [(cam,routeobj),(target,lookpath)]:
 con=o.constraints.new('FOLLOW_PATH');con.target=pa;con.use_fixed_location=True;con.use_curve_follow=False
 con.offset_factor=0;con.keyframe_insert('offset_factor',frame=1)
 con.offset_factor=1;con.keyframe_insert('offset_factor',frame=432)
 # Blender's default Bezier interpolation gives gentle ease-in and ease-out.
track=cam.constraints.new('TRACK_TO');track.target=target;track.track_axis='TRACK_NEGATIVE_Z';track.up_axis='UP_Y'
scene.frame_start=1;scene.frame_end=432;scene.render.fps=24;scene.frame_set(1)
scene.render.resolution_x=2400;scene.render.resolution_y=1500;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.film_transparent=False
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES')
scene['AnimationDurationSeconds']=18;scene['CinematicRoute']='Gate → main avenue → library / Zhiyuan → woodland → lake → sports → aerial';scene['CameraEyeHeight_m']=1.78
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='SOLID';a.spaces.active.shading.color_type='MATERIAL';a.spaces.active.overlay.show_overlays=False
save('NJUST_v03_Lighting_Cameras')
