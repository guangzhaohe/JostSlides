const EVIDENCE = /* EVIDENCE_DATA */;
let widgetState={policy:'60',env:'all',show:'all',case:null,scene:'0000',measurement:0,custom:[0,1.075,6,3]};
const RECIPES={original:[0,1.25,'off',0],60:[0,1.075,6,3],70:[3,1.4,'off',3],80:[2,1.5,'off',2],90:[0,1.75,'off',0]};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct=x=>x==null?'No fit':x.toFixed(2)+'%';
function widgetChange(key,value){widgetState[key]=value;render();sync();}
function option(value,label,selected){return `<option value="${esc(value)}" ${String(value)===String(selected)?'selected':''}>${esc(label)}</option>`;}
let choiceMenu=null,choiceMenuId=0;
function closeChoiceMenu(){
 if(!choiceMenu)return;
 choiceMenu.button.setAttribute('aria-expanded','false');
 choiceMenu.button.removeAttribute('aria-activedescendant');
 choiceMenu.menu.remove();choiceMenu=null;
}
function styleSelects(root){
 // Keep native values/change events for the widgets; replace only their UI.
 for(const select of root.querySelectorAll('select')){
  const style=getComputedStyle(select),font=style.font,padding=style.padding,margin=style.marginTop;
  const control=document.createElement('span');control.className='choice-control';control.style.marginTop=margin;
  select.before(control);control.append(select);select.classList.add('choice-native');select.style.margin='0';
  select.tabIndex=-1;select.setAttribute('aria-hidden','true');
  const button=document.createElement('button');button.type='button';button.className='choice-trigger';
  button.style.font=font;button.style.padding=padding;button.style.paddingRight='1.6em';
  button.setAttribute('role','combobox');button.setAttribute('aria-haspopup','listbox');button.setAttribute('aria-expanded','false');
  button.setAttribute('aria-label',select.getAttribute('aria-label')||select.closest('label')?.firstChild.textContent.trim()||'Choose an option');
  const label=document.createElement('span');label.className='choice-label';button.append(label);control.append(button);
  const menuId='choice-menu-'+(++choiceMenuId);button.setAttribute('aria-controls',menuId);
  function update(){label.textContent=select.selectedOptions[0]?.textContent||'';button.disabled=select.disabled;}
  function choose(index){
   const value=select.options[index];if(!value||value.disabled)return;
   closeChoiceMenu();select.value=value.value;update();
   select.dispatchEvent(new Event('change',{bubbles:true}));
   // Re-rendered evidence controls retain keyboard focus on the same field.
   const replacement=select.id?document.getElementById(select.id):select;
   replacement?.closest('.choice-control')?.querySelector('.choice-trigger')?.focus();
  }
  function highlight(index){
   if(!choiceMenu||choiceMenu.button!==button)return;
   const items=choiceMenu.items;
   choiceMenu.active=Math.max(0,Math.min(items.length-1,index));
   items.forEach((item,i)=>item.dataset.active=String(i===choiceMenu.active));
   const item=items[choiceMenu.active];button.setAttribute('aria-activedescendant',item.id);item.scrollIntoView({block:'nearest'});
  }
  function open(){
   closeChoiceMenu();const menu=document.createElement('div');menu.className='choice-menu';menu.id=menuId;
   menu.setAttribute('role','listbox');menu.setAttribute('aria-label',button.getAttribute('aria-label'));
   const items=[...select.options].map((value,index)=>{
    const item=document.createElement('button');item.type='button';item.className='choice-option';item.id=menuId+'-'+index;
    item.setAttribute('role','option');item.setAttribute('aria-selected',String(value.selected));item.tabIndex=-1;
    item.disabled=value.disabled;item.textContent=value.textContent;item.onclick=()=>choose(index);menu.append(item);return item;
   });
   // Popups escape the scaled/clipped slide but stay in a modal's top layer.
   (button.closest('dialog')||document.body).append(menu);
   const bounds=button.getBoundingClientRect(),scale=bounds.height/button.offsetHeight;
   menu.style.fontSize=Math.max(16,parseFloat(getComputedStyle(button).fontSize)*scale)+'px';
   const width=Math.min(innerWidth-24,Math.max(bounds.width,220));menu.style.width=width+'px';
   menu.style.left=Math.max(12,Math.min(bounds.left,innerWidth-width-12))+'px';
   const below=innerHeight-bounds.bottom-16,above=bounds.top-16,down=below>=Math.min(menu.scrollHeight,320)||below>=above;
   menu.style.maxHeight=Math.max(40,Math.min(320,down?below:above))+'px';
   if(down)menu.style.top=(bounds.bottom+8)+'px';else menu.style.bottom=(innerHeight-bounds.top+8)+'px';
   choiceMenu={button,menu,items,active:select.selectedIndex};button.setAttribute('aria-expanded','true');highlight(select.selectedIndex);
  }
  button.onclick=()=>{if(choiceMenu?.button===button)closeChoiceMenu();else open();};
  let search='',searchedAt=0;
  button.onkeydown=event=>{
   if(event.ctrlKey||event.metaKey||event.altKey)return;
   const key=event.key,isOpen=choiceMenu?.button===button;
   if(key==='Tab'){closeChoiceMenu();return;}
   if(!['ArrowDown','ArrowUp','Home','End','Enter',' ','Escape'].includes(key)&&key.length!==1){closeChoiceMenu();return;}
   if(key==='Escape'&&!isOpen)return;
   event.preventDefault();event.stopPropagation();
   if(key==='Escape'){closeChoiceMenu();return;}
   if(key==='Enter'||key===' '){if(isOpen)choose(choiceMenu.active);else open();return;}
   if(!isOpen)open();
   if(key==='ArrowDown'||key==='ArrowUp'){
    const direction=key==='ArrowDown'?1:-1;let next=choiceMenu.active+direction;
    while(next>=0&&next<select.options.length&&select.options[next].disabled)next+=direction;
    highlight(next);
   }else if(key==='Home'||key==='End')highlight(key==='Home'?0:select.options.length-1);
   else{
    const now=Date.now();search=now-searchedAt>700?key:search+key;searchedAt=now;
    const found=[...select.options].findIndex(o=>!o.disabled&&o.textContent.toLowerCase().startsWith(search.toLowerCase()));
    if(found>=0)highlight(found);
   }
  };
  select.addEventListener('change',update);
  select.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();button.focus();button.click();});
  update();
 }
}
document.addEventListener('pointerdown',event=>{
 if(choiceMenu&&!choiceMenu.menu.contains(event.target)&&!choiceMenu.button.contains(event.target))closeChoiceMenu();
});
window.addEventListener('resize',closeChoiceMenu);
document.addEventListener('scroll',event=>{if(choiceMenu&&!choiceMenu.menu.contains(event.target))closeChoiceMenu();},true);
function evaluateDiode(){
 const p=RECIPES[widgetState.policy]||widgetState.custom;
 return EVIDENCE.diode.cases.filter(c=>widgetState.env==='all'||c.environment===widgetState.env).map(c=>{
  const m=c.metrics.find(m=>m.global_ratio===Number(p[1]));
  const kept=m.success&&c.before_objects>=Number(p[0])&&(p[2]==='off'||(m.case_residual_pct!=null&&m.case_residual_pct<=Number(p[2])))&&m.supporting_anchors>=Number(p[3]);
  return {...c,m,kept};
 });
}
function renderEvidence(el,type,mini){
 const w=document.createElement('div');w.className='evidence '+type;el.append(w);
 if(type==='diode')renderDiode(w,mini);else if(type==='predictions')renderPredictions(w,mini);else renderReal(w,mini);
 if(mini){w.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));w.querySelectorAll('select,button,[tabindex]').forEach(e=>e.tabIndex=-1);}else styleSelects(w);
}
function renderDiode(w,mini){
 const rows=evaluateDiode(),kept=rows.filter(c=>c.kept),errors=kept.map(c=>c.m.error_pct),mean=errors.length?errors.reduce((a,b)=>a+b,0)/errors.length:null;
 const shown=rows.filter(c=>widgetState.show==='all'||(widgetState.show==='kept'?c.kept:!c.kept));
 const pts=shown.filter(c=>c.m.success).sort((a,b)=>b.m.error_pct-a.m.error_pct);
 const selected=shown.find(c=>c.case===widgetState.case)||pts.find(c=>c.kept)||pts[0]||shown[0];
 const ymax=Math.max(10,Math.ceil(Math.max(0,...pts.map(c=>c.m.error_pct))/10)*10);
 let svg='<svg viewBox="0 0 710 295" aria-label="Absolute scale errors ranked from highest to lowest" role="group">';
 for(let n=0;n<=2;n++){let y=40+n*94;svg+=`<line x1="85" y1="${y}" x2="686" y2="${y}" stroke="#c8d3ce"/><text x="78" y="${y+8}" text-anchor="end" font-size="25">${ymax*(2-n)/2}%</text>`;}
 svg+='<text x="85" y="26" font-size="27">Absolute scale error</text><text x="370" y="279" text-anchor="middle" font-size="26">Cases, from largest to smallest error</text>';
 pts.forEach((c,i)=>{let x=95+i*579/Math.max(1,pts.length-1),y=228-c.m.error_pct/ymax*188;
  svg+=`<circle class="case-point" data-case="${c.case}" cx="${x}" cy="${y}" r="${selected?.case===c.case?8:5}" fill="${c.kept?'#315bd6':'#b9662b'}" stroke="${selected?.case===c.case?'#172e35':'none'}" stroke-width="3" tabindex="${mini?-1:0}" role="button" aria-label="${c.case}: ${pct(c.m.error_pct)}, ${c.kept?'kept':'rejected'}"><title>${c.case}: ${pct(c.m.error_pct)}, ${c.kept?'kept':'rejected'}</title></circle>`;
 });svg+='</svg>';
 w.innerHTML=`<div class="evidence-controls"><select id="diode-policy" aria-label="Evidence rejection policy">${[['60','Balanced policy'],['original','Original baseline'],['70','Minimum 3 objects'],['80','Minimum 2 objects'],['90','Wide ratio threshold'],['custom','Custom policy']].map(([v,l])=>option(v,l,widgetState.policy)).join('')}</select><select id="diode-env" aria-label="Evidence environment">${[['all','All environments'],['indoor','Indoor'],['outdoor','Outdoor']].map(([v,l])=>option(v,l,widgetState.env)).join('')}</select><button class="evidence-button" id="policy-settings">Tune policy</button></div>
 <div class="evidence-stats"><div><span>Cases kept</span><strong id="diode-coverage">${kept.length} / ${rows.length}</strong></div><div><span>Mean kept error</span><strong id="diode-mean">${pct(mean)}</strong></div><div><span>Observed kept range</span><strong id="diode-range">${errors.length?pct(Math.min(...errors))+'–'+pct(Math.max(...errors)):'No cases kept'}</strong></div></div>
 <div class="diode-chart">${svg}</div><div class="diode-case">${selected?`<img src="${selected.image}" alt="${selected.case}, representative frame"><select id="diode-case-select" aria-label="Inspect an evidence case">${shown.map(c=>option(c.case,c.case,selected.case)).join('')}</select><div>${pct(selected.m.error_pct)} — ${!selected.m.success?'failed':selected.kept?'kept':'rejected'}</div>`:'No cases match.'}</div>
 <div class="plot-filter"><select id="diode-show" aria-label="Cases shown on plot">${[['all','All fitted cases'],['kept','Kept cases'],['rejected','Rejected cases']].map(([v,l])=>option(v,l,widgetState.show)).join('')}</select><span><b style="color:#315bd6">Kept</b> / <b style="color:#b9662b">Rejected</b></span></div>`;
 if(mini)return;
 w.querySelector('#diode-policy').onchange=e=>{widgetChange('policy',e.target.value);if(e.target.value==='custom')openPolicy();};
 w.querySelector('#diode-env').onchange=e=>widgetChange('env',e.target.value);
 w.querySelector('#diode-show').onchange=e=>widgetChange('show',e.target.value);
 const caseSelect=w.querySelector('#diode-case-select');if(caseSelect)caseSelect.onchange=e=>widgetChange('case',e.target.value);
 w.querySelectorAll('.case-point').forEach(p=>{p.onclick=()=>widgetChange('case',p.dataset.case);p.onkeydown=e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();e.stopPropagation();widgetChange('case',p.dataset.case);}};});
 w.querySelector('#policy-settings').onclick=openPolicy;
}
function evidenceDialog(title,body){
 let d=document.getElementById('evidence-dialog');if(!d){d=document.createElement('dialog');d.id='evidence-dialog';d.className='evidence-dialog';document.body.append(d);}
 d.innerHTML=`<div class="dialog-heading"><h2>${title}</h2><button id="evidence-close">Close</button></div>${body}`;d.querySelector('#evidence-close').onclick=()=>d.close();d.showModal();return d;
}
function openPolicy(){
 const p=RECIPES[widgetState.policy]||widgetState.custom;
 const configs=[['Objects before RANSAC',[0,1,2,3,5,10,20]],['Global inlier ratio',EVIDENCE.diode.ratios],['Maximum residual (%)',['off',2,4,6,8,10,12,14,16]],['Supporting anchors',[0,1,2,3,5,10,20]]];
 const d=evidenceDialog('Tune the saved rejection policy',`<div class="policy-grid">${configs.map(([label,values],i)=>`<label>${label}<select data-param="${i}">${values.map(v=>option(v,v,p[i])).join('')}</select></label>`).join('')}</div><p>Only the global ratio changes the fitted scale. Other controls accept or reject cases using stored diagnostics.</p><p>Error = 100 × |estimated scale − 1|. The range is the observed minimum–maximum, not a confidence interval.</p><button id="apply-policy" class="primary">Apply policy</button>`);
 styleSelects(d);d.addEventListener('close',closeChoiceMenu,{once:true});
 d.querySelector('#apply-policy').onclick=()=>{widgetState.custom=[...d.querySelectorAll('[data-param]')].map(s=>s.value==='off'?'off':Number(s.value));widgetState.policy='custom';d.close();render();sync();};
}
function realOverlay(scene,m){
 const a=m.pixel_a,b=m.pixel_b;
 return `<svg viewBox="0 0 1024 768" role="img" aria-label="Annotated endpoints for ${m.gt_input} physical length"><image width="1024" height="768" href="${scene.images[m.frame_index]}"/><line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#172e35" stroke-width="12"/><line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#ffe278" stroke-width="6"/>${[a,b].map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="14" fill="#ffe278" stroke="#172e35" stroke-width="4"/><text x="${x+20}" y="${y-16}" fill="white" stroke="#172e35" stroke-width="5" paint-order="stroke" font-size="44" font-weight="bold">${i?'B':'A'}</text>`).join('')}</svg>`;
}
function renderReal(w,mini){
 const scene=EVIDENCE.real.find(s=>s.scene===widgetState.scene)||EVIDENCE.real[0];
 const index=Math.min(widgetState.measurement,scene.measurements.length-1),m=scene.measurements[index];
 const overlay=realOverlay(scene,m);
 w.innerHTML=`<div class="evidence-controls"><select id="real-scene" aria-label="Measurement scene">${EVIDENCE.real.map(s=>option(s.scene,'Scene '+s.scene,scene.scene)).join('')}</select><select id="real-measurement" aria-label="Object-size measurement">${scene.measurements.map((v,i)=>option(i,`${v.label} — ${v.gt_input}`,index)).join('')}</select><span>${EVIDENCE.real.reduce((n,s)=>n+s.measurements.length,0)} measurements / ${EVIDENCE.real.length} scenes</span></div><div class="real-photo">${overlay}</div><div class="real-explainer"><div><span>1. Mark two endpoints</span><p>A and B define an object dimension.</p></div><div><span>2. Enter its real size</span><strong>${esc(m.gt_input)}</strong></div><div><span>3. Divide size by 3D span</span><p>Relative 3D span: ${m.unscaled_m.toFixed(3)}</p><strong>Scale: ${m.implied_scale.toFixed(3)}×</strong></div><p class="real-caveat">A scale reference, not dense depth ground truth.</p></div>`;
 if(mini)return;
 w.querySelector('#real-scene').onchange=e=>{widgetState.measurement=0;widgetChange('scene',e.target.value);};
 w.querySelector('#real-measurement').onchange=e=>widgetChange('measurement',Number(e.target.value));
}
function renderPredictions(w,mini){
 const scene=EVIDENCE.real.find(s=>s.scene===widgetState.scene)||EVIDENCE.real[0];
 const index=Math.min(widgetState.measurement,scene.measurements.length-1),m=scene.measurements[index];
 const result=EVIDENCE.real_results.measurements.find(r=>r.scene===scene.scene&&r.annotation_id===m.id);
 const accepted=result.accepted;
 w.innerHTML=`<div class="evidence-controls"><select id="prediction-scene" aria-label="Prediction scene">${EVIDENCE.real.map(s=>option(s.scene,'Scene '+s.scene,scene.scene)).join('')}</select><select id="prediction-measurement" aria-label="Prediction measurement">${scene.measurements.map((v,i)=>option(i,v.label,index)).join('')}</select><span id="prediction-status" class="${accepted?'accepted-result':'rejected-result'}">${accepted?'Accepted scene':'Rejected — diagnostic only'}</span></div>
 <div class="real-photo">${realOverlay(scene,m)}</div>
 <div class="prediction-values"><div><span>Measured length</span><strong id="prediction-measured">${result.ground_truth_cm.toFixed(2)} cm</strong></div><div><span>Unscaled input</span><strong id="prediction-backend">${result.unscaled_cm.toFixed(2)} cm</strong><p class="prediction-error-line"><b id="prediction-backend-error">${pct(result.unscaled_absolute_relative_error_pct)}</b> error</p></div><div><span>Corrected estimate</span><strong id="prediction-estimate">${result.estimated_cm.toFixed(2)} cm</strong><p class="prediction-error-line"><b id="prediction-error">${pct(result.absolute_relative_error_pct)}</b> error</p></div><p id="prediction-scale">Applied scale: ${result.scale.toFixed(3)}×</p></div>`;
 if(mini)return;
 w.querySelector('#prediction-scene').onchange=e=>{widgetState.measurement=0;widgetChange('scene',e.target.value);};
 w.querySelector('#prediction-measurement').onchange=e=>widgetChange('measurement',Number(e.target.value));
}
function showSources(){
 const s=SLIDES[current];
 evidenceDialog('Sources and measurement context',`<p>${esc(s.notes)}</p>${(s.sources||[]).map(([label,url])=>`<p><a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)} ↗</a></p>`).join('')}${s.widget?'<p>All displayed numerical data and images are bundled in this presentation. The viewers are adapted for presentation from the saved research artifacts.</p>':''}`);
}
