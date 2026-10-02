const TITLES = SLIDES.map(s=>s.name);
const LAST=SLIDES.length-1;
const KEY=META.id;
const audience=new URLSearchParams(location.search).has('audience');
document.body.classList.toggle('audience',audience);
const $=s=>document.querySelector(s);
function setupDeckPicker(){
 if(location.protocol==='file:'||!Array.isArray(DECKS)||DECKS.length<2)return;
 for(const menu of [$('#header-deck-menu'),$('#startup-deck-menu')]){
  if(!menu)continue;
  const options=menu.querySelector('.deck-options');
  for(const deck of DECKS){
   const button=document.createElement('button');button.type='button';button.className='deck-option';button.dataset.current=String(deck.name===META.date);
   const date=document.createElement('span');date.className='deck-option-date';date.textContent=deck.date_label;
   const title=document.createElement('span');title.className='deck-option-title';title.textContent=deck.title;
   button.append(date,title);button.onclick=()=>{menu.open=false;if(deck.name!==META.date)location.href=deck.url;};options.append(button);
  }
  menu.hidden=false;
 }
 $('.date').hidden=true;
 document.addEventListener('click',event=>{for(const menu of document.querySelectorAll('.deck-menu[open]'))if(!menu.contains(event.target))menu.open=false;});
}
setupDeckPicker();
let current=Math.max(0,Math.min(LAST,Number(location.hash.slice(1))-1||0));
let notes={},focuses={},audienceWindow=null,toastTimer;
let storageOK=true;
let presentationReady=false,pendingRemoteState=null;
let motionState=null,lastMotionToken=null,motionCounter=0;
let buildStep=0,buildMotion=null,lastBuildToken=null,buildTimer=null,buildPlaying=false,buildDetail=false;
try{notes=JSON.parse(localStorage.getItem(KEY+'-notes')||'{}');if(!notes||typeof notes!=='object'||Array.isArray(notes))notes={};const legacy=META.legacy_slide_ids||[];legacy.forEach((id,i)=>{if(typeof notes[i]==='string'&&notes[id]===undefined)notes[id]=notes[i];delete notes[i];});}catch{storageOK=false;}
function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,4500);}
function geometry(el,x,y,w,h){Object.assign(el.style,{left:x+'px',top:y+'px',width:w+'px',height:h+'px'});}
function renderCoverParticles(el,mini){
 const canvas=document.createElement('canvas');
 canvas.className='cover-particles';canvas.width=1152;canvas.height=648;
 canvas.setAttribute('aria-hidden','true');el.append(canvas);
 if(mini)return;
 const ctx=canvas.getContext('2d');
 const particles=Array.from({length:230},(_,i)=>{
  // Stable positions make the first frame and audience window look alike.
  const random=n=>{const x=Math.sin((i+1)*n*78.233)*43758.5453;return x-Math.floor(x);};
  return {x:340+random(1.1)*880,y:20+random(2.3)*640,r:1+random(3.7)*1.9,
   phase:random(4.1)*Math.PI*2,depth:.35+random(5.3)*.65,purple:random(6.1)>.52};
 });
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 let last=0;
 function paint(ms){
  if(!canvas.isConnected)return;
  if(ms-last<32&&!reduced){requestAnimationFrame(paint);return;}
  last=ms;const t=reduced?0:ms*.00095;
  ctx.clearRect(0,0,1152,648);
  const positions=particles.map(p=>[p.x+Math.sin(t+p.phase)*38*p.depth,
   p.y+Math.cos(t*.81+p.phase)*25*p.depth]);
  for(let i=0;i<particles.length;i++){
   const p=particles[i],[x,y]=positions[i];
   for(let j=i+1;j<particles.length;j++){
    const [xx,yy]=positions[j],distance=Math.hypot(x-xx,y-yy);
    if(distance>83||distance<22)continue;
    ctx.strokeStyle=p.purple
     ?`rgba(164,119,220,${(1-distance/83)*.17*p.depth})`
     :`rgba(96,161,232,${(1-distance/83)*.17*p.depth})`;
    ctx.lineWidth=.7;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(xx,yy);ctx.stroke();
   }
   ctx.fillStyle=p.purple
    ?`rgba(186,149,242,${.68*p.depth})`
    :`rgba(135,193,255,${.72*p.depth})`;
   ctx.beginPath();ctx.arc(x,y,p.r,0,Math.PI*2);ctx.fill();
  }
  if(!reduced)requestAnimationFrame(paint);
 }
 requestAnimationFrame(paint);
}
function renderInto(el,index,mini=false){
 if(!mini)closeChoiceMenu();
 const original=SLIDES[index];
 const detail=!mini&&buildDetail&&original.builds?.[buildStep]?.detail;
 const spec=detail||original;
 el.classList.toggle('pipeline-detail',Boolean(detail));
 if(!mini&&spec.video&&el.dataset.videoSlide===spec.id&&el.querySelector('video'))return;
 const oldVideo=el.querySelector('video');
 el.replaceChildren();delete el.dataset.videoSlide;
 if(oldVideo)releaseVideo(oldVideo);
 el.style.background='#'+spec.bg;
 if(spec.cover_particles)renderCoverParticles(el,mini);
 function revealElement(e,kind,i){const step=(spec.builds||[]).findIndex(group=>(group[kind]||[]).includes(i));if(step>=0){e.dataset.build=step;if(!mini)e.hidden=step>buildStep;}}
 (spec.rects||[]).forEach(([x,y,w,h,color],i)=>{const e=document.createElement('div');e.className='shape';geometry(e,x,y,w,h);e.style.background='#'+color;revealElement(e,'rects',i);el.append(e);});
 for(const picture of spec.images||[]){
  const e=document.createElement('img');e.src=picture.src;e.alt=picture.alt||'';
  e.style.objectFit=picture.fit||'contain';e.style.objectPosition=picture.position||'center';
  if(picture.zoom){
   const frame=document.createElement('div');frame.style.position='absolute';frame.style.overflow='hidden';geometry(frame,...picture.bounds);
   Object.assign(e.style,{width:'100%',height:'100%',transform:`scale(${picture.zoom})`,transformOrigin:picture.position||'center'});
   frame.append(e);el.append(frame);
  }else{e.style.position='absolute';geometry(e,...picture.bounds);el.append(e);}
 }
 if(spec.vectors){
  const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');
  svg.setAttribute('viewBox','0 0 1152 648');svg.setAttribute('aria-hidden','true');svg.classList.add('pipeline-vectors');
  for(const [tag,attributes] of spec.vectors){const shape=document.createElementNS(ns,tag);for(const [key,value] of Object.entries(attributes))shape.setAttribute(key,value);svg.append(shape);}
  el.append(svg);
 }
 spec.text.forEach(([x,y,w,h,content,size,bold,color],i)=>{
  const interactive=content.includes('?')&&!mini;
  const e=document.createElement(interactive?'button':'div');e.className='slide-text'+(interactive?' prompt':'');geometry(e,x,y,w,h);e.textContent=content;Object.assign(e.style,{fontSize:size+'px',fontWeight:bold?'700':'400',color:'#'+color});
  if(interactive){e.title='Highlight this question';e.setAttribute('aria-pressed',focuses[index]===i?'true':'false');e.classList.toggle('focused',focuses[index]===i);e.onclick=()=>{focuses[index]=focuses[index]===i?null:i;render();sync();};}
  revealElement(e,'text',i);el.append(e);
 });
 if(!mini)for(const [i,group] of (spec.builds||[]).entries()){
  const button=document.createElement('button');button.className='build-target';button.dataset.buildTarget=i;
  button.setAttribute('aria-label',`Show step ${i+1}: ${group.label}`);button.setAttribute('aria-pressed',String(i===buildStep));
  geometry(button,...group.bounds);button.onclick=()=>{buildDetail=Boolean(group.detail);showBuild(i);};el.append(button);
 }
 if(spec.widget)renderEvidence(el,spec.widget,mini);
 if(spec.scene)renderScene(el,spec,mini);
 if(spec.video)renderVideo(el,spec,mini);
}
function render(){if(!presentationReady)return;renderInto($('#slide'),current);$('#counter').textContent=`${current+1} / ${SLIDES.length}`;$('#note-number').textContent=String(current+1).padStart(2,'0');$('#slide-name').textContent=TITLES[current];$('#notes-input').value=typeof notes[SLIDES[current].id]==='string'?notes[SLIDES[current].id]:'';$('#speaker-prompts').textContent=SLIDES[current].notes;$('#prev').disabled=current===0&&buildStep===0;$('#next').disabled=current===LAST&&buildStep>=buildCount()-1;$('#progress').style.width=((current+1)/SLIDES.length*100)+'%';$('#announcement').textContent=`Slide ${current+1}: ${TITLES[current]}`;renderBuildControls();updateSoundtrack();resize();}
function buildCount(){return SLIDES[current].builds?.length||0;}
function stopBuildPlayback(){clearTimeout(buildTimer);buildTimer=null;buildPlaying=false;}
function renderBuildControls(){
 const count=buildCount();$('#build-controls').hidden=!count||audience;
 $('#build-status').textContent=count?`Step ${buildStep+1} of ${count}: ${SLIDES[current].builds[buildStep].label}`:'';
 $('#build-play').textContent=buildPlaying?'Pause steps':'Play steps';
 $('#build-play').setAttribute('aria-pressed',String(buildPlaying));
 $('#build-explore').hidden=!SLIDES[current].builds?.[buildStep]?.detail;
 $('#build-explore').textContent=buildDetail?'Pipeline overview':'Explore step';
}
function playBuildMotion(){
 if(!window.DeckMotion||!buildMotion||buildMotion.token===lastBuildToken)return;
 if(buildMotion.slide!==current||buildMotion.step!==buildStep||!Number.isFinite(buildMotion.startedAt))return;
 lastBuildToken=buildMotion.token;
 if(buildDetail){window.DeckMotion.cancel();return;}
 window.DeckMotion.reveal({spec:SLIDES[current],step:buildStep,startedAt:buildMotion.startedAt});
}
function markBuildMotion(){buildMotion={slide:current,step:buildStep,startedAt:Date.now(),token:Date.now()+'-'+(++motionCounter)};}
function showBuild(step,playing=false){
 if(!presentationReady||!buildCount())return;
 stopBuildPlayback();buildPlaying=playing;
 buildStep=Math.max(0,Math.min(buildCount()-1,step));
 motionState=null;markBuildMotion();render();playMotion();playBuildMotion();sync();
}
function advance(direction){
 if(!presentationReady)return;
 const next=buildStep+direction;
 if(buildCount()&&next>=0&&next<buildCount()){showBuild(next);return;}
 stopBuildPlayback();go(current+direction);renderBuildControls();sync();
}
function scheduleBuildPlayback(){
 buildTimer=setTimeout(()=>{
  if(!buildPlaying||!presentationReady)return;
  if(buildStep>=buildCount()-1){stopBuildPlayback();renderBuildControls();sync();return;}
  showBuild(buildStep+1,true);scheduleBuildPlayback();
 },2400);
}
function toggleBuildPlayback(){
 if(!presentationReady||!buildCount())return;
 if(buildPlaying){stopBuildPlayback();renderBuildControls();sync();return;}
 showBuild(buildStep>=buildCount()-1?0:buildStep,true);scheduleBuildPlayback();
}
$('#build-play').onclick=toggleBuildPlayback;
$('#build-replay').onclick=()=>{buildDetail=false;showBuild(0);};
$('#build-explore').onclick=()=>{buildDetail=!buildDetail;showBuild(buildStep);};
document.addEventListener('keydown',e=>{if(presentationReady&&e.key==='Escape'&&buildDetail&&!document.querySelector('dialog[open]')){buildDetail=false;showBuild(buildStep);e.preventDefault();}});
$('#slide').addEventListener('click',e=>{if(buildCount()&&!e.target.closest('button'))advance(1);});
function resize(){const area=$('.stage'),space=audience?0:(innerWidth<=700?20:innerWidth<=950?28:48);const w=Math.max(1,area.clientWidth-space),h=Math.max(1,area.clientHeight-space);const scale=Math.min(w/1152,h/648);$('.slide-frame').style.width=1152*scale+'px';$('.slide-frame').style.height=648*scale+'px';$('#slide').style.transform=`scale(${scale})`;}
function playMotion(){
 if(!window.DeckMotion)return;
 if(!motionState){window.DeckMotion.cancel();lastMotionToken=null;return;}
 if(motionState.token===lastMotionToken)return;
 lastMotionToken=motionState.token;
 const {from,to,startedAt}=motionState;
 if(!Number.isInteger(from)||!Number.isInteger(to)||!SLIDES[from]||!SLIDES[to]||to!==current||!Number.isFinite(startedAt))return;
 window.DeckMotion.play({from:SLIDES[from],to:SLIDES[to],direction:to>from?1:-1,startedAt});
}
function go(index){
 if(!presentationReady)return;
 const previous=current;
 current=Math.max(0,Math.min(LAST,index));
 if(current!==previous){
  buildDetail=false;
  stopBuildPlayback();buildStep=current<previous?Math.max(0,buildCount()-1):0;
  buildMotion=null;lastBuildToken=null;
  if(buildCount())markBuildMotion();
 }
 if(current!==previous&&window.DeckMotion)motionState={from:previous,to:current,startedAt:Date.now(),token:Date.now()+'-'+(++motionCounter)};
 try{history.replaceState(null,'','#'+(current+1));}catch{}
 render();playMotion();playBuildMotion();sync();
}
function sync(){if(!presentationReady)return;const message={type:'asp:state',current,focuses,widgetState,motionState,buildStep,buildMotion,buildPlaying,buildDetail,videoState:audience?null:captureVideoState()};if(audience){window.opener?.postMessage(message,'*');}else if(audienceWindow&&!audienceWindow.closed){audienceWindow.postMessage(message,'*');}}
function receivePresentationState(msg){stopBuildPlayback();current=msg.current;buildStep=Number.isInteger(msg.buildStep)?Math.max(0,Math.min(Math.max(0,buildCount()-1),msg.buildStep)):0;buildMotion=msg.buildMotion||null;buildPlaying=Boolean(msg.buildPlaying);buildDetail=Boolean(msg.buildDetail&&SLIDES[current].builds?.[buildStep]?.detail);focuses=msg.focuses||{};if(msg.widgetState)widgetState=msg.widgetState;motionState=msg.motionState||null;render();playMotion();playBuildMotion();if(audience)applyVideoState(msg.videoState);else{if(buildPlaying)scheduleBuildPlayback();sync();}}
window.addEventListener('message',e=>{if(audience?e.source!==window.opener:e.source!==audienceWindow)return;const msg=e.data;if(!msg||typeof msg!=='object')return;if(msg.type==='asp:video-cache-ready'&&audience){retryVideoPreloads();return;}if(msg.type==='asp:ready'&&!audience){sync();return;}if(msg.type==='asp:state'&&Number.isInteger(msg.current)&&msg.current>=0&&msg.current<SLIDES.length){if(!presentationReady){pendingRemoteState=msg;return;}receivePresentationState(msg);}});
function saveNotes(){notes[SLIDES[current].id]=$('#notes-input').value;try{localStorage.setItem(KEY+'-notes',JSON.stringify(notes));storageOK=true;$('#save-state').textContent='Saved in this browser';}catch{storageOK=false;$('#save-state').textContent='Browser storage unavailable — export to save';}}
$('#notes-input').addEventListener('input',saveNotes);
function toggleNotes(){if(audience)return;$('.notes').hidden=!$('.notes').hidden;$('#notes-toggle').setAttribute('aria-pressed',!$('.notes').hidden);resize();}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch{toast('Fullscreen is unavailable here. Open index.html in a browser tab.');}}
$('#fullscreen').onclick=fullscreen;$('#audience-fullscreen').onclick=fullscreen;document.addEventListener('fullscreenchange',()=>{$('#fullscreen').textContent=document.fullscreenElement?'Exit fullscreen':'Fullscreen';resize();});
$('#notes-toggle').onclick=toggleNotes;$('#prev').onclick=()=>advance(-1);$('#next').onclick=()=>advance(1);
$('#audience-open').onclick=()=>{audienceWindow=window.open(location.pathname+'?audience=1#'+(current+1),'asp-audience','popup,width=1280,height=800');if(!audienceWindow)toast('Allow pop-ups to open the audience window.');else toast('Move the audience window to your presentation screen.');};
function overview(){if(audience)return;const grid=$('#overview-grid');grid.replaceChildren();SLIDES.forEach((s,i)=>{const button=document.createElement('button');button.className='thumb';button.setAttribute('aria-current',String(i===current));const frame=document.createElement('div');frame.className='mini-frame';const slide=document.createElement('div');slide.className='slide';renderInto(slide,i,true);frame.append(slide);const label=document.createElement('span');label.className='thumb-label';label.textContent=`${String(i+1).padStart(2,'0')}  ${TITLES[i]}`;button.append(frame,label);button.onclick=()=>{$('#overview-dialog').close();go(i);};grid.append(button);});$('#overview-dialog').showModal();requestAnimationFrame(()=>document.querySelectorAll('.mini-frame').forEach(el=>el.firstChild.style.transform=`scale(${el.clientWidth/1152})`));}
$('#sources').onclick=showSources;$('#overview').onclick=overview;$('#help').onclick=()=>$('#help-dialog').showModal();document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>document.getElementById(b.dataset.close).close());
$('#export-notes').onclick=()=>{let content=`# ${META.title} — ${META.date_label}\n\n`;TITLES.forEach((title,i)=>content+=`## ${i+1}. ${title}\n\n${notes[SLIDES[i].id]||'No notes yet.'}\n\n`);for(const [id,note] of Object.entries(notes)){if(typeof note==='string'&&note&&!SLIDES.some(s=>s.id===id))content+=`## Archived slide: ${id}\n\n${note}\n\n`;}const url=URL.createObjectURL(new Blob([content],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=META.export_stem+'-notes.md';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
document.addEventListener('keydown',e=>{if(!presentationReady)return;if(e.target.closest('textarea,input,select,[contenteditable=true]')||document.querySelector('dialog[open]')||e.ctrlKey||e.metaKey||e.altKey)return;const k=e.key.toLowerCase();if(['arrowright','arrowdown','pagedown',' ','arrowleft','arrowup','pageup','home','end','f','n','g','?'].includes(k)||/^[1-9]$/.test(k))e.preventDefault();if(['arrowright','arrowdown','pagedown',' '].includes(k))advance(1);if(['arrowleft','arrowup','pageup'].includes(k))advance(-1);if(k==='home')go(0);if(k==='end')go(LAST);if(k==='f')fullscreen();if(k==='n')toggleNotes();if(k==='g')overview();if(k==='?'&&!audience)$('#help-dialog').showModal();if(/^[1-9]$/.test(k))go(Number(k)-1);});
new ResizeObserver(resize).observe($('.stage'));window.addEventListener('resize',resize);window.addEventListener('hashchange',()=>go(Number(location.hash.slice(1))-1||0));
startPresentation();if(!storageOK)$('#save-state').textContent='Browser storage unavailable — export to save';if(audience){window.opener?.postMessage({type:'asp:ready'},'*');}

setInterval(()=>{const video=$('#slide video');if(!audience&&audienceWindow&&!audienceWindow.closed&&video&&!video.paused)sync();},1000);
