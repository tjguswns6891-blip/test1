// banner.html → banner.png (2560×1440) + 안전 영역 표시한 미리보기
const path=require('path');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:2560,height:1440}});
await p.goto('file://'+path.join(__dirname,'banner.html'));await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:path.join(__dirname,'banner.png')});await b.close();console.log('banner.png')})();
