import bpy,json,os
from mathutils import Vector
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=bpy.context.scene
data={'scene':s.name,'units':s.unit_settings.system,'unit_scale':s.unit_settings.scale_length,'objects':[],'collections':[],'materials':[m.name for m in bpy.data.materials]}
for c in bpy.data.collections:data['collections'].append({'name':c.name,'objects':len(c.objects)})
for o in s.objects:
 data['objects'].append({'name':o.name,'type':o.type,'collections':[c.name for c in o.users_collection],'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),'dimensions':list(o.dimensions),'materials':[m.name if m else None for m in getattr(o.data,'materials',[])],'modifiers':[m.type for m in o.modifiers]})
with open(os.path.join(root,'reports','original_inventory.json'),'w',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print('ORIGINAL_AUDIT',len(s.objects),'objects',len(bpy.data.materials),'materials')
