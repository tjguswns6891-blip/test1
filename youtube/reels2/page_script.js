<script>
(function(){
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const store={get(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
  function showTab(t){
    $$('.tabs button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.tab===t)));
    $$('section.part').forEach(s=>s.hidden=s.id!=='part-'+t);
    store.set('tab2',t);
  }
  $$('.tabs button').forEach(b=>b.addEventListener('click',()=>showTab(b.dataset.tab)));
  function setPrompter(on){document.body.classList.toggle('prompter',on);$('#prompter').setAttribute('aria-pressed',String(on));store.set('prompter',on)}
  $('#prompter').addEventListener('click',()=>setPrompter(!document.body.classList.contains('prompter')));
  let scale=store.get('scale',1);
  function applyScale(){document.querySelectorAll('.script').forEach(el=>el.style.fontSize=`calc(var(--fs) * ${scale})`);store.set('scale',scale)}
  $('#bigger').addEventListener('click',()=>{scale=Math.min(1.8,+(scale+0.1).toFixed(2));applyScale()});
  $('#smaller').addEventListener('click',()=>{scale=Math.max(0.7,+(scale-0.1).toFixed(2));applyScale()});
  const done=new Set(store.get('done',[]));
  $$('.scene').forEach(sc=>{
    const b=sc.querySelector('.done');
    const paint=()=>{const on=done.has(sc.id);sc.classList.toggle('is-done',on);b.setAttribute('aria-pressed',String(on))};
    b.addEventListener('click',()=>{done.has(sc.id)?done.delete(sc.id):done.add(sc.id);store.set('done',[...done]);paint()});
    paint();
  });
  showTab(['linalg','circuit','edit'].includes(store.get('tab2','linalg'))?store.get('tab2','linalg'):'linalg');
  setPrompter(store.get('prompter',false));
  applyScale();
  try{navigator.wakeLock&&navigator.wakeLock.request('screen').catch(()=>{})}catch(e){}
})();
</script>
