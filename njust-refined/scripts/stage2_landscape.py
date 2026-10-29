import sys,os,bpy,random,json,math
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
random.seed(195309)
scene=bpy.context.scene;m=palette();records=json.loads(scene['BuildingRecords'])
def clear_area(x,y,margin=0):
 for r in records:
  bx,by,_=r['location'];w,d,_=r['dimensions']
  if abs(x-bx*S)<w*S/2+margin and abs(y-by*S)<d*S/2+margin:return False
 # Preserve library's curved envelope and museum footprint.
 if -29<x<29 and -44<y<-19:return False
 if (x-31*S)**2+(y+33*S)**2<(7.5*S+margin)**2:return False
 return True
for o in list(scene.objects):
 if o.name.startswith('Entrance_Door'):o.location.z=1.76
 if o.name.startswith('Entrance_Canopy'):o.location.z=4.6
 if o.name.startswith('Entrance_Step') or o.name.startswith('Accessible_Ramp'):archive(o,'Replaced with measured 150 mm steps and 1:12 access ramp')
 if '| plinth' in o.get('SourceName',''):o.dimensions.z=.8;o.location.z=1.36
 # Old two-metre benches and toy pedestrians are kept in the archive.
 sn=o.get('SourceName','')
 if any(sn.startswith(s) for s in ['Bench','Lamp','Tiny pedestrian','Shuttle','Campus electric shuttle','Clipped shrub','Canopy support']):archive(o,'Replaced by metric linked props')
 if any(sn.startswith(s) for s in ['Fine details · Metal','Fine details · Windows']) and o.users_collection and o.users_collection[0].name=='Campus_Facilities':archive(o,'Superseded original furniture batch')
for r in records:
 x,y,_=r['location'];w,d,h=r['dimensions'];fy=(y-d/2)*S
 b=Build()
 for j in range(5):b.box((x*S,fy-1.7+j*.3,1.04+j*.15),(2.6,1.8-j*.3,.15))
 b.finish('Stair_150mm',[m['Stone']],coll('Campus_Facilities'),.014)
 # Parallel ramp uses frontage rather than entering the motor lane.
 verts=[(x*S-5,fy-2,.98),(x*S-5,fy-.6,.98),(x*S+4.6,fy-.6,1.78),(x*S+4.6,fy-2,1.78)]
 ramp=mesh('Ramp_1_to_12',verts,[(0,3,2,1)],[m['Sidewalk']],coll('Campus_Facilities'));ramp['slope']=1/12;ramp['LOD']=2
 curve('Ramp_Handrail',[(x*S-5,fy-2,1.85),(x*S+4.6,fy-2,2.65)],.027,m['Metal'],coll('Campus_Facilities'))['LOD']=2
# Recreate the curved library glass in front of the inherited mullions.
lib=Build()
for floor in range(6):
 for i in range(32):
  x=-12.5+(i+.5)*25/32;yy=-17.3-2.4*(x/12.5)**2
  if abs(x)<3.25 and floor<3:continue
  z=.85+floor*1.55+.7;rot=math.atan(-4.8*x/12.5**2)
  lib.box((x*S,yy*S-.05,z*S),(.7*S,.045,1.25*S),0,rot)
  lib.box((x*S,yy*S+.1,z*S),(.68*S,.03,1.22*S),2 if random.random()<.3 else 1,rot)
lib.finish('Library_Curved_Glazing',[m['Glass'],m['Interior_Dark'],m['Interior_Lit']],coll('Campus_Buildings'),.007)
for side in [-1,1]:
 for k in range(12):
  y=(-16.7+k*.45)*S
  box('Library_metal_screen',(side*12.93*S,y,5.3*S),(.1,.09,8.8*S),m['Window_Frame'],coll('Campus_Buildings'),.005)
# Build reusable plant assets. Crowns are branching leaf meshes, not solid faceted blobs.
leaves=[material('Tree_Leaf_'+str(i),c,.77,0,9,.003) for i,c in enumerate(['405D34','526B3A','697C46','768651','8A945A'])]
tree_mats=[m['Tree_Trunk']]+leaves
def treeasset(idx,lod):
 conifer=idx>=5;rr=random.Random(3200+idx);b=Build();height=8+idx*.25 if not conifer else 11+(idx-5)*1.1
 b.beam((0,0,0),(.09,.08,height*.81),.17 if not conifer else .19,0,9,.035)
 nbranch=12 if lod==0 else 20 if lod==1 else 28
 for j in range(nbranch):
  angle=rr.random()*2*pi;z=rr.uniform(height*.38,height*.84)
  radius=(1-(z/height))*(4.6 if conifer else 5.7)+.2
  end=Vector((radius*cos(angle),radius*sin(angle),z+rr.uniform(.2,1.1)))
  start=Vector((.04,0,z-.6));b.beam(start,end,.045,0,6,.009)
  if lod==0:
   for k in range(6):
    center=end+Vector((rr.uniform(-.4,.4),rr.uniform(-.4,.4),rr.uniform(-.4,.5)))
    b.leaf(center,.8,.65,rr.randint(1,5),(rr.random()*pi,rr.random()*pi,rr.random()*pi))
  else:
   clumps=3 if lod==1 else 5
   for k in range(clumps):
    cc=end+Vector((rr.uniform(-.65,.65),rr.uniform(-.65,.65),rr.uniform(-.35,.6)))
    b.beam(end,cc,.012,0,5,.003)
    count=20 if lod==1 else 34
    for q in range(count):
     a=rr.random()*2*pi;rad=rr.random()**.5*.55
     center=cc+Vector((rad*cos(a),rad*sin(a),rr.uniform(-.4,.4)))
     b.leaf(center,rr.uniform(.14,.25) if not conifer else .22,rr.uniform(.085,.145),rr.randint(1,5),(rr.random()*2*pi,rr.uniform(-1,1),rr.uniform(-1,1)))
 if conifer:
  for k in range(90 if lod else 20):
   z=rr.uniform(height*.72,height);a=rr.random()*2*pi;rad=(1-z/height)*2.7
   b.leaf((rad*cos(a),rad*sin(a),z),.28,.12,rr.randint(1,5),(a,rr.random(),rr.random()))
 c=source_asset(('Broadleaf' if not conifer else 'Metasequoia')+'_%02d_LOD%d'%(idx,lod),b,tree_mats)
 for o in c.objects:
  for p in o.data.polygons:p.use_smooth=p.material_index==0
 return c
def bank(name,assets):
 c=bpy.data.collections.new(name)
 for a in assets:
  for o in a.objects:c.objects.link(o)
 return c
trees={lod:[treeasset(i,lod) for i in range(8)] for lod in range(3)}
treebanks={lod:bank('TREE_BANK_LOD'+str(lod),trees[lod]) for lod in range(3)}
cedarbanks={lod:bank('CEDAR_BANK_LOD'+str(lod),trees[lod][5:]) for lod in range(3)}
broadbanks={lod:bank('BROADLEAF_BANK_LOD'+str(lod),trees[lod][:5]) for lod in range(3)}
lodref=bpy.data.objects.new('LOD_Camera_Reference',None);coll('LOD_Assets').objects.link(lodref);lodref.location=(190,-230,170);lodref.hide_render=True
def scatter(name,points,banks,count,category='Campus_Vegetation',density=1,scale=(.75,1.25),rotation=2*pi,distance=90):
 me=bpy.data.meshes.new(name+'_Points');me.from_pydata(points,[],[]);o=bpy.data.objects.new(name,me);coll(category).objects.link(o)
 ng=bpy.data.node_groups.new(name+'_GeometryNodes','GeometryNodeTree');ng.is_modifier=True
 def socket(n,t,io='INPUT',default=None,lo=None,hi=None):
  s=ng.interface.new_socket(name=n,in_out=io,socket_type=t)
  if default is not None:s.default_value=default
  if lo is not None:s.min_value=lo
  if hi is not None:s.max_value=hi
  return s
 socket('Geometry','NodeSocketGeometry');socket('Geometry','NodeSocketGeometry','OUTPUT')
 for n,t,v,lo,hi in [('Density','NodeSocketFloat',density,0,1),('Random Seed','NodeSocketInt',1953,0,999999),('Scale Min','NodeSocketFloat',scale[0],.1,3),('Scale Max','NodeSocketFloat',scale[1],.1,3),('Rotation','NodeSocketFloat',rotation,0,2*pi),('Distance','NodeSocketFloat',distance,10,400)]:socket(n,t,default=v,lo=lo,hi=hi)
 n=ng.nodes;l=ng.links;inp=n.new('NodeGroupInput');inp.location=(-950,0);out=n.new('NodeGroupOutput');out.location=(850,50)
 index=n.new('GeometryNodeInputIndex');index.location=(-950,-500)
 rnd=n.new('FunctionNodeRandomValue');rnd.data_type='FLOAT';rnd.inputs['Min'].default_value=0;rnd.inputs['Max'].default_value=1;l.new(inp.outputs['Random Seed'],rnd.inputs['Seed']);l.new(index.outputs[0],rnd.inputs['ID'])
 keep=n.new('ShaderNodeMath');keep.operation='LESS_THAN';l.new(rnd.outputs['Value'],keep.inputs[0]);l.new(inp.outputs['Density'],keep.inputs[1])
 pos=n.new('GeometryNodeInputPosition');cam=n.new('GeometryNodeObjectInfo');cam.inputs['Object'].default_value=lodref
 dist=n.new('ShaderNodeVectorMath');dist.operation='DISTANCE';l.new(pos.outputs[0],dist.inputs[0]);l.new(cam.outputs['Location'],dist.inputs[1])
 near=n.new('ShaderNodeMath');near.operation='LESS_THAN';l.new(dist.outputs['Value'],near.inputs[0]);l.new(inp.outputs['Distance'],near.inputs[1])
 farlimit=n.new('ShaderNodeMath');farlimit.operation='MULTIPLY';farlimit.inputs[1].default_value=2;l.new(inp.outputs['Distance'],farlimit.inputs[0])
 mid=n.new('ShaderNodeMath');mid.operation='LESS_THAN';l.new(dist.outputs['Value'],mid.inputs[0]);l.new(farlimit.outputs[0],mid.inputs[1])
 midonly=n.new('ShaderNodeMath');midonly.operation='SUBTRACT';l.new(mid.outputs[0],midonly.inputs[0]);l.new(near.outputs[0],midonly.inputs[1])
 far=n.new('ShaderNodeMath');far.operation='SUBTRACT';far.inputs[0].default_value=1;l.new(mid.outputs[0],far.inputs[1])
 size=n.new('FunctionNodeRandomValue');size.data_type='FLOAT';l.new(inp.outputs['Scale Min'],size.inputs['Min']);l.new(inp.outputs['Scale Max'],size.inputs['Max']);l.new(inp.outputs['Random Seed'],size.inputs['Seed'])
 ang=n.new('FunctionNodeRandomValue');ang.data_type='FLOAT';ang.inputs['Min'].default_value=0;l.new(inp.outputs['Rotation'],ang.inputs['Max']);l.new(inp.outputs['Random Seed'],ang.inputs['Seed'])
 combine=n.new('ShaderNodeCombineXYZ');l.new(ang.outputs['Value'],combine.inputs['Z'])
 pick=n.new('FunctionNodeRandomValue');pick.data_type='INT';pick.inputs['Min'].default_value=0;pick.inputs['Max'].default_value=max(0,count-1);l.new(inp.outputs['Random Seed'],pick.inputs['Seed'])
 join=n.new('GeometryNodeJoinGeometry');join.location=(650,50)
 for lod,mask in [(0,far),(1,midonly),(2,near)]:
  ci=n.new('GeometryNodeCollectionInfo');ci.inputs['Collection'].default_value=banks[lod];ci.inputs['Separate Children'].default_value=True;ci.inputs['Reset Children'].default_value=True;ci.location=(-200,350-lod*300)
  select=n.new('ShaderNodeMath');select.operation='MULTIPLY';l.new(keep.outputs[0],select.inputs[0]);l.new(mask.outputs[0],select.inputs[1])
  inst=n.new('GeometryNodeInstanceOnPoints');inst.location=(320,350-lod*300);inst.inputs['Pick Instance'].default_value=True;l.new(inp.outputs['Geometry'],inst.inputs['Points']);l.new(select.outputs[0],inst.inputs['Selection']);l.new(ci.outputs['Instances'],inst.inputs['Instance']);l.new(pick.outputs['Value'],inst.inputs['Instance Index']);l.new(size.outputs['Value'],inst.inputs['Scale']);l.new(combine.outputs[0],inst.inputs['Rotation']);l.new(inst.outputs[0],join.inputs[0])
 l.new(join.outputs[0],out.inputs[0]);mod=o.modifiers.new('Parametric distribution & distance LOD','NODES');mod.node_group=ng;o['SourcePointCount']=len(points);o['LOD_Distance_m']=distance;return o
roadtrees=[];woodtrees=[]
for o in list(scene.objects):
 sn=o.get('SourceName','')
 if sn.startswith('梧桐') or sn.startswith('水杉'):
  x,y,_=o.location
  if sn.startswith('水杉'):
   x+=random.uniform(-1.1,1.1);y+=random.uniform(-1.1,1.1)
   if clear_area(x,y,1.1):woodtrees.append((x,y,.91))
  elif clear_area(x,y,2):roadtrees.append((x+random.uniform(-.15,.15),y+random.uniform(-.15,.15),.91))
  archive(o,'Leaf-and-branch Geometry Nodes tree instances replace solid low-poly crowns')
scatter('GN_Road_Trees',roadtrees,broadbanks,5,distance=110)
scatter('GN_Woodland_Random',woodtrees,cedarbanks,3,distance=115)
# A low-cost context belt softens the inherited model boundary in eye-level shots.
belt=[]
for i in range(120):
 a=i*2*pi/120;r=random.uniform(151,169);belt.append((r*cos(a),r*sin(a),.28))
scatter('GN_Context_Tree_Belt',belt,broadbanks,5,scale=(.8,1.4),distance=75)
# Five shrubs and three ground-cover flowers, kept as shared assets.
shrubassets=[]
for k in range(5):
 b=Build();rr=random.Random(300+k)
 for j in range(220):
  a=rr.random()*2*pi;r=rr.random()**.5*.48;z=rr.uniform(.15,.7)
  b.leaf((r*cos(a),r*sin(a),z),.12,.065,rr.randrange(1,6),(a,rr.random(),rr.random()))
 shrubassets.append(source_asset('Shrub_Variant_'+str(k),b,tree_mats))
sb=bank('Shrub_Bank',shrubassets)
shrubpoints=[]
for xx in [-14,14]:
 for yy in range(-20,20,2):
  x,y=xx*S,yy*S
  if clear_area(x,y,.7):shrubpoints.append((x,y,.95))
for x,y in [(-12,-38),(12,-38),(-12,-29),(12,-29),(26,27),(41,27)]:
 for k in range(6):shrubpoints.append((x*S+k*.55,y*S,.98))
scatter('GN_Shrubs',shrubpoints,{i:sb for i in range(3)},5,distance=70)
flowercolors=[material('Flower_Violet','9380B3',.77,0,25,.001),material('Flower_Lilac','B4A5CA',.73,0,25,.001),material('Flower_Pale','CDC2D8',.79,0,25,.001)]
flowerassets=[]
for k in range(3):
 b=Build()
 for j in range(5):
  x,y=random.uniform(-.14,.14),random.uniform(-.14,.14);z=random.uniform(.16,.33);b.beam((x,y,0),(x,y,z),.005,0,5)
  for p in range(4):a=p*pi/2;b.leaf((x+.029*cos(a),y+.029*sin(a),z),.07,.038,1,(a,0,.2))
 flowerassets.append(source_asset('Flower_Variant_'+str(k),b,[leaves[2],flowercolors[k]]))
fb=bank('Flowers_Bank',flowerassets)
flpts=[]
for px,py,w,d in [(32,35.5,24,14),(-8,36,12,9),(-43,33,4,14)]:
 for i in range(int(w*d*1.5)):
  x=(px+random.uniform(-w/2,w/2))*S;y=(py+random.uniform(-d/2,d/2))*S
  if clear_area(x,y,.3):flpts.append((x,y,.99))
scatter('GN_Close_Flowerbeds',flpts,{i:fb for i in range(3)},3,density=.8,scale=(.8,1.15),distance=65)
for o in scene.objects:
 if o.get('SourceName','').startswith('Violet woodland floor'):
  o.data.materials[0]=material('Flowerbed_Ground','6B6655',.98,0,30,.02)
 if o.get('SourceName','').startswith('二月兰'):
  for i,ma in enumerate(o.data.materials):o.data.materials[i]=flowercolors[i%3]
grass=Build()
for j in range(8):
 a=random.random()*2*pi;x=random.uniform(-.1,.1);y=random.uniform(-.1,.1);grass.leaf((x,y,.09),.21,.012,j%len(leaves),(a,1.3,.2))
ga=source_asset('Ground_Cover_Grass',grass,leaves);gb=bank('Grass_Bank',[ga]);gp=[]
for i in range(700):
 x=random.uniform(20,44)*S;y=random.uniform(28,42)*S
 if clear_area(x,y,.2):gp.append((x,y,.96))
scatter('GN_Local_Grass',gp,{i:gb for i in range(3)},1,density=.5,distance=35)
# Campus props library: one mesh per reusable module, no per-instance duplication.
props={}
def prop(name,b,mats,bevel=.012):
 c=source_asset(name,b,mats,bevel);props[name]=c;return c
b=Build();b.beam((0,0,0),(0,0,5.7),.055,0,12);b.beam((0,0,5.45),(.7,0,5.7),.034,0,10);b.box((.63,0,5.7),(.7,.3,.1),0);b.box((.63,0,5.637),(.58,.25,.025),1);prop('Street_Lamp',b,[m['Painted_Metal'],m['Luminaire']])
b=Build()
for j in range(5):b.box((0,-.2+j*.1,.46),(1.6,.075,.055),0)
for z in [.65,.78,.91]:b.box((0,.26,z),(1.6,.05,.085),0)
for x in [-.58,.58]:b.box((x,0,.23),(.06,.45,.46),1);b.box((x,.24,.66),(.04,.04,.53),1)
prop('Bench',b,[m['Wood'],m['Painted_Metal']])
b=Build();b.box((0,0,.43),(.5,.42,.86),0);b.box((0,0,.89),(.55,.47,.06),1);b.box((0,-.22,.73),(.34,.025,.11),1);prop('Waste_Bin',b,[m['Painted_Metal'],m['Metal']])
b=Build();b.beam((0,0,0),(0,0,.7),.095,0,12);b.beam((-.2,0,.52),(.2,0,.52),.055,0,12);b.box((0,0,.73),(.22,.22,.08),0);prop('Fire_Hydrant',b,[material('Hydrant_Red','9F4D3E',.45,.15)])
b=Build();b.box((0,0,.65),(.8,.43,1.3),0);b.box((0,-.23,.72),(.71,.02,1.05),1);prop('Electrical_Cabinet',b,[m['Concrete'],m['Painted_Metal']])
b=Build();b.beam((0,0,0),(0,0,.76),.075,0,12);b.beam((0,0,.54),(0,0,.59),.079,1,12);prop('Bollard',b,[m['Stone'],m['Metal']])
b=Build();b.box((0,0,.32),(1.25,.56,.64),0)
for i in range(20):b.leaf((random.uniform(-.5,.5),random.uniform(-.2,.2),random.uniform(.6,.95)),.22,.12,1,(random.random()*pi,.4,.2))
prop('Flower_Planter',b,[m['Concrete'],leaves[2]])
b=Build()
for x in [-.52,.52]:b.beam((x,0,0),(x,0,.75),.023,0,10)
b.beam((-.52,0,.75),(.52,0,.75),.023,0,10);prop('Bicycle_Rack',b,[m['Metal']])
# Road bicycle, 1.78 m wheelbase envelope, and a small electric scooter.
for electric in [False,True]:
 b=Build()
 for x in [-.56,.56]:
  n=28
  for j in range(n):
   a=j*2*pi/n;aa=(j+1)*2*pi/n;b.beam((x+.31*cos(a),0,.33+.31*sin(a)),(x+.31*cos(aa),0,.33+.31*sin(aa)),.024,0,5)
  for j in range(8):
   a=j*2*pi/8;b.beam((x,0,.33),(x+.28*cos(a),0,.33+.28*sin(a)),.005,1,4)
 for a,bb in [((-.56,0,.33),(-.1,0,.72)),((-.1,0,.72),(.18,0,.33)),((.18,0,.33),(-.56,0,.33)),((-.1,0,.72),(.48,0,.78)),((.48,0,.78),(.56,0,.33)),((.18,0,.33),(.48,0,.78))]:b.beam(a,bb,.025,2,8)
 b.beam((-.1,0,.7),(-.12,0,.9),.02,1);b.box((-.16,0,.92),(.23,.14,.045),0);b.beam((.48,0,.78),(.43,0,1.03),.023,1);b.beam((.43,-.23,1.03),(.43,.23,1.03),.021,1)
 if electric:b.box((0,0,.5),(.45,.24,.3),2)
 prop('Electric_Bike' if electric else 'Bicycle',b,[m['Painted_Metal'],m['Metal'],material('Bicycle_Paint','597879',.35,.35)],.002)
b=Build()
for x in [-2.7,2.7]:
 for y in [-1,1]:b.beam((x,y,0),(x,y,2.5),.045,0,10)
b.box((0,0,2.56),(6,2.7,.12),1);prop('Shelter',b,[m['Metal'],m['Roof_Metal']])
b=Build();b.box((0,0,1.05),(2.4,.5,2.1),0)
for x in [-.8,0,.8]:
 for z in [.38,1.03,1.68]:b.box((x,-.264,z),(.73,.035,.6),1)
prop('Parcel_Lockers',b,[m['Painted_Metal'],m['Concrete']])
b=Build();b.box((0,0,.95),(.85,.7,1.9),0);b.box((0,-.365,1.12),(.62,.025,1.1),1);prop('Vending_Machine',b,[m['Painted_Metal'],m['Glass']])
b=Build()
for x in [-.9,.9]:b.beam((x,0,0),(x,0,2.1),.035,0,10)
b.box((0,0,1.5),(2.2,.12,1.2),1);b.box((0,-.08,1.5),(2,.025,1),2);prop('Notice_Board',b,[m['Metal'],m['Painted_Metal'],m['Wall_White']])
b=Build();b.beam((0,0,0),(0,0,2.5),.035,0);b.box((0,0,2.18),(.52,.12,.55),1);prop('Campus_Shuttle_Stop',b,[m['Metal'],m['Painted_Metal']])
lamppts=[]
for xx in [-15.4,15.4]:
 for yy in range(-40,44,8):
  x,y=xx*S,yy*S
  if clear_area(x,y,.2):lamppts.append((x,y,1.04))
lpbank=bank('Lamp_Bank',[props['Street_Lamp']]);scatter('GN_Lamp_Array',lamppts,{i:lpbank for i in range(3)},1,'Campus_Facilities',scale=(1,1),rotation=0,distance=95)
scene['LampPoints']=json.dumps(lamppts)
bikepts=[]
for i,(x,y) in enumerate([(-40,-31),(-28,-31),(-39,45.7),(-27,45.7),(40,-20),(28,-20)]):
 # Shelters are located in entrance forecourts, outside road lanes.
 cx=x*S;cy=y*S
 instance('Bike_Shelter',props['Shelter'],(cx,cy,1.02),lod=1)
 for k in range(7):bikepts.append((cx-2.3+k*.7,cy,.99));instance('Bike_Rack',props['Bicycle_Rack'],(cx-2.3+k*.7,cy+.45,1.02),pi/2,lod=2)
 if i<2:instance('Parcel_Lockers',props['Parcel_Lockers'],(cx+5,cy,1.02),lod=2)
bb=bank('Bike_Bank',[props['Bicycle'],props['Electric_Bike']]);scatter('GN_Bicycle_Parking',bikepts,{i:bb for i in range(3)},2,'Campus_Vehicles',scale=(.95,1.05),rotation=.15,distance=85)
for i,r in enumerate(records):
 x,y,_=r['location'];w,d,_=r['dimensions'];fy=(y-d/2)*S
 for label,dx in [('Waste_Bin',-3.2),('Bollard',2.2),('Flower_Planter',-4.5)]:
  xx=x*S+dx;yy=fy-2.8
  if clear_area(xx,yy,.1):instance(label,props[label],(xx,yy,1.03),lod=2)
 if i%4==0:instance('Fire_Hydrant',props['Fire_Hydrant'],((x+w/2+.5)*S,fy-1,1.02),lod=2)
for x,y in [(-12,-29),(12,-29),(-40,31),(-15,38),(23,27.8),(40,27.8),(-24,40)]:
 instance('Bench',props['Bench'],(x*S,y*S,1.02),lod=2)
for label,x,y in [('Notice_Board',12,-30),('Notice_Board',-13,9),('Electrical_Cabinet',44,-21),('Electrical_Cabinet',-45,-32),('Campus_Shuttle_Stop',15,-41),('Vending_Machine',-24,-31)]:instance(label,props[label],(x*S,y*S,1.03),lod=2)
# Real-height low-cost people with articulated limbs and shared meshes.
skin=material('Skin','BE9675',.76);clothes=[material('Clothes_'+str(i),c,.84) for i,c in enumerate(['506C72','CDC7AF','6F5951','8F8E82'])]
humans=[]
for j in range(4):
 b=Build();b.beam((0,0,.77),(0,0,1.38),.14,1,10,.19)
 b.beam((0,0,1.43),(0,0,1.63),.095,0,12,.095)
 for side in [-1,1]:
  b.beam((side*.105,0,.83),(side*.13,side*.06,.4),.068,2,8,.049);b.beam((side*.13,side*.06,.4),(side*.12,side*.13,.06),.043,2,8,.035)
  b.box((side*.12,side*.13-.04,.05),(.12,.25,.1),2)
  b.beam((side*.18,0,1.29),(side*.26,side*.06,1.02),.047,1,8,.032);b.beam((side*.26,side*.06,1.02),(side*.22,side*.16,.82),.031,0,8,.026)
 # Smooth small head ellipsoid via lathe-like stacked rings.
 k=len(b.v);n=12
 for z,rad in [(1.52,.07),(1.59,.105),(1.68,.07),(1.71,.012)]:
  for q in range(n):a=2*pi*q/n;b.v.append((rad*cos(a),rad*.9*sin(a),z))
 for ring in range(3):
  for q in range(n):b.f.append((k+ring*n+q,k+ring*n+(q+1)%n,k+(ring+1)*n+(q+1)%n,k+(ring+1)*n+q));b.i.append(0)
 humans.append(source_asset('Person_1p71m_'+str(j),b,[skin,clothes[j],m['Painted_Metal']]))
hb=bank('People_Bank',humans);pp=[]
for i in range(38):
 if i<22:x=random.choice([-15.7,15.7])*S;y=random.uniform(-40,40)*S
 else:x=random.uniform(-12,12)*S;y=random.uniform(-39,-37)*S
 if clear_area(x,y,.25):pp.append((x,y,1.05))
pp.extend([(-39*S+2,5*S,1.35),(-39*S-2,-1*S,1.35),(-53*S,11*S,1.15)])
scatter('GN_Pedestrian_Life',pp,{i:hb for i in range(3)},4,'Campus_People',scale=(.96,1.04),distance=90)
# Modest campus service fleet, all cars have a 1.8 m body width.
cars=[]
for k in range(3):
 b=Build();b.box((0,0,.62),(1.8,4.25,.73),0);b.box((0,-.15,1.13),(1.59,2.12,.55),1)
 for xx in [-.87,.87]:
  for yy in [-1.25,1.25]:b.beam((xx-.07,yy,.35),(xx+.07,yy,.35),.31,2,16)
 for xx in [-.56,.56]:b.box((xx,-2.14,.7),(.42,.025,.14),3)
 cars.append(source_asset('Car_1p8m_'+str(k),b,[material('Car_Paint_'+str(k),['B9B9AB','7C898B','5B686B'][k],.25,.4),m['Glass'],m['Painted_Metal'],m['Luminaire']],.12))
cb=bank('Car_Bank',cars);cp=[(18*S+1.8,-15*S,.9),(-18*S-1.8,-30*S,.9),(48*S+1.8,12*S,.9),(-48*S+1.8,38*S,.9)]
scatter('GN_Parking_Vehicles',cp,{i:cb for i in range(3)},3,'Campus_Vehicles',scale=(1,1),rotation=0,distance=110)
# Water: lower the transparent surface beneath the stone coping; add dark beds.
for o in list(coll('Campus_Water').objects):
 sn=o.get('SourceName','')
 if sn in ['Zixia lake','Friendship river']:
  # World-space vertex z is converted through the inherited object's scale.
  bed=o.copy();bed.data=o.data.copy();bed.name='Water_Bed_'+sn;coll('Campus_Water').objects.link(bed)
  for v in bed.data.vertices:v.co.z=(.35-bed.location.z)/bed.scale.z
  bed.data.materials.clear();bed.data.materials.append(m['Soil'])
  for v in o.data.vertices:v.co.z=(.79-o.location.z)/o.scale.z
 if sn=='Quiet water ripples' or sn.startswith('Quiet water ripples'):archive(o,'Procedural water normals replace decorative drawn ripple strokes')
reeds=Build()
for i in range(170):
 a=random.uniform(0,2*pi);x=(-28+10.6*cos(a))*S;y=(31+6.4*sin(a))*S
 if abs(y-31*S)<2.4:continue
 reeds.beam((x,y,.76),(x+random.uniform(-.08,.08),y,random.uniform(1.2,1.8)),.008,0,5)
 for j in range(2):reeds.leaf((x,y,1+j*.15),.5,.025,1,(a,.8,.4))
reeds.finish('Lakeside_Reeds',[m['Tree_Trunk'],leaves[2]],coll('Campus_Water'))['LOD']=2
# Sports: keep the inherited grounds; correct sports equipment to real dimensions.
for o in list(coll('Campus_Sports').objects):
 sn=o.get('SourceName','')
 if any(sn.startswith(t) for t in ['Goal frame','Goal net','Hoop post','Court line','Court centre circle','Court centre stripe']):archive(o,'Measured goal/hoop geometry and practice-court markings replace scaled miniature equipment')
for yy in [5*S-6.65*S,5*S+6.65*S]:
 x=-39*S;b=Build();b.beam((x-1.5,yy,1.33),(x-1.5,yy,3.33),.04,0,10);b.beam((x+1.5,yy,1.33),(x+1.5,yy,3.33),.04,0,10);b.beam((x-1.5,yy,3.33),(x+1.5,yy,3.33),.04,0,10)
 side=1 if yy>5*S else -1
 for i in range(21):b.beam((x-1.5+i*.15,yy,3.33),(x-1.5+i*.15,yy+side*.8,1.33),.007,0,4)
 b.finish('Practice_Football_Goal_3x2m',[m['Marking_White']],coll('Campus_Sports'))
for yy in [-20,-11,0,11]:
 x=-53*S;y=yy*S;b=Build();groundz=1.11
 # One hoop per retained narrow court: explicitly a practice court, not a regulation arena.
 b.beam((x,y+5.7,groundz),(x,y+5.7,groundz+3.45),.075,0,12);b.beam((x,y+5.7,groundz+3.2),(x,y+4.7,groundz+3.2),.055,0,10);b.box((x,y+4.7,groundz+3.5),(1.8,.05,1.05),1)
 for j in range(32):
  a=j*2*pi/32;aa=(j+1)*2*pi/32;b.beam((x+.225*cos(a),y+4.39+.225*sin(a),groundz+3.05),(x+.225*cos(aa),y+4.39+.225*sin(aa),groundz+3.05),.014,2,5)
 for j in range(12):
  a=j*2*pi/12;b.beam((x+.225*cos(a),y+4.39+.225*sin(a),groundz+3.05),(x+.13*cos(a),y+4.39+.13*sin(a),groundz+2.65),.006,1,4)
 b.finish('Basketball_Hoop_3p05m',[m['Painted_Metal'],m['Marking_White'],material('Hoop_Orange','A66742',.45)],coll('Campus_Sports'))
 curve('Practice_Court_Boundary',[(x-4.15,y-6.9,1.125),(x+4.15,y-6.9,1.125),(x+4.15,y+6.9,1.125),(x-4.15,y+6.9,1.125)],.024,m['Marking_White'],coll('Campus_Sports'),True)
 curve('Practice_FreeThrow_Area',[(x-1.8,y+5.9,1.13),(x-1.8,y+.1,1.13),(x+1.8,y+.1,1.13),(x+1.8,y+5.9,1.13)],.024,m['Marking_White'],coll('Campus_Sports'))
for x,y in [(-46,-5),(-46,16),(-31,-5),(-31,16)]:
 b=Build();b.beam((x*S,y*S,.96),(x*S,y*S,12),.085,0,12)
 for j in range(3):b.box((x*S-.45+j*.45,y*S,11.9),(.35,.25,.24),1)
 b.finish('Sports_Light_Mast',[m['Painted_Metal'],m['Luminaire']],coll('Campus_Sports'))
# Exact official identity texture, sampled directly, without redrawing the crest.
wordmark=os.path.join(ROOT,'references','njust-official-wordmark.png')
im=bpy.data.images.load(wordmark,check_existing=True)
idmat=material('NJUST_Official_Wordmark','E2DDD0',.6);nt=idmat.node_tree;p=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],p.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],p.inputs['Alpha']);idmat.surface_render_method='DITHERED'
x,y,z=0,-46.51*S,4.05;w=20;h=w*55/342
box('Official_identity_backing',(x,y+.02,z),(w+.7,.08,h+.5),m['Painted_Metal'],coll('Campus_Signs'))
o=mesh('Official_NJUST_Sign',[(x-w/2,y-.04,z-h/2),(x+w/2,y-.04,z-h/2),(x+w/2,y-.04,z+h/2),(x-w/2,y-.04,z+h/2)],[(0,1,2,3)],[idmat],coll('Campus_Signs'))
uv=o.data.uv_layers.new()
for loop,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):loop.uv=co
for o in list(coll('Campus_Signs').objects):
 if o.get('SourceName')=='University name on stone':archive(o,'Exact university header artwork replaces approximation of official identity')
for body,x,y in [('图书馆  →',13,-28),('致远楼  ↑',-14,8),('二月兰 · 水杉林  →',17,28),('紫霞湖 · 三迎桥  ←',-16,30)]:
 instance('Direction_Board',props['Notice_Board'],(x*S,y*S,1),lod=1)
 text('Verified_Landmark_Direction',body,(x*S,y*S-.09,2.5),.22,m['Painted_Metal'])
scene['TreeVariants']=8;scene['ShrubVariants']=5;scene['FlowerVariants']=3;scene['TreePoints']=len(roadtrees)+len(woodtrees);scene['PropsLibrary']=json.dumps(list(props));scene['GNSystems']=[o.name for o in scene.objects if o.name.startswith('GN_')]
scene['SportsCaveat']='Inherited footprints are too small for standard 11-a-side football/competition basketball. Retained as clearly identified practice courts with metric equipment; no claim of regulation size.'
save('NJUST_v02_Landscape_Materials')
