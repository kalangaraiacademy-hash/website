/* Kalangarai Charitable & Educational Trust – shared site script */
function store(k,v){try{ if(v===undefined) return localStorage.getItem(k); localStorage.setItem(k,v);}catch(e){return null}}
const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];

/* ---------- language: English / Tamil / Hindi ---------- */
function setLanguage(lang){
  document.documentElement.lang=lang;
  ['ta','hi'].forEach(l=>document.body.classList.toggle('lang-'+l,lang===l));
  $$('[data-en][data-ta]').forEach(el=>{el.textContent=el.getAttribute('data-'+lang)||el.getAttribute('data-en')});
  $$('[data-en-html]').forEach(el=>{el.innerHTML=el.getAttribute('data-'+lang+'-html')||el.getAttribute('data-en-html')});
  $$('[data-en-placeholder]').forEach(el=>{el.placeholder=el.getAttribute('data-'+lang+'-placeholder')||el.getAttribute('data-en-placeholder')});
  ['en','ta','hi'].forEach(l=>{const b=document.getElementById(l+'Btn');if(!b)return;b.classList.toggle('active',lang===l);b.setAttribute('aria-pressed',lang===l)});
  const cur=document.getElementById('langCur');if(cur)cur.textContent={en:'EN',ta:'தமிழ்',hi:'हिंदी'}[lang];
  const lf=document.getElementById('langFloat');if(lf){lf.classList.remove('open');const t=document.getElementById('langToggle');if(t)t.setAttribute('aria-expanded','false')}
  store('kalangarai-language',lang);
  if(window.fitNav) window.fitNav();
}
const savedLang=store('kalangarai-language');
if(savedLang==='ta'||savedLang==='hi') setLanguage(savedLang);
const msg=(en,ta,hi)=>({ta,hi}[document.documentElement.lang]||en);

/* ---------- navigation ---------- */
const menuBtn=$('#menuBtn'),navLinks=$('#navLinks');
const closeMenu=()=>{navLinks.classList.remove('open');menuBtn.textContent='☰';menuBtn.setAttribute('aria-expanded','false')};
menuBtn.addEventListener('click',()=>{const o=navLinks.classList.toggle('open');menuBtn.textContent=o?'✕':'☰';menuBtn.setAttribute('aria-expanded',o)});
$$('a',navLinks).forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('click',e=>{
  if(navLinks.classList.contains('open')&&!navLinks.contains(e.target)&&e.target!==menuBtn) closeMenu();
  if(!e.target.closest('.mdd')) $$('.mdd.open').forEach(d=>{d.classList.remove('open');$('.mdd-btn',d).setAttribute('aria-expanded','false')});
});
// dropdowns: click/tap to open (hover also works on desktop)
$$('.mdd').forEach(dd=>{
  const btn=$('.mdd-btn',dd);
  btn.addEventListener('click',e=>{e.stopPropagation();const o=!dd.classList.contains('open');
    $$('.mdd.open').forEach(d=>{if(d!==dd){d.classList.remove('open');$('.mdd-btn',d).setAttribute('aria-expanded','false')}});
    dd.classList.toggle('open',o);btn.setAttribute('aria-expanded',o)});
});
// on small screens, open the section that contains the current page
if(window.matchMedia('(max-width:1023.98px)').matches){const c=$('.mdd.current');if(c)c.classList.add('open')}
function pickInterest(v){const s=$('#interest');if(s)s.value=v}

/* ---------- header shadow + back to top ---------- */
const headerEl=$('header'),toTop=$('#toTop');
const onScroll=()=>{const y=window.scrollY;headerEl.classList.toggle('scrolled',y>40);toTop.classList.toggle('show',y>700)};
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
toTop.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));

/* ---------- tap-to-enlarge photos ---------- */
(function(){
  const lb=$('#lightbox'),img=$('img',lb),cap=$('figcaption',lb);
  const pics=$$('.g-grid img,.ach img,.t-img img,.ss-photos img,.feature > img,.about-img img,.zoom img,img.zoom');
  if(!pics.length) return;
  let i=0,lastFocus=null;
  const show=n=>{i=(n+pics.length)%pics.length;const p=pics[i];img.src=p.currentSrc||p.src;img.alt=p.alt;
    const fc=p.closest('figure')?.querySelector('figcaption');cap.textContent=fc?fc.textContent:p.alt};
  const open=n=>{lastFocus=document.activeElement;show(n);lb.classList.add('open');document.body.style.overflow='hidden';$('.lb-close',lb).focus()};
  const close=()=>{lb.classList.remove('open');document.body.style.overflow='';lastFocus&&lastFocus.focus()};
  pics.forEach((p,n)=>{p.setAttribute('data-zoom','');p.tabIndex=0;p.setAttribute('role','button');
    p.addEventListener('click',()=>open(n));p.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();open(n)}})});
  $('.lb-close',lb).onclick=close;$('.lb-prev',lb).onclick=()=>show(i-1);$('.lb-next',lb).onclick=()=>show(i+1);
  lb.addEventListener('click',e=>{if(e.target===lb)close()});
  document.addEventListener('keydown',e=>{
    if(e.key==='Escape'){if(lb.classList.contains('open'))close();else closeMenu()}
    if(!lb.classList.contains('open'))return;
    if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)});
  let x0=null;lb.addEventListener('touchstart',e=>{x0=e.touches[0].clientX},{passive:true});
  lb.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>50)show(i+(dx<0?1:-1));x0=null});
})();
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu()});

/* ---------- reveal on scroll + count-up numbers ---------- */
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12});
$$('.reveal').forEach(el=>io.observe(el));
const cio=new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting) return; const el=e.target,end=+el.dataset.count,plus=el.textContent.includes('+');let t0=null;
  const step=ts=>{t0=t0||ts;const p=Math.min((ts-t0)/1200,1);el.textContent=Math.round(end*(1-Math.pow(1-p,3)))+(plus?'+':'');if(p<1)requestAnimationFrame(step)};
  requestAnimationFrame(step);cio.unobserve(el);
}),{threshold:.6});
$$('[data-count]').forEach(el=>cio.observe(el));

/* ---------- forms: open the visitor's email app with the details filled in ----------
   Any <form data-mailto="Subject prefix"> works. There is no server, so nothing is stored. */
$$('form[data-mailto]').forEach(form=>form.addEventListener('submit',function(e){
  e.preventDefault();
  const f=new FormData(this),lines=[];let who='';
  for(const [k,v] of f.entries()){ if(!v) continue; const el=this.elements[k];
    const label=(el&&el.dataset&&el.dataset.label)||k; lines.push(`${label}: ${v}`); if(k==='name') who=v }
  const subject=`${this.dataset.mailto}${who?' – '+who:''}`;
  window.location.href='mailto:kalangaraiias@gmail.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(lines.join('\n'));
  const st=$('.form-status',this);
  if(st) st.textContent=msg('Your email app will open with the details filled in — just press send. Or call +91 70947 91551.',
    'உங்கள் மின்னஞ்சல் செயலி திறக்கும் — அனுப்பு என்பதை அழுத்தவும். அல்லது +91 70947 91551 எண்ணில் அழைக்கவும்.',
    'आपका ईमेल ऐप विवरण के साथ खुलेगा — बस भेजें दबाएँ। या +91 70947 91551 पर कॉल करें।');
}));
// pre-select an enquiry type from the URL, e.g. contact.html?type=CSR%20Partnership
(function(){const t=new URLSearchParams(location.search).get('type');if(t)pickInterest(t)})();

/* ---------- donate box: choose amount + programme, then pledge on WhatsApp or email ---------- */
(function(){
  const box=$('#donateBox'); if(!box) return;
  const amt=$('#donAmount',box),prog=$('#donProgramme',box);
  $$('.amounts button',box).forEach(b=>b.addEventListener('click',()=>{
    $$('.amounts button',box).forEach(x=>x.classList.toggle('active',x===b));amt.value=b.dataset.amount}));
  amt.addEventListener('input',()=>$$('.amounts button',box).forEach(x=>x.classList.toggle('active',x.dataset.amount===amt.value)));
  const text=()=>`Hello Kalangarai Trust, I would like to donate ₹${amt.value||'___'} towards: ${prog.value}. Please share the bank / UPI details and receipt process.`;
  $('#donWhatsapp',box).addEventListener('click',e=>{e.preventDefault();window.open('https://wa.me/917094791551?text='+encodeURIComponent(text()),'_blank','noopener')});
  $('#donEmail',box).addEventListener('click',e=>{e.preventDefault();
    location.href='mailto:kalangaraiias@gmail.com?subject='+encodeURIComponent('Donation pledge – ₹'+(amt.value||''))+'&body='+encodeURIComponent(text())});
  const p=new URLSearchParams(location.search).get('programme');
  if(p){const o=[...prog.options].find(o=>o.value===p);if(o)prog.value=p}
})();

/* ---------- gallery filter ---------- */
(function(){
  const bar=$('.filter-bar'); if(!bar) return;
  $$('button',bar).forEach(b=>b.addEventListener('click',()=>{
    $$('button',bar).forEach(x=>x.classList.toggle('active',x===b));
    const f=b.dataset.filter;$$('.masonry figure').forEach(fig=>fig.hidden=!(f==='all'||fig.dataset.cat===f))}));
})();

/* ---------- collapsible language picker ---------- */
(function(){const lf=$('#langFloat'),t=$('#langToggle');if(!lf||!t)return;
  t.addEventListener('click',e=>{e.stopPropagation();const o=lf.classList.toggle('open');t.setAttribute('aria-expanded',o)});
  document.addEventListener('click',e=>{if(!lf.contains(e.target)){lf.classList.remove('open');t.setAttribute('aria-expanded','false')}});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){lf.classList.remove('open');t.setAttribute('aria-expanded','false')}});
})();

/* ---------- auto-fit navigation: works at any screen size, zoom, scaling, language or font ---------- */
(function(){
  const header=$('header'),bar=$('.nav1'),menu=$('#navLinks'),logo=$('.nav1 .logo'),actions=$('.nav1 .nav-actions');
  if(!header||!bar||!menu) return;
  const small=window.matchMedia('(max-width:1023.98px)');
  // compare the visible top-level items (not the hidden dropdown panels) with the logo and the Donate button
  const overflowing=()=>{
    const kids=[...menu.children].filter(k=>getComputedStyle(k).display!=='none');
    if(!kids.length) return false;
    const first=kids[0].getBoundingClientRect(),last=kids[kids.length-1].getBoundingClientRect();
    const l=logo.getBoundingClientRect(),a=actions.getBoundingClientRect(),m=menu.getBoundingClientRect();
    return first.left<l.right+12 || last.right>a.left-12 || kids.some(k=>k.getBoundingClientRect().top>first.top+first.height);
  };
  let busy=false;
  function fit(){
    if(busy) return; busy=true;
    header.classList.add('nav-measuring');
    header.classList.remove('nav-tight','nav-tight2','nav-collapsed');
    if(!small.matches && overflowing()){
      header.classList.add('nav-tight');
      if(overflowing()){header.classList.add('nav-tight2');
        if(overflowing()){header.classList.remove('nav-tight','nav-tight2');header.classList.add('nav-collapsed')}}
    }
    if(!header.classList.contains('nav-collapsed')&&!small.matches&&menu.classList.contains('open')) closeMenu();
    void header.offsetWidth; header.classList.remove('nav-measuring'); busy=false;
  }
  window.fitNav=fit;
  fit();
  let t; const later=()=>{clearTimeout(t);t=setTimeout(fit,60)};
  window.addEventListener('resize',later);
  if(window.ResizeObserver) new ResizeObserver(later).observe(document.documentElement);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(fit);
  window.addEventListener('load',fit);
  header.addEventListener('transitionend',e=>{if(e.target===bar)later()});
})();
