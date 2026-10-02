// Self-contained scientific scenes. Data arrive embedded in the deck; no loaders.
function renderScene(el,spec,mini=false){
 if(spec.scene.kind==='correction')return renderCorrectionScene(el,spec,mini);
 if(spec.scene.kind==='pair')return renderPairScene(el,spec,mini);
 if(spec.scene.kind==='steps')return renderStepsScene(el,spec,mini);
 const scene=spec.scene,host=document.createElement('div');host.className='scene-view';
 const bounds=scene.bounds||[48,168,1056,400];geometry(host,...bounds);host.style.position='absolute';
 const canvas=document.createElement('canvas');canvas.width=bounds[2]*2;canvas.height=(bounds[3]-54)*2;
 canvas.setAttribute('aria-label',scene.kind==='cloud'?'Interactive colored point cloud':scene.kind==='normalized-shift'?'Interactive scale and shift equivalence under pinhole projection':'Two scaled scenes with an identical pinhole projection');
 canvas.style.width=bounds[2]+'px';canvas.style.height=(bounds[3]-54)+'px';host.append(canvas);el.append(host);
 const ctx=canvas.getContext('2d');ctx.scale(2,2);const W=bounds[2],H=bounds[3]-54;
 host.addEventListener('click',e=>e.stopPropagation());
 const key=spec.id+'-scene';widgetState.scenes??={};
 const defaults={yaw:scene.initial_yaw??-.18,pitch:scene.initial_pitch??.05,scale:2,shift:2,aligned:false};
 let state=widgetState.scenes[key]||{...defaults};
 const controls=document.createElement('div');controls.className='scene-controls';host.append(controls);
 function save(){widgetState.scenes[key]={...state};if(!mini)sync();}
 function textAt(s,x,y,color='#f5f5f5',size=30){ctx.fillStyle=color;ctx.font=`${size}px Deck, sans-serif`;ctx.fillText(s,x,y);}
 function line(a,b,color='#b8e3d1',width=2){ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
 if(scene.kind==='cloud'){
  const points=scene.points,colors=scene.colors,comparison=Boolean(scene.prediction_points);
  const reference=comparison?points.concat(scene.prediction_points):points;
  const center=[0,0,0];for(const p of reference)for(let k=0;k<3;k++)center[k]+=p[k]/reference.length;
  const radius=Math.max(...reference.map(p=>Math.hypot(...p.map((v,k)=>v-center[k]))));
  let rawButton,alignedButton;
  function paint(){
   ctx.fillStyle='#080c10';ctx.fillRect(0,0,W,H);
   const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
   const shown=comparison?points.concat(scene.prediction_points.map(p=>p.map(v=>v*(state.aligned?scene.alignment_scale:1)))):points;
  function project(p,i){let [x,y,z]=p.map((v,k)=>(v-center[k])/radius);const xx=x*cy-z*sy,zz=x*sy+z*cy,yy=y*cp-zz*sp,z2=y*sp+zz*cp;const f=H*1.8/(3+z2);return [W/2+xx*f,H/2-yy*f,z2,i];}
   const projected=shown.map(project).sort((a,b)=>b[2]-a[2]);
   // Use the same framing in raw and aligned modes; only prediction scale changes.
   const frame=reference.map(project),xs=frame.map(p=>p[0]),ys=frame.map(p=>p[1]);
   const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
   const fit=Math.min((W-100)/Math.max(1,xmax-xmin),(H-30)/Math.max(1,ymax-ymin));
   ctx.globalAlpha=comparison?.62:1;
   for(const [x,y,z,i] of projected){const c=i<points.length?colors[i]:[236,147,215];ctx.fillStyle=`rgb(${c[0]},${c[1]},${c[2]})`;ctx.fillRect(W/2+(x-(xmin+xmax)/2)*fit,H/2+(y-(ymin+ymax)/2)*fit,comparison?2:3,comparison?2:3);}
   ctx.globalAlpha=1;
   if(comparison){host.dataset.aligned=String(Boolean(state.aligned));rawButton?.setAttribute('aria-pressed',String(!state.aligned));alignedButton?.setAttribute('aria-pressed',String(Boolean(state.aligned)));}
  }
  if(comparison){
   rawButton=document.createElement('button');rawButton.textContent='Raw scale';rawButton.onclick=()=>{state.aligned=false;paint();save();};
   alignedButton=document.createElement('button');alignedButton.textContent='Aligned scale';alignedButton.onclick=()=>{state.aligned=true;paint();save();};
   controls.append(rawButton,alignedButton);
  }else{
   const reset=document.createElement('button');reset.textContent='Reset view';reset.onclick=()=>{state={...defaults};paint();save();};controls.append(reset);
   const hint=document.createElement('span');hint.textContent='Drag to inspect';controls.append(hint);
  }
  let last=null,lastSync=0;canvas.onpointerdown=e=>{if(mini)return;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);e.stopPropagation();};
  canvas.onpointermove=e=>{if(!last)return;state.yaw+=(e.clientX-last[0])*.008;state.pitch=Math.max(-1,Math.min(1,state.pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];paint();if(performance.now()-lastSync>33){save();lastSync=performance.now();}};
  canvas.onpointerup=e=>{last=null;save();};canvas.onpointercancel=()=>{last=null;};paint();
 }else if(scene.kind==='normalized-shift'){
  host.classList.add('normalized-shift-scene');
  const scaleLabel=document.createElement('label'),scaleRange=document.createElement('input'),scaleOutput=document.createElement('output');
  scaleLabel.append('Scale',scaleRange,scaleOutput);scaleRange.type='range';scaleRange.min='.5';scaleRange.max='2.5';scaleRange.step='.1';scaleRange.value=state.scale;scaleRange.setAttribute('aria-label','Affine point-map scale');
  const shiftLabel=document.createElement('label'),shiftRange=document.createElement('input'),shiftOutput=document.createElement('output');
  shiftLabel.append('Shift',shiftRange,shiftOutput);shiftRange.type='range';shiftRange.min='0';shiftRange.max='4';shiftRange.step='.1';shiftRange.value=state.shift;shiftRange.setAttribute('aria-label','Affine point-map depth shift');
  controls.append(scaleLabel,shiftLabel);
  function paint(){
   ctx.fillStyle='#080c10';ctx.fillRect(0,0,W,H);
   const camera=[72,H/2+10],baseDepth=4,baseHalf=1.05;
   // Fit the full slider range while reserving space for the caption.
   const worldPx=Math.min(60,(H-170)/(2*2.5*baseHalf),(W-160)/14);
   const scaledDepth=state.scale*baseDepth+state.shift,scaledHalf=state.scale*baseHalf;
   const normalizedShift=state.shift/state.scale,shiftOnlyDepth=baseDepth+normalizedShift,shiftOnlyHalf=baseHalf;
   const sx=camera[0]+scaledDepth*worldPx,nx=camera[0]+shiftOnlyDepth*worldPx;
   const scaledTop=[sx,camera[1]-scaledHalf*worldPx],scaledBottom=[sx,camera[1]+scaledHalf*worldPx];
   const normalTop=[nx,camera[1]-shiftOnlyHalf*worldPx],normalBottom=[nx,camera[1]+shiftOnlyHalf*worldPx];
   const farTop=sx>nx?scaledTop:normalTop,farBottom=sx>nx?scaledBottom:normalBottom;
   const planeX=150,rayRatio=scaledHalf/scaledDepth,projectedHalf=(planeX-camera[0])*rayRatio;
   line(camera,farTop,'#526078',3);line(camera,farBottom,'#526078',3);
   line([planeX,camera[1]-105],[planeX,camera[1]+105],'#EBCB8B',5);
   ctx.fillStyle='#EBCB8B';ctx.beginPath();ctx.arc(planeX,camera[1]-projectedHalf,8,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(planeX,camera[1]+projectedHalf,8,0,Math.PI*2);ctx.fill();
   ctx.fillStyle='#EBCB8B';ctx.beginPath();ctx.arc(...camera,11,0,Math.PI*2);ctx.fill();
   ctx.beginPath();ctx.moveTo(camera[0]-30,camera[1]-20);ctx.lineTo(camera[0]-30,camera[1]+20);ctx.lineTo(camera[0],camera[1]);ctx.closePath();ctx.fill();
   line(scaledTop,scaledBottom,'#EC93D7',10);line(normalTop,normalBottom,'#b8e3d1',7);
   for(const p of [scaledTop,scaledBottom]){ctx.fillStyle='#EC93D7';ctx.beginPath();ctx.arc(...p,9,0,Math.PI*2);ctx.fill();}
   for(const p of [normalTop,normalBottom]){ctx.fillStyle='#b8e3d1';ctx.beginPath();ctx.arc(...p,8,0,Math.PI*2);ctx.fill();}
   textAt('Camera',18,camera[1]+70,'#EBCB8B',28);textAt('Image plane',105,52,'#EBCB8B',28);
   textAt(`Scale ${state.scale.toFixed(1)} then shift ${state.shift.toFixed(1)}`,520,48,'#EC93D7',28);
   textAt(`Shift only ${normalizedShift.toFixed(2)}`,520,88,'#b8e3d1',28);
   textAt('Same projection in both cases',520,H-22,'#f5f5f5',30);
   scaleOutput.value=state.scale.toFixed(1)+'×';shiftOutput.value=state.shift.toFixed(1);
   host.dataset.scale=state.scale.toFixed(1);host.dataset.shift=state.shift.toFixed(1);host.dataset.normalizedShift=normalizedShift.toFixed(3);
   host.dataset.projectionError=String(Math.abs(scaledHalf/scaledDepth-shiftOnlyHalf/shiftOnlyDepth));
  }
  scaleRange.oninput=()=>{state.scale=Number(scaleRange.value);paint();save();};
  shiftRange.oninput=()=>{state.shift=Number(shiftRange.value);paint();save();};
  paint();
 }else if(scene.kind==='ambiguity'){
  function paint(){
   ctx.fillStyle='#080c10';ctx.fillRect(0,0,W,H);
   const camera=[0,0,-5],cameraScreen=[80,H/2],base=[];
   for(const z of [0,2])for(const y of [-1,1])for(const x of [-1,1])base.push([x,y,z]);
   const scaled=base.map(p=>p.map((v,k)=>camera[k]+state.scale*(v-camera[k])));
   const project=p=>[p[0]/(p[2]-camera[2]),p[1]/(p[2]-camera[2])];
   const imagePoints=scaled.map(project),originalPoints=base.map(project);
   const error=Math.max(...originalPoints.map((p,i)=>Math.hypot(p[0]-imagePoints[i][0],p[1]-imagePoints[i][1])));
   host.dataset.projectionError=error;host.dataset.scale=state.scale;
   function scenePoint(p){const basePoint=[215+p[0]*30+p[2]*20,H/2-p[1]*27-p[2]*8];
    return [cameraScreen[0]+state.scale*(basePoint[0]-cameraScreen[0]),cameraScreen[1]+state.scale*(basePoint[1]-cameraScreen[1])];}
   const corners=base.map(scenePoint);
   ctx.fillStyle='#EBCB8B';ctx.beginPath();ctx.arc(...cameraScreen,9,0,Math.PI*2);ctx.fill();
   line([135,89],[135,H-89],'#EBCB8B',3);
   for(let i=0;i<4;i++)line(cameraScreen,corners[i],'#526078',1);
   for(let i=0;i<8;i++)for(let bit=0;bit<3;bit++){const j=i^(1<<bit);if(j>i)line(corners[i],corners[j],'#b8e3d1',3);}
   textAt('Fixed camera',23,H-17,'#EBCB8B');textAt(`Scene ×${state.scale.toFixed(1)}`,255,38);
   textAt('Unchanged image',762,38);ctx.strokeStyle='#526078';ctx.lineWidth=2;ctx.strokeRect(758,64,274,204);
   const imagePoint=p=>[895+p[0]*300,167-p[1]*300];
   for(let i=0;i<8;i++)for(let bit=0;bit<3;bit++){const j=i^(1<<bit);if(j>i)line(imagePoint(imagePoints[i]),imagePoint(imagePoints[j]),'#b8e3d1',3);}
  }
  const label=document.createElement('label');label.textContent='Change scene size';const range=document.createElement('input');range.type='range';range.min='1';range.max='3';range.step='.1';range.value=state.scale;range.setAttribute('aria-label','Scene size around a fixed camera');
  range.oninput=()=>{state.scale=Number(range.value);paint();save();};controls.append(label,range);paint();
 }
 if(mini)controls.hidden=true;
}

function renderStepsScene(el,spec,mini=false){
 const scene=spec.scene,host=document.createElement('div');host.className='scene-view steps-scene';
 geometry(host,...scene.bounds);host.style.position='absolute';el.append(host);
 host.addEventListener('click',e=>e.stopPropagation());
 widgetState.scenes??={};const key=spec.id+'-scene';
 let state={step:0,...widgetState.scenes[key]};
 state.step=Math.max(0,Math.min(scene.frames.length-1,Number(state.step)||0));
 const image=document.createElement('img');image.className='steps-image';host.append(image);
 const controls=document.createElement('div');controls.className='scene-controls steps-controls';host.append(controls);
 const back=document.createElement('button');back.textContent='Previous';controls.append(back);
 const range=document.createElement('input');range.type='range';range.min=0;range.max=scene.frames.length-1;range.step=1;range.setAttribute('aria-label','Refinement step');controls.append(range);
 const next=document.createElement('button');next.textContent='Next';controls.append(next);
 const label=document.createElement('span');label.className='steps-label';controls.append(label);
 function save(){widgetState.scenes[key]={step:state.step};if(!mini)sync();}
 function paint(){const frame=scene.frames[state.step];image.src=frame.image;image.alt=frame.label;range.value=state.step;label.textContent=frame.label;host.dataset.step=String(state.step);back.disabled=state.step===0;next.disabled=state.step===scene.frames.length-1;}
 function setStep(value){state.step=Math.max(0,Math.min(scene.frames.length-1,value));paint();save();}
 back.onclick=()=>setStep(state.step-1);next.onclick=()=>setStep(state.step+1);range.oninput=()=>setStep(Number(range.value));
 if(mini)controls.hidden=true;paint();
}

function renderCorrectionScene(el,spec,mini=false){
 const scene=spec.scene,host=document.createElement('div');host.className='scene-view correction-scene';
 geometry(host,...scene.bounds);host.style.position='absolute';el.append(host);
 host.addEventListener('click',e=>e.stopPropagation());
 widgetState.scenes??={};const key=spec.id+'-scene';
 const initial={yaw:scene.initial_yaw??-.55,pitch:scene.initial_pitch??-.12};
 const state={...initial,...widgetState.scenes[key]};
 const canvases=[];const contexts=[];
 for(let i=0;i<2;i++){
  const canvas=document.createElement('canvas');canvas.width=680;canvas.height=600;
  canvas.className='correction-cloud';canvas.setAttribute('aria-label',i?'After correction overlaid with ground truth; drag to orbit both panels':'Before correction overlaid with ground truth; drag to orbit both panels');
  host.append(canvas);canvases.push(canvas);const ctx=canvas.getContext('2d');ctx.scale(2,2);contexts.push(ctx);
 }
 const controls=document.createElement('div');controls.className='correction-controls';host.append(controls);
 const legend=document.createElement('span');legend.innerHTML='<span class="correction-gt">Reference</span><span class="correction-pred">Input</span>';controls.append(legend);
 const reset=document.createElement('button');reset.textContent='Reset view';controls.append(reset);
 const gt=scene.ground_truth,pred=scene.prediction,scale=scene.applied_scale;
 const all=gt.concat(pred,pred.map(p=>p.map(v=>v*scale)));
 const center=[0,1,2].map(k=>all.reduce((sum,p)=>sum+p[k],0)/all.length);
 const radius=Math.max(...all.map(p=>Math.hypot(...p.map((v,k)=>v-center[k]))));
 function save(){widgetState.scenes[key]={yaw:state.yaw,pitch:state.pitch};if(!mini)sync();}
 function paint(){
  const cy=Math.cos(state.yaw),sy=Math.sin(state.yaw),cp=Math.cos(state.pitch),sp=Math.sin(state.pitch);
  function project(p){const [x,y,z]=p.map((v,k)=>(v-center[k])/radius);
   const xx=x*cy-z*sy,zz=x*sy+z*cy,yy=y*cp-zz*sp,z2=y*sp+zz*cp;
   const f=600/(2.9+z2);return [xx*f,yy*f,z2];}
  const reference=all.map(project),xs=reference.map(p=>p[0]),ys=reference.map(p=>p[1]);
  const left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);
  const fit=Math.min(290/Math.max(1,right-left),268/Math.max(1,bottom-top));
  const mx=(left+right)/2,my=(top+bottom)/2;
  contexts.forEach((ctx,i)=>{
   ctx.fillStyle='#080c10';ctx.fillRect(0,0,340,300);
   const cloud=gt.map((p,j)=>[...project(p),0]).concat(pred.map((p,j)=>[...project(i?p.map(v=>v*scale):p),1]));
   cloud.sort((a,b)=>b[2]-a[2]);ctx.globalAlpha=.7;
   for(const [x,y,z,kind] of cloud){ctx.fillStyle=kind?'#EC93D7':'#80DAD6';ctx.fillRect(170+(x-mx)*fit,150+(y-my)*fit,2.4,2.4);}
   ctx.globalAlpha=1;
  });
  host.dataset.sharedYaw=String(state.yaw);host.dataset.sharedPitch=String(state.pitch);
 }
 let last=null,lastSync=0;
 for(const canvas of canvases){
  canvas.onpointerdown=e=>{if(mini)return;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);e.stopPropagation();};
  canvas.onpointermove=e=>{if(!last)return;state.yaw+=(e.clientX-last[0])*.008;state.pitch=Math.max(-1,Math.min(1,state.pitch+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];paint();if(performance.now()-lastSync>33){save();lastSync=performance.now();}};
  canvas.onpointerup=()=>{last=null;save();};canvas.onpointercancel=()=>{last=null;};
 }
 reset.onclick=()=>{Object.assign(state,initial);paint();save();};if(mini)reset.hidden=true;
 paint();
}

function renderPairScene(el,spec,mini=false){
 const scene=spec.scene,host=document.createElement('div');host.className='scene-view pair-scene';
 geometry(host,...scene.bounds);host.style.position='absolute';el.append(host);
 host.addEventListener('click',e=>e.stopPropagation());
 const key=spec.id+'-scene';widgetState.scenes??={};
 const defaults={frame:0,yaw:[scene.initial_yaw??-.34,scene.initial_yaw??-.34],pitch:[scene.initial_pitch??-.08,scene.initial_pitch??-.08]};
 let state={...defaults,...widgetState.scenes[key]};
 if(!Array.isArray(state.yaw)||state.yaw.length!==2||!Array.isArray(state.pitch)||state.pitch.length!==2)state={...defaults};
 state.frame=Math.max(0,Math.min(scene.cases[1].frames.length-1,state.frame||0));
 const panels=[];let timer=null;
 function save(){widgetState.scenes[key]={...state,yaw:[...state.yaw],pitch:[...state.pitch]};if(!mini)sync();}
 function stop(){if(timer){clearInterval(timer);timer=null;}if(panels[1])panels[1].play.textContent='Play';}
 function paint(i){
  const panel=panels[i],frame=scene.cases[i].frames[i===0?0:state.frame];
  panel.image.src=frame.image;host.dataset.frame=String(state.frame);
  if(i===1){panel.slider.value=state.frame;panel.count.textContent=`${state.frame+1} / ${scene.cases[1].frames.length}`;}
  const {ctx}=panel,W=508,H=235;ctx.fillStyle='#080c10';ctx.fillRect(0,0,W,H);
  const points=frame.points,colors=frame.colors,view=scene.cases[i].view;
  const center=view.center,radius=view.radius;
  const cy=Math.cos(state.yaw[i]),sy=Math.sin(state.yaw[i]),cp=Math.cos(state.pitch[i]),sp=Math.sin(state.pitch[i]);
  const projected=points.map((p,j)=>{const [x,y,z]=p.map((v,k)=>(v-center[k])/radius);
   const xx=x*cy-z*sy,zz=x*sy+z*cy,yy=y*cp-zz*sp,z2=y*sp+zz*cp;
   return [xx,yy,z2,j];}).sort((a,b)=>b[2]-a[2]);
  const fit=view.fit,[midX,midY]=view.projection_center;
  for(const [x,y,z,j] of projected){const c=colors[j];ctx.fillStyle=`rgb(${c[0]},${c[1]},${c[2]})`;
   ctx.fillRect(W/2+(x-midX)*fit,H/2+(y-midY)*fit,1.8,1.8);}
 }
 scene.cases.forEach((choice,i)=>{
  const panel=document.createElement('div');panel.className='pair-panel';panel.style.left=(i?548:0)+'px';host.append(panel);
  const image=document.createElement('img');image.className='pair-image';image.alt=`${choice.label} input`;panel.append(image);
  const canvas=document.createElement('canvas');canvas.className='pair-cloud';canvas.width=1016;canvas.height=470;
  canvas.setAttribute('aria-label',`${choice.label} orbitable depth reconstruction`);panel.append(canvas);
  const ctx=canvas.getContext('2d');ctx.scale(2,2);const item={image,canvas,ctx};panels.push(item);
  if(i===1){
   const controls=document.createElement('div');controls.className='pair-controls';panel.append(controls);
   const play=document.createElement('button');play.textContent='Play';controls.append(play);
   const slider=document.createElement('input');slider.type='range';slider.min=0;slider.max=choice.frames.length-1;slider.step=1;slider.setAttribute('aria-label','Sequence frame');controls.append(slider);
   const count=document.createElement('span');controls.append(count);Object.assign(item,{play,slider,count});
   slider.oninput=()=>{state.frame=Number(slider.value);paint(1);save();};
   play.onclick=()=>{if(timer){stop();return;}play.textContent='Pause';timer=setInterval(()=>{
    if(!host.isConnected){stop();return;}state.frame=(state.frame+1)%choice.frames.length;paint(1);save();
   },550);};
  }
  let last=null,lastSync=0;
  canvas.onpointerdown=e=>{if(mini)return;last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);e.stopPropagation();};
  canvas.onpointermove=e=>{if(!last)return;state.yaw[i]+=(e.clientX-last[0])*.008;
   state.pitch[i]=Math.max(-1,Math.min(1,state.pitch[i]+(e.clientY-last[1])*.008));last=[e.clientX,e.clientY];paint(i);
   if(performance.now()-lastSync>33){save();lastSync=performance.now();}};
  canvas.onpointerup=()=>{last=null;save();};canvas.onpointercancel=()=>{last=null;};
 });
 if(mini)panels[1].play.parentElement.hidden=true;
 paint(0);paint(1);
}
