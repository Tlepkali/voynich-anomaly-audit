import json, collections, math, sys, os
sys.path.insert(0,".")
N=4000
VOW={"lat":"aeiou","eng":"aeiou","it":"aeiou","de":"aeiouäöü","eu":"aeiou","fi":"aeiouäöy",
     "tr":"aeiouıöü","mn":"аэиоуүөяеёюы","ka":"აეიოუ","el":"αεηιουω","sa":"ािीुूेैोौृ",
     "ko":"".join(chr(c) for c in range(0x1161,0x1176)), "he":"", "ar":""}
FILES=[("lat","латынь (Плиний)","ref/latin.clean"),("eng","английский","ref/english.clean"),
       ("it","итальянский","ref/wiki_it.clean"),("de","немецкий","ref/wiki_de.clean"),
       ("el","греческий","ref/wiki_el.clean"),("he","иврит (абджад)","ref/wiki_he.clean"),
       ("ar","арабский (абджад)","ref/wiki_ar.clean"),("sa","санскрит","ref/wiki_sa.clean"),
       ("tr","турецкий","ref/wiki_tr.clean"),("ko","корейский (чамо)","ref/wiki_ko.clean"),
       ("mn","монгольский","ref/wiki_mn.clean"),("ka","грузинский","ref/wiki_ka.clean"),
       ("eu","баскский","ref/wiki_eu.clean"),("fi","финский","ref/wiki_fi.clean")]
def skeleton(w, v):
    if not v or len(w)<=3: return w
    core="".join(c for c in w[1:-1] if c not in v)
    return (w[0]+core+w[-1])[:7] or w
def trunc(w,k=4): return w[:k]
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return (same/exp if exp else 0)
def mi_pos(ws):
    j=collections.Counter()
    for w in ws:
        for i,c in enumerate(w):
            p="1" if len(w)==1 else ("b" if i==0 else ("e" if i==len(w)-1 else "m"))
            j[(c,p)]+=1
    T=sum(j.values()); pg=collections.Counter(); pp=collections.Counter()
    for (a,b),n in j.items(): pg[a]+=n; pp[b]+=n
    return sum(n/T*math.log2((n/T)/((pg[a]/T)*(pp[b]/T))) for (a,b),n in j.items())
def row(ws):
    w=ws[:N]; ty=collections.Counter(w)
    return (len(ty)/len(w), sum(len(x) for x in w)/len(w), mi_pos(w), rep(w))
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w][:N]
tv=row(VOY)
print("="*112)
print("ГИПОТЕЗА СОКРАЩЕНИЙ НА ЧЕТЫРНАДЦАТИ ЯЗЫКАХ")
print("="*112)
print("цель — TTR 0,393, слотовость 0,668;  «Δ» = насколько сократилось расстояние до цели\n")
print(f"  {'язык':20s} | {'исходно':^22s} | {'скелет согласных':^22s} | {'обрубание до 4':^22s}")
print(f"  {'':20s} | {'TTR':>7s} {'слотов.':>7s} {'ср.дл':>5s} | {'TTR':>7s} {'слотов.':>7s} {'ср.дл':>5s} | {'TTR':>7s} {'слотов.':>7s} {'ср.дл':>5s}")
print("  "+"-"*108)
res=[]
for code,lab,path in FILES:
    if not os.path.exists(path): continue
    ws=open(path).read().split()
    if len(ws)<N: continue
    v=VOW.get(code,"")
    a=row(ws); b=row([skeleton(w,v) for w in ws]); c=row([trunc(w) for w in ws])
    d0=abs(a[0]-tv[0])/tv[0]+abs(a[2]-tv[2])/tv[2]
    d1=abs(b[0]-tv[0])/tv[0]+abs(b[2]-tv[2])/tv[2]
    res.append((d1,lab,a,b,c,d0))
    print(f"  {lab:20s} | {a[0]:7.3f} {a[2]:7.3f} {a[1]:5.2f} | {b[0]:7.3f} {b[2]:7.3f} {b[1]:5.2f} | "
          f"{c[0]:7.3f} {c[2]:7.3f} {c[1]:5.2f}")
print("  "+"-"*108)
print(f"  {'РУКОПИСЬ':20s} | {tv[0]:7.3f} {tv[2]:7.3f} {tv[1]:5.2f} |")
print("\n  насколько скелет согласных приближает к рукописи (сумма отн. отклонений по TTR и слотовости):")
res.sort()
for d1,lab,a,b,c,d0 in res:
    mark=" ←" if d1<0.25 else ""
    print(f"     {lab:20s} было {d0:5.2f} → стало {d1:5.2f}   {'улучшение' if d1<d0 else 'ухудшение':10s}{mark}")
