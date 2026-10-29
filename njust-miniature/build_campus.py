"""NJUST • Violet Spring — editable, procedurally built Blender miniature.
Run: blender --background --python build_campus.py
All geometry is original. Layout is an artistic compression of the campus.
"""
import bpy, math, random, os, json, sys
from mathutils import Vector
from collections import defaultdict
from math import sin, cos, pi

ROOT=os.path.dirname(os.path.abspath(__file__))
random.seed(1953)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in list(bpy.data.collections):
    if d.name!='Collection': bpy.data.collections.remove(d)
scene=bpy.context.scene
COL=None
def collection(name):
    global COL
    COL=bpy.data.collections.new(name); scene.collection.children.link(COL)
    return COL
def link(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    COL.objects.link(obj)
    return obj
def mat(name,h,rough=.5,metal=0,emission=0):
    rgb=tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
    # Convert display colors to scene linear for predictable art direction.
    rgb=tuple(v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb)
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=emission
    return m
ivory=mat('Architecture | warm limestone','E9E2CD',.42)
white=mat('Architecture | porcelain trim','F7F2E5',.3)
stone=mat('Landscape | pale travertine','C7C7B5',.7)
brick=mat('Architecture | russet brick','A65D4F',.68)
roof=mat('Roofs | fired terracotta','B9745D',.65)
roof2=mat('Roofs | patinated slate','668084',.6)
glass=mat('Windows | teal blue glass','426770',.22,.32)
glass2=mat('Windows | sky reflection','82AFB1',.24,.28)
lit=mat('Windows | warm occupied rooms','F9D594',.3,0,.7)
dark=mat('Metal | deep evergreen','223E3F',.45,.2)
gold=mat('Details | champagne brass','C6A76D',.28,.65)
plinth=mat('Plinth | midnight teal','173C40',.36,.15)
asphalt=mat('Road | blue grey','758B89',.83)
path=mat('Paths | warm sand','D9D2B9',.8)
lawn=mat('Landscape | spring sage','8CAC7C',.94)
lawn2=mat('Landscape | fresh lawn','A3BD89',.9)
greens=[mat('Foliage | '+str(i),h,.87) for i,h in enumerate(['4E795C','6B9161','7C9F6C','97AE74','486F59','A8BA81'])]
trunk=mat('Trees | cinnamon bark','796550',.97)
purple=[mat('Flowers | viola '+str(i),h,.64) for i,h in enumerate(['8863BD','A787D0','B99DDD','CEBCEB','7455A0'])]
pink=mat('Blossoms | soft rose','D9AEC0',.8)
trackmat=mat('Sport | terracotta track','B97564',.88)
field=mat('Sport | pitch green','53846B',.86)
field2=mat('Sport | stripe green','629478',.86)
courtmat=mat('Sport | blue court','719EAA',.83)
water=mat('Water | jade','5AABB0',.19,.35)
p=water.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.4
n=water.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=2.7;n.inputs['Detail'].default_value=2
b=water.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=.075
water.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);water.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
ground=mat('Studio | oat paper','D8D8C8',.9)

# Batch small architectural parts into one editable mesh per material/collection.
batches={}
def box(name,loc,size,ma,bevel=0,rot=0,batch=False):
    x,y,z=loc;a,b,c=[v/2 for v in size]
    if batch:
        key=(COL.name,ma.name)
        if key not in batches:batches[key]=[[],[]]
        vs,fs=batches[key];k=len(vs)
        co=[(-a,-b,-c),(-a,-b,c),(-a,b,-c),(-a,b,c),(a,-b,-c),(a,-b,c),(a,b,-c),(a,b,c)]
        vs.extend([(x+u*cos(rot)-v*sin(rot),y+u*sin(rot)+v*cos(rot),z+w) for u,v,w in co])
        fs.extend([tuple(k+i for i in f) for f in [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]])
        return None
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=link(bpy.context.object);o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.rotation_euler.z=rot;o.data.materials.append(ma)
    if bevel:
        m=o.modifiers.new('Soft crafted edges','BEVEL');m.width=bevel;m.segments=3
        o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
    return o
def mesh(name,vs,fs,ma):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(ma);me.update()
    o=bpy.data.objects.new(name,me);COL.objects.link(o);return o
def curve(name,points,r,ma,closed=False):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=r;cu.bevel_resolution=2
    s=cu.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    s.use_cyclic_u=closed;o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(ma);return o
def cyl(name,loc,r,depth,ma,vertices=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc);o=link(bpy.context.object);o.name=name;o.data.materials.append(ma);return o
def sphere(name,loc,scale,ma,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=link(bpy.context.object);o.name=name;o.scale=scale;o.data.materials.append(ma);return o
def beam(name,a,b,r,ma):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,ma,12);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
font=bpy.data.fonts.load('C:/Windows/Fonts/msyh.ttc')
font_en=bpy.data.fonts.load('C:/Windows/Fonts/bahnschrift.ttf')
def text_obj(name,body,loc,size,ma,rotation=(0,0,0),align='CENTER',latin=False):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.font=font_en if latin else font;cu.size=size;cu.align_x=align;cu.align_y='CENTER';cu.extrude=.007;cu.bevel_depth=.002
    o=bpy.data.objects.new(name,cu);COL.objects.link(o);o.location=loc;o.rotation_euler=rotation;cu.materials.append(ma);return o
def ellipse(cx,cy,rx,ry,z,n=96):return [(cx+rx*cos(i*2*pi/n),cy+ry*sin(i*2*pi/n),z) for i in range(n)]
def disk(name,cx,cy,rx,ry,z,ma):return mesh(name,ellipse(cx,cy,rx,ry,z),[tuple(range(96))],ma)
def ribbon(name,pts,width,z,ma):
    vs=[]
    for i,(x,y) in enumerate(pts):
        a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)]);d=(b-a).normalized();v=Vector((-d.y,d.x))*width/2
        vs.extend([(x+v.x,y+v.y,z),(x-v.x,y-v.y,z)])
    return mesh(name,vs,[(i,i+1,i+3,i+2) for i in range(0,len(vs)-2,2)],ma)
def pitchroof(name,x,y,w,d,z,ma):
    vs=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x-w/2,y,z+1.35),(x+w/2,y,z+1.35)]
    mesh(name,vs,[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)],ma)
    curve('Roof ridge',[(x-w/2,y,z+1.39),(x+w/2,y,z+1.39)],.055,ma)
def block(name,x,y,w,d,h,floors=4,wall=ivory,pitched=False):
    box(name+' | plinth',(x,y,.5),(w+.6,d+.6,.8),stone,.12)
    box(name+' | facade',(x,y,.8+h/2),(w,d,h),wall,.12)
    for j in range(floors):
        z=1.45+(j+.5)*(h-.6)/floors
        cols=max(2,int(w/1.3))
        for i in range(cols):
            xx=x-w/2+(i+.5)*w/cols
            for yy in [y-d/2-.022,y+d/2+.022]:
                gm=random.choices([glass,glass2,lit],[.65,.3,.05])[0]
                box('Window',(xx,yy,z),(.77,.08,(h-.6)/floors*.55),gm,batch=True)
                box('Sill',(xx,yy,z-(h-.6)/floors*.28),(.92,.18,.075),white,batch=True)
        for yy in [y-d/2-.06,y+d/2+.06]:box('Floor string course',(x,yy,.95+(j+1)*(h-.5)/floors),(w+.15,.15,.105),white,batch=True)
        for side in [-1,1]:
            for k in range(max(1,int(d/1.5))):
                yy=y-d/2+(k+.5)*d/max(1,int(d/1.5))
                box('Side window',(x+side*(w/2+.03),yy,z),(.07,.7,(h-.6)/floors*.5),glass,batch=True)
    box('Roof cornice',(x,y,h+.85),(w+.35,d+.35,.24),white,.06)
    if pitched:pitchroof('Tile roof',x,y,w+.6,d+.6,h+1,roof)
    else:
        box('Roof inset',(x,y,h+1),(w-.45,d-.45,.12),roof2,batch=True)
        for xx in [x-w*.28,x+w*.24]:
            box('Roof equipment',(xx,y,h+1.35),(1.4,1,.55),stone,batch=True)
            for k in range(4):box('Vent fins',(xx-.5+k*.33,y,h+1.64),(.1,.85,.07),dark,batch=True)
    box('Entrance',(x,y-d/2-.045,1.8),(1.7,.13,2.2),glass,batch=True)
    box('Entrance canopy',(x,y-d/2-.65,3),(2.5,1.4,.2),white,.07)

collection('00 · Exhibition base & identity')
box('Floating museum plinth',(0,0,-2),(116,114,4),plinth,2)
box('Brass inlay',(0,0,-.65),(116.08,114.08,.16),gold,.06)
box('Chamfered limestone rim',(0,0,-.25),(114.8,112.8,.55),ivory,.9)
box('Campus ground',(0,0,.05),(112.7,110.7,.3),lawn,.9)
box('Title panel',(0,-52.9,.24),(74,7,.17),plinth,.5)
text_obj('Title / Chinese','南京理工大学',(0,-52.25,.35),2.6,white)
text_obj('Title / English','N J U S T   /   V I O L E T   S P R I N G',(0,-54.5,.35),.65,gold,latin=True)
text_obj('Edition','孝陵卫 · 春日校园微缩',(40,-52.8,.3),.58,dark)
text_obj('Edition number','01 / 1953',(-43,-52.8,.3),.83,dark,latin=True)
text_obj('Front engraved label','N A N J I N G   /   3 2 . 0 2 ° N   1 1 8 . 8 5 ° E',(0,-57.07,-2),.9,gold,(pi/2,0,0),latin=True)

collection('01 · Paths, roads & civic spaces')
for x in [-18,18,-48,48]:
    box('Road verge',(x,1,.24),(4.7,99,.17),stone,.1)
    box('Campus avenue',(x,1,.34),(3.5,99,.12),asphalt,.1)
for y in [-43,-25,5,26,45]:
    box('Road verge',(0,y,.25),(100,4.5,.15),stone,.12)
    box('Cross avenue',(0,y,.34),(99.8,3.3,.13),asphalt,.12)
for x in [-18,18,-48,48]:
    for y in range(-40,46,4):box('Lane dash',(x,y,.418),(.055,1.6,.012),white,batch=True)
for y in [-43,-25,5,26,45]:
    for x in range(-46,49,4):box('Lane dash',(x,y,.418),(1.65,.055,.013),white,batch=True)
for x in [-18,18]:
    for y in [-43,-25,5,26,45]:
        for t in [-1,1]:
            for k in range(6):box('Zebra crossing',(x-1.2+k*.48,y+t*3,.425),(.24,1.35,.018),white,batch=True)
box('Central promenade',(0,-5,.26),(5.5,78,.17),path,.1)
box('Library civic lawn',(0,-1,.29),(27,7,.18),lawn2,.3)
for x in [-10,10]:
    box('Formal garden curb',(x,-.5,.32),(4.7,7,.15),stone,.08)
    box('Formal garden',(x,-.5,.43),(4.2,6.6,.15),lawn2,.08)
box('Arrival plaza',(0,-36.5,.3),(28,10,.15),path,.3)
for x in range(-13,14,2):box('Plaza paving joints',(x,-36.5,.385),(.018,9.4,.01),stone,batch=True)
for y in range(-40,-31,2):box('Plaza paving joints',(0,y,.385),(27,.02,.01),stone,batch=True)

collection('02 · 致远楼 / Zhiyuan administration')
# Twin high-rise volumes with a recessed central entrance, drawn from official aerials.
for x in [-5.25,5.25]:block('致远楼',x,15,9.9,6,15.5,11,ivory)
box('Central glazed spine',(0,14.9,8.2),(1.3,6.2,14.5),glass,.08)
box('Crown',(0,15,17),(11,5.5,1.7),ivory,.13)
for i in range(13):box('Crown glazing',(-4.9+i*.8,12.23,17),(.48,.09,.78),glass,batch=True)
box('Tower rooftop',(0,15,18),(11.5,6,.22),white,.07)
box('Ceremonial entry',(0,11.55,2.15),(4.5,1.2,3.1),white,.09)
box('Entry glass',(0,10.9,2),(2.8,.12,2.6),glass,batch=True)
for i in range(7):box('Ceremonial steps',(0,9.3+i*.22,.45+i*.085),(8,2-i*.2,.18),stone,batch=True)
text_obj('Zhiyuan name','致 远 楼',(0,10.83,3.25),.45,gold,(pi/2,0,0))
for x in [30]:
    block('Academic courtyard front',x,12,17,4.7,7,5,ivory)
    for dx in [-6.2,6.2]:block('Academic courtyard wing',x+dx,18,4.5,8,7,5,ivory)
    box('Courtyard lawn',(x,18,.33),(7,7,.12),lawn2,.3)
block('West academic pavilion',-26.5,13.5,9.5,5.5,6,4,ivory)

collection('03 · 图书馆 / Curved library')
# Two curved wings frame a deep glazed entrance; window ribs remain real geometry.
lx,ly=0,-14
for floor in range(6):
    z=.85+floor*1.55
    for i in range(32):
        x=-12.5+(i+.5)*25/32
        yy=ly-3.3-2.4*(x/12.5)**2
        if abs(x)<3.25 and floor<3:continue
        rot=math.atan(-4.8*x/12.5**2)
        box('Curved facade glazing',(x,yy,z+.7),(.77,.2,1.37),glass2 if i%5==0 else glass,rot=rot,batch=True)
        box('Limestone vertical rib',(x-.39,yy-.13,z+.73),(.11,.39,1.55),white,rot=rot,batch=True)
        box('Library horizontal band',(x,yy-.12,z),(.84,.38,.15),ivory,rot=rot,batch=True)
for side in [-1,1]:
    box('Library solid end',(side*12.9,ly-1.8,5.25),(.9,8.5,10),ivory,.1)
    block('Library reading wing',side*8,ly+.5,9,5.8,9,6,ivory)
box('Library rear volume',(0,ly+3,5),(25,2,8.6),ivory,.1)
box('Recessed entrance glass',(0,ly-1.6,2.9),(6.1,.2,5.2),glass,.07)
for x in [-3.4,3.4]:box('Entry portal jamb',(x,ly-3.5,3.4),(.45,.85,6),white,.07)
box('Entry portal lintel',(0,ly-3.5,6.3),(7.2,.85,.55),white,.07)
text_obj('Library lettering','图 书 馆',(0,ly-3.96,6.32),.52,gold,(pi/2,0,0))
for j in range(5):box('Library broad steps',(0,ly-6.1+j*.35,.42+j*.09),(8.3,3.1-j*.5,.18),stone,batch=True)
roofpts=[(-13,ly+4.1,10.05),(13,ly+4.1,10.05)]+[(12.9-i*25.8/40,ly-3.3-2.4*((12.9-i*25.8/40)/12.5)**2,10.05) for i in range(41)]
mesh('Curving library roof',roofpts,[tuple(range(len(roofpts)))],ivory)
curve('Continuous white roof rim',roofpts,.17,white,True)
box('Library skylight',(0,ly+.75,10.25),(7.8,3.4,.25),glass2,.12)
for x in range(-3,4):box('Skylight mullion',(x,ly+.75,10.42),(.06,3.4,.05),white,batch=True)

collection('04 · 二道门、校风碑与校名石')
# Small architectural landmarks are intentionally enlarged for miniature readability.
gy=29.6
for x in [-7.5,-3.3,3.3,7.5]:
    box('Historic gate pillar',(x,gy,2.85),(.8,1,5.2),ivory,.08)
    box('Pillar foot',(x,gy,.7),(1.12,1.25,.7),stone,.08)
    box('Pillar capital',(x,gy,5.35),(1.15,1.3,.3),white,.07)
    sphere('Pillar finial',(x,gy,5.7),(.3,.3,.32),ivory,2)
for x,w,z in [(-5.4,3.5,4.65),(0,6.5,5),(5.4,3.5,4.65)]:
    box('Historic gate lintel',(x,gy,z),(w,.66,.83),ivory,.08)
    box('Historic cornice',(x,gy,z+.47),(w+.4,1,.18),white,.07)
text_obj('Motto on second gate','进德修业  志道鼎新',(0,gy-.346,5.03),.42,dark,(pi/2,0,0))
for x in [-5.4,5.4]:
    for k in range(6):box('Open stone tracery',(x-1.35+k*.54,gy,3.65),(.11,.35,1.1),ivory,batch=True)
box('Motto monument base',(0,-34.7,.7),(7.3,4,.65),stone,.18)
for x in [-2.65,2.65]:box('Motto monument upright',(x,-34.7,3.1),(.55,1,4.3),ivory,.08)
box('Motto monument crosspiece',(0,-34.7,5.35),(6,1,.7),ivory,.08)
text_obj('School spirit','团结 献身 求是 创新',(0,-35.22,5.35),.34,gold,(pi/2,0,0))
for x in [-2,-1,0,1,2]:box('Monument grille',(x,-34.7,4.65),(.12,.3,.6),gold,batch=True)
box('Name stone',(0,-45.8,1.72),(15.5,1.35,2.45),stone,.45)
text_obj('University name on stone','南京理工大学',(0,-46.49,1.88),1.34,gold,(pi/2,0,0))
for x in [-11,11]:
    box('Arrival gatehouse',(x,-45.7,1.5),(3.2,2.4,2.3),ivory,.12)
    box('Gatehouse glazing',(x,-46.94,1.6),(2.5,.07,1.4),glass,batch=True)
    box('Gatehouse roof',(x,-45.7,2.8),(3.8,2.8,.3),white,.1)

collection('05 · 兵器博物馆 / Museum & heritage court')
mx,my=31,-33
cyl('Museum circular drum',(mx,my,3.2),7,5.5,ivory,64)
for i in range(64):
    a=2*pi*i/64
    box('Museum glazing',(mx+7.05*cos(a),my+7.05*sin(a),3.25),(.5,.1,3.3),glass,rot=a+pi/2,batch=True)
for i in range(12):
    a=pi+i*pi/11
    curve('Fan roof rib',[(mx+8*cos(a),my+8*sin(a),5.7),(mx+4*cos(a),my+4*sin(a),7.1),(mx,my,7.5)],.12,white)
cyl('Museum oculus',(mx,my,6.5),3.8,1,glass2,64)
for r in [3.9,4.4]:curve('Floating museum crown',ellipse(mx,my,r,r,7.45),.11,white,True)
box('Museum annex',(mx+5,my+3,3),(5,6,5.5),ivory,.16)
text_obj('Museum sign','兵器博物馆',(mx,my-7.15,4.1),.56,gold,(pi/2,0,0))
box('Heritage forecourt',(32,-42,.34),(19,4,.18),path,.3)
# Sculptural display silhouettes: decorative, no functional internals.
for xx in [26.5,36.5]:
    box('Outdoor exhibit pedestal',(xx,-41.7,.6),(4.8,2.9,.5),stone,.12)
    box('Historic vehicle silhouette',(xx,-41.7,1.25),(2.9,1.4,.8),dark,.17)
    for yy in [-42.5,-40.9]:
        for dx in [-1,-.5,0,.5,1]:
            o=cyl('Exhibit wheel',(xx+dx,yy,1.05),.3,.15,dark,12);o.rotation_euler.x=pi/2
    sphere('Exhibit turret',(xx,-41.7,1.95),(.85,.7,.5),greens[0],2)
    beam('Exhibit silhouette barrel',(xx,-41.7,2.1),(xx+2,-41.7,2.55),.095,dark)

collection('06 · 教学街区 / Academic quarters')
for x in [28,40]:
    for y in [-15,-5]:block('Engineering school',x,y,8.5,5.6,6.5,4,brick,True)
for y in [-18]:
    block('Historic teaching block',-30,y,15,4.8,5,3,ivory,True)
block('Historic west wing',-36, -12.5,3.7,5.8,5,3,ivory,True)

collection('07 · 生活片区 / Residential fabric')
for x in [-39,-27,-9,4,28,40]:
    block('Residence hall',x,49.4,9,4.4,4.5,3,ivory,True)
for x in [-40,-28]:
    for y in [-35,-46.5]:block('Student residence',x,y,8.5,4.4,4.8,4,ivory,True)

collection('08 · 体育场 / Athletics & courts')
# Oval track oriented north-south, placed in the western campus district.
sx,sy=-39,5
def stadiumloop(r,straight,z):
    pts=[]
    for i in range(49):
        a=i*pi/48;pts.append((sx+r*cos(a),sy+straight/2+r*sin(a),z))
    for i in range(49):
        a=pi+i*pi/48;pts.append((sx+r*cos(a),sy-straight/2+r*sin(a),z))
    return pts
pts=stadiumloop(6.1,11,.5);mesh('Oval clay running track',pts,[tuple(range(len(pts)))],trackmat)
for r in [4.4,4.75,5.1,5.45,5.8,6.05]:curve('Running lane',stadiumloop(r,11,.53),.027,white,True)
pts=stadiumloop(4.1,11,.55);mesh('Infield',pts,[tuple(range(len(pts)))],field)
box('Football grass',(sx,sy,.57),(7.2,14,.08),field)
for j in range(7):box('Mown pitch stripe',(sx,sy-6+j*2,.617),(7.2,1,.011),field2,batch=True)
curve('Football boundary',[(sx-3.3,sy-6.7,.64),(sx+3.3,sy-6.7,.64),(sx+3.3,sy+6.7,.64),(sx-3.3,sy+6.7,.64)],.025,white,True)
curve('Halfway line',[(sx-3.3,sy,.65),(sx+3.3,sy,.65)],.024,white)
curve('Centre circle',ellipse(sx,sy,1.15,1.15,.65),.023,white,True)
for side in [-1,1]:
    yy=sy+side*6.65
    curve('Penalty area',[(sx-2.2,yy,.65),(sx-2.2,yy-side*2.5,.65),(sx+2.2,yy-side*2.5,.65),(sx+2.2,yy,.65)],.024,white)
    curve('Goal frame',[(sx-1,yy, .65),(sx-1,yy,1.5),(sx+1,yy,1.5),(sx+1,yy,.65)],.045,white)
    for i in range(9):curve('Goal net',[(sx-.96+i*.24,yy,1.5),(sx-.96+i*.24,yy+side*.7,.7)],.009,white)
for k in range(4):box('Grandstand tier',(sx-7.3-k*.32,sy,.65+k*.3),(.65,14,.3),ivory,batch=True)
box('Spectator canopy',(sx-8,sy,3),(3,15,.22),white,.16)
for yy in [sy-6,sy,sy+6]:beam('Canopy support',(sx-8,yy,.5),(sx-8,yy,3),.1,dark)
box('Residence garden',( -28,-29.6,.45),(7,4,.15),lawn2,.3)
for y in [-20,-11,0,11]:
    x=-53
    box('Basketball court',(x,y,.38),(4.4,7.2,.16),courtmat,.1)
    curve('Court line',[(x-1.9,y-3.2,.49),(x+1.9,y-3.2,.49),(x+1.9,y+3.2,.49),(x-1.9,y+3.2,.49)],.025,white,True)
    curve('Court centre circle',ellipse(x,y,.68,.68,.49),.025,white,True)
    curve('Court centre stripe',[(x-1.9,y,.49),(x+1.9,y,.49)],.025,white)
    for yy in [y-3,y+3]:
        beam('Hoop post',(x,yy,.5),(x,yy,2),.04,dark)
        box('Backboard',(x,yy,1.85),(.7,.07,.5),white,batch=True)

collection('09 · 友谊河、紫霞湖、三迎桥')
riverpts=[(-55+i*1.1,23+1.4*sin(i*.09)) for i in range(101)]
ribbon('Stone canal banks',riverpts,4.6,.43,stone)
ribbon('Friendship river',riverpts,3.3,.46,water)
for x in [-48,-18,0,18,48]:
    yy=23+1.4*sin((x+55)/1.1*.09)
    box('Road over river',(x,yy,.7),(4.1,5,.35),path,.1)
    for s in [-1,1]:
        curve('Bridge railing',[(x+s*2,yy-2.5,1.4),(x+s*2,yy+2.5,1.4)],.055,white)
        for k in range(7):box('Bridge post',(x+s*2,yy-2.4+k*.8,1.1),(.13,.13,.8),white,batch=True)
lakepts=[]
cx,cy=-28,31
for i in range(100):
    a=2*pi*i/100;r=1+.1*sin(3*a)+.065*cos(5*a)
    lakepts.append((cx+11*r*cos(a),cy+7*r*sin(a),.51))
mesh('Lake stone edge',[(cx+(x-cx)*1.06,cy+(y-cy)*1.06,z-.05) for x,y,z in lakepts],[tuple(range(100))],stone)
mesh('Zixia lake',lakepts,[tuple(range(100))],water)
for i in range(15):
    xx=random.uniform(-35,-23);yy=random.uniform(27.5,34.5)
    curve('Quiet water ripples',[(xx+j*.35,yy+.06*sin(j),.53) for j in range(6)],.012,glass2)
# True open arch bridge, with a smoothly crowned deck and repeated balusters.
bx,by=-28,31
N=32
for side in [-1,1]:
    vs=[]
    for i in range(N+1):
        t=-1+2*i/N;x=bx+t*11.7;top=.8+1.65*(1-t*t);bottom=.58+1.45*math.sqrt(max(0,1-t*t))
        vs.extend([(x,by+side*1.08,bottom),(x,by+side*1.08,top)])
    mesh('Open arch masonry',vs,[(i,i+1,i+3,i+2) for i in range(0,N*2,2)],ivory)
    pts=[]
    for i in range(17):
        t=-1+2*i/16;xx=bx+t*11.7;z=.8+1.65*(1-t*t)
        box('Bridge baluster',(xx,by+side*1.05,z+.47),(.15,.17,.94),white,batch=True)
        sphere('Stone finial',(xx,by+side*1.05,z+.99),(.13,.13,.13),white,1)
        pts.append((xx,by+side*1.05,z+.86))
    curve('Arched handrail',pts,.085,white)
vs=[]
for i in range(N+1):
    t=-1+2*i/N;z=.83+1.65*(1-t*t);vs.extend([(bx+t*11.7,by-1.07,z),(bx+t*11.7,by+1.07,z)])
mesh('Bridge curved deck',vs,[(i,i+1,i+3,i+2) for i in range(0,N*2,2)],stone)
for k in range(25):
    t=-1+2*k/24;z=.845+1.65*(1-t*t)
    curve('Deck paver seams',[(bx+t*11.7,by-1,z),(bx+t*11.7,by+1,z)],.014,ivory)

collection('10 · 水杉林 / Violet woodland')
# Hundreds of individually editable trees, instanced from compact mesh prototypes.
def make_tree_mesh(name,conifer=False,variant=0):
    vs=[];fs=[];mi=[]
    def frustum(z,r1,r2,h,n=9,offset=(0,0)):
        k=len(vs)
        for zz,r in [(z,r1),(z+h,r2)]:
            vs.extend([(offset[0]+r*cos(i*2*pi/n),offset[1]+r*sin(i*2*pi/n),zz) for i in range(n)])
        fs.extend([tuple(k+i for i in reversed(range(n))),tuple(k+n+i for i in range(n))]);mi.extend([0,0])
        for i in range(n):fs.append((k+i,k+(i+1)%n,k+(i+1)%n+n,k+i+n));mi.append(0)
    frustum(0,.11,.045,5.1 if conifer else 2.8,8)
    def foliage(cx,cy,cz,rx,ry,rz,idx):
        k=len(vs);rings=5;seg=9
        for j in range(rings+1):
            a=pi*j/rings
            for i in range(seg):
                t=2*pi*i/seg+(j%2)*.2;rr=1+random.uniform(-.12,.12)
                vs.append((cx+rx*sin(a)*cos(t)*rr,cy+ry*sin(a)*sin(t)*rr,cz+rz*cos(a)))
        for j in range(rings):
            for i in range(seg):fs.append((k+j*seg+i,k+j*seg+(i+1)%seg,k+(j+1)*seg+(i+1)%seg,k+(j+1)*seg+i));mi.append(idx)
    if conifer:
        for j in range(5):
            foliage(0,0,3.6+j*.65,1.05-j*.17,1-j*.16,.85,1+(j+variant)%len(greens))
    else:
        foliage(0,0,2.9,1.15,1.02,1.1,1+variant%len(greens))
        for j in range(4):
            a=2*pi*j/4;foliage(.7*cos(a),.7*sin(a),2.3+random.random()*.4,.72,.76,.82,1+(variant+j)%len(greens))
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(trunk)
    for m in greens:me.materials.append(m)
    for p,idx in zip(me.polygons,mi):p.material_index=idx
    return me
tree_meshes=[make_tree_mesh('Broadleaf prototype '+str(i),False,i) for i in range(4)]
cedar_meshes=[make_tree_mesh('Metasequoia prototype '+str(i),True,i) for i in range(3)]
def tree(x,y,s=1,cedar=False):
    me=random.choice(cedar_meshes if cedar else tree_meshes);o=bpy.data.objects.new('水杉 / Metasequoia' if cedar else '梧桐 / Canopy tree',me);COL.objects.link(o);o.location=(x,y,.39);o.scale=(s,s,s*random.uniform(.92,1.1));o.rotation_euler.z=random.random()*2*pi
    return o
forest_patches=[(32,35.5,24,14),(-8,36,12,9),(51,34,5,13),(-43,33,4,14)]
flower_vs=[];flower_fs=[];flower_mi=[]
for px,py,w,d in forest_patches:
    box('Violet woodland floor',(px,py,.38),(w,d,.14),purple[4],.65)
    for i in range(int(w*d*12)):
        x=px+random.uniform(-w/2+.2,w/2-.2);y=py+random.uniform(-d/2+.2,d/2-.2)
        z=random.uniform(.51,.83);sz=random.uniform(.08,.17);k=len(flower_vs)
        for j in range(4):
            a=j*pi/2+random.random()*.2
            cxx=x+sz*.7*cos(a);cyy=y+sz*.7*sin(a)
            flower_vs.extend([(cxx,cyy,z+.025),(cxx+sz*cos(a-.9),cyy+sz*sin(a-.9),z),(cxx+sz*1.2*cos(a),cyy+sz*1.2*sin(a),z+.015),(cxx+sz*cos(a+.9),cyy+sz*sin(a+.9),z)])
            flower_fs.append(tuple(k+j*4+v for v in [0,1,2,3]));flower_mi.append(random.randrange(len(purple)))
    for ix in range(int(w/2.7)):
        for iy in range(int(d/2.8)):
            tree(px-w/2+1.4+ix*2.8+random.uniform(-.3,.3),py-d/2+1.3+iy*2.8,random.uniform(.85,1.2),True)
me=bpy.data.meshes.new('Four-petalled Orychophragmus flower carpet');me.from_pydata(flower_vs,[],flower_fs)
for m in purple:me.materials.append(m)
for p,i in zip(me.polygons,flower_mi):p.material_index=i
o=bpy.data.objects.new('二月兰 · individually modeled petals',me);COL.objects.link(o)
for px,py,w,d in forest_patches:
    pts=[(px-w/2+i*w/24,py+sin(i*pi/12)*d*.14) for i in range(25)]
    ribbon('Woodland meandering path',pts,.85,.86,path)
    for i in range(0,25,2):
        x,y=pts[i];box('Woodland stepping stone',(x,y,.9),(.38,.75,.075),stone,batch=True)

collection('11 · Avenue trees, garden furniture & campus life')
for x in [-20.8,20.8]:
    for y in range(-40,23,5):tree(x,y,random.uniform(.83,1.08))
for y in [-40,1.8,42]:
    for x in range(-43,46,6):
        if abs(x)<13 and y==-40:continue
        if x<-31 and y==1.8:continue
        tree(x,y,random.uniform(.85,1.15))
for x in [-51,51]:
    for y in range(-47,22,6):
        if x==-51 and -24<y<17:continue
        tree(x,y,random.uniform(.9,1.3))
for x in range(-49,50,4):tree(x,54,random.uniform(.65,.9))
for x,y in [(-14,31),(-16,35),(-19,39),(-34,39),(-39,27),(-38,38),(-26,40),(-8,-29),(8,-29),(-11,8),(11,8)]:tree(x,y,1.15)
def shrub(x,y,s=1):
    sphere('Clipped shrub',(x,y,.75*s),(s,.65*s,.53*s),random.choice(greens),2)
for y in [-29,-39]:
    for x in list(range(-13,-5,2))+list(range(6,14,2)):shrub(x,y,.6)
for x in [-14,14]:
    for y in range(-20,20,3):shrub(x,y,.72)
def lamp(x,y):
    cyl('Lamp base',(x,y,.58),.16,.4,dark,12)
    beam('Lamp column',(x,y,.65),(x,y,3.3),.055,dark)
    beam('Lamp arm',(x,y,3.2),(x+.5,y,3.4),.04,dark)
    box('Lamp housing',(x+.45,y,3.37),(.55,.28,.12),dark,.05)
    box('Lamp diffuser',(x+.45,y,3.295),(.39,.22,.035),lit,batch=True)
for x in [-15.4,15.4]:
    for y in range(-40,44,8):lamp(x,y)
for y in [-40,8,27]:
    for x in [-44,-29,29,44]:
        if (y==8 and x==-44) or (y==27 and x==-29):continue
        lamp(x,y)
def bench(x,y,angle=0):
    for i in range(4):box('Bench wooden slat',(x,y-.34+i*.21,1),(1.75,.16,.13),roof,rot=angle,batch=True)
    for xx in [x-.65,x+.65]:box('Bench leg',(xx,y,.69),(.12,.55,.58),dark,batch=True)
    box('Bench back',(x,y+.4,1.36),(1.75,.1,.52),roof,batch=True)
for x,y in [(-11,-28),(11,-28),(-14,9),(14,9),(-40,31),(-15,38),(23,28),(38,27),(-24,39),(11,36)]:bench(x,y)
# Garden interpretation signs, discrete and legible in detail cameras.
def sign(label,x,y,w=4):
    for xx in [x-w*.35,x+w*.35]:beam('Sign post',(xx,y,.4),(xx,y,1.6),.045,gold)
    box('Landscape sign',(x,y,1.65),(w,.17,.7),plinth,.05)
    text_obj('Sign · '+label,label,(x,y-.1,1.67),.32,white,(pi/2,0,0))
sign('二月兰 · 水杉林',32,28,5)
sign('紫霞湖 · 三迎桥',-28,21.3,5)
sign('进德修业  志道鼎新',0,-29.3,6)
# Miniature pedestrians give the architectural model an inhabited scale.
peoplem=[mat('People | '+str(i),h,.7) for i,h in enumerate(['F2D8B3','C85E4E','F0DEAA','F3F0E6','477C87','655178'])]
for i in range(57):
    if i<25:x=random.choice([-17,17])+random.uniform(-.7,.7);y=random.uniform(-41,43)
    elif i<39:x=random.uniform(-12,12);y=random.uniform(-39,-37)
    else:x=random.uniform(-11,11);y=random.uniform(6.8,8.6)
    h=random.uniform(.66,.9)
    cyl('Tiny pedestrian body',(x,y,.48+h*.43),.12,h*.53,random.choice(peoplem[1:]),8)
    sphere('Tiny pedestrian head',(x,y,.5+h*.84),(.12,.12,.135),peoplem[0],2)
    for dx in [-.06,.06]:beam('Tiny pedestrian leg',(x+dx,y,.43),(x+dx,y,.48+h*.27),.037,dark)
for x,y in [(-17,-18),(17,11),(48,-17),(-48,-32),(18,38)]:
    box('Campus electric shuttle',(x,y,1),(1.15,2.3,.83),white,.24)
    box('Shuttle glass',(x,y,1.51),(1.03,1.4,.4),glass,.18)
    for xx in [x-.6,x+.6]:
        for yy in [y-.73,y+.73]:sphere('Shuttle wheel',(xx,yy,.68),(.12,.24,.24),dark,2)

collection('12 · Time garden & landscape details')
disk('Time garden paving',1,37.3,4.7,4.7,.42,path)
cyl('Sundial stone base',(1,37.3,.85),1.8,.8,stone,48)
o=cyl('Sundial bronze disc',(1,37.3,1.55),1.6,.16,gold,48);o.rotation_euler.x=.55
beam('Sundial gnomon',(1,37.3,1.6),(1,38.3,4),.09,gold)
for i in range(12):
    a=i*2*pi/12
    box('Garden hour marker',(1+3.7*cos(a),37.3+3.7*sin(a),.47),(.3,.6,.08),ivory,rot=a,batch=True)
for x,y in [(-8,-36),(8,-36)]:
    disk('Circular flower planter',x,y,1.5,1.5,.6,stone)
    for j in range(30):
        a=random.random()*2*pi;r=random.random()*1.25;sphere('Planter purple blossoms',(x+r*cos(a),y+r*sin(a),.8),(.19,.19,.17),random.choice(purple),1)
for x in [-9,9]:
    beam('Flagpole',(x,8,.4),(x,8,7),.048,gold)
    box('University pennant',(x+.75,8,6.3),(1.5,.06,.85),purple[4],batch=True)
    text_obj('Flag NJUST','NJUST',(x+.75,7.96,6.3),.22,white,(pi/2,0,0),latin=True)
# Corner compass inlay is an orientation cue for the composition, not a survey map.
text_obj('Compass north','N',(-51,46,.5),1.1,dark,latin=True)
mesh('Compass pointer',[(-51,50,.5),(-51.7,47.3,.5),(-51,47.8,.5),(-50.3,47.3,.5)],[(0,1,2),(0,2,3)],gold)

# Flush batched details.
for (cname,mname),(vs,fs) in batches.items():
    COL=bpy.data.collections[cname];mesh('Fine details · '+mname,vs,fs,bpy.data.materials[mname])

collection('13 · Studio, lights & cameras')
box('Matte studio floor',(0,0,-4.5),(2000,2000,1),ground,.1)
world=bpy.data.worlds.new('Soft overcast studio');scene.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.76,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5
def light(name,kind,loc,energy,color,size=0):
    data=bpy.data.lights.new(name,kind);data.energy=energy;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler();return o
sun=light('Late afternoon sun','SUN',(-50,-70,100),2.4,(1,.87,.69));sun.data.angle=.16
light('Large softbox','AREA',(-45,-25,95),45000,(1,.91,.78),80)
light('Sky bounce','AREA',(45,30,65),30000,(.72,.85,1),70)
def camera(name,loc,target,scale,lens=48):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);COL.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;data.lens=lens;data.clip_end=1500;return o
hero=camera('01 | Complete campus', (137,-176,159),(0,1,1),170)
garden_cam=camera('02 | Violet woodland',(70,6,38),(32,35,2),39)
lake_cam=camera('05 | Lake & bridge',(-69,-3,35),(-28,31,1),43)
architecture_cam=camera('03 | Academic heart',(63,-94,67),(0,-5,3),99)
top_cam=camera('04 | Plan view',(0,-.01,180),(0,0,0),127)
scene.camera=hero
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True
scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
    prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU'
except Exception:scene.cycles.device='CPU'
scene.render.resolution_x=2400;scene.render.resolution_y=2000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.film_transparent=False
scene.render.image_settings.color_depth='8'
scene['Project']='南京理工大学 · 紫金兰杉 | NJUST — Violet Spring'
scene['Scope']='Artistic miniature inspired by the Xiaolingwei campus; compressed distances, simplified building geometry, not survey accurate.'
scene['References']='See README.md and references/ for official NJUST campus map, aerial photographs, architecture and landscape sources.'
scene['Seed']=1953
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'NJUST_Violet_Spring.blend'))
print('MODEL_SAVED',len(scene.objects),'objects',flush=True)
manifest={'objects':len(scene.objects),'mesh_vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'cameras':[o.name for o in [hero,garden_cam,architecture_cam,top_cam,lake_cam]],'blender':bpy.app.version_string}
with open(os.path.join(ROOT,'scene_manifest.json'),'w',encoding='utf-8') as f:json.dump(manifest,f,ensure_ascii=False,indent=2)
if '--model-only' not in sys.argv:
    for cam,file,rx,ry in [(hero,'01_campus_hero',2800,2300),(garden_cam,'02_violet_garden',2100,1500),(architecture_cam,'03_architecture',2100,1600),(top_cam,'04_campus_plan',2000,2000),(lake_cam,'05_lake_bridge',2100,1500)]:
        scene.camera=cam;scene.render.resolution_x=rx;scene.render.resolution_y=ry;scene.render.filepath=os.path.join(ROOT,'renders',file+'.png');bpy.ops.render.render(write_still=True);print('RENDER_DONE',file,flush=True)
    scene.camera=hero;scene.render.resolution_x=2400;scene.render.resolution_y=2000
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'NJUST_Violet_Spring.blend'))
print('COMPLETE',flush=True)
