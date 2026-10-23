const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file:///home/claude/test1/youtube/ai_reels/claude_code5/cta_card.html');await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:'/tmp/claude-0/-home-claude-test1/9982dce4-cc82-5946-af98-81d6e28d5021/scratchpad/cc5/raw/cta_card.png',omitBackground:true});await b.close();})();
