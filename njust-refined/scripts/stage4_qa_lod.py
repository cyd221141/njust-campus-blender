import sys,os,bpy,bmesh,math,json
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
from lighting import *
scene=bpy.context.scene;m=palette()
lookup={o.get('SourceName'):o for o in scene.objects if o.get('SourceName')}
# Explicit vertex edits avoid stale dimension caches after applying transforms.
ground=lookup['Campus ground'];ground.scale=(1,1,1)
for v in ground.data.vertices:v.co.z=(.84 if v.co.z>0 else -.4)-ground.location.z
for mod in ground.modifiers:
 if mod.type=='BEVEL':mod.width=.045
studio=lookup['Matte studio floor'];studio.scale=(1,1,1);studio.location.z=0
for v in studio.data.vertices:v.co.z=.22 if v.co.z>0 else -.5
# Carve genuine water openings through the ground, retaining live Boolean modifiers.
cutters=coll('Water_Cutters',coll('Campus_Ground'))
for sn in ['Zixia lake','Friendship river']:
 surf=lookup[sn];cutter=surf.copy();cutter.data=surf.data.copy();cutter.name='CUTTER_'+sn;cutters.objects.link(cutter)
 so=cutter.modifiers.new('Water excavation volume','SOLIDIFY');so.thickness=4;so.offset=0
 cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE'
 mod=ground.modifiers.new('Excavate '+sn,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
# The scaled deck approaches are lowered to the motor-road level.
for o in scene.objects:
 sn=o.get('SourceName','')
 if sn.startswith('Road over river'):o.location.z-=.9
 if sn.startswith('Bridge railing'):
  for sp in o.data.splines:
   for p in sp.points:p.co.z=2.08/o.scale.z
# Prevent tree trunks intersecting the existing bridge and footpaths.
for name in ['GN_Road_Trees','GN_Woodland_Random']:
 o=bpy.data.objects[name];pts=[tuple(v.co) for v in o.data.vertices if not((-40.5*S<v.co.x<-15.5*S) and abs(v.co.y-31*S)<2.8)]
 me=bpy.data.meshes.new(name+'_clear_bridge');me.from_pydata(pts,[],[]);o.data=me
# Medium LOD has fuller leaf coverage; distant LOD is a decimated linked version.
for o in list(bpy.data.objects):
 if not(o.name.startswith('Broadleaf_') or o.name.startswith('Metasequoia_')):continue
 if not o.name.endswith(('LOD1','LOD2')):continue
 # Components of exactly seven leaf vertices; branch geometry is untouched.
 me=o.data;edges={}
 for p in me.polygons:
  if p.material_index:
   ids=list(p.vertices)
   for a in ids:edges.setdefault(a,set()).update(ids)
 visited=set();fac=1.85 if o.name.endswith('LOD1') else 1.3
 for start in edges:
  if start in visited:continue
  stack=[start];comp=[];visited.add(start)
  while stack:
   v=stack.pop();comp.append(v)
   for w in edges[v]:
    if w not in visited:visited.add(w);stack.append(w)
  centre=sum((me.vertices[v].co for v in comp),Vector())/len(comp)
  for v in comp:me.vertices[v].co=centre+(me.vertices[v].co-centre)*fac
for o in list(bpy.data.objects):
 if (o.name.startswith('Broadleaf_') or o.name.startswith('Metasequoia_')) and o.name.endswith('LOD0'):
  other=bpy.data.objects.get(o.name[:-1]+'1')
  if other:o.data=other.data;de=o.modifiers.new('Distant crown LOD reduction','DECIMATE');de.ratio=.38
# News-site header contains a correct crest but a news-site wordmark: only use crest UVs.
wrong=bpy.data.objects.get('Official_NJUST_Sign')
if wrong:archive(wrong,'News-site wordmark removed; only the verified university crest is sampled below')
back=bpy.data.objects.get('Official_identity_backing')
if back:
 # mesh is local, so dimensions can be changed after a dependency update.
 bpy.context.view_layer.update();back.dimensions.x=28;back.dimensions.z=4.1
sn=lookup['University name on stone'];relocate(sn,coll('Campus_Signs'));sn.hide_render=False;sn.hide_set(False);sn.pop('SupersededReason',None);sn.data.body='南京理工大学';sn.data.size=1.2;sn.location.x=2.5;sn.location.z=4.17;sn.location.y=-46.51*S-.09
sn.data.materials[0]=material('NJUST_Identity_Ivory','EAE5D7',.48,.1)
idmat=bpy.data.materials['NJUST_Official_Wordmark'];x=-10.7;y=-46.51*S-.09;z=4.03;w=2.8;h=2.8
o=mesh('Verified_University_Crest',[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)],[(0,1,2,3)],[idmat],coll('Campus_Signs'))
uv=o.data.uv_layers.new()
for lp,co in zip(uv.data,[(0,0),(.159,0),(.159,1),(0,1)]):lp.uv=co
text('University_English','NANJING UNIVERSITY OF SCIENCE & TECHNOLOGY',(2.5,y-.01,2.68),.4,bpy.data.materials['NJUST_Identity_Ivory'])
for n,pos,target,lens in [('Camera_Gate',(10,-155,8.4),(0,-73,10),42)]:
 c=bpy.data.objects[n];c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
# Low-rise windows remain LOD1. LOD2 accessories are culled by the supplied control script.
for category in ['Campus_Buildings','Campus_Roads','Campus_Facilities','Campus_Sports','Campus_Vehicles','Campus_People','Campus_Vegetation']:
 c=coll(category)
 for lod in range(3):
  child=coll(category+'_LOD'+str(lod),c)
  for o in list(c.objects):
   lv=int(o.get('LOD',0 if o.get('CoreBuilding') or o.get('SourceName') else 1))
   if lv==lod:relocate(o,child);o['LOD']=lod
scene['LODPolicy']='Geometry Nodes: camera distance controls LOD0/1/2 without realizing instances. Manual LOD2 accessories: update_lod() culls beyond 95 m; supplied renderer and animation invoke it.'
scene['ScaleCaveat']='Uniform 2.2x metric calibration preserves all normalized building footprints. Campus overall distances remain compressed. Low-rise floor spacing and sports footprints remain inherited constraints; see report.'
scene['RendererProfiles']='Cycles OptiX 80 samples denoise; Eevee 32 samples for preview / 16 samples flythrough.'
set_camera('Camera_Master_Aerial');set_lighting('GOLDEN_HOUR');set_engine('CYCLES');update_lod(distance=110)
# Save a machine-readable fidelity and dependency report.
bpy.context.view_layer.update()
cores=[o for o in scene.objects if o.get('CoreBuilding')];errors=[]
for o in cores:
 src=Vector(o['SourcePosition']);delta=(o.location/S-src).length
 if delta>1e-4:errors.append({'object':o.name,'normalised_position_error':delta})
report={'core_buildings_preserved':len(cores),'core_position_errors':errors,'scene_objects':len(scene.objects),'unique_meshes':len({o.data.name for o in scene.objects if o.type=='MESH'}),'linked_collection_instances':sum(o.instance_type=='COLLECTION' for o in scene.objects),'geometry_nodes_systems':[o.name for o in scene.objects if any(md.type=='NODES' for md in o.modifiers)],'tree_variants':8,'shrub_variants':5,'flower_variants':3,'lighting_presets':['DAY','GOLDEN_HOUR','NIGHT'],'cameras':[o.name for o in scene.objects if o.type=='CAMERA' and not o.get('SupersededReason')],'window_count':scene['WindowCount'],'lit_window_fraction':scene['NightLitWindowFraction'],'unit_system':scene.unit_settings.system,'unit_scale':scene.unit_settings.scale_length,'known_limitations':['Compressed original campus distances','Inherited gate and museum silhouettes lack measured references','Practice sports grounds are not full regulation dimensions','Low-rise floor spacing inherited from initial model']}
with open(os.path.join(ROOT,'reports','refinement_audit.json'),'w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
for script in ['lighting.py','render_scene.py']:
 path=os.path.join(ROOT,'scripts',script);t=bpy.data.texts.load(path);t.name='NJUST_'+script
save('NJUST_v04_Refined')
