from pathlib import Path
import os
import subprocess, json, re, hashlib, zipfile
R=Path(__file__).resolve().parents[1]
FF=Path(os.environ.get('FFMPEG_PATH','ffmpeg'))
PROBE=R/'node_modules/@remotion/compositor-win32-x64-msvc/ffprobe.exe'
results={}
for label,w,h in [('Bilibili',1920,1080),('Douyin',1080,1920)]:
 p=R/'output'/f'NJUST_{label}_48s_1080p.mp4'
 info=json.loads(subprocess.check_output([str(PROBE),'-v','error','-show_entries','format=duration,size,bit_rate:stream=codec_name,codec_type,width,height,r_frame_rate,duration,nb_frames,sample_rate,channels,pix_fmt','-of','json',str(p)]))
 v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'])==(w,h)
 assert v['r_frame_rate']=='30/1' and int(v['nb_frames'])==1440
 assert abs(float(info['format']['duration'])-48)<.1
 assert a['codec_name']=='aac' and a['channels']==2 and a['sample_rate']=='48000'
 # Decode the complete video/audio streams and measure the actual delivered AAC.
 cache=R/'reports'/'audio-wide-check.log'
 if label=='Bilibili' and cache.exists() and cache.stat().st_mtime>p.stat().st_mtime:
  log=cache.read_text(encoding='utf-8-sig');assert re.search(r'frame=\s*1440',log)
 else:
  check=subprocess.run([str(FF),'-hide_banner','-nostats','-v','info','-i',str(p),'-af','loudnorm=I=-14:TP=-1.2:LRA=8:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
  assert check.returncode==0,check.stderr[-2000:]
  log=check.stderr
 (R/'reports'/f'validate_{label}.log').write_text(log,encoding='utf-8')
 meter=json.loads(re.search(r'\{\s*"input_i".*?\}',log,re.S).group(0))
 assert -17<float(meter['input_i'])<-11
 assert float(meter['input_tp'])<0
 results[label]={'file':p.name,'metadata':info,'audio_loudness':meter,'full_decode':'passed','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 print(label,info['format']['size'],'bytes',meter['input_i'],'LUFS',meter['input_tp'],'dBTP',flush=True)
(R/'reports'/'delivery_validation.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
with zipfile.ZipFile(R/'output'/'NJUST_Publish_Pack.zip','w',zipfile.ZIP_STORED) as z:
 for p in sorted((R/'output').iterdir()):
  if p.suffix.lower() in ['.mp4','.png','.md']:z.write(p,p.name)
 z.write(R/'reports'/'delivery_validation.json','delivery_validation.json')
print('Delivery validated and publishing pack created.',flush=True)
