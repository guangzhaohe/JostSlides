// One prepared audio player continues across slides that share a soundtrack.
const soundtrackPool=new Map();
let activeSoundtrack=null;

async function prepareSoundtrack(entry){
 if(entry.ready||entry.loading)return;
 entry.loading=true;entry.error=false;
 try{
  if(location.protocol!=='file:'){
   let shared;
   try{shared=window.opener?.DeckSoundtrackPreloader?.asset(entry.source);}catch{}
   entry.blobPromise=shared||fetch(entry.source).then(response=>{
    if(!response.ok)throw new Error('Soundtrack download failed');
    return response.blob();
   });
   const blob=await entry.blobPromise;
   if(!blob.size)throw new Error('Soundtrack is empty');
   if(entry.objectURL)URL.revokeObjectURL(entry.objectURL);
   entry.objectURL=URL.createObjectURL(blob);
  }
  await new Promise((resolve,reject)=>{
   const audio=entry.audio;
   const finish=error=>{clearTimeout(timer);audio.removeEventListener('loadeddata',loaded);audio.removeEventListener('error',failed);error?reject(error):resolve();};
   const loaded=()=>finish();
   const failed=()=>finish(new Error('Soundtrack cannot be decoded'));
   const timer=setTimeout(()=>finish(new Error('Soundtrack preparation timed out')),30000);
   audio.addEventListener('loadeddata',loaded);audio.addEventListener('error',failed);
   audio.src=entry.objectURL||entry.source;audio.load();
  });
  entry.ready=true;
 }catch{entry.error=true;}
 finally{entry.loading=false;updatePresentationStartup();}
}

function initSoundtracks(){
 for(const spec of SLIDES){
  if(!spec.soundtrack)continue;
  const source=new URL(spec.soundtrack.src,location.href).href;
  if(soundtrackPool.has(source))continue;
  const audio=new Audio();audio.preload='auto';audio.loop=true;audio.muted=audience;
  audio.volume=spec.soundtrack.volume??0.08;
  soundtrackPool.set(source,{source,audio,ready:false,error:false,loading:false,blocked:false,blobPromise:null,objectURL:null});
 }
 window.DeckSoundtrackPreloader={asset:source=>soundtrackPool.get(source)?.blobPromise};
 for(const entry of soundtrackPool.values())prepareSoundtrack(entry);
 document.querySelector('#music-toggle').onclick=()=>{
  if(!activeSoundtrack)return;
  if(activeSoundtrack.blocked||activeSoundtrack.audio.paused){activeSoundtrack.audio.muted=false;playSoundtrack(activeSoundtrack);}
  else activeSoundtrack.audio.muted=!activeSoundtrack.audio.muted;
  renderSoundtrackControls();
 };
 document.querySelector('#music-volume').oninput=event=>{
  if(!activeSoundtrack)return;
  activeSoundtrack.audio.volume=Number(event.target.value)/100;
  renderSoundtrackControls();
 };
}

function retrySoundtracks(){for(const entry of soundtrackPool.values())if(entry.error)prepareSoundtrack(entry);}

function playSoundtrack(entry){
 if(audience||!entry.ready||activeSoundtrack!==entry)return;
 entry.audio.play().then(()=>{
  // Navigation can happen while the browser is granting playback.
  if(activeSoundtrack!==entry){entry.audio.pause();return;}
  entry.blocked=false;renderSoundtrackControls();
 }).catch(()=>{entry.blocked=true;renderSoundtrackControls();});
}

function renderSoundtrackControls(){
 const panel=document.querySelector('#music-controls');
 panel.hidden=!activeSoundtrack||audience;
 if(!activeSoundtrack)return;
 const {audio,blocked}=activeSoundtrack;
 document.querySelector('#music-toggle').textContent=blocked?'Enable music':audio.muted?'Unmute music':'Mute music';
 document.querySelector('#music-volume').value=Math.round(audio.volume*100);
 document.querySelector('#music-status').textContent=`Demo music, ${Math.round(audio.volume*100)}%`;
}

function updateSoundtrack(){
 if(!presentationReady)return;
 const spec=SLIDES[current].soundtrack;
 const entry=spec?soundtrackPool.get(new URL(spec.src,location.href).href):null;
 if(entry!==activeSoundtrack){
  if(activeSoundtrack){activeSoundtrack.audio.pause();activeSoundtrack.audio.currentTime=0;}
  activeSoundtrack=entry||null;
  if(entry&&!audience)playSoundtrack(entry);
 }
 renderSoundtrackControls();
}
