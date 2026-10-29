import bpy,bmesh,math,random,os,json
from mathutils import Vector,Matrix
from math import sin,cos,pi
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=2.2
scene=bpy.context.scene
def coll(name,parent=None):
 c=bpy.data.collections.get(name)
 if c is None:
  c=bpy.data.collections.new(name)
  (parent or scene.collection).children.link(c)
 return c
def relocate(o,c):
 for cc in list(o.users_collection):cc.objects.unlink(o)
 c.objects.link(o)
def rgb(h):
 vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in vals)+(1,)
def material(name,color,rough=.55,metal=0,noise=0,bump=.02):
 m=bpy.data.materials.get(name)
 if m:return m
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgb(color)
 nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(color);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if noise:
  tc=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=noise;tex.inputs['Detail'].default_value=3;l.new(tc.outputs['Object'],tex.inputs['Vector'])
  ramp=n.new('ShaderNodeValToRGB');base=rgb(color);ramp.color_ramp.elements[0].color=tuple(v*.77 for v in base[:3])+(1,);ramp.color_ramp.elements[1].color=tuple(min(v*1.14,1) for v in base[:3])+(1,)
  l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
  b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.19;b.inputs['Distance'].default_value=bump;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
  rem=n.new('ShaderNodeMapRange');rem.inputs['To Min'].default_value=max(.05,rough-.08);rem.inputs['To Max'].default_value=min(1,rough+.1);l.new(tex.outputs['Fac'],rem.inputs[0]);l.new(rem.outputs[0],p.inputs['Roughness'])
 m.asset_mark();return m
def mesh(name,verts,faces,mats,c=None,ids=None,smooth=False):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 for m in mats:me.materials.append(m)
 if ids:
  for p,i in zip(me.polygons,ids):p.material_index=i
 if smooth:
  for p in me.polygons:p.use_smooth=True
 o=bpy.data.objects.new(name,me);(c or coll('Campus_Facilities')).objects.link(o);return o
class Build:
 def __init__(self):self.v=[];self.f=[];self.i=[]
 def box(self,loc,size,idx=0,rot=0):
  x,y,z=loc;a,b,c=[u/2 for u in size];k=len(self.v)
  self.v.extend([(x+u*cos(rot)-v*sin(rot),y+u*sin(rot)+v*cos(rot),z+w) for u,v,w in [(-a,-b,-c),(-a,-b,c),(-a,b,-c),(-a,b,c),(a,-b,-c),(a,-b,c),(a,b,-c),(a,b,c)]])
  fs=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]
  self.f.extend([tuple(k+i for i in f) for f in fs]);self.i.extend([idx]*6)
 def beam(self,a,b,r,idx=0,n=8,r2=None):
  a,b=Vector(a),Vector(b);d=(b-a).normalized();u=d.cross(Vector((0,0,1)))
  if u.length<.01:u=d.cross(Vector((0,1,0)))
  u.normalize();v=d.cross(u);k=len(self.v)
  for p,rad in [(a,r),(b,r if r2 is None else r2)]:self.v.extend([tuple(p+rad*(u*cos(j*2*pi/n)+v*sin(j*2*pi/n))) for j in range(n)])
  self.f.append(tuple(k+j for j in reversed(range(n))));self.i.append(idx)
  self.f.append(tuple(k+n+j for j in range(n)));self.i.append(idx)
  for j in range(n):self.f.append((k+j,k+(j+1)%n,k+(j+1)%n+n,k+j+n));self.i.append(idx)
 def leaf(self,center,length,width,idx,angles):
  M=Matrix.Rotation(angles[0],3,'Z')@Matrix.Rotation(angles[1],3,'Y')@Matrix.Rotation(angles[2],3,'X');k=len(self.v);c=Vector(center)
  for v in [(0,0,.016),(-length/2,0,0),(-length*.23,-width/2,0),(length*.23,-width*.42,0),(length/2,0,0),(length*.23,width*.42,0),(-length*.23,width/2,0)]:self.v.append(tuple(c+M@Vector(v)))
  for j in range(6):self.f.append((k,k+1+j,k+1+(j+1)%6));self.i.append(idx)
 def finish(self,name,mats,c=None,bevel=0,smooth=False):
  o=mesh(name,self.v,self.f,mats,c,self.i,smooth)
  if bevel:
   mod=o.modifiers.new('Edge micro bevel','BEVEL');mod.width=bevel;mod.segments=2;o.modifiers.new('Architectural normals','WEIGHTED_NORMAL')
  return o
def box(name,loc,size,mat,c=None,bevel=.02,rot=0):
 b=Build();b.box((0,0,0),size);o=b.finish(name,[mat],c,bevel);o.location=loc;o.rotation_euler.z=rot;return o
def curve(name,points,r,mat,c=None,closed=False):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,v in zip(sp.points,points):p.co=(*v,1)
 sp.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);(c or coll('Campus_Facilities')).objects.link(o);cu.materials.append(mat);return o
def text(name,body,loc,size,mat,c=None,rot=(pi/2,0,0),align='CENTER'):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.font=bpy.data.fonts.get('Microsoft YaHei Regular') or bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc');cu.size=size;cu.align_x=align;cu.align_y='CENTER';cu.extrude=.003
 o=bpy.data.objects.new(name,cu);(c or coll('Campus_Signs')).objects.link(o);o.location=loc;o.rotation_euler=rot;cu.materials.append(mat);return o
def source_asset(name,builder,mats,bevel=0):
 c=bpy.data.collections.new('ASSET_'+name);o=builder.finish(name,mats,c,bevel);o.asset_mark();c.asset_mark();return c
def instance(name,asset,loc,rot=0,scale=1,lod=1,c=None):
 o=bpy.data.objects.new(name,None);o.instance_type='COLLECTION';o.instance_collection=asset;(c or coll('Campus_Facilities')).objects.link(o);o.location=loc;o.rotation_euler.z=rot;o.scale=(scale,)*3;o['LOD']=lod;return o
def archive(o,reason):
 o['SupersededReason']=reason;relocate(o,coll('Legacy_Superseded'));o.hide_render=True;o.hide_set(True)
def save(version):
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,version+'.blend'));print('CHECKPOINT',version,flush=True)
def wallstyle(m):
 # Subtle architectural finish; no exaggerated grunge.
 nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF')
 geom=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geom.outputs['Position'],sep.inputs[0])
 band=n.new('ShaderNodeMapRange');band.inputs['From Min'].default_value=.9;band.inputs['From Max'].default_value=2.4;band.inputs['To Min'].default_value=.79;band.inputs['To Max'].default_value=1;l.new(sep.outputs['Z'],band.inputs[0]);band.clamp=True
 base=n.new('ShaderNodeMixRGB');base.blend_type='MULTIPLY';base.inputs[0].default_value=1
 if p.inputs['Base Color'].is_linked:l.new(p.inputs['Base Color'].links[0].from_socket,base.inputs[1])
 else:base.inputs[1].default_value=p.inputs['Base Color'].default_value
 l.new(band.outputs[0],base.inputs[2]);l.new(base.outputs[0],p.inputs['Base Color'])
def palette():
 colors={'Wall_White':('DEDFD7',.66,0,.35,.015),'Wall_Warm':('D1C6AE',.74,0,.43,.02),'Wall_Brick':('955E4C',.85,0,2,.025),'Concrete':('ABAFA8',.84,0,3,.022),'Asphalt':('535A5C',.92,0,90,.006),'Sidewalk':('C1BEB1',.83,0,14,.008),'Stone':('B9BCB5',.76,0,6,.025),'Roof_Red':('875F51',.8,0,22,.03),'Roof_Metal':('777F80',.42,.5,9,.009),'Grass':('60764C',.91,0,.6,.035),'Tree_Leaf':('59783F',.74,0,4,.006),'Tree_Trunk':('655246',.96,0,13,.035),'Running_Track':('A46655',.92,0,100,.007),'Basketball_Court':('637D84',.8,0,45,.006),'Metal':('777F7D',.3,.78,10,.001),'Painted_Metal':('374844',.4,.25,14,.002),'Window_Frame':('B1B7B4',.34,.65,0,.0),'Marking_White':('D6D5C5',.85,0,55,.001),'Tactile':('BCAD7D',.8,0,25,.01),'Wood':('8A7660',.78,0,9,.014),'Soil':('5E5340',1,0,20,.04)}
 mats={k:material(k,*v) for k,v in colors.items()}
 for k in ['Wall_White','Wall_Warm','Wall_Brick']:wallstyle(mats[k]) if not mats[k].get('weathered') else None;mats[k]['weathered']=True
 glass=material('Glass','A0B2B0',.19,.06);p=glass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.55;p.inputs['IOR'].default_value=1.46;mats['Glass']=glass
 interior=material('Interior_Dark','293B3B',.83);mats['Interior_Dark']=interior
 for k,color in [('Interior_Lit','EBC797'),('Luminaire','FFE1B1')]:
  m=material(k,color,.5);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=rgb(color);p.inputs['Emission Strength'].default_value=.1;mats[k]=m
 water=material('Water','799393',.095);p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.88;p.inputs['IOR'].default_value=1.333;p.inputs['Coat Weight'].default_value=.25
 tex=water.node_tree.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.7;tex.inputs['Detail'].default_value=2
 bu=water.node_tree.nodes.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.1;bu.inputs['Distance'].default_value=.027;water.node_tree.links.new(tex.outputs['Fac'],bu.inputs['Height']);water.node_tree.links.new(bu.outputs['Normal'],p.inputs['Normal']);mats['Water']=water
 return mats
