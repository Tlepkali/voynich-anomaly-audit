import json, collections, math, random, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows,pages=D["rows"],D["pages"]
VL=[[w for w in r["words"] if '?' not in w] for r in rows if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
NW=4000
LENS=[]; tot=0
for l in VL:
    if tot>=NW: break
    LENS.append(len(l)); tot+=len(l)
NW=tot
print(f"общий размер выборки: {NW} слов, {len(LENS)} строк\n")
def cut(words):
    out=[];k=0
    for n in LENS:
        if k+n>len(words): return None
        out.append(words[k:k+n]); k+=n
    return out
CORP={}
CORP["Войнич"]=cut([w for l in VL for w in l])
CORP["латынь (Плиний)"]=cut(open("ref/latin.clean").read().split())
CORP["английский (проза)"]=cut(open("ref/english.clean").read().split())
for tag,lab in (("it","итальянский"),("de","немецкий"),("el","греческий"),("he","иврит"),("ar","арабский"),("sa","санскрит"),("tr","турецкий"),("ko","корейский (чамо)"),("mn","монгольский"),("ka","грузинский"),("eu","баскский"),("fi","финский")):
    try: CORP[lab]=cut(open(f"ref/wiki_{tag}.clean").read().split())
    except FileNotFoundError: pass
CORP={k:v for k,v in CORP.items() if v}
KEYS=[("mean_len","ср.длина"),("h1","h1"),("cv","CV длин"),("h2","h2"),
      ("mi_pos","слотовость"),("rep_ratio","повторы ×"),("ed1","отл. в 1 знак"),
      ("ttr","TTR"),("hapax","хапаксы"),("wh2","H(слово|пред)"),
      ("zipf","наклон Ципфа"),("line_div","эффект строки")]
def build(items, LINES, p_rep, p_mut, seed=1):
    rnd=random.Random(seed); s=" ".join(items)
    tr=collections.defaultdict(list)
    for i in range(len(s)-2): tr[s[i:i+2]].append(s[i+2])
    starts=[w[0] for w in items]
    al=collections.Counter(c for x in items for c in x); AK=list(al); AW=list(al.values())
    def fresh():
        cur=" "+rnd.choice(starts); buf=[cur[1]]
        for _ in range(40):
            nx=rnd.choice(tr.get(cur) or [" "])
            if nx==" ": break
            buf.append(nx); cur=cur[1]+nx
        return "".join(buf) or AK[0]
    def mut(w):
        if not w: return AK[0]
        i=rnd.randrange(len(w)); op=rnd.random(); ch=rnd.choices(AK,weights=AW)[0]
        if op<0.45: return w[:i]+ch+w[i+1:]
        if op<0.75: return w[:i]+ch+w[i:]
        return (w[:i]+w[i+1:]) or AK[0]
    fi=collections.Counter(l[0][0] for l in LINES); fk=list(fi); fw=[fi[x] for x in fk]
    out=[]; prev=None
    for n in [len(l) for l in LINES]:
        line=[]
        for j in range(n):
            if j==0:
                want=rnd.choices(fk,fw)[0]; w=None
                for _ in range(30):
                    c=fresh()
                    if c and c[0]==want: w=c; break
                w=w or fresh()
            elif prev and rnd.random()<p_rep: w=prev
            elif prev and rnd.random()<p_mut: w=mut(prev)
            else: w=fresh()
            line.append(w); prev=w
        out.append(line)
    return out
res={}
for lab,LINES in CORP.items():
    W=[w for l in LINES for w in l]
    T=metrics.all_metrics(W,LINES)
    best=None
    for pr in [0.0,0.004,0.012]:
        for pm in [0.0,0.03,0.09]:
            L=build(W,LINES,pr,pm); ws=[w for l in L for w in l]
            M=metrics.all_metrics(ws,L)
            e=abs(M['rep_ratio']-T['rep_ratio'])/max(T['rep_ratio'],1e-6)+abs(M['ed1']-T['ed1'])/max(T['ed1'],1e-6)
            if best is None or e<best[0]: best=(e,pr,pm,M)
    _,PR,PM,M=best
    hits=sum(1 for k,_ in KEYS if abs(M[k]-T[k])/max(abs(T[k]),1e-9)<=0.15)
    res[lab]=(T,M,hits,PR,PM)
    print(f"  {lab:22s} попаданий {hits:2d}/12   копирование p={PR}/{PM}")
json.dump({k:(v[0],v[1],v[2]) for k,v in res.items()}, open("multi.json","w"))
print("\n" + "="*96)
print("КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ: цель → модель (ошибка)")
print("="*96)
print(f"  {'язык':22s} {'TTR':>20s} {'хапаксы':>18s} {'повторы ×':>20s}")
for lab,(T,M,h,PR,PM) in sorted(res.items(), key=lambda kv: abs(kv[1][1]['ttr']-kv[1][0]['ttr'])/kv[1][0]['ttr']):
    e1=abs(M['ttr']-T['ttr'])/T['ttr']; e2=abs(M['hapax']-T['hapax'])/T['hapax']
    print(f"  {lab:22s} {T['ttr']:.3f}→{M['ttr']:.3f} ({e1:4.0%}) {T['hapax']:.3f}→{M['hapax']:.3f} ({e2:3.0%}) "
          f"{T['rep_ratio']:6.3f}→{M['rep_ratio']:5.3f}")
