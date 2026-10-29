import bpy,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from refine_lib import *
s=bpy.context.scene
for o in s.objects:
 sn=o.get('SourceName','')
 if sn.startswith('Woodland meandering path'):
  for v in o.data.vertices:v.co.z=(1.015-o.location.z)/o.scale.z
 if sn.startswith('Fine details · Landscape | pale travertine') and any('Vegetation' in c.name for c in o.users_collection):
  for v in o.data.vertices:v.co.z=1.035+(v.co.z-1.98)*.3
save('NJUST_Final')
