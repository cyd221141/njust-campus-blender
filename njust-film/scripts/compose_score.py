"""Original 120 BPM electronic score and synchronized transitions; no sampled songs."""
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile
R=Path(__file__).resolve().parents[1];SR=48000;D=48;N=SR*D
rng=np.random.default_rng(1953);mix=np.zeros((N,2),dtype=np.float64)
def add(x,t,g=1,pan=0):
 start=round(t*SR);end=min(N,start+len(x));n=end-start
 if n<=0:return
 left=np.sqrt((1-pan)/2);right=np.sqrt((1+pan)/2)
 if x.ndim==1:mix[start:end,0]+=x[:n]*g*left;mix[start:end,1]+=x[:n]*g*right
 else:mix[start:end]+=x[:n]*g
def note(m):return 440*2**((m-69)/12)
def pluck(m,d=.43):
 t=np.arange(int(SR*d))/SR;f=note(m);x=sum(np.sin(2*np.pi*f*k*t)*np.exp(-t*(4+k*3))/k for k in range(1,6));return x*(1-np.exp(-t*240))
def kick():
 t=np.arange(int(SR*.48))/SR;phase=2*np.pi*(43*t+90*.025*(1-np.exp(-t/.025)))
 return np.sin(phase)*np.exp(-t*9)+rng.normal(0,.05,len(t))*np.exp(-t*240)
def snare():
 t=np.arange(int(SR*.25))/SR;noise=rng.normal(size=len(t));noise=signal.sosfilt(signal.butter(2,[900,11000],btype='bandpass',fs=SR,output='sos'),noise)
 return noise*np.exp(-t*19)*.55+np.sin(2*np.pi*185*t)*np.exp(-t*29)*.33
def hat(opened=False):
 t=np.arange(int(SR*(.23 if opened else .075)))/SR;noise=rng.normal(size=len(t));noise=signal.sosfilt(signal.butter(2,8500,btype='highpass',fs=SR,output='sos'),noise)
 return noise*np.exp(-t*(23 if opened else 70))*.22
K=kick();S=snare()
# Warm, slowly evolving pad chords in D minor / Bb / F / C.
chords=[[50,57,60,64],[46,53,57,60],[48,53,57,60],[48,55,58,62]]
for bar in range(12):
 st=bar*4;t=np.arange(SR*5)/SR;ch=chords[bar%4];pad=np.zeros((len(t),2))
 for j,m in enumerate(ch):
  for side,det in enumerate([.9978,1.0022]):
   x=sum(np.sin(2*np.pi*note(m)*det*k*t+j*.9)/(k**1.7) for k in range(1,7));pad[:,side]+=x
 env=np.minimum(t/1.0,1)*np.minimum(np.maximum(5-t,0)/1.2,1)
 pump=(.55+.45*(1-np.exp(-(t%.5)*12))) if st>=24 else np.ones(len(t))
 pad*=env[:,None]*pump[:,None]
 add(pad,st,.048 if st<24 else .082)
# A distinct repeating arpeggio opens into a wider lead after the drop.
for k in range(176):
 st=2+k*.25
 if st>45:break
 ch=chords[int(st//4)%4];m=ch[[0,2,1,3,2,1,3,1][k%8]]+24
 v=.035 if st<8 else .065 if st<24 else .11
 if 22<st<24:v*=max(0,(24-st)/2)
 x=pluck(m);add(x,st,v,np.sin(k*1.5)*.55);add(x,st+.375,v*.28,-np.sin(k*1.5)*.6)
# Kick, backbeat and bass on the same half-second grid as edit points.
for b in range(92):
 st=b*.5
 if st<4 or 22.5<=st<24:continue
 strength=.34 if st<8 else .48 if st<24 else .7
 add(K,st,strength)
 if b%4 in [1,3]:add(S,st,.26 if st<24 else .43)
 if st>=8:
  add(hat(),st+.25,.32,(-1 if b%2 else 1)*.35)
  if st>=24:add(hat(b%4==3),st,.28,.2)
 root=chords[int(st//4)%4][0]-12
 t=np.arange(int(SR*.43))/SR;freq=note(root);bass=np.sin(2*np.pi*freq*t)+.22*np.sin(2*np.pi*freq*2*t)+.08*np.sin(2*np.pi*freq*3*t)
 env=(1-np.exp(-t*100))*np.exp(-t*3.5);add(bass*env,st+.035,.2 if st<24 else .3)
# Original impacts, reverse-air sweeps, UI ticks and a build-up into the reveal.
for cut in [0,4,8,12,16,20,24,28,32,36,40,44]:
 t=np.arange(int(SR*1.15))/SR;boom=np.sin(2*np.pi*(37*t+22*.13*(1-np.exp(-t/.13))))*np.exp(-t*4)
 add(boom,cut,.32 if cut!=24 else .65)
 if cut:
  t=np.arange(int(SR*.65))/SR;noise=rng.normal(size=len(t));noise=signal.sosfilt(signal.butter(2,[1200,6000],btype='bandpass',fs=SR,output='sos'),noise);env=(t/.65)**3
  add(noise*env,cut-.65,.11,-.2);add(noise[::-1]*env[::-1],cut,.09,.2)
for t0 in np.arange(20,24,.125):add(hat(),float(t0),.10+(t0-20)*.04,np.sin(t0*4)*.5)
for t0 in [5,5.5,6,6.5,12,12.25,12.5,16,16.25]:
 t=np.arange(int(SR*.065))/SR;add(np.sin(2*np.pi*1350*t)*np.exp(-t*80),t0,.035,.45)
add(pluck(74,2),46,.3,-.15);add(pluck(81,2),46,.13,.15)
# Gentle master saturation, fades and headroom; final LUFS normalization via FFmpeg.
fade=np.ones(N);fade[:SR//50]=np.linspace(0,1,SR//50);fade[-SR*2:]=np.linspace(1,0,SR*2)**1.4
mix=np.tanh(mix*1.35)*fade[:,None];mix*=.84/max(np.max(np.abs(mix)),1e-9)
wavfile.write(R/'public/audio/score_raw.wav',SR,(mix*32767).astype(np.int16))
print('ORIGINAL_SCORE',D,'seconds',SR,'Hz stereo','peak',np.max(np.abs(mix)))
