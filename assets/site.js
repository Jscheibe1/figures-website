/* Figures - shared behavior. No dependencies. */
(function(){
var d=document,root=d.documentElement,reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
var $=function(s,c){return (c||d).querySelector(s)},$$=function(s,c){return [].slice.call((c||d).querySelectorAll(s))};

/* header + menu */
var head=$('.site-head'),btn=$('.menu-btn'),menu=$('#menu');
function setMenu(open){root.classList.toggle('menu-open',open);btn.setAttribute('aria-expanded',open);btn.querySelector('span').textContent=open?'Close':'Menu';d.body.style.overflow=open?'hidden':'';if(open){var a=$('a',menu);a&&a.focus({preventScroll:true})}}
if(btn){btn.addEventListener('click',function(){setMenu(!root.classList.contains('menu-open'))});
d.addEventListener('keydown',function(e){if(e.key==='Escape'&&root.classList.contains('menu-open')){setMenu(false);btn.focus()}});
$$('a',menu).forEach(function(a){a.addEventListener('click',function(){setMenu(false)})})}

/* scroll-linked: header, spinning seals, hero drift, step progress */
var spins=$$('.spin'),drift=$('[data-drift]'),steps=$$('.steps'),ticking=false;
function frame(){ticking=false;var y=window.scrollY||0,vh=window.innerHeight;
 if(head)head.classList.toggle('is-solid',y>12||head.hasAttribute('data-solid'));
 if(!reduce){spins.forEach(function(el){var r=el.parentNode.getBoundingClientRect(),p;
   if(r.bottom<-80||r.top>vh+80)return;
   if(el.getAttribute('data-spin')==='exit'){p=Math.max(0,Math.min(1,y/(vh*0.85)));el.style.transform='rotate('+(-8+360*p).toFixed(1)+'deg)'}
   else{p=Math.max(0,Math.min(1,(vh-r.top)/(vh*0.6)));p=1-Math.pow(1-p,2);el.style.transform='rotate('+(-8-360*(1-p)).toFixed(1)+'deg)'}});
  if(drift&&y<vh*1.2)drift.style.transform='translate3d(0,'+(y*0.12).toFixed(1)+'px,0)';
  steps.forEach(function(s){var r=s.getBoundingClientRect();var p=(vh*0.8-r.top)/(r.height+vh*0.3);s.style.setProperty('--p',Math.max(0,Math.min(1,p)).toFixed(3))})}
}
function onScroll(){if(!ticking){ticking=true;requestAnimationFrame(frame)}}
addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',onScroll);frame();

/* one-time reveals */
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('is-in');io.unobserve(e.target)}})},{threshold:.35});
 $$('[data-in],[data-stamp]').forEach(function(el){io.observe(el)});
 /* touch: light the row crossing the middle of the screen */
 /* touch: the one block on the reading line (a little above the middle of the screen) lifts, the way hover does with a mouse */
 if(!reduce&&matchMedia('(hover: none)').matches&&window.innerHeight<=(screen.height||9999)*1.2){
  var hotEls=$$('a.row,.list>div,a.svc-row,.facts>div,.step,.faq-group details,.fit-item,.two .body p,.panel p:not(:last-child)'),hotCur=null,hotTick=false;
  var pickHot=function(){hotTick=false;var vh=window.innerHeight,y=vh*0.46,best=null,bd=1e9;
   for(var i=0;i<hotEls.length;i++){var r=hotEls[i].getBoundingClientRect();if(!r.width||r.bottom<0||r.top>vh)continue;var d=y<r.top?r.top-y:(y>r.bottom?y-r.bottom:0);if(d<bd){bd=d;best=hotEls[i]}}
   if(bd>vh*0.14)best=null;
   if(best!==hotCur){if(hotCur)hotCur.classList.remove('is-hot');if(best)best.classList.add('is-hot');hotCur=best}};
  if(hotEls.length){addEventListener('scroll',function(){if(!hotTick){hotTick=true;requestAnimationFrame(pickHot)}},{passive:true});addEventListener('resize',pickHot);pickHot()}
 }
}else{$$('[data-in],[data-stamp]').forEach(function(el){el.classList.add('is-in')})}

/* swipe rail */
$$('.swipe-wrap').forEach(function(w){var rail=$('.swipe',w),bar=$('.swipe-bar i',w),prev=$('.prev',w),next=$('.next',w);
 function upd(){var max=rail.scrollWidth-rail.clientWidth,p=max>0?rail.scrollLeft/max:1,vis=rail.clientWidth/rail.scrollWidth;bar.style.width=Math.min(100,(vis+(1-vis)*p)*100)+'%';prev.disabled=rail.scrollLeft<4;next.disabled=rail.scrollLeft>max-4}
 function step(dir){var c=$('.card',rail);rail.scrollBy({left:dir*(c.offsetWidth+18),behavior:reduce?'auto':'smooth'})}
 prev.addEventListener('click',function(){step(-1)});next.addEventListener('click',function(){step(1)});
 rail.addEventListener('scroll',upd,{passive:true});addEventListener('resize',upd);upd();
 var down=false,sx=0,sl=0,moved=false;
 rail.addEventListener('pointerdown',function(e){if(e.pointerType!=='mouse')return;down=true;moved=false;sx=e.clientX;sl=rail.scrollLeft});
 addEventListener('pointermove',function(e){if(!down)return;var dx=e.clientX-sx;if(Math.abs(dx)>4){moved=true;rail.classList.add('is-drag')}rail.scrollLeft=sl-dx});
 addEventListener('pointerup',function(){if(!down)return;down=false;rail.classList.remove('is-drag')});
 rail.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation()}},true);
 rail.addEventListener('keydown',function(e){if(e.key==='ArrowRight')step(1);if(e.key==='ArrowLeft')step(-1)});
});

/* fit check */
var fit=$('.fit');if(fit){var boxes=$$('input[type=checkbox]',fit),out=$('.fit-out',fit),msg=$('.fit-msg',fit),dots=$$('.fit-meter i',fit),cta=$('.fit-cta',fit);
 var lines=['Check the ones that are true for you.','That\'s one. Keep going.','You\'re halfway there.','One more and it\'s a fit.','<b>That\'s a fit.</b> The application takes about two minutes.'];
 function calc(){var n=boxes.filter(function(b){return b.checked}).length;dots.forEach(function(i,k){i.classList.toggle('on',k<n)});msg.innerHTML=lines[n];out.classList.toggle('is-fit',n===boxes.length);cta.classList.toggle('ghost',n!==boxes.length)}
 boxes.forEach(function(b){b.addEventListener('change',calc)});calc()}

/* copy buttons */
$$('.copy').forEach(function(b){b.addEventListener('click',function(){var t=b.getAttribute('data-copy'),old=b.textContent;function ok(){b.textContent='Copied';b.classList.add('is-done');setTimeout(function(){b.textContent=old;b.classList.remove('is-done')},1600)}
 if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(t).then(ok,function(){sel()})}else sel();
 function sel(){var v=b.parentNode.querySelector('.v');if(v){var r=d.createRange();r.selectNodeContents(v);var s=getSelection();s.removeAllRanges();s.addRange(r)}}})});

/* forms: steps + send */
$$('form[data-form]').forEach(function(form){var stepsEl=$$('.fstep',form),i=0,bar=$('.prog-bar i',form),lab=$('.prog b',form),msg=$('.form-msg',form),done=$('.form-done',form.parentNode);
 function show(n){i=n;stepsEl.forEach(function(s,k){s.classList.toggle('is-on',k===n)});if(bar){bar.style.width=((n+1)/stepsEl.length*100)+'%';lab.textContent='Step '+(n+1)+' of '+stepsEl.length}
  var b=$('.back',form);if(b)b.style.visibility=n?'visible':'hidden';var nx=$('.next',form),sd=$('.send',form);if(nx){nx.hidden=n===stepsEl.length-1;sd.hidden=n!==stepsEl.length-1}}
 function valid(n){var ok=true;$$('input,select,textarea',stepsEl[n]).some(function(el){if(!el.checkValidity()){el.reportValidity();ok=false;return true}});
  if(ok)$$('[data-min]',stepsEl[n]).forEach(function(g){if(!$$('input:checked',g).length){ok=false;msg.textContent=g.getAttribute('data-msg');msg.classList.add('is-on')}});
  if(ok)msg.classList.remove('is-on');return ok}
 if(stepsEl.length){show(0);
  $('.next',form).addEventListener('click',function(){if(valid(i)){show(i+1);var f=$('input,select,textarea',stepsEl[i]);form.scrollIntoView({block:'nearest'})}});
  $('.back',form).addEventListener('click',function(){show(i-1)})}
 var sells=$$('input[name=sells]',form),hint=$('.hint',form);
 sells.forEach(function(r){r.addEventListener('change',function(){hint.classList.toggle('is-on',r.value==='Nothing yet'&&r.checked)})});
 form.addEventListener('submit',function(e){e.preventDefault();
  for(var n=0;n<stepsEl.length;n++){if(!valid(n)){show(n);return}}
  if(!form.checkValidity()){form.reportValidity();return}
  var url=form.getAttribute('action'),send=$('.send',form)||$('button[type=submit]',form);msg.classList.remove('is-on');
  if(!url||url.indexOf('REPLACE')>-1){msg.textContent='This form isn\'t connected yet. Please email info@wearefigures.com and we\'ll take it from there.';msg.classList.add('is-on');return}
  send.disabled=true;var old=send.textContent;send.textContent='Sending';
  fetch(url,{method:'POST',headers:{Accept:'application/json'},body:new FormData(form)}).then(function(r){if(!r.ok)throw 0;form.hidden=true;done.classList.add('is-on');done.scrollIntoView({block:'center'})})
  .catch(function(){send.disabled=false;send.textContent=old;msg.textContent='That didn\'t send. Check your connection and try again, or email info@wearefigures.com.';msg.classList.add('is-on')})})});
})();
