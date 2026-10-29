import React from 'react';
import {AbsoluteFill,Img,staticFile,useCurrentFrame,useVideoConfig,interpolate,Easing} from 'remotion';
import {Video} from '@remotion/media';
export const C={ink:'#07111e',cyan:'#83e9ff',violet:'#c0a2ff',white:'#f4f7fa',gold:'#ffdbad'};
export const clamp={extrapolateLeft:'clamp' as const,extrapolateRight:'clamp' as const};
export const ease=Easing.bezier(.16,1,.3,1);
export const usePortrait=()=>{const {width,height}=useVideoConfig();return height>width};
export const Media:React.FC<{src:string;video?:boolean;rate?:number;trim?:number;position?:string;zoom?:number;contain?:boolean;brightness?:number}>=({src,video=false,rate=1,trim=0,position='50% 50%',zoom=1,contain=false,brightness=1})=>{
 const f=useCurrentFrame();const v=usePortrait();const scale=zoom*interpolate(f,[0,120],[1,1.065],clamp);
 return <AbsoluteFill style={{overflow:'hidden',background:C.ink}}>
  <AbsoluteFill style={{transform:`scale(${scale})`,transformOrigin:position,filter:`brightness(${brightness})`}}>
   {video?<Video src={staticFile('media/'+src)} trimBefore={trim} playbackRate={rate} muted objectFit={contain?'contain':'cover'} style={{width:'100%',height:'100%',objectPosition:position}}/>:<Img src={staticFile('media/'+src)} style={{width:'100%',height:'100%',objectFit:contain?'contain':'cover',objectPosition:position}}/>}
  </AbsoluteFill>
  <AbsoluteFill style={{background:`linear-gradient(180deg,rgba(3,9,18,${v?.38:.2}) 0%, transparent 40%, rgba(3,9,18,.12) 60%,rgba(3,9,18,${v?.83:.8}) 100%)`}}/>
  <AbsoluteFill style={{boxShadow:'inset 0 0 240px rgba(2,8,18,.22)'}}/>
 </AbsoluteFill>
};
export const Frame:React.FC<{children:React.ReactNode;section?:string;process?:boolean}>=({children,section='',process=false})=>{
 const f=useCurrentFrame(),v=usePortrait();const flash=interpolate(f,[0,3,8],[.20,.04,0],clamp);
 return <AbsoluteFill style={{background:C.ink,color:C.white,fontFamily: '"Microsoft YaHei", "Noto Sans CJK SC", sans-serif' ,overflow:'hidden'}}>{children}
  <div style={{position:'absolute',top:v?125:65,left:v?88:90,fontFamily: 'Bahnschrift, Arial, sans-serif' ,fontSize:v?23:20,letterSpacing:5,color:'#e6f6ff',display:'flex',alignItems:'center',gap:15}}><i style={{display:'block',height:9,width:9,borderRadius:5,background:C.cyan,boxShadow:`0 0 24px ${C.cyan}`}}/>NJUST <span style={{opacity:.55}}> / </span> {section}</div>
  {process&&<div style={{position:'absolute',bottom:v?300:48,right:v?125:84,fontSize:v?22:18,color:'#c5d8e5',letterSpacing:1}}>制作过程演示 · 基于工程资产</div>}
  <AbsoluteFill style={{background:C.cyan,opacity:flash,pointerEvents:'none'}}/>
 </AbsoluteFill>
};
export const Title:React.FC<{lines:string[];eyebrow?:string;sub?:string;accent?:string;top?:boolean;huge?:boolean}>=({lines,eyebrow,sub,accent=C.cyan,top=false,huge=false})=>{
 const f=useCurrentFrame(),v=usePortrait();return <div style={{position:'absolute',left:v?88:90,right:v?130:90,...(top?{top:v?235:210}:{bottom:v?360:125})}}>
  {eyebrow&&<div style={{fontFamily: 'Bahnschrift, Arial, sans-serif' ,fontSize:v?27:24,letterSpacing:6,color:accent,marginBottom:26,opacity:interpolate(f,[3,18],[0,1],clamp)}}>{eyebrow}</div>}
  {lines.map((line,i)=><div key={i} style={{overflow:'hidden',paddingBottom:6}}><div style={{fontSize:v?(huge?108:88):(huge?140:104),lineHeight:1.18,letterSpacing:v?-3:-4,fontWeight:700,color:i===lines.length-1?accent:C.white,textShadow:'0 4px 25px rgba(0,0,0,.3)',opacity:interpolate(f,[5+i*4,16+i*4],[0,1],clamp),translate:`0 ${interpolate(f,[5+i*4,29+i*4],[130,0],{...clamp,easing:ease})}px`}}>{line}</div></div>)}
  {sub&&<div style={{fontSize:v?31:30,lineHeight:1.6,letterSpacing:2,marginTop:23,color:'#dde5ed',opacity:interpolate(f,[27,43],[0,1],clamp),translate:`0 ${interpolate(f,[27,43],[18,0],clamp)}px`}}>{sub}</div>}
 </div>
};
export const Grid=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{backgroundImage:'linear-gradient(#72ddff0d 1px,transparent 1px),linear-gradient(90deg,#72ddff0d 1px,transparent 1px)',backgroundSize:'80px 80px',backgroundPosition:`${f*.22}px ${f*.4}px`,opacity:.8}}/>};
export const Scan=()=>{const f=useCurrentFrame();return <div style={{position:'absolute',left:0,right:0,top:`${interpolate(f,[15,112],[5,95],clamp)}%`,height:2,background:C.cyan,boxShadow:`0 0 28px 7px ${C.cyan}55`}}/>};
