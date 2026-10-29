import sys,os,bpy,random,json,bmesh
sys.path.insert(0,os.path.dirname(__file__))
import refine_lib as R
from refine_lib import *
random.seed(953)
original=bpy.context.scene;original.name='Original_Backup'
scene=bpy.data.scenes.new('Refined_Version');bpy.context.window.scene=scene;R.scene=scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene['UniformScaleFromOriginal']=S
names=['Campus_Buildings','Campus_Roads','Campus_Ground','Campus_Vegetation','Campus_Sports','Campus_Water','Campus_Facilities','Campus_Signs','Campus_Vehicles','Campus_People','Campus_Lighting','Campus_Cameras','LOD_Assets','Campus_Props','Legacy_Superseded']
for n in names:coll(n)
lookup={};copied={};matcopies={};building_records=[]
def category(o):
 n=o.name;cs=' '.join(c.name for c in o.users_collection)
 if o.type=='CAMERA':return 'Campus_Cameras'
 if o.type=='LIGHT':return 'Campus_Lighting'
 if o.type=='FONT' or 'sign' in n.lower():return 'Campus_Signs'
 if '10 ·' in cs or any(v in n for v in ['梧桐','Clipped shrub','blossoms']):return 'Campus_Vegetation'
 if '08 ·' in cs:return 'Campus_Sports'
 if '09 ·' in cs:return 'Campus_Water'
 if '01 ·' in cs:return 'Campus_Roads'
 if 'Tiny pedestrian' in n:return 'Campus_People'
 if 'Shuttle' in n or 'shuttle' in n:return 'Campus_Vehicles'
 if '00 ·' in cs or n=='Matte studio floor':return 'Campus_Ground'
 if any(v in cs for v in ['02 ·','03 ·','04 ·','05 ·','06 ·','07 ·']):return 'Campus_Buildings'
 return 'Campus_Facilities'
for src in original.objects:
 o=src.copy();o.name=src.name+'__REF'
 if src.data:
  key=(src.type,src.data.name)
  if key not in copied:copied[key]=src.data.copy()
  o.data=copied[key]
  if hasattr(o.data,'materials'):
   for i,m in enumerate(src.data.materials):
    if m:
     if m.name not in matcopies:matcopies[m.name]=m.copy()
     o.data.materials[i]=matcopies[m.name]
 coll(category(src)).objects.link(o);o.location=src.location*S;o.scale=src.scale*S;o['SourceName']=src.name;o['SourcePosition']=list(src.location);lookup[src.name]=o
 if src.type=='CAMERA' and src.data.type=='ORTHO':o.data.ortho_scale*=S
 if src.type=='LIGHT':archive(o,'Original miniature studio lighting replaced by physical presets')
 if src.type=='CAMERA':archive(o,'Preserved original miniature camera')
 if '| facade' in src.name:
  o['CoreBuilding']=True
  building_records.append({'name':src.name,'location':list(src.location),'dimensions':list(src.dimensions)})
# Copy-on-write transforms preserve shared geometry and all original data.
for o in list(scene.objects):
 if o.type=='MESH' and o.data.users==1:
  o.data.transform(Matrix.Diagonal((*o.scale,1)));o.scale=(1,1,1)
  if o.get('CoreBuilding'):
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   for mod in o.modifiers:
    if mod.type=='BEVEL':mod.width=.065;mod.segments=3
for n in ['Floating museum plinth','Brass inlay','Chamfered limestone rim','Title panel','Title / Chinese','Title / English','Edition','Edition number','Front engraved label','Compass north','Compass pointer']:
 if n in lookup:archive(lookup[n],'Presentation plinth retained in Original_Backup; architectural visualization uses a landscape horizon')
ground=lookup['Campus ground'];ground.dimensions.z=1.56
studio=lookup['Matte studio floor'];studio.location.z=-.25;studio.dimensions.z=1
m=palette()
mapping={'Architecture | warm limestone':'Wall_White','Architecture | porcelain trim':'Wall_White','Landscape | pale travertine':'Stone','Architecture | russet brick':'Wall_Brick','Roofs | fired terracotta':'Roof_Red','Roofs | patinated slate':'Roof_Metal','Road | blue grey':'Asphalt','Paths | warm sand':'Sidewalk','Landscape | spring sage':'Grass','Landscape | fresh lawn':'Grass','Trees | cinnamon bark':'Tree_Trunk','Sport | terracotta track':'Running_Track','Sport | blue court':'Basketball_Court','Water | jade':'Water','Studio | oat paper':'Grass','Metal | deep evergreen':'Painted_Metal'}
for o in scene.objects:
 if hasattr(o.data,'materials'):
  for i,ma in enumerate(o.data.materials):
   base=next((k for k in mapping if ma and ma.name.startswith(k)),None)
   if base:o.data.materials[i]=m[mapping[base]]
# Replace identified baked window batches with depth-bearing linked assemblies.
for srcn,o in lookup.items():
 if srcn.startswith('Fine details · Windows') and any(o in c.objects.values() for c in [coll('Campus_Buildings')]):archive(o,'Baked window faces replaced by modular recessed-frame assemblies')
assets={}
for typ,(w,h) in {'A':(1.68,1.48),'B':(1.57,1.52),'C':(1.65,1.32)}.items():
 for litstate in [False,True]:
  b=Build();frame=.065
  for xx in [-w/2,w/2]:b.box((xx,0,0),(frame,.17,h+.13),0)
  for zz in [-h/2,h/2]:b.box((0,0,zz),(w,.17,frame),0)
  b.box((0,-.005,0),(.046,.14,h),0);b.box((0,.027,0),(w-.07,.025,h-.07),1)
  b.box((0,.18,0),(w-.075,.02,h-.07),2)
  # One simple interior plane and a sill; glass is offset in front of wall.
  b.box((0,-.13,-h/2-.1),(w+.2,.44,.1),3)
  if typ=='C':b.box((0,.145,.15),(w-.1,.025,.16),3)
  assets[typ,litstate]=source_asset('Window_Type_'+typ+('_Lit' if litstate else ''),b,[m['Window_Frame'],m['Glass'],m['Interior_Lit'] if litstate else m['Interior_Dark'],m['Concrete']],.008)
# Accessory library, real-world dimensions in metres.
b=Build();b.box((0,0,.36),(.82,.35,.64));b.box((0,-.187,.36),(.68,.025,.48),1)
for i in range(9):b.box((-.31+i*.077,-.21,.36),(.019,.025,.45),0)
for x in [-.3,.3]:b.box((x,.1,.015),(.04,.58,.05),2)
ac=source_asset('AC_Unit',b,[m['Concrete'],m['Interior_Dark'],m['Metal']],.018)
b=Build();b.box((0,0,1.16),(1.8,.18,2.32),0);b.box((0,-.105,1.18),(1.61,.03,2.09),1)
for xx in [-.45,.45]:b.box((xx,-.14,1.16),(.036,.04,2.1),0);b.box((xx+.22,-.21,1.17),(.03,.09,.4),2)
door=source_asset('Door_Main',b,[m['Window_Frame'],m['Glass'],m['Metal']],.009)
b=Build();b.box((0,0,0),(3,1.5,.11),0)
for xx in [-1.35,1.35]:b.beam((xx,-.55,0),(xx,.4,.55),.022,1)
canopy=source_asset('Canopy',b,[m['Glass'],m['Metal']],.01)
b=Build();b.box((0,0,.45),(1.7,1,.9),0)
for xx in [-.5,.5]:
 b.beam((xx,0,.9),(xx,0,1.02),.27,1,20)
 for i in range(6):b.box((xx-.2+i*.08,0,1.03),(.03,.45,.024),2)
hvac=source_asset('Roof_Equipment',b,[m['Roof_Metal'],m['Interior_Dark'],m['Metal']],.025)
window_count=0;lit_count=0
for rec in building_records:
 name=rec['name'];x,y,z=rec['location'];w,d,h=rec['dimensions'];obj=lookup[name]
 dorm='residence' in name.lower() or 'Residence' in name
 old='Historic' in name;lab='Engineering' in name;highest='致远' in name
 floors=11 if highest else 6 if 'Library' in name else 5 if 'courtyard' in name else 4 if ('pavilion' in name or lab or 'Student residence' in name) else 3
 typ='C' if dorm else 'B' if old else 'A';cols=max(2,int(w/1.3));fh=(h-.6)/floors*S
 if dorm or old:obj.data.materials[0]=m['Wall_Warm']
 for j in range(floors):
  zz=(1.45+(j+.5)*(h-.6)/floors)*S
  for i in range(cols):
   xx=(x-w/2+(i+.5)*w/cols)*S
   for side in [-1,1]:
    yy=(y+side*d/2)*S+side*.24
    occupied=random.random()<.3
    o=instance('Window_'+typ,assets[typ,occupied],(xx,yy,zz),0 if side==-1 else pi,lod=1,c=coll('Campus_Buildings'))
    # Height follows the existing floor spacing while width remains plausible.
    o.scale.z=min(1.15,max(.82,fh*.57/1.48));window_count+=1;lit_count+=occupied
   if dorm and (i+j)%2==0:instance('Dormitory_AC',ac,(xx+.65,(y-d/2)*S-.46,zz-1.15),lod=2,c=coll('Campus_Buildings'))
  # Less prominent side elevations use the same shared window asset.
  for side in [-1,1]:
   for k in range(max(1,int(d/1.5))):
    yy=(y-d/2+(k+.5)*d/max(1,int(d/1.5)))*S;xx=(x+side*w/2)*S+side*.24
    occupied=random.random()<.3;instance('Side_Window',assets[typ,occupied],(xx,yy,zz),side*pi/2,lod=1,c=coll('Campus_Buildings'));window_count+=1;lit_count+=occupied
 fy=(y-d/2)*S
 instance('Entrance_Door',door,(x*S,fy-.28,.95),lod=1,c=coll('Campus_Buildings'))
 instance('Entrance_Canopy',canopy,(x*S,fy-.95,3.65),lod=1,c=coll('Campus_Buildings'))
 # Drain pipes are linked cylinders on selected exposed building corners.
 for side in [-1,1]:
  pts=[((x+side*(w/2-.15))*S,fy-.35,(h+.6)*S),((x+side*(w/2-.15))*S,fy-.35,1.13),((x+side*(w/2-.15))*S,fy-.6,1.02)]
  o=curve('Drain_Pipe',pts,.045,m['Roof_Metal'],coll('Campus_Buildings'));o['LOD']=2
 if not(dorm or old or lab):
  rz=(h+1.08)*S
  for px in [-w*.24,w*.24]:instance('Rooftop_HVAC',hvac,((x+px)*S,y*S,rz),lod=1,c=coll('Campus_Buildings'))
  for side in [-1,1]:box('Parapet',(x*S,(y+side*(d/2-.08))*S,rz+.28),(w*S,.17,.56),m['Concrete'],coll('Campus_Buildings'),.045)
  for side in [-1,1]:box('Parapet',((x+side*(w/2-.08))*S,y*S,rz+.28),(.17,d*S,.56),m['Concrete'],coll('Campus_Buildings'),.045)
  if highest:
   for px in [-2,2]:curve('Lightning_Conductor',[((x+px)*S,y*S,rz),((x+px)*S,y*S,rz+2)],.016,m['Metal'],coll('Campus_Buildings'))
 if lab:
  for px in [-2,2]:
   o=curve('Laboratory_Exhaust',[((x+px)*S,y*S,(h+1)*S),((x+px)*S,y*S,(h+2.7)*S),((x+px+.5)*S,y*S,(h+2.7)*S)],.16,m['Roof_Metal'],coll('Campus_Buildings'));o['LOD']=1
 # Explicitly distinguish generic building identifiers from verified names.
 label='致远楼' if highest else '图书馆' if 'Library' in name else '教学区' if not dorm else '生活区'
 text('Building_Sign',label,(x*S,fy-.3,4.08),.4,m['Painted_Metal'])
 # Low-rise entry step: 3 x 150 mm, with a gentle adjacent ramp.
 for j in range(3):box('Entrance_Step',(x*S,fy-.55-j*.27,.95+j*.15),(2.6,1.7-j*.27,.15),m['Stone'],coll('Campus_Facilities'),.018)
 vs=[(x*S+1.5,fy-2,.94),(x*S+3,fy-2,.94),(x*S+3,fy+.15,1.39),(x*S+1.5,fy+.15,1.39)]
 mesh('Accessible_Ramp',vs,[(0,1,2,3)],[m['Sidewalk']],coll('Campus_Facilities'))
# Restore recessed entry glazing hidden with the old batches in the tower.
box('Zhiyuan_Glass_Lobby',(0,10.9*S,3.7),(5.6,.12,5.3),m['Glass'],coll('Campus_Buildings'))
# Original curved library sheets stay in place; deepen their existing mullions.
for o in coll('Campus_Buildings').objects:
 if o.get('SourceName','').startswith('Fine details · Architecture'):
  mod=o.modifiers.new('Fine edge highlight','BEVEL');mod.width=.012;mod.segments=2
# Street hierarchy: existing centre lines are retained; raised sidewalks and curbs are added.
roads=coll('Campus_Roads');streetblocks=Build();curbblocks=Build();tactile=Build()
for xx in [-18,18,-48,48]:
 for sy in range(-47,50,3):
  if any(abs(sy-yy)<2.5 for yy in [-43,-25,5,26,45]):continue
  if sy in range(21,26):continue
  for side in [-1,1]:
   x=xx*S+side*(3.5*S/2+.66);y=sy*S
   # Basketball strip occupies the outer west verge.
   if xx==-48 and side==-1 and -24<sy<17:continue
   streetblocks.box((x,y,.96),(1.2,6.53,.17))
   curbblocks.box((xx*S+side*(3.5*S/2+.08),y,.982),(.16,6.55,.22))
   if xx in [-18,18]:
    tactile.box((x,y,1.055),(.3,6.5,.025))
for yy in [-43,-25,5,45]:
 for x in range(-46,48,3):
  if any(abs(x-xx)<2.5 for xx in [-48,-18,18,48]):continue
  if yy==5 and x<-32:continue
  for side in [-1,1]:
   streetblocks.box((x*S,yy*S+side*(3.3*S/2+.65),.96),(6.53,1.15,.17))
   curbblocks.box((x*S,yy*S+side*(3.3*S/2+.08),.982),(6.55,.16,.22))
streetblocks.finish('Raised_Sidewalks',[m['Sidewalk']],roads,.025);curbblocks.finish('Bevelled_Curbs_160mm',[m['Stone']],roads,.018);tactile.finish('Tactile_Guidance_Strips',[m['Tactile']],roads,.008)
road_details=Build()
for xx in [-18,18]:
 for yy in [-36,-16,14,38]:
  x,y=xx*S,yy*S
  # Direction arrows in two traffic lanes.
  for side in [-1,1]:
   ax=x+side*1.75
   road_details.box((ax,y,.904),(.11,1.6,.012),0)
   road_details.box((ax-side*.22,y+side*.7,.904),(.11,.65,.012),0,side*.65)
   road_details.box((ax+side*.22,y+side*.7,.904),(.11,.65,.012),0,-side*.65)
  road_details.box((x+2.8,y+4,.91),(.55,.55,.035),1)
  for j in range(6):road_details.box((x+2.6+j*.08,y+4,.935),(.025,.48,.009),2)
for yy in [-39,41]:
 for i in range(8):road_details.box((18*S-3+i*.8,yy*S,.97),(.77,.38,.15),3 if i%2 else 2)
rd=road_details.finish('Road_Arrows_Drains_Speed_Bumps',[m['Marking_White'],m['Metal'],m['Painted_Metal'],m['Tactile']],roads,.005);rd['LOD']=2
# Correct the verified institutional text without inventing a new landmark shape.
lookup['Motto on second gate'].data.body='团结  献身  求是  创新'
lookup['School spirit'].data.body='团结  献身  求是  创新'
lookup['University name on stone'].data.extrude=.015
lookup['University name on stone'].data.materials[0]=material('Lettering_Bronze','9C8452',.3,.7)
scene['WindowCount']=window_count;scene['NightLitWindowFraction']=lit_count/window_count
scene['BuildingRecords']=json.dumps(building_records,ensure_ascii=False)
scene['IdentityCaveat']='Inherited gate, museum and unnamed blocks retain source silhouettes; not verified as exact replicas. Do not infer survey accuracy.'
with open(os.path.join(ROOT,'reports','stage1.json'),'w',encoding='utf-8') as f:json.dump({'core_buildings':len(building_records),'windows':window_count,'lit_fraction':lit_count/window_count,'scale':S,'preserves_normalized_building_positions':True},f,indent=2)
save('NJUST_v01_Buildings_Roads')
