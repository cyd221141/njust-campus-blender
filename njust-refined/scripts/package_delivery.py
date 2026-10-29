from pathlib import Path
import json,hashlib,zipfile,struct,re
root=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
original=root.parent/'njust-miniature'/'NJUST_Violet_Spring.blend';backup=root/'NJUST_v00_Original.blend'
files=[root/'NJUST_Final.blend',root/'README.md',root/'修改报告.md',root/'index.html',root/'animation'/'NJUST_Campus_Flythrough_18s.mp4']
files+=sorted(p for p in (root/'renders').glob('*.png') if re.match(r'^\d\d_',p.name))
files+=sorted((root/'scripts').glob('*.py'))+sorted((root/'scripts').glob('*.ps1'))+sorted((root/'references').glob('*'))
files+=sorted((root/'reports').glob('*.json'))
manifest={'original_backup_matches':sha(original)==sha(backup),'backup_sha256':sha(backup),'files':[]}
for p in files:
 if not p.is_file():raise RuntimeError('Missing delivery file: '+str(p))
 item={'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix=='.png':
  with p.open('rb') as f:data=f.read(24)
  item['dimensions']=struct.unpack('>II',data[16:24])
 manifest['files'].append(item)
out=root/'reports'/'delivery_manifest.json';out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'NJUST_Delivery.zip','w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
 for p in files+[out]:z.write(p,p.relative_to(root).as_posix())
print(json.dumps({'verified_files':len(files),'original_backup_matches':manifest['original_backup_matches'],'zip_bytes':(root/'NJUST_Delivery.zip').stat().st_size},indent=2))
