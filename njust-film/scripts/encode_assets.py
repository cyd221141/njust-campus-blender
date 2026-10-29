from pathlib import Path
import os
import subprocess,json
R=Path(__file__).resolve().parents[1]
FF=os.environ.get('FFMPEG_PATH','ffmpeg')
for name,n in [('assembly',120),('hero',120),('grove',90),('night',90)]:
 files=list((R/'process'/name).glob('*.png'))
 if len(files)!=n:raise RuntimeError(f'{name}: {len(files)}/{n} frames')
 with (R/'reports'/f'encode_{name}.log').open('w') as log:
  subprocess.run([FF,'-y','-framerate','30','-i',str(R/'process'/name/'%04d.png'),'-frames:v',str(n),'-c:v','libx264','-threads','4','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(R/'public'/'media'/f'{name}.mp4')],stdout=log,stderr=log,check=True)
 print(name,n,'frames encoded',flush=True)
