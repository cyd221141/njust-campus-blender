"""Run this text in Blender to add the NJUST controls to the 3D View N-panel."""
import bpy
ns={};exec(bpy.data.texts['lighting.py'].as_string(),ns)
class NJUST_OT_preset(bpy.types.Operator):
 bl_idname='njust.preset';bl_label='Lighting preset'
 value:bpy.props.StringProperty()
 def execute(self,context):ns['set_lighting'](self.value);return {'FINISHED'}
class NJUST_OT_camera(bpy.types.Operator):
 bl_idname='njust.camera';bl_label='Campus camera'
 value:bpy.props.StringProperty()
 def execute(self,context):
  ns['set_camera'](self.value);ns['update_lod']()
  for a in context.screen.areas:
   if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA'
  return {'FINISHED'}
class NJUST_OT_engine(bpy.types.Operator):
 bl_idname='njust.engine';bl_label='Render profile'
 value:bpy.props.StringProperty()
 def execute(self,context):ns['set_engine'](self.value);return {'FINISHED'}
class NJUST_PT_panel(bpy.types.Panel):
 bl_label='NJUST Campus';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='NJUST'
 def draw(self,context):
  l=self.layout;l.label(text='Lighting')
  for p in ['DAY','GOLDEN_HOUR','NIGHT']:l.operator('njust.preset',text=p.replace('_',' ')).value=p
  l.separator();r=l.row()
  for p in ['CYCLES','EEVEE']:r.operator('njust.engine',text=p).value=p
  l.separator();l.label(text='Cameras / refresh distance LOD')
  for o in context.scene.objects:
   if o.type=='CAMERA' and not o.get('SupersededReason'):l.operator('njust.camera',text=o.name.replace('Camera_','')).value=o.name
  l.separator();l.label(text='Select GN object > Modifier for scatter controls')
for c in [NJUST_OT_preset,NJUST_OT_camera,NJUST_OT_engine,NJUST_PT_panel]:
 old=getattr(bpy.types,c.__name__,None)
 if old:bpy.utils.unregister_class(old)
 bpy.utils.register_class(c)
