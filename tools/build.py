import os, sys, json, shutil, base64, html, re
from lib import *
from fontTools.ttLib import TTFont
from fontTools import subset
MODE=sys.argv[1] if len(sys.argv)>1 else 'deploy'
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/figures-website'
DOMAIN='https://wearefigures.com'   # bought 23 Nov 2026 on Squarespace Domains; apex is canonical
FORM_APPLY='https://formspree.io/f/meagpdkz'   # Formspree 'applications', added 23 Nov 2026
FORM_CONTACT='https://formspree.io/f/xoedpbwn'   # Formspree 'contact', added 23 Nov 2026
EMAIL='info@wearefigures.com'; PHONE='(310) 279-0405'; TEL='+13102790405'
IG='https://www.instagram.com/we.are.figures/'; IGH='@we.are.figures'   # Instagram, confirmed by Josh 23 Nov 2026
V='20261124e'
INDEXNOW='4532206c322440ee6a6be0a731770bee'   # IndexNow key; the file /<key>.txt is written at the site root
PREVIEW=MODE=='preview'
def U(slug):
    if PREVIEW: return ('index' if slug=='' else slug)+'.html'
    return '/'+slug
def A(path): return ('assets/' if PREVIEW else '/assets/')+path

# ---------- fonts
FD=os.path.join(OUT,'assets','fonts'); os.makedirs(FD,exist_ok=True)
SRC={'archivo-black':'/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf','inter-400':'/usr/share/fonts/opentype/inter/Inter-Regular.otf','inter-600':'/usr/share/fonts/opentype/inter/Inter-SemiBold.otf','inter-700':'/usr/share/fonts/opentype/inter/Inter-Bold.otf'}
for n,p in SRC.items():
    dst=f'{FD}/{n}.woff'
    if not os.path.exists(dst):
        o=subset.Options(); o.flavor='woff'; o.layout_features=['kern','liga','calt','tnum','case']; o.unicodes=list(range(0x20,0x7f))+list(range(0xa0,0x100))+[0x2013,0x2014,0x2018,0x2019,0x201c,0x201d,0x2022,0x2026,0x2192,0x2713]
        f=subset.load_font(p,o); s=subset.Subsetter(o); s.populate(unicodes=o.unicodes); s.subset(f); subset.save_font(f,dst,o)

# ---------- graphics
def facets(W,H,kind,ghost=True,gx=None):
    base,tints,gh={'blue':(BL,["#3D76FF","#2459E0","#4680FF","#1F4FE0"],'ghostblue'),'midnight':(MN,["#111A47","#0E1438","#16215A","#070B22"],'ghostmid'),'pink':(PK,["#FF4795","#F01A78","#FF5CA2","#E01872"],'ghostpink'),'ice':(IC,["#E0E8FF","#F6F8FF","#D5DFFF","#FFFFFF"],None)}[kind]
    k=24/20; o=[f'<rect width="{W}" height="{H}" fill="{base}"/>']
    for x0,wd,ti,op in [(-.10,.16,0,.55),(.22,.20,1,.5),(.58,.14,2,.6),(.80,.30,3,.45)]:
        xa=x0*W; xb=xa+wd*W; dx=H/k
        o.append(f'<polygon points="{xa+dx:.0f},0 {xb+dx:.0f},0 {xb:.0f},{H} {xa:.0f},{H}" fill="{tints[ti]}" opacity="{op}"/>')
    s=min(W,H)
    o.append(f'<polygon points="{W-.46*s:.0f},0 {W},0 {W},{.55*s:.0f}" fill="{tints[1]}" opacity=".55"/><polygon points="0,{H-.5*s:.0f} {.42*s:.0f},{H} 0,{H}" fill="{tints[3]}" opacity=".6"/>')
    if ghost and gh: o.append(f'<g opacity=".55">{fold_at(gh,gx if gx is not None else W-.16*s,H*.42,1.15*s)}</g>')
    return ''.join(o)
def BG(kind,W=1600,H=900,ghost=False,drift=False,gx=None):
    return f'<div class="bg" aria-hidden="true"{" data-drift" if drift else ""}><svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">{facets(W,H,kind,ghost,gx)}</svg></div>'
def fold_anim(pal):
    u=uid(); s1,s2,t1,t2,m1,m2,d,fl=FP[pal]
    return f'''<svg class="unfold" viewBox="14 6 78 92" role="img" aria-label="The Figures folded F"><defs>{lg(u+'s',s2,s1)}{lg(u+'t',t1,t2,1,0)}{lg(u+'m',m1,m2,1,0)}</defs><polygon class="p1" points="20,36 40,36 40,78 20,92" fill="url(#{u}s)"/><polygon class="p2" points="20,36 40,12 40,36" fill="{d}"/><polygon class="p3" points="40,12 86,12 66,36 40,36" fill="url(#{u}t)"/><polygon class="p4" points="86,12 86,36 66,36" fill="{fl}"/><polygon class="p5" points="20,66 40,46 40,66" fill="{d}" opacity=".85"/><polygon class="p6" points="40,46 74,46 60,66 40,66" fill="url(#{u}m)"/><polygon class="p7" points="40,46 54,46 40,62" fill="{d}" opacity=".28"/><polygon class="p8" points="74,46 74,60 64,60" fill="{fl}" opacity=".9"/></svg>'''
hz_i,hz_vb=m_horizontal('bright',WH)
SPRITE=f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="s-blue" viewBox="-3 -3 109 109">{seal('blue',0)}</symbol><symbol id="s-light" viewBox="-3 -3 109 109">{seal('bluelight',0)}</symbol><symbol id="s-onblue" viewBox="-3 -3 109 109">{seal('onblue',0)}</symbol><symbol id="logo" viewBox="{hz_vb[0]} {hz_vb[1]+6} {hz_vb[2]} {hz_vb[3]-12}">{hz_i}</symbol><symbol id="spark" viewBox="0 0 100 100"><path d="{SPARK}"/></symbol></svg>'''
def SEAL(k,cls='stamp',spin=True,tilt=-8):
    inner=f'<svg viewBox="-3 -3 109 109" aria-hidden="true"><use href="#s-{k}"/></svg>'
    if spin: return f'<div class="{cls}" aria-hidden="true"><div class="spin">{inner}</div></div>'
    return f'<div class="{cls}" aria-hidden="true" style="rotate:{tilt}deg">{inner}</div>'
LOGO='<svg viewBox="0 0 352.8 88" role="img" aria-label="Figures"><use href="#logo"/></svg>'
ARROW='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M4 12h16M13 5l7 7-7 7"/></svg>'
ARROWL='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M20 12H4M11 5l-7 7 7 7"/></svg>'
CHECK='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><path d="M4 12.5l5.5 5.5L20 7"/></svg>'
CROSS='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>'

SERVICES=[
 dict(slug='paid-ads',name='Paid ads',nav='Paid ads',pill='Most people start here',short='We build and run your campaigns on Meta, Google and TikTok. We judge them by what they sell, and so should you.',paid='A share of sales, a fee on ad spend, a flat fee or a mix',covers='We handle tracking, campaigns, creative testing and budget on Meta, Google and TikTok'),
 dict(slug='creative-direction',name='Creative direction',nav='Creative direction',short='We set the look and the ideas behind everything you post and launch, so your content, your ads and your page all feel like you. We\'ll even help set up the shoots.',paid='A project price or a monthly fee',covers='We set the look, come up with the concepts, set up and direct the shoots, and shape the ad creative'),
 dict(slug='branding-websites',name='Branding and websites',nav='Branding and websites',short="Don't have a logo or a website you're happy with? We design the brand and the guidelines, then build the site to match. You know the price before we start.",paid='A project price, quoted up front',covers='We design the logo, the colors and the brand guidelines, and we design and build the website'),
 dict(slug='content',name='Content',nav='Content',short='We help you create your content, from the ideas and the scripts to the edits, so you\'ve always got something worth posting and worth putting ad money behind. On some projects, we shoot it for you too.',paid='Usually a flat monthly fee',covers='We help with the ideas, the scripts, the shoot plan, the edits and the ad cuts, and on some projects we shoot it too'),
 dict(slug='social-media-management',name='Social management',nav='Social management',short='We handle the posting, the captions, the comments and the calendar every week, so your accounts never go quiet.',paid='Usually a flat monthly fee',covers='We run the calendar, the posting, the captions and the comments, and review it with you every month'),
 dict(slug='strategy-reporting',name='Strategy and reporting',nav='Strategy and reporting',short='You get one plan for what you sell, one set of numbers, and a straight answer on what the work brought in.',paid='Usually part of other work, or quoted on its own',covers='We review your offer and your funnel, write the plan, set up tracking and show you the numbers'),
]
STEPS=[('Apply','It takes about two minutes. We ask what you sell, where you sell it and what you want help with.'),
       ('A 15-minute call','We go through what you sell together and tell you straight whether we can help.'),
       ('The plan, in writing','You get the plan, the terms and how sales will be counted before you agree to anything.'),
       ('We get to work','We set up tracking, make the first round of work, put it live and send you the first numbers.')]
def steps_html(): return '<div class="steps">'+''.join(f'<div class="step"><b>{i+1:02d}</b><h3>{t}</h3><p>{p}</p></div>' for i,(t,p) in enumerate(STEPS))+'</div>'
def cta(h='Tell us what you sell.',p='The application takes about two minutes. If it looks like a fit, the next step is a 15-minute call.',btn='Start the application'):
    return f'''<section class="band blue cta">{BG('blue',1600,700,True)}{SEAL('onblue')}<div class="wrap"><h2>{h}</h2><p>{p}</p><a class="btn white" href="{U('apply')}">{btn}</a></div></section>'''

# ---------- chrome
MENU_MAIN=[('', 'Home'),('services','Services'),('about','About'),('faq','FAQ'),('contact','Contact'),('apply','Apply')]
def header(cur,solid):
    main=''.join(f'<a style="--i:{i}" href="{U(s)}"{" aria-current=\"page\"" if s==cur else ""}>{n}</a>' for i,(s,n) in enumerate(MENU_MAIN[1:]))
    svc=''.join(f'<li><a href="{U(s["slug"])}"{" aria-current=\"page\"" if s["slug"]==cur else ""}>{s["nav"]}</a></li>' for s in SERVICES)
    return f'''<a class="skip" href="#main">Skip to content</a>{SPRITE}
<header class="site-head{' is-solid' if solid else ''}"{' data-solid' if solid else ''}><div class="wrap"><a class="brand" href="{U('')}" aria-label="Figures home">{LOGO}</a><div class="head-right"><a class="head-apply" href="{U('apply')}">Apply</a><button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><i></i><span>Menu</span></button></div></div></header>
<div class="menu" id="menu">{BG('midnight',1600,1000,False)}<div class="wrap menu-grid"><nav class="menu-main" aria-label="Main">{main}</nav><div class="menu-side"><div><h2>SERVICES</h2><ul>{svc}</ul></div><div><h2>GET IN TOUCH</h2><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="tel:{TEL}">{PHONE}</a></li><li><a href="{IG}" rel="noopener">Instagram</a></li><li><span>Los Angeles</span></li></ul></div></div></div></div>'''
def footer():
    svc=''.join(f'<li><a href="{U(s["slug"])}">{s["nav"]}</a></li>' for s in SERVICES)
    return f'''<footer class="site-foot"><div class="ghost" aria-hidden="true"><svg viewBox="14 6 78 92">{fold('ghostmid')}</svg></div><div class="wrap"><div class="foot-grid">
<div class="foot-brand"><a href="{U('')}" aria-label="Figures home">{LOGO}</a><p>Figures is a digital marketing agency in Los Angeles for creators with something to sell. We do paid ads, creative direction, branding and websites, content, social management and strategy.</p></div>
<div class="foot-col"><h2>SERVICES</h2><ul>{svc}<li><a href="{U('services')}">All services</a></li></ul></div>
<div class="foot-col"><h2>FIGURES</h2><ul><li><a href="{U('about')}">About</a></li><li><a href="{U('faq')}">FAQ</a></li><li><a href="{U('apply')}">Apply</a></li><li><a href="{U('contact')}">Contact</a></li></ul></div>
<div class="foot-col"><h2>GET IN TOUCH</h2><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="tel:{TEL}">{PHONE}</a></li><li><a href="{IG}" rel="noopener" aria-label="Figures on Instagram, {IGH}">Instagram</a></li><li>Los Angeles</li></ul></div></div>
<div class="foot-base"><span>&copy; 2026 Figures. A division of <a href="https://www.scheibeadvisory.com/" rel="noopener">Scheibe Advisory LLC</a>.</span><nav aria-label="Legal"><a href="{U('privacy')}">Privacy</a><a href="{U('terms')}">Terms</a><a href="{U('accessibility')}">Accessibility</a></nav></div></div></footer>'''
def page_head(h1,lede,crumbs=None,extra=''):
    c=''
    if crumbs: c='<nav class="crumbs" aria-label="Breadcrumb">'+'<span>/</span>'.join(f'<a href="{U(s)}">{n}</a>' if s is not None else n for s,n in crumbs)+'</nav>'
    return f'''<section class="page-head">{BG('midnight',1600,800,True)}<div class="wrap">{c}<h1>{h1}</h1><p>{lede}</p>{extra}</div></section>'''

# ---------- structured data
ORG={"@type":["Organization","ProfessionalService"],"@id":DOMAIN+"/#organization","name":"Figures","alternateName":"Figures Agency","url":DOMAIN+"/","slogan":"We grow when you do.","description":"Figures is a digital marketing agency in Los Angeles for creators with something to sell: paid ads, creative direction, branding and websites, content, social media management, and strategy and reporting.","logo":{"@type":"ImageObject","@id":DOMAIN+"/#logo","url":DOMAIN+"/assets/logo-512.png","width":512,"height":512},"image":DOMAIN+"/assets/og-image.png","email":EMAIL,"telephone":TEL,"address":{"@type":"PostalAddress","addressLocality":"Los Angeles","addressRegion":"CA","addressCountry":"US"},"areaServed":{"@type":"Country","name":"United States"},"sameAs":[IG],"parentOrganization":{"@type":"Organization","name":"Scheibe Advisory LLC","url":"https://www.scheibeadvisory.com/"},"contactPoint":{"@type":"ContactPoint","contactType":"customer service","email":EMAIL,"telephone":TEL,"availableLanguage":"English"},"knowsAbout":["Digital marketing","Paid social advertising","Meta ads","Google Ads","TikTok ads","Creator marketing","Creative direction","Brand identity","Logo design","Website design","Content creation","Video editing","Social media management","Performance marketing","Performance-based marketing","Revenue share marketing","Creator economy"]}
SITE={"@type":"WebSite","@id":DOMAIN+"/#website","url":DOMAIN+"/","name":"Figures","publisher":{"@id":DOMAIN+"/#organization"},"inLanguage":"en-US"}
def graph(p):
    url=DOMAIN+'/'+p['slug']; g=[ORG,SITE]
    wp={"@type":p.get('ptype','WebPage'),"@id":url+"#webpage","url":url,"name":p['title'],"description":p['desc'],"isPartOf":{"@id":DOMAIN+"/#website"},"about":{"@id":DOMAIN+"/#organization"},"inLanguage":"en-US","primaryImageOfPage":{"@type":"ImageObject","url":DOMAIN+"/assets/"+p['og']}}
    g.append(wp)
    if p['slug']:
        items=[{"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"}]
        if p.get('parent'): items.append({"@type":"ListItem","position":2,"name":"Services","item":DOMAIN+"/services"})
        items.append({"@type":"ListItem","position":len(items)+1,"name":p['crumb'],"item":url})
        g.append({"@type":"BreadcrumbList","@id":url+"#breadcrumb","itemListElement":items})
    g+=p.get('schema',[])
    return json.dumps({"@context":"https://schema.org","@graph":g},separators=(',',':'),ensure_ascii=False)

CSS=open('site.css').read(); JS=open('site.js').read()
def _widow(m):
    text,tag=m.group(1),m.group(2); parts=text.rstrip().split(' ')
    if len(parts)<5: return m.group(0)
    n=3 if len(parts[-1].strip('.,?!"\''))<=3 else 2
    while n>=2 and len(' '.join(parts[-n:]))>24: n-=1
    if n<2: return m.group(0)
    return '>'+' '.join(parts[:-n])+' '+'&nbsp;'.join(parts[-n:])+'</'+tag+'>'
def no_widows(h):
    """never leave one short word alone on the last line of a paragraph"""
    return re.sub(r'>([^<>]{28,})</(p|dd|li|span)>',_widow,h)
def render(p):
    assert len(p['desc'])<=160,(p['slug'],len(p['desc']))
    url=DOMAIN+'/'+p['slug']; t=html.escape(p['title']); dsc=html.escape(p['desc'])
    p['body']=re.sub(r'(<div class="body"><p>)([^<]*?[.?!]) ([^<]+?</p>)',r'\1\2</p><p>\3',p['body'])
    p['body']=no_widows(p['body'])
    body=header(p['slug'],p['slug']!='' )+('<main id="main">'+p['body']+'</main>'+footer()).replace('15-minute','<span class="nw">15-minute</span>')
    if PREVIEW:
        css=CSS
        for n in SRC: css=css.replace(f'url("__F__{n}.woff")','url(data:font/woff;base64,'+base64.b64encode(open(f'{FD}/{n}.woff','rb').read()).decode()+')')
        inner=f'<title>{t}</title><meta name="claude:viewport-fit-sides" content="cover"><style>{css}{p.get("css","")}</style><script>document.documentElement.classList.add("js")</script>{body}<script>{JS}</script>'
        if p['slug']=='': return inner
        return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{inner.split("<script>document",1)[0]}</head><body><script>document{inner.split("<script>document",1)[1]}</body></html>'
    robots='noindex' if p.get('noindex') else 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'
    canon='' if p.get('noindex') else f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="en-us" href="{url}">\n<link rel="alternate" hreflang="x-default" href="{url}">\n'
    ld='' if p.get('noindex') else f'<script type="application/ld+json">{graph(p)}</script>\n'
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{dsc}">
{canon}<meta name="robots" content="{robots}">
<meta name="theme-color" content="#0A0F2E">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/assets/site.webmanifest">
<link rel="preload" href="/assets/fonts/archivo-black.woff" as="font" type="font/woff" crossorigin>
<link rel="preload" href="/assets/fonts/inter-400.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={V}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Figures">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{dsc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/assets/{p['og']}">
<meta property="og:image:secure_url" content="{DOMAIN}/assets/{p['og']}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(p['ogalt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{dsc}">
<meta name="twitter:image" content="{DOMAIN}/assets/{p['og']}">
<meta name="twitter:image:alt" content="{html.escape(p['ogalt'])}">
{ld}<script>document.documentElement.className='js'</script>
{('<style>'+p['css']+'</style>') if p.get('css') else ''}
</head>
<body>
{body}
<script src="/assets/site.js?v={V}" defer></script>
</body>
</html>
'''

# ================= PAGES =================
P=[]
# ---- HOME
rows=''.join(f'<a class="row" href="{U(s["slug"])}"><h3>{s["name"]}{"<span class=pill>"+s["pill"]+"</span>" if s.get("pill") else ""}</h3><p>{s["short"]}</p><span class="go">{ARROW}</span></a>' for s in SERVICES)
tick=''.join(f'<span>{w}<svg viewBox="0 0 100 100"><use href="#spark"/></svg></span>' for w in ['Paid ads','Creative direction','Branding and websites','Content','Social management','Strategy and reporting','Paid on results','Los Angeles'])
WHO=[('Product creators','c-blue','blue','Your own merch, physical products or digital downloads.','The sales the ads generate.'),
     ('Affiliate marketers','','midnight','Other brands\' products, for a commission.','The commissions the ads generate.'),
     ('Subscription creators','c-ice','ice','Memberships, paid communities and subscriber platforms.','New subscriber revenue from the ads.'),
     ('Service providers','','midnight','Coaching, courses, bookings and client work.','Booked revenue from the leads we bring in.'),
     ('Not sure which one you are?','c-blue','blue','Plenty of people sell two or three of these at once.','Tell us on the application and we\'ll work it out on the call.')]
cards=''.join(f'<article class="card {c}"><div class="bg" aria-hidden="true"><svg viewBox="0 0 380 460" preserveAspectRatio="xMidYMid slice">{facets(380,460,k,k!="ice",300)}</svg></div><h3>{t}</h3><dl><div><dt>{"You sell" if i<4 else "That's normal"}</dt><dd>{a}</dd></div><div><dt>{"The result we go after" if i<4 else "What to do"}</dt><dd>{b}</dd></div></dl></article>' for i,(t,c,k,a,b) in enumerate(WHO))
FIT=[('You have something to sell today.','A product, an offer, a membership or a service that is live right now.'),
     ('The sale can be tracked.','There\'s a store, a link, a checkout or a booking page we can measure.'),
     ('There\'s room in the price.','After the cost of the ads, each sale still leaves you a profit.'),
     ('People already buy it.','It\'s already selling, so we\'re growing something real.')]
fit=''.join(f'<label class="fit-item"><input type="checkbox"><span class="box">{CHECK}</span><span><b>{a}</b><span>{b}</span></span></label>' for a,b in FIT)
home=f'''<section class="hero">{BG('midnight',1600,1000,False,True)}<div class="wrap hero-grid">
<div class="hero-copy"><h1><span>We grow</span><span class="hi">when you do.</span></h1>
<p>Figures is a digital marketing agency in Los Angeles for creators with something to sell. We run your ads, help you create your content and manage your accounts. How we get paid is set up around your business, and you see it in writing before you agree to anything.</p>
<div class="cta-row"><a class="btn" href="{U('apply')}">Apply to work with us</a><a class="tlink" href="#pay">See how we get paid</a></div></div>
<div class="hero-mark"><div class="f">{fold_anim('bright')}</div>{SEAL('blue').replace('class="spin"','class="spin" data-spin="exit"')}</div></div></section>
<div class="ticker" aria-hidden="true"><div class="ticker-track">{tick*4}</div></div>
<section class="band white" id="services"><div class="wrap"><div class="band-head"><h2>What we do</h2><p>We do six things. Hire us for one of them or hand over all six.</p></div><div class="ledger">{rows}</div><p class="foot-line">Not sure which one you need? <a class="tlink" href="{U('services')}">See how they fit together.</a></p></div></section>
<section class="band ice" id="pay"><div class="wrap"><div class="band-head"><h2>How we get paid</h2><p>There isn\'t one price list. We set the deal up around what you sell and how you sell it.</p></div>
<div class="pay" data-stamp><div class="deal usual"><h3>Ways we set it up</h3><ul><li><i class="tick">{CHECK}</i><span>A share of the sales your ads generate.</span></li><li><i class="tick">{CHECK}</i><span>A fee based on your ad spend.</span></li><li><i class="tick">{CHECK}</i><span>A flat monthly fee, a project price, or a mix of these.</span></li></ul></div>
<div class="deal ours">{SEAL('light','stamp',False,10)}<h3>What stays the same</h3><ul><li><i class="tick">{CHECK}</i><span>You see the terms in writing before you agree to anything.</span></li><li><i class="tick">{CHECK}</i><span>Where it fits, part of what we earn is tied to your sales.</span></li><li><i class="tick">{CHECK}</i><span>We report on what you sold.</span></li></ul></div></div>
<div class="facts"><div><b>Your ad budget stays yours</b><p>Ad spend goes from your card straight to the platform. We never hold it.</p></div><div><b>We agree on the terms first</b><p>Before anything launches, we put in writing what you pay and how a sale gets counted, so we\'re both reading the same number.</p></div><div><b>No promises we can\'t keep</b><p>Nobody can guarantee what an ad will do. We show you what happened and what we\'re changing.</p></div></div></div></section>
<section class="band mid" id="who">{BG('midnight',1600,900)}<div class="wrap"><div class="band-head"><h2>Who we work with</h2><p>You already have an audience and something they can buy. That second part matters, because ads only work when there\'s something to sell.</p></div>
<div class="swipe-wrap"><div class="swipe" tabindex="0" aria-label="Who we work with, swipe or use the arrow keys">{cards}</div><div class="swipe-ui"><div class="swipe-bar"><i></i></div><button class="prev" type="button" aria-label="Previous">{ARROWL}</button><button class="next" type="button" aria-label="Next">{ARROW}</button></div></div></div></section>
<section class="band white" id="fit"><div class="wrap"><div class="band-head"><h2>Four things we check</h2><p>Before we run ads for anyone, we go through this list on the call. Run it on yourself first.</p></div>
<div class="fit"><div class="fit-list">{fit}</div><div class="fit-out"><div class="fit-seal"><div class="ghost"><svg viewBox="-3 -3 109 109" aria-hidden="true"><use href="#s-light"/></svg></div><div class="live"><svg viewBox="-3 -3 109 109" aria-hidden="true"><use href="#s-light"/></svg></div></div><div class="fit-meter" aria-hidden="true"><i></i><i></i><i></i><i></i></div><p class="fit-msg" aria-live="polite">All four true? Then we should talk.</p><a class="btn fit-cta" href="{U('apply')}">Apply to work with us</a></div></div></div></section>
<section class="band ice" id="start"><div class="wrap"><div class="band-head"><h2>How it starts</h2><p>There\'s no pitch deck and no long onboarding. It goes like this.</p></div>{steps_html()}</div></section>
{cta()}'''
P.append(dict(slug='',title='Figures | Digital Marketing Agency for Creators, Los Angeles',desc='Figures is a digital marketing agency in Los Angeles for creators with something to sell. Paid ads, content, branding and social, all judged by what you sold.',og='og-image.png',ogalt='Figures. We grow when you do.',body=home,
 schema=[{"@type":"OfferCatalog","@id":DOMAIN+"/#services","name":"Figures services","itemListElement":[{"@type":"Offer","itemOffered":{"@type":"Service","name":s['name'],"url":DOMAIN+'/'+s['slug'],"provider":{"@id":DOMAIN+"/#organization"}}} for s in SERVICES]}]))

# ---- SERVICE PAGES
def others(cur):
    return '<section class="band ice"><div class="wrap"><div class="band-head"><h2>The other five</h2></div><div class="others">'+''.join(f'<a class="other" href="{U(s["slug"])}"><h3>{s["name"]}</h3><span>{s["covers"]}.</span></a>' for s in SERVICES if s['slug']!=cur)+'</div></div></section>'
def svc_page(slug,title,desc,h1,lede,ih,ip,inc,ph,pp,alt,stype,ctah=None):
    s=[x for x in SERVICES if x['slug']==slug][0]
    body=page_head(h1,lede,[('', 'Home'),('services','Services'),(None,s['name'])],f'<div class="cta-row"><a class="btn" href="{U("apply")}">Apply to work with us</a></div>')+f'''
<section class="band white"><div class="wrap two"><h2>{ih}</h2><div class="body">{''.join(f'<p>{x}</p>' for x in ip)}</div></div></section>
<section class="band white" style="padding-top:0"><div class="wrap"><div class="band-head"><h2>What is included</h2></div><div class="list">{''.join(f'<div><h3>{a}</h3><p>{b}</p></div>' for a,b in inc)}</div></div></section>
<section class="band white" style="padding-top:0"><div class="wrap"><div class="panel">{BG('midnight',1200,500)}<div><h2>{ph}</h2>{''.join(f'<p>{x}</p>' for x in pp)}<p><a class="tlink" href="{U('faq')}">More on how we get paid</a></p></div>{SEAL('blue')}</div></div></section>
{others(slug)}{cta(*(ctah or ()))}'''
    P.append(dict(slug=slug,title=title,desc=desc,og=f'og-{slug}.png',ogalt=alt,body=body,parent=True,crumb=s['name'],
      schema=[{"@type":"Service","@id":DOMAIN+'/'+slug+"#service","name":stype,"serviceType":stype,"description":desc,"provider":{"@id":DOMAIN+"/#organization"},"areaServed":{"@type":"Country","name":"United States"},"audience":{"@type":"Audience","audienceType":"Creators and influencers with a product, offer, subscription or service to sell"},"url":DOMAIN+'/'+slug,"hasOfferCatalog":{"@type":"OfferCatalog","name":s['name']+": what is included","itemListElement":[{"@type":"Offer","itemOffered":{"@type":"Service","name":a,"description":b}} for a,b in inc]}}]))
svc_page('paid-ads','Paid Ads for Creators | Meta, Google and TikTok | Figures','Paid ads for creators on Meta, Google and TikTok. Figures builds and runs your campaigns, with pricing set around your business, performance-based included.',
 'Paid ads for creators.','We build your campaigns on Meta, Google and TikTok and run them every day. Judge us by what they sell.',
 'Why ads come first',['Ads are the quickest way to find out whether what you sell can grow. You learn what a customer costs, which videos pull, and whether the offer holds up with people who\'ve never heard of you.','It\'s also the easiest work to measure, which is why we\'re happy to tie what we earn to it.'],
 [('Tracking and setup','We check or build your pixels, conversion tracking and ad accounts, so every sale can be traced back to the ad it came from.'),('Campaigns','We build them on Meta, Google and TikTok, depending on where your buyers are.'),('Creative testing','We keep putting in new hooks, cuts and angles, and we turn off the ones that lose.'),('Budget','We move spend toward what\'s selling. It\'s your budget and your card, and you set the ceiling.'),('Reporting','You see what was spent, what came back and what we\'re changing next.')],
 'How ads are paid',["There isn't one fixed price for ads. Depending on what you sell, it can be a share of the sales the ads generate, a fee based on your ad spend, a flat monthly fee, or a mix.",'A share of sales is what people call performance-based, revenue share or commission-based marketing. We like working that way when it fits.','Whatever we agree goes in writing before launch. You pay the ad platforms directly, so your budget never passes through us.'],'Paid ads for creators on Meta, Google and TikTok.','Paid advertising management',ctah=('Got something that sells?','Then let\'s find out how far ads can take it. The application takes about two minutes.'))
svc_page('creative-direction','Creative Direction for Creators and Their Brands | Figures','Creative direction for creators: the look, the concepts and the art direction behind your content, launches and ads, so it all looks like one brand.',
 'Creative direction for creators.','We set the look, the concepts and the art direction behind your content, your launches and your ads, so all of it looks like it came from the same person.',
 'Decide the look once',['Most pages grow one post at a time, and after a while nothing matches. The product shots look one way, the ads look another, and the launch looks like a third person made it.','Creative direction is deciding what your brand looks and feels like before the camera comes out, then holding every shoot, edit and ad to it. It\'s what makes people know a post is yours before they see your name.'],
 [('Visual identity','We write down your colors, type, framing and editing style, so anyone who touches your content gets it right.'),('Concepts','We come up with the ideas for your launches, drops and campaigns, built around what you sell and who buys it.'),('Shoot direction','You get moodboards, shot lists and references before the shoot, and we direct on set when we shoot in Los Angeles.'),('Shoot setup','We even help set up the shoot itself, from finding the location and the crew to planning the day.'),('Ad creative','We decide the look of your ads on purpose, then test it so the numbers get a say.'),('Your page and your launches','We pull your grid, covers, thumbnails and launch assets into one consistent look.'),('Across industries','This isn\'t only for creators. Where it\'s needed, we set up shoots and direct creative for brands and businesses in other industries too.')],
 'How creative direction is paid',['Creative direction is quoted after the call. It can be a one-time project, like a launch or a new look, or part of a flat monthly fee alongside content.','If the work feeds ads we run for you, the ads are priced on their own.'],'Creative direction for creators.','Creative direction',ctah=('Show us what you are building.','Tell us about the brand, the launch or the shoot. The application takes about two minutes.'))
svc_page('branding-websites','Brand Identity, Logo and Website Design for Creators | Figures',"No logo or website you're happy with? Figures does brand identity and web design for creators: three logo options, brand guidelines and a site to match.",
 'Branding and websites for creators.',"Don't have a logo or a website yet? Or have both, and you're not happy with either? We design the brand, build the site to match, and tell you the price before we start.",
 'Starting fresh, or starting over',["You don't need anything to start. Maybe you haven't made a logo or a website yet. Maybe you have both, they were put together in an afternoon, and you're just not happy with them anymore.","Either way, it's the same one-time job. We design the brand, write down how to use it, and build a site people can buy from. It has a start and an end, so it isn't a monthly commitment."],
 [('Three logo directions','We design three different directions for your logo and walk you through each one. You pick the one that feels like you, and we refine it from there.'),('The full logo set',"You get the main logo, a stacked version and a small mark for profile pictures, so there's a version for every place it has to go."),('Colors and type',"We choose your colors and your typefaces, check that they're easy to read together, and give you the exact codes."),('A brand guidelines document','One document shows how all of it gets used, with what to do and what not to do. A designer, a printer or a manufacturer can get it right without calling you.'),('Every file, ready to use','You get a full brand kit: the logos in every format and color, profile pictures and covers sized for each platform, and templates for posts and ads.'),('Your website','We design it and build it, phone first. It gets the pages you need, a clear way to buy or apply, and your own words on it instead of filler.'),('Built to be found','The search basics are done properly from the first day: page titles, descriptions, share images and a site that loads fast.')],
 'How branding and websites are paid',['Branding and websites are priced per project. We quote the package after the call, and you know the full price before we start.','Packages are built around what you need. Take the brand on its own, the website on its own, or both together.'],'Branding and websites for creators.','Brand identity and website design',ctah=('Not happy with what you have?','Or starting from nothing? Tell us where you are and what you need. The application takes about two minutes.'))
svc_page('content','Content for Creators: Ideas, Scripts, Shoots and Edits | Figures','Figures helps creators make content that sells: ideas, scripts, shoot planning and edits, built for your feed first and then cut again for ads.',
 'Content you can sell with.','We help you create it, from the ideas and the scripts to the shoot plan and the edits. Everything\'s built for your feed first, then cut again for ads.',
 'Made to be used twice',['The usual problem isn\'t ideas, it\'s time. You know what works with your audience. There just isn\'t enough of you to plan it, shoot it, cut it and still run the business.','So we take the planning and the editing off your plate, and on some projects the shooting too. We build every piece to work twice: once as the post, and again as an ad with a hook, an offer and a reason to click.'],
 [('Ideas and scripts','You get a month of concepts built around what you sell, written the way you talk.'),('Shoots','Most of the time you film it and we plan it with you, with shot lists and direction. On some projects, we bring a production team and shoot it in Los Angeles.'),('Edits','Everything\'s cut, captioned and sized for each platform, and you approve it before anything goes out.'),('Ad cuts','We recut the best moments as ads, so your paid and your organic are pulling the same way.'),('A content bank','Everything gets filed and labeled, so nothing good gets used once and lost.')],
 'How content is paid',['Content usually runs on a flat monthly fee that we quote after the call, based on how much you need from us.','If you run ads with us too, this is what those ads are made from, and the ads are priced on their own.'],'Content help for creators: ideas, scripts, shoots and edits.','Content creation and editing',ctah=('Running out of things to post?','Tell us what you sell and how often you want to show up. The application takes about two minutes.'))
svc_page('social-media-management','Social Media Management for Creators | Figures','Social media management for creators. Figures handles the calendar, posting, captions and comments every week, so your accounts stay active while you work.',
 'Social media management for creators.','We handle the calendar, the posting, the captions and the comments every week, so your accounts stay active while you get on with everything else.',
 'It still sounds like you',['Handing over your accounts is a trust thing, and we get that. So we learn how you talk first, you approve the plan, and nothing goes out that you wouldn\'t have posted yourself.','The point isn\'t to post more for the sake of it. It\'s to keep the people who already follow you warm, so when you launch something or an ad reaches them, they already know who you are.'],
 [('The calendar','We plan a month ahead around your launches, your drops and whatever\'s going on in your world.'),('Posting','We schedule and publish on every account, at the times your audience is around.'),('Captions','We write them in your voice and send them to you first, until you trust us enough to stop checking.'),('Community','We answer the comments and the messages, and pass you the ones that need you.'),('The monthly review','Once a month we go through what grew, what fell flat and what we\'re doing differently.')],
 'How social is paid',['Social management usually runs on a flat monthly fee that we quote after the call, based on how many accounts and how often you post.','When there\'s a sale we can trace back to the work, we show you. That\'s the number we want to be judged on.'],'Social media management for creators.','Social media management',ctah=('Hand over the posting.','Tell us which accounts, and how much of it you want off your plate. The application takes about two minutes.'))
svc_page('strategy-reporting','Marketing Strategy and Reporting for Creators | Figures','Strategy and reporting for creators who sell. Figures reviews your offer and funnel, builds one plan, and reports on sales, cost and profit in plain words.',
 'A plan, and the numbers to check it.','This is strategy and reporting for creators who sell. We work out what to push, where to push it and whether it worked.',
 'Start with what sells',['Before any ads or content, we look at what you sell, what it costs you, who buys it and where they come from. A lot of the time the fix is in the offer or the checkout, not the marketing.','Then everything gets measured against one set of numbers that we both look at. We don\'t count reach, and we don\'t dress up impressions as progress. We count sales, cost and what\'s left.'],
 [('Offer review','We look at what you sell, what you charge and whether there\'s enough margin to advertise it.'),('Funnel check','We walk the path from your bio link to the thank-you page and fix the places people drop off.'),('The plan','You get one page that says what we\'re pushing, on which platforms and in what order.'),('Tracking','We set it up once and set it up properly, so the numbers aren\'t a guess.'),('The report','You see what was spent, what came back and what changes next, in plain words.')],
 'How strategy is paid',['Strategy and reporting usually come as part of the ads, content or social work we do together.','If a plan is the only thing you need, tell us on the application and we\'ll quote it after the call.'],'Strategy and reporting for creators who sell.','Marketing strategy and reporting',ctah=('Start with a plan.','Tell us what you sell and where it\'s stuck. The application takes about two minutes.'))

# ---- SERVICES OVERVIEW
mat=''.join(f'<a class="svc-row" href="{U(s["slug"])}"><h3>{s["name"]}</h3><p>{s["covers"]}.</p><span class="paid"><small>Paid by</small>{s["paid"]}.</span><span class="go">{ARROW}</span></a>' for s in SERVICES)
P.append(dict(slug='services',title='Services | Ads, Content and Social for Creators | Figures',desc='What Figures does for creators: paid ads, creative direction, branding and websites, content, social media management, and strategy and reporting.',og='og-services.png',ogalt='Figures services: ads, content, social and strategy.',crumb='Services',ptype='CollectionPage',
 body=page_head('Everything your socials need, from one team.','These six services work on their own, and they work better together. Most people start with ads and add the rest as the numbers come in.',[('', 'Home'),(None,'Services')])+f'''
<section class="band white"><div class="wrap"><div class="band-head"><h2>Side by side</h2></div><div class="svc-rows">{mat}</div></div></section>
<section class="band mid">{BG('midnight',1600,900,True)}<div class="wrap two"><h2>How they fit together</h2><div class="body"><p>Ads need content to run, and the content that works best in ads is usually the stuff that already did well on your page. So the two feed each other.</p><p>Social management keeps your audience warm between launches, which helps your ads because people already recognize you. The plan and the numbers sit over all of it, so nobody\'s guessing.</p><p>Creative direction is what makes all of it look like one brand, so the ad, the post and the launch feel like the same person.</p><p>Branding and websites sit underneath everything else. The logo is on every post, and the website is where your ads send people.</p><p>You don\'t have to take all six. Start with the one that hurts the most.</p></div></div></section>
<section class="band white"><div class="wrap"><div class="band-head"><h2>Three ways people start</h2></div><div class="list"><div><h3>Ads only</h3><p>You already make good content and you post it yourself. You want it in front of more buyers, and you want to know what it brought in.</p></div><div><h3>Ads and content</h3><p>You\'ve got something that sells, but not enough footage to keep the ads fresh. We help you make more of it, and we run it.</p></div><div><h3>The whole thing</h3><p>You\'d rather run the business and be on camera. We take the ads, the look, the content, the posting and the numbers.</p></div></div></div></section>
{cta('Start with one.','Tell us what you sell and what\'s taking too much of your time. We\'ll tell you where we\'d start.')}'''))

# ---- ABOUT
P.append(dict(slug='about',title='About Figures | A Digital Marketing Agency for Creators',desc='Figures is a digital marketing agency in Los Angeles built on one idea: judge us by what you sold, not what we posted. A division of Scheibe Advisory LLC.',og='og-about.png',ogalt='About Figures. Figures are the point.',crumb='About',ptype='AboutPage',
 body=page_head('Figures are the point.','We\'re a digital marketing agency in Los Angeles built on one idea. Judge us by what you sold, not by what we posted.',[('', 'Home'),(None,'About')])+f'''
<section class="band white"><div class="wrap two"><h2>What the name means</h2><div class="body"><p>The name means two things, and we meant both of them.</p><p>First, it's the numbers. Your sales, your subscribers and your commissions are how you find out if any of this is working.</p><p>It's also you. You're the public figure here, the one with the audience and something to sell to it.</p><p>We called it Figures so we couldn't hide from either one.</p></div></div></section>
<section class="band mid">{BG('midnight',1600,900,True)}<div class="wrap two"><h2>Why we set it up this way</h2><div class="body"><p>Most agency reports find something nice to say.</p><p>Reach was up, impressions were up, and you still can\'t tell whether any of it sold anything.</p><p>We didn\'t want to work like that. So we set up every deal around what you sell, we tie what we earn to your sales where it fits, and we judge all of our work by what you sold.</p></div></div></section>
<section class="band white"><div class="wrap"><div class="band-head"><h2>What we won\'t do</h2></div><div class="list"><div><h3>Guarantee a result</h3><p>Nobody honest can. We tell you what happened and what we\'re changing because of it.</p></div><div><h3>Sell you reach</h3><p>Views are nice. They don\'t pay you, so we don\'t count them as a result.</p></div><div><h3>Take on everyone</h3><p>If there\'s nothing to sell yet, we\'ll say so and tell you what to build first.</p></div><div><h3>Hide a bad month</h3><p>You see the same numbers we do, in the good months and the bad ones.</p></div></div></div></section>
<section class="band white" style="padding-top:0"><div class="wrap"><div class="panel blue">{BG('blue',1200,500)}<div><h2>Who\'s behind it</h2><p>Figures is a division of <a class="tlink" style="text-decoration-color:#fff" href="https://www.scheibeadvisory.com/" rel="noopener">Scheibe Advisory LLC</a>, a strategic advisory firm in Los Angeles.</p><p>Scheibe Advisory works with founders and companies on growth and partnerships. Figures is the part built for creators, with its own people for ads, content and social.</p></div>{SEAL('onblue')}</div></div></section>
{cta()}'''))

# ---- FAQ
FAQ=[('Getting started',[
 ('What is Figures?','Figures is a digital marketing agency in Los Angeles for creators with something to sell. We run paid ads, handle creative direction, design brands and websites, help create content, manage social accounts and report on what all of it produced.'),
 ('Who do you work with?','We work with creators who already have an audience and something that audience can buy. That covers people selling their own products, affiliate marketers, creators with subscriptions or memberships, and service providers like coaches.'),
 ('Do you only work with creators?','Mostly, yes. The exceptions are creative direction, shoot setup, and branding and websites. We also do those for brands and businesses in other industries when they need it.'),
 ('Do I need a certain number of followers?','No. Follower count matters less than whether people buy from you. A small audience that buys is a better fit than a big one that doesn\'t.'),
 ('What if I don\'t sell anything yet?','Then ads don\'t make sense yet, because there\'s nothing to sell. If a launch is close, apply anyway and tell us when. If it\'s further off, we\'ll tell you what we\'d build first.'),
 ('What happens after I apply?','We read every application ourselves and reply by email. If it looks like a fit, the next step is a 15-minute call where we go through what you sell and what you need.')]),
 ('Money',[
 ('How do you get paid?',"It depends on what you sell and what you need, so there isn't one price list. On ads, it can be a share of the sales the ads generate, a fee based on your ad spend, a flat monthly fee, or a mix. Content and social media usually run on a flat monthly fee. Branding and websites are priced per project. You see all of it in writing before you agree to anything."),
 ('What does "paid on results" actually mean?',"It means we want what we earn to move with what you sell. On ads, we set the deal up that way wherever it fits your business. On everything else, it means we measure the work by what you sold, and that's the number we expect to be judged on."),
 ('Is Figures a performance-based agency?',"We can be, and on ads we often are. You might hear it called performance-based, revenue share or commission-based marketing, where our fee is a share of the sales the ads generate. Whether that's the right setup for you depends on what you sell, and we work it out on the call."),
 ('Who pays for the ad spend?','You do, directly to Meta, Google or TikTok from your own card. We never hold your ad budget.'),
 ('How do you decide which sales came from the ads?','We agree on that in writing before anything launches. It\'s usually a mix of the platform\'s tracking and your own store or checkout data, and we both read the same number.'),
 ('Is there a minimum ad budget?','It depends on what you sell and what it costs. If the budget is too small to learn anything from, we\'ll tell you that on the call instead of taking the work.'),
 ('Do you guarantee results?','No, and you should be careful with anyone who does. What we can promise is that you\'ll see exactly what the work brought in.')]),
 ('Working together',[
 ('Which platforms do you run ads on?','Meta, which covers Instagram and Facebook, Google, which covers Search and YouTube, and TikTok. Where we start depends on where your buyers are.'),
 ('Can I hire you for just one thing?','Yes. Most people start with ads and add content or social later. A brand or website package also works on its own, and so does the plan.'),
 ("What if I don't have a logo or a website yet?","That's what the branding and website packages are for. We can start from nothing, or rework what you already have if you're not happy with it."),
 ('What comes in a branding package?','You get three logo directions to choose from, the full logo set, your colors and typefaces, a brand guidelines document, and a brand kit with every file sized and ready to use. A website can be added to the package or done on its own.'),
 ('Do I have to be in Los Angeles?','No. Most content is filmed by you, wherever you are, and we plan it with you. When we shoot it ourselves, that happens in Los Angeles. Everything else works from anywhere.'),
 ('Is live selling the same thing as what you do?','No. Live selling is selling on a live stream. We run ads, content and social for creators who already sell something, wherever they sell it.'),
 ('Who is behind Figures?','Figures is a division of Scheibe Advisory LLC, a strategic advisory firm in Los Angeles.')])]
FAQ[2]=(FAQ[2][0],[x for x in FAQ[2][1] if not x[0].startswith('Is live selling')])
FAQ_LINKS=[('We run paid ads','We run <a href="'+U('paid-ads')+'">paid ads</a>'),('handle creative direction','handle <a href="'+U('creative-direction')+'">creative direction</a>'),('design brands and websites','design <a href="'+U('branding-websites')+'">brands and websites</a>'),('help create content','help create <a href="'+U('content')+'">content</a>'),('manage social accounts','manage <a href="'+U('social-media-management')+'">social accounts</a>'),('report on what all of it produced','<a href="'+U('strategy-reporting')+'">report on what all of it produced</a>'),("That's what the branding and website packages are for","That's what the <a href=\""+U('branding-websites')+"\">branding and website packages</a> are for")]
def faq_link(a):
    for k,v in FAQ_LINKS:
        if k in a: a=a.replace(k,v,1)
    return a
faq_html=''.join(f'<div class="faq-group"><h2>{g}</h2>'+''.join(f'<details><summary>{q}<i aria-hidden="true"></i></summary><p>{faq_link(a)}</p></details>' for q,a in qs)+'</div>' for g,qs in FAQ)
P.append(dict(slug='faq',title='FAQ | How Figures Works and How We Get Paid',desc='Straight answers about Figures: who we work with, how pricing works, who pays for ad spend, and what happens after you apply.',og='og-faq.png',ogalt='Figures FAQ. How it works and how we get paid.',crumb='FAQ',ptype='FAQPage',
 body=page_head('Questions people ask us.','Most of them are about money, which is fair. If yours isn\'t here, email us and we\'ll answer it.',[('', 'Home'),(None,'FAQ')])+f'''<section class="band white"><div class="wrap" style="max-width:920px">{faq_html}</div></section>{cta('Still deciding?','The application is short, and applying doesn\'t commit you to anything.')}''',
 schema=[]))
P[-1]['faqs']=[(q,a) for g,qs in FAQ for q,a in qs]

# ---- APPLY
chip=lambda name,val,typ='radio',req='': f'<label class="chip"><input type="{typ}" name="{name}" value="{val}"{req}><span>{val}</span></label>'
TICK=f'<i class="tick">{CHECK}</i>'
P.append(dict(slug='apply',title='Apply | Work With Figures',desc='Apply to work with Figures in about two minutes. Tell us who you are, what you sell and which services you need. The next step is a 15-minute call.',og='og-apply.png',ogalt='Apply to work with Figures. It takes about two minutes.',crumb='Apply',
 body=f"""<section class="apply-hero">{BG('midnight',1600,1100,True)}<div class="wrap apply-grid">
<div class="a-head"><nav class="crumbs" aria-label="Breadcrumb"><a href="{U('')}">Home</a><span>/</span>Apply</nav><h1>Apply in about two minutes.</h1><p>It\'s three short steps and mostly taps. There\'s no pitch on the other end. We read it and we write back.</p></div>
<div class="form-card"><form data-form action="{FORM_APPLY}" method="POST" novalidate>
<input type="hidden" name="_subject" value="New Figures application"><p class="hp" aria-hidden="true"><label>Leave this empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
<div class="prog"><b>Step 1 of 3</b><div class="prog-bar"><i></i></div></div>
<fieldset class="fstep is-on"><legend>About you</legend>
<div class="frow"><div class="field"><label for="a-name">Your name</label><input id="a-name" name="name" type="text" autocomplete="name" required></div>
<div class="field"><label for="a-city">Where you are based <small>(optional)</small></label><input id="a-city" name="based_in" type="text" autocomplete="address-level2" placeholder="City"></div></div>
<div class="frow"><div class="field"><label for="a-email">Email</label><input id="a-email" name="email" type="email" autocomplete="email" required></div>
<div class="field"><label for="a-phone">Phone <small>(optional)</small></label><input id="a-phone" name="phone" type="tel" autocomplete="tel"></div></div>
<div class="field"><span class="lab">Best way to reach you</span><div class="chips g3">{chip('reach_by','Email','radio',' required')}{chip('reach_by','Call')}{chip('reach_by','Text')}</div></div></fieldset>
<fieldset class="fstep"><legend>Your pages and what you sell</legend>
<div class="field"><label for="a-link">Your main page</label><input id="a-link" name="main_profile" type="text" placeholder="instagram.com/you or tiktok.com/@you" autocapitalize="off" required></div>
<div class="field"><label for="a-other">Any other pages <small>(optional)</small></label><input id="a-other" name="other_profiles" type="text" placeholder="YouTube, a second account, your website" autocapitalize="off"></div>
<div class="field"><span class="lab">What do you sell?</span><div class="chips g2">{chip('sells','My own products','radio',' required')}{chip('sells','Affiliate offers')}{chip('sells','Subscriptions')}{chip('sells','Services')}{chip('sells','Nothing yet')}</div><p class="hint">That\'s fine to say. Ads only make sense once there\'s something to sell, but branding, content and a plan can start earlier. Keep going and tell us what you\'re planning in the last step.</p></div>
<div class="field"><label for="a-store">Where do people buy it? <small>(a link, optional)</small></label><input id="a-store" name="store_link" type="text" placeholder="yourstore.com" autocapitalize="off"></div></fieldset>
<fieldset class="fstep"><legend>What you need</legend>
<div class="field"><span class="lab">Which services are you after? <small>(pick any)</small></span><div class="chips g2" data-min="1" data-msg="Pick at least one service, or choose Not sure yet.">{chip('services','Paid ads','checkbox')}{chip('services','Creative direction','checkbox')}{chip('services','Branding','checkbox')}{chip('services','Website','checkbox')}{chip('services','Content','checkbox')}{chip('services','Social management','checkbox')}{chip('services','Strategy and reporting','checkbox')}{chip('services','Not sure yet','checkbox')}</div></div>
<div class="field"><span class="lab">When do you want to start?</span><div class="chips g2">{chip('start','Right away','radio',' required')}{chip('start','Within a month')}{chip('start','In a few months')}{chip('start','Just looking')}</div></div>
<div class="field"><label for="a-sales">Roughly what do your sales bring in a month? <small>(optional)</small></label><select id="a-sales" name="monthly_sales"><option value="" selected>Pick one</option><option>Under $5,000</option><option>$5,000 to $20,000</option><option>$20,000 to $50,000</option><option>$50,000 to $100,000</option><option>Over $100,000</option><option>I would rather say on the call</option></select></div>
<div class="field"><label for="a-more">Anything we should know? <small>(optional)</small></label><textarea id="a-more" name="notes" placeholder="What you are trying to get done, what you have tried, a launch date."></textarea></div>
<div class="field"><label for="a-heard">How did you hear about us? <small>(optional)</small></label><input id="a-heard" name="heard_from" type="text"></div></fieldset>
<p class="form-msg" role="alert"></p>
<div class="fnav"><button class="back" type="button">Back</button><span class="spacer"></span><button class="btn next" type="button">Next</button><button class="btn send" type="submit" hidden>Send application</button></div>
<p class="fine">We use what you send to reply to you and nothing else. See the <a href="{U('privacy')}">privacy policy</a>.</p></form>
<div class="form-done" role="status">{SEAL('light','stamp',False,-8)}<h2>Got it.</h2><p>We read every application ourselves and reply by email. If it looks like a fit, the next step is a 15-minute call.</p></div></div>
<div class="a-next"><h2>What happens next</h2><ul class="next-list"><li>{TICK}<span><b>We read it ourselves.</b><span class="d">You\'ll get a reply by email either way.</span></span></li><li>{TICK}<span><b>We get on a 15-minute call.</b><span class="d">If it looks like a fit, we go through what you sell and what you need.</span></span></li><li>{TICK}<span><b>You get a plan in writing.</b><span class="d">You see the plan and the terms before you agree to anything.</span></span></li></ul></div>
</div></section>
<section class="band ice"><div class="wrap"><div class="band-head"><h2>Rather talk first?</h2><p>That works too. Email or call, whichever is easier.</p></div><div class="reach"><div><span class="k">Email</span><a class="v" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy" type="button" data-copy="{EMAIL}">Copy</button></div><div><span class="k">Phone</span><a class="v" href="tel:{TEL}">{PHONE}</a><button class="copy" type="button" data-copy="{PHONE}">Copy</button></div></div></div></section>"""))

# ---- CONTACT
P.append(dict(slug='contact',title='Contact Figures | Los Angeles',desc='Contact Figures in Los Angeles. Email info@wearefigures.com or call (310) 279-0405. Want to work with us? The application takes two minutes.',og='og-contact.png',ogalt='Contact Figures in Los Angeles.',crumb='Contact',ptype='ContactPage',
 body=page_head('Talk to a person.','Email is the quickest way to reach us. If you want to work with us, the application is even quicker.',[('', 'Home'),(None,'Contact')],f'<div class="cta-row"><a class="btn" href="{U("apply")}">Go to the application</a></div>')+f'''
<section class="band white"><div class="wrap"><div class="reach"><div><span class="k">Email</span><a class="v" href="mailto:{EMAIL}">{EMAIL}</a><button class="copy" type="button" data-copy="{EMAIL}">Copy</button></div><div><span class="k">Phone</span><a class="v" href="tel:{TEL}">{PHONE}</a><button class="copy" type="button" data-copy="{PHONE}">Copy</button></div><div><span class="k">Based in</span><span class="v">Los Angeles</span><span></span></div></div></div></section>
<section class="band ice"><div class="wrap apply"><div><h2 style="font-size:clamp(1.9rem,4.4vw,3.2rem)">Or send a note.</h2><p style="margin-top:18px;color:var(--ink2);max-width:26rem">Use this for press, partnerships, a question about how we work, or anything that isn\'t an application.</p></div>
<div class="form-card"><form data-form action="{FORM_CONTACT}" method="POST"><input type="hidden" name="_subject" value="Figures contact form"><p class="hp" aria-hidden="true"><label>Leave this empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
<div class="field"><label for="c-name">Your name</label><input id="c-name" name="name" type="text" autocomplete="name" required></div><div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div><div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" required></textarea></div>
<p class="form-msg" role="alert"></p><div class="fnav"><span class="spacer"></span><button class="btn" type="submit">Send message</button></div></form><div class="form-done" role="status"><h2>Sent.</h2><p>Thanks. We\'ll reply by email.</p></div></div></div></section>'''))

# ---- LEGAL
def legal(slug,title,desc,h1,lede,body):
    P.append(dict(slug=slug,title=title,desc=desc,og='og-image.png',ogalt='Figures. We grow when you do.',crumb=h1.rstrip('.'),body=page_head(h1,lede,[('', 'Home'),(None,h1.rstrip('.'))])+f'<section class="band white"><div class="wrap"><div class="prose">{body}</div></div></section>'))
legal('privacy','Privacy Policy | Figures','How Figures, a division of Scheibe Advisory LLC, collects and uses information sent through wearefigures.com, including the application and contact forms.','Privacy.','What we collect on this site and what we do with it. Last updated November 23, 2026.',f"""
<p>Figures is a division of Scheibe Advisory LLC, a California limited liability company ("we", "us"). This policy covers this website, wearefigures.com. If you become a client, your agreement with us covers how we handle anything you share during the work.</p>
<h2>What we collect</h2><ul><li><b>The application form:</b> your name, email and the way you prefer to be reached. If you choose to give them: your phone number, where you are based, a monthly sales range, notes and how you heard about us. We also ask for your main social page and any other pages, what you sell, where people buy it, which services you are interested in and when you want to start.</li><li><b>The contact form:</b> your name, email and message.</li><li><b>Basic server logs:</b> our hosting provider records standard request data such as IP address and browser type to keep the site running and secure.</li></ul>
<h2>What we do not use</h2><p>This site sets no cookies and runs no analytics, advertising pixels or trackers. The fonts are served from this site, so no font provider sees your visit.</p>
<h2>How we use it</h2><p>We use what you send to review your application, reply to you and, if we work together, set up the engagement. We look at the public social pages you give us for the same reason. We do not sell your information, and we do not share it for anyone else's marketing.</p>
<h2>Calls and texts</h2><p>If you ask us to call or text, we use your number only to reply about your application. We do not send marketing texts.</p>
<h2>Who handles it for us</h2><p>Forms are processed by Formspree, the site is hosted by Vercel, and our email runs on Google Workspace. Each handles data on our behalf under its own terms.</p>
<h2>How long we keep it</h2><p>Applications that do not lead to an engagement are deleted within 12 months. Records for clients are kept as long as the engagement and our legal and tax obligations require.</p>
<h2>Your choices</h2><p>You can ask us what we hold about you, ask us to correct it or ask us to delete it by emailing <a href="mailto:{EMAIL}">{EMAIL}</a>. Depending on where you live, including California, the law may give you further rights, such as the right to know and the right to delete. We will not treat you differently for using them.</p>
<h2>Children</h2><p>This site is for adults running a business. We do not knowingly collect information from anyone under 18.</p>
<h2>Changes and contact</h2><p>If this policy changes, the date at the top changes with it. Questions go to <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE}.</p>""")
legal('terms','Terms of Use | Figures','Terms for using wearefigures.com. Figures is a division of Scheibe Advisory LLC. Client work is governed by a separate signed agreement.','Terms.','The rules for using this website. Last updated November 23, 2026.',f"""
<p>This website, wearefigures.com, is operated by Scheibe Advisory LLC, a California limited liability company ("we", "us"). Figures is a division of Scheibe Advisory LLC. By using the site you agree to these terms.</p>
<h2>What this site is</h2><p>The site describes our services and lets you apply to work with us. Nothing on it is an offer or a contract. Any work we do for a client is governed by a separate written agreement signed by both sides, and that agreement controls if it differs from anything here.</p>
<h2>What we offer</h2><p>We describe six services: paid ads, creative direction, branding and websites, content, social media management, and strategy and reporting. What is included for any client is set out in that client's agreement, not on this site.</p>
<h2>Fees</h2><p>How we are paid is described on this site in general terms and varies by client. It may include a share of the sales generated by advertising, a fee based on advertising spend, flat monthly fees, project prices or a combination of these. The actual fees and how sales are attributed are set out in each client's agreement. Clients pay advertising platforms directly for ad spend.</p>
<h2>No guarantee of results</h2><p>Advertising and social media results depend on many things outside our control. Nothing on this site is a promise or guarantee of sales, revenue, followers or any other outcome.</p>
<h2>Applying</h2><p>Sending an application does not create a client relationship and does not oblige either of us to work together. You must be 18 or older, and the information you send should be accurate. By applying, you agree that we can contact you about your application in the way you chose on the form.</p>
<h2>Our content</h2><p>The Figures name, logo, seal, text and design on this site belong to us. Please do not copy or reuse them without asking.</p>
<h2>Other platforms</h2><p>We mention Meta, Instagram, Facebook, Google, YouTube and TikTok because we run ads there. Those names belong to their owners, and we are not affiliated with or endorsed by any of them.</p>
<h2>Liability</h2><p>The site is provided as is. To the extent the law allows, we are not liable for losses that come from using the site or relying on its content.</p>
<h2>Changes, governing law and contact</h2><p>If these terms change, the date at the top changes with it. They are governed by California law. Questions go to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>""")
legal('accessibility','Accessibility | Figures','Figures aims to make wearefigures.com usable by everyone and works toward WCAG 2.2 AA. Tell us about any barrier and we will fix it.','Accessibility.','We want everyone to be able to use this site. Last updated November 23, 2026.',f"""
<p>We build this site to work toward the Web Content Accessibility Guidelines (WCAG) 2.2 at level AA.</p>
<h2>What we have done</h2><ul><li>Every page works with a keyboard, with a visible focus outline and a skip link to the main content.</li><li>The swipe rows can be moved with the arrow keys or the on-screen buttons, and the menu closes with the Escape key.</li><li>Body text and controls meet the AA contrast level. The measured pairs are on record with the site.</li><li>Headings, landmarks and form labels are marked up for screen readers, and form errors are announced.</li><li>Motion is switched off for visitors who have asked their device to reduce it. That covers the logo animation, the turning seal and the moving strip.</li><li>The application works without JavaScript. All three steps show on one page.</li><li>The layout holds from a small phone to a large screen, and text can be enlarged without breaking it.</li></ul>
<h2>What we know is not perfect</h2><p>The large blue line in the home page headline is decorative-sized display text and meets the contrast level for large text only. We have not yet had the site tested by people who use assistive technology every day.</p>
<h2>If something does not work</h2><p>Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE} and tell us which page and what happened. We will reply and fix it. If you cannot use the application form, we are glad to take your details by email or phone instead.</p>""")
# ---- 404
P.append(dict(slug='404',title='Page Not Found | Figures',desc='That page does not exist. Head back to the Figures home page, the services or the application.',og='og-image.png',ogalt='Figures',crumb='Not found',noindex=True,
 body=page_head('That page doesn\'t add up.','The link is broken or the page moved. These will get you back on track.',None,f'<div class="cta-row"><a class="btn" href="{U("")}">Go home</a><a class="tlink" href="{U("services")}">Services</a><a class="tlink" href="{U("apply")}">Apply</a></div>')))

# FAQ schema
for p in P:
    if p.get('faqs'): p['schema']=[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in p['faqs']]
def graph_faq(p):
    return p
# ================= WRITE =================
os.makedirs(OUT+'/assets',exist_ok=True)
for p in P:
    if p.get('faqs') and not PREVIEW:
        qs=p.pop('schema'); p['schema']=[]
        out=render(p); out=out.replace('"@type":"FAQPage"','"@type":"FAQPage","mainEntity":'+json.dumps(qs,separators=(',',':'),ensure_ascii=False))
    else:
        if p.get('faqs'): p['schema']=[]
        out=render(p)
    open(f'{OUT}/{p["slug"] or "index"}.html','w').write(out)
if not PREVIEW:
    open(OUT+'/assets/site.css','w').write(CSS.replace('__F__','/assets/fonts/'))
    open(OUT+'/assets/site.js','w').write(JS)
    pages=[p for p in P if not p.get('noindex')]
    sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'+''.join(f'  <url><loc>{DOMAIN}/{p["slug"]}</loc><lastmod>2026-11-23</lastmod><image:image><image:loc>{DOMAIN}/assets/{p["og"]}</image:loc></image:image></url>\n' for p in pages)+'</urlset>\n'
    open(OUT+'/sitemap.xml','w').write(sm)
    open(OUT+'/'+INDEXNOW+'.txt','w').write(INDEXNOW)
    open(OUT+'/robots.txt','w').write(f'User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n')
    open(OUT+'/llms.txt','w').write(f'''# Figures

> Figures is a digital marketing agency in Los Angeles for creators with something to sell. It runs paid ads on Meta, Google and TikTok, provides creative direction, designs brand identities and websites, helps creators plan, script and edit their content (and shoots it on some projects), manages social accounts, and provides strategy and reporting. Figures is a division of Scheibe Advisory LLC (California).

Facts worth getting right:
- Pricing is set per client and agreed in writing before work starts. On paid ads it can be a share of the sales the ads bring in (performance-based, also called revenue share), a fee based on ad spend, a flat monthly fee, or a mix.
- Content and social media management usually run on a flat monthly fee quoted after an introductory call. Creative direction is quoted per project or as part of a monthly fee. Branding and website packages (three logo directions, the full logo set, colors and type, a brand guidelines document, a brand kit of ready-to-use files, and a designed and built website) are priced per project and quoted before work starts. Strategy and reporting usually come as part of ads, content or social work, or are quoted on their own.
- Clients pay ad spend directly to the ad platforms. Figures does not hold client ad budgets.
- How sales are attributed is agreed in writing before any campaign launches.
- Figures does not guarantee results.
- Figures works with creators who already sell something: their own products, affiliate offers, subscriptions or memberships, or services such as coaching.
- The process is: a two-minute application, a 15-minute call, a written plan and terms, then launch.
- Contact: {EMAIL}, {PHONE}, Los Angeles. No street address is published. Instagram: {IG} ({IGH}).

## Pages
'''+''.join(f'- [{p["crumb"] if p["slug"] else "Home"}]({DOMAIN}/{p["slug"]}): {p["desc"]}\n' for p in pages))
    shutil.copy('vercel.json',OUT+'/vercel.json')
    json.dump({"name":"Figures","short_name":"Figures","start_url":"/","display":"browser","background_color":"#0A0F2E","theme_color":"#0A0F2E","icons":[{"src":"/assets/favicon-192.png","sizes":"192x192","type":"image/png"},{"src":"/assets/logo-512.png","sizes":"512x512","type":"image/png"}]},open(OUT+'/assets/site.webmanifest','w'),indent=1)
    # og + icon svgs for the renderer
    def og(headline,sub):
        o=[facets(1200,630,'midnight',True,1010)]
        o.append(f'<g transform="translate(70 62) scale(.62)">{m_horizontal("bright",WH)[0]}</g>')
        y=300 if len(headline)>1 else 350
        for j,t in enumerate(headline):
            sz=min(92,92*1000/max(1,text_path(AB,t,92,WH,ls=1)[1]))
            o.append(text_path(AB,t,sz,WH if j==0 or len(headline)==1 else BL,ls=1,x=70,y=y+j*92)[0])
        o.append(f'<g opacity=".9">{text_path(INS,sub,30,"#B9C4E8",x=70,y=560)[0]}</g>')
        o.append(f'<g transform="translate(905 345) scale(2.3)">{seal("blue",10)}</g>')
        return ''.join(o)
    OG={'og-image':(['WE GROW','WHEN YOU DO.'],'A digital marketing agency for creators.'),'og-paid-ads':(['PAID ADS','FOR CREATORS.'],'Built and run on Meta, Google and TikTok.'),'og-creative-direction':(['CREATIVE','DIRECTION.'],'The look and the concepts behind your content.'),'og-branding-websites':(['BRANDING','AND WEBSITES.'],'Logo, guidelines and a website to match.'),'og-content':(['CONTENT YOU','CAN SELL WITH.'],'Ideas, scripts, shoot plans and edits.'),'og-social-media-management':(['SOCIAL','MANAGEMENT.'],'The calendar, posting, captions and comments.'),'og-strategy-reporting':(['A PLAN, AND','THE NUMBERS.'],'Strategy and reporting for creators who sell.'),'og-services':(['ADS, CONTENT','AND SOCIAL.'],'Everything your socials need, from one team.'),'og-about':(['FIGURES ARE','THE POINT.'],'A creator agency judged by what you sold.'),'og-faq':(['QUESTIONS','PEOPLE ASK.'],'How Figures works and how we get paid.'),'og-apply':(['APPLY IN','TWO MINUTES.'],'Three short steps, then a 15-minute call.'),'og-contact':(['TALK TO','A PERSON.'],EMAIL+'   '+PHONE)}
    jobs=[dict(name=k+'.png',svg=og(*v),vb=[0,0,1200,630],w=1200,h=630,t=False) for k,v in OG.items()]
    ci,cvb=m_compact(BL,'onblue')
    open(OUT+'/assets/favicon.svg','w').write(svgdoc(ci,cvb,64,64))
    for n,s in [('favicon-32.png',32),('favicon-192.png',192)]: jobs.append(dict(name=n,svg=ci,vb=list(cvb),w=s,h=s,t=True))
    sq=f'<rect width="100" height="100" fill="{BL}"/>'+fold_at('onblue',50,50,58)
    for n,s in [('apple-touch-icon.png',180),('logo-512.png',512)]: jobs.append(dict(name=n,svg=sq,vb=[0,0,100,100],w=s,h=s,t=False))
    for nm,(i,vb) in {'logo-on-dark.svg':m_horizontal('bright',WH),'logo-on-light.svg':m_horizontal('blue',MN),'seal-blue.svg':m_seal('blue')}.items(): open(OUT+'/assets/'+nm,'w').write(svgdoc(i,vb))
    json.dump(jobs,open('imgjobs.json','w'))
print(MODE,len(P),'pages ->',OUT)
