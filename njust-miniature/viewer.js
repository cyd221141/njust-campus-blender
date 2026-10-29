import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const host=document.querySelector('#view'),loading=document.querySelector('#loading');
const scene=new THREE.Scene();scene.background=new THREE.Color('#e6e7dc');
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.7));renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;host.append(renderer.domElement);
const fittedFov=()=>Math.max(40,THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(20))*1.1/(innerWidth/innerHeight))));
const camera=new THREE.PerspectiveCamera(fittedFov(),innerWidth/innerHeight,.1,1400);
camera.position.set(110,128,142);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,2,0);controls.enableDamping=true;controls.dampingFactor=.06;controls.minDistance=12;controls.maxDistance=360;controls.maxPolarAngle=Math.PI*.48;controls.autoRotateSpeed=.35;
scene.add(new THREE.HemisphereLight('#e4f0ff','#8c9977',2.2));
const sun=new THREE.DirectionalLight('#fff0d2',3);sun.position.set(-65,100,70);sun.castShadow=true;sun.shadow.mapSize.set(4096,4096);Object.assign(sun.shadow.camera,{left:-95,right:95,top:95,bottom:-95,near:1,far:300});sun.shadow.normalBias=.05;sun.shadow.bias=-.00015;scene.add(sun);
const fill=new THREE.DirectionalLight('#dceaff',1.1);fill.position.set(60,45,-50);scene.add(fill);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(2400,2400),new THREE.MeshStandardMaterial({color:'#d9ddcd',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-4.06;floor.receiveShadow=true;scene.add(floor);
window.__campus={loaded:false};
new GLTFLoader().load('./NJUST_Violet_Spring.glb',g=>{
 g.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});scene.add(g.scene);loading.style.display='none';window.__campus.loaded=true;window.__campus.meshes=0;g.scene.traverse(o=>{if(o.isMesh)window.__campus.meshes++;});
},p=>{if(p.total)loading.querySelector('span').textContent=`正在展开春日校园 · ${Math.round(p.loaded/p.total*100)}%`;},e=>{console.error(e);loading.classList.add('error');loading.innerHTML='模型未能加载。请通过「打开校园预览.cmd」启动本地预览。<br><a href="renders/01_campus_hero.png">也可以先查看完整渲染图 →</a>';window.__campus.error=String(e);});
const views={
 hero:{p:[110,128,142],t:[0,2,0],title:'在一方沙盘里，重逢南理工',desc:'沿着校园轴线，走过弧形图书馆与致远楼，再去水杉林下，寻找那片紫色的春天。'},
 architecture:{p:[57,57,88],t:[0,4,5],title:'书页般展开的校园中心',desc:'暖白色的弧形图书馆，层层窗格的致远楼，以及承载记忆的校园轴线。'},
 garden:{p:[65,33,-8],t:[32,2,-35],title:'水杉林下，紫色花海',desc:'一株株高挑的水杉，与成片的四瓣二月兰。林间小径、长椅与路灯，留住春天的片刻。'},
 lake:{p:[-61,32,2],t:[-28,1,-31],title:'三迎桥，卧在一池春水上',desc:'浅青色湖面与白石拱桥相映。走过小桥，听见树影、校园与水的呼吸。'},
 plan:{p:[0,205,.01],t:[0,0,0],title:'把整座春日校园，收进眼底',desc:'教学、生活、运动与林水景观，以经过艺术化压缩的布局，组成一座完整的微缩校园。'}
};
let transition=null;
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{
 const v=views[b.dataset.view];controls.autoRotate=false;document.querySelector('#rotate').classList.remove('active');
 transition={start:performance.now(),p0:camera.position.clone(),t0:controls.target.clone(),p1:new THREE.Vector3(...v.p),t1:new THREE.Vector3(...v.t)};
 document.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('active',x===b));document.querySelector('#scene-title').textContent=v.title;document.querySelector('#scene-desc').textContent=v.desc;
});
controls.addEventListener('start',()=>{transition=null;});
document.querySelector('#rotate').onclick=e=>{controls.autoRotate=!controls.autoRotate;e.currentTarget.classList.toggle('active',controls.autoRotate);};
document.querySelector('#gallery-open').onclick=()=>document.querySelector('#gallery').classList.add('open');
document.querySelector('#gallery-close').onclick=()=>document.querySelector('#gallery').classList.remove('open');
addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelector('#gallery').classList.remove('open');});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.fov=fittedFov();camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
renderer.setAnimationLoop(()=>{if(transition){let t=Math.min(1,(performance.now()-transition.start)/1400);t=t*t*(3-2*t);camera.position.lerpVectors(transition.p0,transition.p1,t);controls.target.lerpVectors(transition.t0,transition.t1,t);if(t===1)transition=null;}controls.update();renderer.render(scene,camera);});
