const {chromium}=require('D:/entertain/.npm-cache/_npx/31e32ef8478fbf80/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-first-run','--disable-gpu']});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8767',{waitUntil:'networkidle'});
 await page.locator('.tabs button').filter({hasText:'夜色'}).click();
 if(!((await page.locator('#hero').getAttribute('src')).includes('08_Night')))throw Error('Lighting tab did not switch');
 await page.locator('.tabs button').filter({hasText:'余晖'}).click();
 await page.locator('.card').nth(2).click();if(!await page.locator('#lightbox').evaluate(x=>x.open))throw Error('Large image failed');
 await page.locator('#close').click();
 const video=await page.locator('video').evaluate(v=>({width:v.videoWidth,height:v.videoHeight,duration:v.duration,error:v.error?.message||null}));
 if(video.width!==1920||video.height!==1080||Math.abs(video.duration-18)>.1||video.error)throw Error('Video check: '+JSON.stringify(video));
 const count=await page.locator('.card').count();if(count!==10)throw Error('Missing views');
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'D:/entertain/njust-refined/reports/gallery_desktop.png'});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:'D:/entertain/njust-refined/reports/gallery_mobile.png'});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(overflow)throw Error('Mobile overflow');
 const report={images:count,lightingTabs:true,lightbox:true,video,mobileOverflow:overflow,errors};fs.writeFileSync('D:/entertain/njust-refined/reports/gallery_verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
