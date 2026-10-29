import {AbsoluteFill,useCurrentFrame,interpolate} from 'remotion';
import {C,Frame,Media,Title,usePortrait,clamp} from './Shared';
export const Hook=()=>{const v=usePortrait();const f=useCurrentFrame();return <Frame section="CAMPUS REIMAGINED">
 {v?<Media src="portrait_GOLDEN_HOUR.png" position="50% 43%" zoom={1.08}/>:<Media video src="hero.mp4"/>}
 <div style={{position:'absolute',top:v?260:170,left:v?70:60,fontSize:v?250:380,lineHeight:1,fontFamily: 'Bahnschrift, Arial, sans-serif' ,letterSpacing:-20,color:'transparent',WebkitTextStroke:'2px #d8f5ff55',opacity:.32,translate:`${interpolate(f,[0,120],[-25,20],clamp)}px 0`}}>NJUST</div>
 <Title huge lines={['把南理工','装进 Blender']} eyebrow="从一座模型，到一整个世界" sub="校园建模过程 × 最终视觉展示"/>
 </Frame>};
export const Finale=()=>{const v=usePortrait(),f=useCurrentFrame();return <Frame section="FROM CODE TO CAMPUS">
 {v?<Media src="portrait_GOLDEN_HOUR.png" zoom={1.08}/>:<Media video src="hero.mp4"/>}
 <Title lines={['在另一种世界里','与南理工重逢']} eyebrow="NANJING · A CAMPUS STUDY" accent={C.gold} sub="Blender 建模 / 程序化细节 / 光影渲染"/>
 <div style={{position:'absolute',left:v?90:92,bottom:v?270:65,fontSize:v?23:20,color:'#ccd8df'}}>校园艺术化建模作品 · 非实景航拍</div>
 <AbsoluteFill style={{background:'#030910',opacity:interpolate(f,[107,119],[0,1],clamp)}}/>
 </Frame>};
