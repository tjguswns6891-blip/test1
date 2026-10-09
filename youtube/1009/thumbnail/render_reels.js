// reels.html 의 section.r 을 reel_<id>.png (1080×1920) 로 찍는다
const path=require('path');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(__dirname,'reels.html'));await p.evaluate(()=>document.fonts.ready);
for(const id of await p.$$eval('section.r',e=>e.map(x=>x.id))){await p.locator('#'+id).screenshot({path:path.join(__dirname,`reel_${id}.png`)});console.log(`reel_${id}.png`)}
await b.close()})();
