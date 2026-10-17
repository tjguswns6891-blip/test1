// v2.html 의 section.thumb 를 thumbnail_<id>.png (1280×720) 로 찍는다
const path=require('path');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});
await p.goto('file://'+path.join(__dirname,'v2.html'));await p.evaluate(()=>document.fonts.ready);
for(const id of await p.$$eval('section.thumb',e=>e.map(x=>x.id))){
  await p.locator('#'+id).screenshot({path:path.join(__dirname,`thumbnail_${id}.png`)});console.log(`thumbnail_${id}.png`)}
await b.close()})();
