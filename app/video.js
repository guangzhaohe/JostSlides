// Download complete videos on opening, then keep their players ready for slide entry.
const videoPool=new Map();
let videoParking=null;

function updateVideoPreloadStatus(){
 const panel=document.querySelector('#video-preload');
 if(!panel)return;
 const entries=[...videoPool.values()],ready=entries.filter(e=>e.ready).length,failed=entries.some(e=>e.error);
 panel.hidden=!entries.length;
 panel.dataset.state=failed?'error':ready===entries.length?'ready':'loading';
 document.querySelector('#video-preload-text').textContent=failed?'A video could not be prepared':ready===entries.length?'Videos ready':`Preparing videos ${ready} / ${entries.length}`;
 document.querySelector('#video-preload-retry').hidden=!failed;
 if(entries.length&&ready===entries.length&&!audience&&audienceWindow&&!audienceWindow.closed)audienceWindow.postMessage({type:'asp:video-cache-ready'},'*');
 updatePresentationStartup();
}

function readVideoBlob(entry){
 // The audience window shares the presenter's completed download, including when
 // it opens after network access disappears. Each window owns its own object URL.
 try{
  const shared=window.opener?.DeckVideoPreloader?.asset(entry.source);
  if(shared)return shared;
 }catch{}
 return fetch(entry.source).then(async response=>{
  if(!response.ok)throw new Error(`Video download failed: ${response.status}`);
  const blob=await response.blob();
  if(!blob.size)throw new Error('Video download was empty');
  return blob;
 });
}

async function prepareVideo(entry){
 if(entry.preparing||entry.ready)return;
 entry.preparing=true;entry.error=false;updateVideoPreloadStatus();
 try{
  const local=location.protocol==='file:';
  if(!local){
   entry.blobPromise=readVideoBlob(entry);
   const blob=await entry.blobPromise;
   if(entry.objectURL)URL.revokeObjectURL(entry.objectURL);
   entry.objectURL=URL.createObjectURL(blob);
  }
  const video=entry.video;
  await new Promise((resolve,reject)=>{
   const finish=(error)=>{clearTimeout(timer);video.removeEventListener('loadeddata',loaded);video.removeEventListener('error',failed);error?reject(error):resolve();};
   const loaded=()=>finish();
   const failed=()=>finish(new Error('Video cannot be decoded'));
   const timer=setTimeout(()=>finish(new Error('Video preparation timed out')),30000);
   video.addEventListener('loadeddata',loaded);video.addEventListener('error',failed);
   video.src=entry.objectURL||entry.source;video.load();
  });
  entry.ready=true;
  if(document.querySelector('#slide video')===video){
   if(audience){if(video.remoteState)applyVideoState(video.remoteState);}
   else video.play().catch(()=>{});
  }
 }catch(error){entry.error=true;}
 finally{entry.preparing=false;updateVideoPreloadStatus();}
}

function initVideoPreload(){
 const specs=SLIDES.filter(s=>s.video);
 if(!specs.length)return;
 videoParking=document.createElement('div');videoParking.className='video-parking';videoParking.setAttribute('aria-hidden','true');document.body.append(videoParking);
 for(const spec of specs){
  const source=new URL(spec.video.src,location.href).href;
  if(videoPool.has(source))continue;
  const video=document.createElement('video');
  video.className='slide-video';video.poster=spec.video.poster;video.dataset.source=source;
  video.playsInline=true;video.muted=true;video.defaultMuted=true;video.preload='auto';
  for(const event of ['play','pause','seeked','ratechange','ended'])video.addEventListener(event,()=>{
   if(!audience&&document.querySelector('#slide video')===video)sync();
  });
  video.addEventListener('ended',()=>{
   if(audience||!presentationReady||document.querySelector('#slide video')!==video)return;
   const next=SLIDES[current].video?.next;
   if(next){const index=SLIDES.findIndex(s=>s.id===next);if(index>=0)go(index);}
  });
  video.addEventListener('loadedmetadata',()=>{if(video.remoteState)applyVideoState(video.remoteState);});
  videoParking.append(video);
  videoPool.set(source,{source,video,ready:false,error:false,preparing:false,blobPromise:null,objectURL:null});
 }
 window.DeckVideoPreloader={asset:source=>videoPool.get(source)?.blobPromise};
 document.querySelector('#video-preload-retry').onclick=retryVideoPreloads;
 for(const entry of videoPool.values())prepareVideo(entry);
}

function retryVideoPreloads(){for(const entry of videoPool.values())if(entry.error)prepareVideo(entry);}

function releaseVideo(video){
 video.pause();video.remoteState=null;
 if(video.readyState)video.currentTime=0;
 videoParking?.append(video);
}

// Full-slide playback is controlled by the presenter and mirrored to the audience.
function renderVideo(el,spec,mini){
 const media=spec.video;
 const bounds=media.bounds||[0,0,1152,648];
 if(mini){const poster=document.createElement('img');poster.src=media.poster;poster.alt=spec.name;poster.className='slide-video';geometry(poster,...bounds);poster.style.opacity=1-(media.dim||0);media.background?el.prepend(poster):el.append(poster);return;}
 const entry=videoPool.get(new URL(media.src,location.href).href),video=entry.video;
 video.setAttribute('aria-label',spec.name);video.controls=!audience;
 video.loop=Boolean(media.loop);video.style.opacity=1-(media.dim||0);
 geometry(video,...bounds);video.muted=audience||media.muted!==false;
 el.dataset.videoSlide=spec.id;media.background?el.prepend(video):el.append(video);
 if(!audience&&entry.ready&&media.autoplay!==false)video.play().catch(()=>{});
}
function captureVideoState(){
 const video=document.querySelector('#slide video');
 return video?{slideId:SLIDES[current].id,time:video.currentTime,paused:video.paused,rate:video.playbackRate,at:Date.now()}:null;
}
function applyVideoState(state){
 const video=document.querySelector('#slide video');
 if(!video||!state||state.slideId!==SLIDES[current].id||!Number.isFinite(state.time)||!Number.isFinite(state.at))return;
 video.remoteState=state;
 if(!video.readyState)return;
 const rate=Number.isFinite(state.rate)&&state.rate>0?state.rate:1;
 const target=Math.max(0,Math.min(video.duration||Infinity,state.time+(state.paused?0:Math.max(0,Date.now()-state.at)/1000*rate)));
 if(Math.abs(video.currentTime-target)>.3)video.currentTime=target;
 video.playbackRate=rate;
 if(state.paused)video.pause();else video.play().catch(()=>{});
}
