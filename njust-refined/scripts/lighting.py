import bpy,math,os
def set_lighting(preset='GOLDEN_HOUR'):
 s=bpy.context.scene;s['LightingPreset']=preset
 for p in ['DAY','GOLDEN_HOUR','NIGHT']:
  c=bpy.data.collections.get('LIGHTING_'+p)
  if c:c.hide_render=p!=preset;c.hide_viewport=p!=preset
 s.world=bpy.data.worlds['WORLD_'+preset]
 for name,strength in [('Interior_Lit',2.8 if preset=='NIGHT' else .045),('Luminaire',7 if preset=='NIGHT' else .035)]:
  m=bpy.data.materials.get(name)
  if m:m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=strength
 s.view_settings.exposure=1.3 if preset=='NIGHT' else .65
def set_engine(engine='CYCLES',quality='FINAL'):
 s=bpy.context.scene;s.render.engine='BLENDER_EEVEE' if engine=='EEVEE' else 'CYCLES'
 if engine=='CYCLES':
  s.cycles.samples=80 if quality=='FINAL' else 24;s.cycles.use_denoising=True;s.cycles.denoiser='OPTIX';s.cycles.max_bounces=7;s.cycles.transmission_bounces=4;s.cycles.diffuse_bounces=3;s.cycles.glossy_bounces=3
  p=bpy.context.preferences.addons['cycles'].preferences
  try:
   p.compute_device_type='OPTIX';p.get_devices()
   for d in p.devices:d.use=d.type=='OPTIX'
   s.cycles.device='GPU'
  except:s.cycles.device='CPU'
 else:
  s.eevee.taa_render_samples=32 if quality=='FINAL' else 16
 s.render.use_simplify=True;s.render.simplify_subdivision=1;s.render.simplify_subdivision_render=1
def aim_lod(camera):
 ref=bpy.data.objects.get('LOD_Camera_Reference')
 if ref:
  ref.constraints.clear();c=ref.constraints.new('COPY_LOCATION');c.target=camera
def set_camera(name):
 s=bpy.context.scene;s.camera=bpy.data.objects[name];aim_lod(s.camera)
def update_lod(camera=None,distance=95):
 s=bpy.context.scene;cam=camera or s.camera
 if not cam:return
 pos=cam.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
 for o in s.objects:
  if o.get('LOD')==2 and not o.get('SupersededReason'):
   visible=(o.matrix_world.translation-pos).length<distance
   # Meshes batched in world coordinates use their bounding-box centre.
   if o.type=='MESH' and o.location.length<.01:
    from mathutils import Vector
    centre=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8;visible=(centre-pos).length<distance+max(o.dimensions)/2
   o.hide_render=not visible;o.hide_set(not visible)
