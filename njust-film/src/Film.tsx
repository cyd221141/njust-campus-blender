import {AbsoluteFill,Sequence,useCurrentFrame,useVideoConfig,staticFile} from 'remotion';
import {Audio} from '@remotion/media';
import {Hook,Finale} from './Hook';import {Origin,Assembly,Facade,Nature,Material} from './Process';import {DayNight,Gate,Avenue,Lake,Night} from './Campus';
import {C} from './Shared';
export const SCENES=[Hook,Origin,Assembly,Facade,Nature,Material,DayNight,Gate,Avenue,Lake,Night,Finale];
export const Film=()=>{const f=useCurrentFrame(),{width,height}=useVideoConfig();const v=height>width;return <AbsoluteFill style={{background:C.ink}}>
 {SCENES.map((Scene,i)=><Sequence key={i} name={Scene.name} from={i*120} durationInFrames={120}><Scene/></Sequence>)}
 <Audio src={staticFile('audio/score.wav')}/>
 <div style={{position:'absolute',bottom:v?224:25,left:v?90:90,right:v?150:90,height:2,background:'#c4e9fa22'}}><div style={{height:2,width:`${f/1439*100}%`,background:C.cyan,boxShadow:`0 0 14px ${C.cyan}`}}/></div>
 <div style={{position:'absolute',right:v?150:88,top:v?128:68,fontFamily: 'Bahnschrift, Arial, sans-serif' ,color:'#e8f2fa',fontSize:v?24:21,letterSpacing:3}}>{String(Math.floor(f/120)+1).padStart(2,'0')}<span style={{opacity:.4}}> / 12</span></div>
 </AbsoluteFill>};
