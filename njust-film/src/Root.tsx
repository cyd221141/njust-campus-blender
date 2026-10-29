import "./index.css";
import {Composition,Folder} from 'remotion';
import {Film,SCENES} from './Film';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="NJUST-Bilibili" component={Film} durationInFrames={1440} fps={30} width={1920} height={1080}/>
      <Composition id="NJUST-Douyin" component={Film} durationInFrames={1440} fps={30} width={1080} height={1920}/>
      <Folder name="Editable-Scenes">{SCENES.map((Scene,i)=><Composition key={i} id={`Scene-${i+1}-${Scene.name}`} component={Scene} durationInFrames={120} fps={30} width={1920} height={1080}/>)}</Folder>
    </>
  );
};
