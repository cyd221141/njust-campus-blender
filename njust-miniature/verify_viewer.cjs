const { chromium }=require('D:/entertain/.npm-cache/_npx/31e32ef8478fbf80/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-first-run']});
 const page=await browser.newPage({viewport:{width:1600,height:1050},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8766',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>window.__campus?.loaded||window.__campus?.error,{},{timeout:60000});
 const campus=await page.evaluate(()=>window.__campus);if(!campus.loaded)throw new Error(JSON.stringify(campus));
 const dir='D:/entertain/njust-miniature/output/playwright';fs.mkdirSync(dir,{recursive:true});
 await page.screenshot({path:dir+'/viewer-overview.png'});
 const titles={};
 for(const name of ['architecture','garden','lake','plan','hero']){
  await page.locator(`[data-view="${name}"]`).click();await page.waitForTimeout(1550);
  titles[name]=await page.locator('#scene-title').innerText();
 }
 await page.locator('#rotate').click();if(!await page.locator('#rotate').evaluate(e=>e.classList.contains('active')))throw new Error('Auto rotate failed');
 await page.locator('#rotate').click();await page.locator('#gallery-open').click();
 if(!await page.locator('#gallery').evaluate(e=>e.classList.contains('open')))throw new Error('Gallery failed');
 await page.locator('#gallery-close').click();
 const status=await page.request.get('http://127.0.0.1:8766/NJUST_Violet_Spring.blend');
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:dir+'/viewer-mobile.png'});
 const report={campus,titles,errors,blendDownloadStatus:status.status(),checked:['GLB load','5 camera buttons','auto rotation toggle','gallery open/close','Blender download','mobile layout']};
 fs.writeFileSync(dir+'/verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 await browser.close();if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1);});
