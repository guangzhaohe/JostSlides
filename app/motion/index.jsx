import React, {useEffect, useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Player} from '@remotion/player';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';

const FPS = 60;
const FRAMES = 54;
const duration = FRAMES / FPS * 1000;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)};
const progress = (frame, start, end) => interpolate(frame, [start, end], [0, 1], clamp);

function SlideLayer({spec, incoming, direction, visibleStep = Infinity, revealStep = null}) {
  const frame = useCurrentFrame();
  const building = revealStep !== null;
  const travel = building ? 1 : progress(frame, incoming ? 3 : 0, incoming ? 30 : 22);
  const elementStyle = (kind, index) => {
    const group = (spec.builds || []).findIndex(step => (step[kind] || []).includes(index));
    const reveal = group === revealStep ? progress(frame, 0, 30) : 1;
    return {visibility: group > visibleStep ? 'hidden' : 'visible',
      opacity: reveal, transform: `translateY(${14 * (1 - reveal)}px)`};
  };
  return <AbsoluteFill style={{backgroundColor: '#' + spec.bg,
    opacity: incoming ? travel : 1 - travel,
    transform: `translateX(${direction * (incoming ? 28 * (1 - travel) : -20 * travel)}px)`}}>
    {(spec.rects || []).map(([x,y,width,height,color], i) =>
      <div key={'r'+i} style={{position:'absolute',left:x,top:y,width,height,background:'#'+color,...elementStyle('rects', i)}} />)}
    {(spec.images || []).map((picture, i) => {
      const [left,top,width,height] = picture.bounds;
      if (picture.zoom) return <div key={'image'+i} style={{position:'absolute',left,top,width,height,overflow:'hidden'}}>
        <img src={picture.src} alt={picture.alt||''} style={{width:'100%',height:'100%',objectFit:picture.fit||'contain',objectPosition:picture.position||'center',transform:`scale(${picture.zoom})`,transformOrigin:picture.position||'center'}}/>
      </div>;
      return <img key={'image'+i} src={picture.src} alt={picture.alt||''} style={{position:'absolute',left,top,width,height,objectFit:picture.fit||'contain',objectPosition:picture.position||'center'}}/>;
    })}
    {spec.vectors && <svg viewBox="0 0 1152 648" style={{position:'absolute',inset:0,width:'100%',height:'100%'}}>
      {spec.vectors.map(([tag, attributes], i) => {
        const props = {...attributes, key:i};
        if ('stroke-width' in props) {props.strokeWidth=props['stroke-width'];delete props['stroke-width'];}
        return React.createElement(tag, props);
      })}
    </svg>}
    {spec.text.map(([x,y,width,height,text,size,bold,color], i) => {
      const reveal = incoming && !building ? progress(frame, 4 + Math.min(i, 6) * 3, 27 + Math.min(i, 6) * 3) : 1;
      return <div key={i} style={{position:'absolute',left:x,top:y,width,height,
        fontFamily:'Deck, Arial, sans-serif',fontSize:size,fontWeight:bold ? 700 : 400,
        lineHeight:1.19,whiteSpace:'pre',color:'#'+color,
        opacity:reveal,transform:`translateY(${12 * (1 - reveal)}px)`,
        ...(building ? elementStyle('text', i) : {})}}>{text}</div>;
    })}
  </AbsoluteFill>;
}

function BuildReveal({spec, step}) {
  return <SlideLayer spec={spec} incoming direction={0} visibleStep={step} revealStep={step}/>;
}

function SlideTransition({from, to, direction}) {
  return <AbsoluteFill style={{backgroundColor:'#'+to.bg}}>
    <SlideLayer spec={from} incoming={false} direction={direction}/>
    <SlideLayer spec={to} incoming direction={direction}/>
  </AbsoluteFill>;
}

function TransitionPlayer({state, initialFrame, onEnd}) {
  const ref = useRef(null);
  useEffect(() => {
    const player = ref.current;
    player.addEventListener('ended', onEnd);
    player.addEventListener('error', onEnd);
    return () => {
      player.removeEventListener('ended', onEnd);
      player.removeEventListener('error', onEnd);
    };
  }, [onEnd]);
  return <Player ref={ref} component={state.kind === 'build' ? BuildReveal : SlideTransition} inputProps={state}
    durationInFrames={FRAMES} compositionWidth={1152} compositionHeight={648}
    fps={FPS} initialFrame={initialFrame} autoPlay loop={false} controls={false}
    clickToPlay={false} doubleClickToFullscreen={false} spaceKeyToPlayOrPause={false}
    moveToBeginningWhenEnded={false} style={{width:'100%',height:'100%'}} />;
}

let active = null;
function cancel() {
  if (!active) return;
  const {root, host, frame, timer} = active;
  active = null;
  clearTimeout(timer);
  root.unmount();
  host.remove();
  frame.classList.remove('motion-active');
}

function play(state) {
    cancel();
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (state.kind !== 'build' && (state.from.widget || state.to.widget || state.from.scene || state.to.scene || state.from.video || state.to.video || state.from.builds || state.to.builds)) return;
    const elapsed = Math.max(0, Date.now() - state.startedAt);
    if (elapsed >= duration) return;
    const frame = document.querySelector('.slide-frame');
    const host = document.createElement('div');
    host.className = 'motion-overlay';
    host.setAttribute('aria-hidden', 'true');
    frame.append(host);
    const root = createRoot(host);
    const instance = {root, host, frame, timer:null};
    active = instance;
    const onEnd = () => {
      // Unmount outside React's commit; an old callback cannot cancel a newer transition.
      queueMicrotask(() => {if (active === instance) cancel();});
    };
    flushSync(() => root.render(<TransitionPlayer state={state}
      initialFrame={Math.min(FRAMES-1, Math.floor(elapsed / 1000 * FPS))} onEnd={onEnd}/>));
    frame.classList.add('motion-active');
    // Keep the destination usable if browser playback stalls or a tab was hidden.
    instance.timer = setTimeout(onEnd, duration - elapsed + 400);
}

window.DeckMotion = {
  cancel,
  play,
  reveal(state) {play({...state, kind:'build'});},
};
