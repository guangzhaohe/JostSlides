// No slide is rendered until fonts, every bundled image, video and soundtrack are ready.
const startupImages=new Map();
let startupFontsReady=false,startupFontsError=false;

function collectStartupImages(value){
 if(typeof value==='string'&&value.startsWith('data:image/'))startupImages.set(value,{image:new Image(),ready:false,error:false,loading:false});
 else if(Array.isArray(value))value.forEach(collectStartupImages);
 else if(value&&typeof value==='object')Object.values(value).forEach(collectStartupImages);
}

async function prepareStartupImage(source,entry){
 if(entry.ready||entry.loading)return;
 entry.loading=true;entry.error=false;
 try{entry.image.src=source;await entry.image.decode();entry.ready=true;}
 catch{entry.error=true;}
 finally{entry.loading=false;updatePresentationStartup();}
}

async function prepareStartupFonts(){
 if(startupFontsReady)return;
 startupFontsError=false;
 try{
  await Promise.all([...document.fonts].map(font=>font.load()));
  await document.fonts.ready;
  startupFontsReady=true;
 }catch{startupFontsError=true;}
 updatePresentationStartup();
}

function updatePresentationStartup(){
 if(presentationReady)return;
 const images=[...startupImages.values()],videos=[...videoPool.values()],sounds=[...soundtrackPool.values()];
 const ready=images.filter(e=>e.ready).length+videos.filter(e=>e.ready).length+sounds.filter(e=>e.ready).length+Number(startupFontsReady);
 const total=images.length+videos.length+sounds.length+1;
 const failed=startupFontsError||images.some(e=>e.error)||videos.some(e=>e.error)||sounds.some(e=>e.error);
 const screen=document.querySelector('#startup-screen');
 screen.dataset.state=failed?'error':'loading';
 document.querySelector('#startup-progress').max=total;
 document.querySelector('#startup-progress').value=ready;
 document.querySelector('#startup-detail').textContent=failed?'Some assets could not load. Retry to open the presentation.':`Preparing all slide assets, ${Math.floor(ready/total*100)}%`;
 document.querySelector('#startup-retry').hidden=!failed;
 if(!failed&&ready===total){
  presentationReady=true;
  if(pendingRemoteState){receivePresentationState(pendingRemoteState);pendingRemoteState=null;}else render();
  document.querySelector('.shell').inert=false;
  document.body.classList.remove('loading');
  screen.hidden=true;
  resize();
  if(audience)window.opener?.postMessage({type:'asp:ready'},'*');else sync();
 }
}

function startPresentation(){
 collectStartupImages(SLIDES);collectStartupImages(EVIDENCE);
 document.querySelector('#startup-retry').onclick=()=>{
  retryVideoPreloads();retrySoundtracks();prepareStartupFonts();
  for(const [source,entry] of startupImages)if(entry.error)prepareStartupImage(source,entry);
  updatePresentationStartup();
 };
 initSoundtracks();initVideoPreload();
 prepareStartupFonts();
 for(const [source,entry] of startupImages)prepareStartupImage(source,entry);
 updatePresentationStartup();
}
