import {AbsoluteFill,useCurrentFrame,interpolate} from 'remotion';
import {C,Frame,Media,Title,usePortrait,clamp,ease} from './Shared';
export const DayNight=()=>{const f=useCurrentFrame(),v=usePortrait();const p=interpolate(f,[43,76],[0,1],{...clamp,easing:ease});return <Frame section="THE REVEAL">
 <Media src={v?'portrait_DAY.png':'01_Day_Aerial.png'} zoom={v?1.08:1}/>
 <AbsoluteFill style={{opacity:p}}><Media src={v?'portrait_NIGHT.png':'08_Night.png'} zoom={v?1.08:1} brightness={1.65}/></AbsoluteFill>
 <Title lines={['同一座校园，','两种心跳']} eyebrow={f<60?'DAYLIGHT / 白昼':'NIGHTFALL / 夜色'} accent={f<60?C.gold:C.violet}/>
 </Frame>};
export const Gate=()=>{const v=usePortrait();return <Frame section="STEP INSIDE">
 <Media src="03_Gate.png" position={v?'50% 58%':'50% 50%'} zoom={1.02}/>
 <Title lines={['这一刻，','走进南理工']} eyebrow="南京理工大学" accent={C.gold}/>
 </Frame>};
export const Avenue=()=>{const v=usePortrait();return <Frame section="THE AVENUE">
 <Media src="flythrough.mp4" video trim={90} position={v?'60% 50%':'50% 50%'} rate={.75}/>
 <Title lines={['穿过林荫，','看见致远']} eyebrow="ARCHITECTURE / 校园楼宇" accent={C.white}/>
 </Frame>};
export const Lake=()=>{const v=usePortrait();return <Frame section="WATER & REFLECTIONS">
 <Media src="flythrough.mp4" video trim={300} rate={.85} position={v?'48% 50%':'50% 50%'}/>
 <Title lines={['桥与水，','也有了光']} eyebrow="LANDSCAPE / 水岸光影" accent={C.cyan}/>
 </Frame>};
export const Night=()=>{const v=usePortrait();return <Frame section="AFTER DARK">
 {v?<Media src="portrait_NIGHT.png" zoom={1.1} brightness={1.65}/>:<Media src="night.mp4" video rate={.75} brightness={1.45}/>}
 <Title lines={['灯火亮起，','校园再次醒来']} eyebrow="NIGHT / 约 30% 随机亮窗" accent={C.violet}/>
 </Frame>};
