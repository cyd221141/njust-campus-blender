import {AbsoluteFill,Img,staticFile,useCurrentFrame,interpolate} from 'remotion';
import {C,Frame,Media,Title,Grid,Scan,usePortrait,clamp,ease} from './Shared';
export const Origin=()=>{const f=useCurrentFrame(),v=usePortrait();const wire=interpolate(f,[35,52],[0,1],clamp);return <Frame section="THE STARTING POINT" process>
 <Media src="original.png" contain={v} zoom={v?1.12:1.0}/>
 <AbsoluteFill style={{background:C.ink,opacity:wire}}><Grid/><Img src={staticFile('media/wire.png')} style={{width:'100%',height:'100%',objectFit:v?'contain':'cover',transform:`scale(${v?1.1:1})`}}/><Scan/></AbsoluteFill>
 <Title lines={f<42?['起点，','一座校园模型']:['看见骨架，','再赋予细节']} eyebrow={f<42?'BEFORE / 原始版本':'WIREFRAME / 主体结构'} accent={C.cyan}/>
 </Frame>};
export const Assembly=()=>{const v=usePortrait(),f=useCurrentFrame();return <Frame section="01 / BUILD THE SPACE" process>
 <Media src="assembly.mp4" video contain={v} zoom={v?1.2:1}/><Grid/>
 <Title lines={['从体块，','到建筑群']} eyebrow="01 / 空间生长" sub="保留原有布局 · 逐层完善校园"/>
 <div style={{position:'absolute',right:v?135:100,top:v?300:180,textAlign:'right'}}><span style={{fontFamily: 'Bahnschrift, Arial, sans-serif' ,fontSize:v?140:180,color:C.white}}>{Math.min(24,Math.floor(f/3.7))}</span><div style={{fontSize:v?28:23,color:C.cyan,letterSpacing:4}}>栋主体建筑</div></div>
 </Frame>};
export const Facade=()=>{const f=useCurrentFrame(),v=usePortrait();const n=Math.round(interpolate(f,[5,72],[0,2046],{...clamp,easing:ease}));return <Frame section="02 / DETAIL MATTERS" process>
 <Media src="09_Central_Building.png" position={v?'58% 50%':'50% 50%'} zoom={1.02}/>
 <div style={{position:'absolute',left:v?88:92,top:v?245:210,color:C.cyan}}><div style={{fontSize:v?32:25,letterSpacing:6}}>02 / 立面精修</div><div style={{fontSize:v?220:280,fontFamily: 'Bahnschrift, Arial, sans-serif' ,fontWeight:700,letterSpacing:-12,lineHeight:1.12,textShadow:'0 0 45px #09273e'}}>{n.toLocaleString('en-US')}</div><div style={{fontSize:v?43:42}}>扇窗，把细节填满。</div></div>
 <Title lines={['让建筑，','有了表情']} accent={C.white}/>
 </Frame>};
export const Nature=()=>{const v=usePortrait(),f=useCurrentFrame();return <Frame section="03 / BRING IT TO LIFE" process>
 <Media src="grove.mp4" video rate={.75} position={v?'60% 50%':'50% 50%'}/>
 <Title lines={['把春天，','种进校园']} eyebrow="03 / 植被与生活" accent={C.violet} sub="水杉 · 二月兰 · 林间步道"/>
 <div style={{position:'absolute',top:v?280:205,right:v?145:100,fontFamily: 'Bahnschrift, Arial, sans-serif' ,fontSize:v?39:35,color:'#e2edce',textAlign:'right',opacity:interpolate(f,[15,35],[0,1],clamp)}}>8 TREE VARIANTS<br/><span style={{fontSize:v?25:23,letterSpacing:3}}>10 PROCEDURAL SYSTEMS</span></div>
 </Frame>};
export const Material=()=>{const f=useCurrentFrame(),v=usePortrait();const wipe=interpolate(f,[20,95],[0,100],{...clamp,easing:ease});return <Frame section="04 / LIGHT FINDS FORM" process>
 <Media src="clay.png" contain={v}/>
 <AbsoluteFill style={{clipPath:`inset(0 ${100-wipe}% 0 0)`}}>{v?<Media src="portrait_GOLDEN_HOUR.png"/>:<Media src="hero.mp4" video/>}</AbsoluteFill>
 {wipe>0&&wipe<100&&<div style={{position:'absolute',top:0,bottom:0,left:`${wipe}%`,width:4,background:C.cyan,boxShadow:`0 0 45px ${C.cyan}`}}/>}
 <Title lines={['材质就位，','光影接管']} eyebrow="04 / 从白模到成片" accent={C.gold}/>
 </Frame>};
