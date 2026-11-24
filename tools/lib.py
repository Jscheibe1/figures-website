import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
BL,MN,IC,WH,SK,PK,YL,GN="#2E6BFF","#0A0F2E","#EEF2FF","#FFFFFF","#8FB0FF","#FF2D87","#FFE14A","#16B364"
PD="#1A0A12"  # campaign dark
AB=TTFont('/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf')
INS=TTFont('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf')
SPARK="M50 0C52 30 70 48 100 50C70 52 52 70 50 100C48 70 30 52 0 50C30 48 48 30 50 0Z"
_n=[0]
def uid():
    _n[0]+=1; return f'g{_n[0]}'
def glyph(font,ch):
    gs=font.getGlyphSet(); name=font.getBestCmap()[ord(ch)]
    pen=SVGPathPen(gs); gs[name].draw(pen); return pen.getCommands(), gs[name].width
def text_path(font,text,size,fill,ls=0.0,x=0,y=0,anchor='start'):
    """outlined text; baseline at y; returns (svg, width)"""
    upm=font['head'].unitsPerEm; s=size/upm; out=[]; cx=0
    for i,ch in enumerate(text):
        if ch==' ':
            cx+=glyph(font,'n')[1]*0.5*s+ls; continue
        d,adv=glyph(font,ch)
        out.append(f'<path transform="translate({cx:.3f} 0) scale({s:.5f} {-s:.5f})" d="{d}"/>')
        cx+=adv*s+ls
    w=cx-ls
    ox={'start':x,'middle':x-w/2,'end':x-w}[anchor]
    return f'<g fill="{fill}" transform="translate({ox:.3f} {y:.3f})">{"".join(out)}</g>', w
def text_arc(font,text,size,fill,cx,cy,r,ls,top=True):
    upm=font['head'].unitsPerEm; s=size/upm
    advs=[(glyph(font,'n')[1]*0.5 if ch==' ' else glyph(font,ch)[1])*s for ch in text]
    W=sum(advs)+ls*(len(text)-1); pos=-W/2; out=[]
    for ch,adv in zip(text,advs):
        mid=pos+adv/2; th=mid/r
        if ch!=' ':
            d,_=glyph(font,ch)
            if top: px,py,rot=cx+r*math.sin(th),cy-r*math.cos(th),math.degrees(th)
            else:   px,py,rot=cx+r*math.sin(th),cy+r*math.cos(th),-math.degrees(th)
            out.append(f'<path transform="translate({px:.3f} {py:.3f}) rotate({rot:.3f}) translate({-adv/2:.3f} 0) scale({s:.5f} {-s:.5f})" d="{d}"/>')
        pos+=adv+ls
    return f'<g fill="{fill}">{"".join(out)}</g>'
def lg(i,a,b,x2=0,y2=1): return f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
# fold palettes: stem-bottom, stem-top, arm-top a,b, arm-mid a,b, crease, flap
FP=dict(
 blue =("#1F4FE0","#2E6BFF","#2E6BFF","#6F9BFF","#6F9BFF","#A9C3FF","#0F2A8F","#1F4FE0"),   # on light grounds
 bright=("#2E6BFF","#4D82FF","#5B8CFF","#8FB0FF","#A9C3FF","#DCE6FF","#1B3FB5","#3D74F5"),  # on Midnight
 white=("#FFFFFF","#E6ECFF","#DCE4FF","#FFFFFF","#B9C7FF","#E6ECFF","#5B8CFF","#8FB0FF"),   # in the seal, on Midnight disc
 onblue=("#FFFFFF","#EEF2FF","#DCE6FF","#FFFFFF","#C5D4FF","#EEF2FF","#0A0F2E","#A9C3FF"),  # on Signal Blue
 pink =("#FFFFFF","#FFFFFF","#FFE14A","#FFE14A","#FFE14A","#FFEE8A","#E3B200","#FFC93A"),   # campaign
 black=("#000000",)*6+("#000000","#000000"), wht=("#FFFFFF",)*8, midnight=(MN,)*8,
 ghostblue=("#3A74FF","#3F78FF","#4680FF","#5B8CFF","#4680FF","#5B8CFF","#2459E0","#3A74FF"),
 ghostmid=("#111A47","#131D4D","#16215A","#1B2868","#16215A","#1B2868","#070B22","#111A47"),
 ghostpink=("#FF4795","#FF4F9A","#FF5CA2","#FF74B0","#FF5CA2","#FF74B0","#E01872","#FF4795"),
)
def fold(pal):
    u=uid(); s1,s2,t1,t2,m1,m2,d,fl=FP[pal] if isinstance(pal,str) else pal
    flat=len(set((s1,s2,t1,t2,m1,m2,d,fl)))==1
    if flat:
        return f'<g fill="{s1}"><polygon points="20,36 40,12 86,12 86,36 40,36 40,46 74,46 74,60 64,60 60,66 40,66 40,78 20,92"/></g>'
    return f'''<defs>{lg(u+'s',s2,s1)}{lg(u+'t',t1,t2,1,0)}{lg(u+'m',m1,m2,1,0)}</defs><polygon points="20,36 40,36 40,78 20,92" fill="url(#{u}s)"/><polygon points="20,36 40,12 40,36" fill="{d}"/><polygon points="40,12 86,12 66,36 40,36" fill="url(#{u}t)"/><polygon points="86,12 86,36 66,36" fill="{fl}"/><polygon points="20,66 40,46 40,66" fill="{d}" opacity=".85"/><polygon points="40,46 74,46 60,66 40,66" fill="url(#{u}m)"/><polygon points="40,46 54,46 40,62" fill="{d}" opacity=".28"/><polygon points="74,46 74,60 64,60" fill="{fl}" opacity=".9"/>'''
# fold bbox: x 20..86 (66), y 12..92 (80); centre (53,52)
def fold_at(pal,cx,cy,h):
    s=h/80; return f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate(-53 -52)">{fold(pal)}</g>'
def burst(n,ro,ri,cx=50,cy=50):
    return " ".join(f"{cx+(ro if i%2==0 else ri)*math.cos(math.pi*i/n-math.pi/2):.2f},{cy+(ro if i%2==0 else ri)*math.sin(math.pi*i/n-math.pi/2):.2f}" for i in range(n*2))
SEALS=dict(
 blue     =dict(a=BL,ink=MN,txt=WH,hard="#000000",fp='white'),
 bluelight=dict(a=BL,ink=MN,txt=WH,hard=MN,fp='white'),
 onblue   =dict(a=MN,ink=BL,txt=WH,hard="#1B49C9",fp='onblue'),
 pink     =dict(a=PK,ink=PD,txt=YL,hard="#000000",fp='pink'),
 pinklight=dict(a=PK,ink=PD,txt=YL,hard=PD,fp='pink'),
 onpink   =dict(a=PD,ink=PK,txt=YL,hard="#B3105A",fp='pink'),
 black    =dict(a="#000000",ink="#FFFFFF",txt="#FFFFFF",hard=None,fp='black'),
 white    =dict(a="#FFFFFF",ink="#000000",txt="#000000",hard=None,fp='wht'),
)
def seal(kind,rot=-8):
    """seal drawn in a 0..100 box (shadow reaches ~103)"""
    p=SEALS[kind]; a,ink,txt,hard=p['a'],p['ink'],p['txt'],p['hard']
    sh=f'<polygon points="{burst(24,48,42.5,52.5,52.5)}" fill="{hard}"/>' if hard else ''
    return f'''<g transform="rotate({rot} 50 50)">{sh}<polygon points="{burst(24,48,42.5)}" fill="{a}"/>
<circle cx="50" cy="50" r="38.5" fill="none" stroke="{txt}" stroke-width=".9"/><circle cx="50" cy="50" r="21.5" fill="{ink}"/><circle cx="50" cy="50" r="24" fill="none" stroke="{ink}" stroke-width=".9"/>
{text_arc(AB,"FIGURES",8.6,txt,50,50,27,.9,True)}{text_arc(AB,"PAID ON RESULTS",5.1,txt,50,50,34.8,.8,False)}
<g transform="translate(15.5 46.5) scale(.07)"><path d="{SPARK}" fill="{txt}"/></g><g transform="translate(77.5 46.5) scale(.07)"><path d="{SPARK}" fill="{txt}"/></g>
<g transform="translate(50 50) scale(.36) translate(-51 -54)">{fold(p['fp'])}</g></g>'''
def svgdoc(inner,vb,w=None,h=None):
    x,y,vw,vh=vb; w=w or vw; h=h or vh
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {vw} {vh}" width="{w}" height="{h}">{inner}</svg>'
# ---- composed marks: each returns (inner, viewBox)
def m_fold(pal,pad=10):
    return fold_at(pal,50,50,100-2*pad*1.0), (0,0,100,100)
def wordmark(fill,size=44):
    return text_path(AB,"FIGURES",size,fill,ls=size*.012)
def m_wordmark(fill):
    g,w=text_path(AB,"FIGURES",44,fill,ls=.5,x=8,y=8+44*.688)
    return g,(0,0,w+16,44*.688+16)
def m_horizontal(pal,fill,byline=False):
    capsz=50; cap=capsz*.688; H=100
    icon=fold_at(pal,10+33,50,80)
    g,w=text_path(AB,"FIGURES",capsz,fill,ls=.6,x=10+66+16,y=50+cap/2)
    extra=''
    return icon+g,(0,0,10+66+16+w+10,H)
def m_stacked(pal,fill,byline=True):
    capsz=30; cap=capsz*.688
    g,w=text_path(AB,"FIGURES",capsz,fill,ls=.4,x=0,y=0,anchor='middle')
    W=max(w,80)+24; cx=W/2
    icon=fold_at(pal,cx,12+40,80)
    g,_=text_path(AB,"FIGURES",capsz,fill,ls=.4,x=cx,y=12+80+14+cap,anchor='middle')
    H=12+80+14+cap+12; by=''
    if byline:
        b,_=text_path(INS,"BY SCHEIBE ADVISORY",6.2,fill,ls=1.0,x=cx,y=H+4,anchor='middle'); by=f'<g opacity=".7">{b}</g>'; H+=14
    return icon+g+by,(0,0,W,H)
def m_seal(kind):
    return seal(kind),(-3,-3,109,109)
def m_seal_lockup(kind,fill):
    capsz=44; cap=capsz*.688
    g,w=text_path(AB,"FIGURES",capsz,fill,ls=.5,x=112,y=50+cap/2)
    return seal(kind)+g,(-3,-3,112+w+12,109)
def m_compact(bg,pal):
    return f'<circle cx="50" cy="50" r="50" fill="{bg}"/>'+fold_at(pal,50,50,58),(0,0,100,100)
