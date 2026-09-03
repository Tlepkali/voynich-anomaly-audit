import json, collections, math, random, re, sys
sys.path.insert(0,"."); import metrics
def script(c):
    o=ord(c)
    if 0x3040<=o<=0x309F: return "хирагана"
    if 0x30A0<=o<=0x30FF: return "катакана"
    return "иероглиф"
def seg_ja(t):
    out=[]; cur=""; sc=None
    for c in t:
        if c==" ":
            if cur: out.append(cur); cur=""; sc=None
            continue
        s=script(c)
        if s!=sc and cur: out.append(cur); cur=""
        cur+=c; sc=s
    if cur: out.append(cur)
    return out
def seg_zh_pmi(t, target_len=1.6):
    txt=t.replace(" ","")
    uni=collections.Counter(txt); N=len(txt)
    bi=collections.Counter(zip(txt,txt[1:])); M=sum(bi.values())
    def pmi(a,b):
        p=bi[(a,b)]/M; 
        if p==0: return -20
        return math.log2(p/((uni[a]/N)*(uni[b]/N)))
    scores=sorted(pmi(a,b) for a,b in zip(txt,txt[1:]))
    # подбираем порог так, чтобы средняя длина слова вышла ~1.6
    lo,hi=0,len(scores)-1
    for _ in range(30):
        mid=(lo+hi)//2; th=scores[mid]
        cuts=sum(1 for a,b in zip(txt,txt[1:]) if pmi(a,b)<th)
        ml=len(txt)/max(1,cuts+1)
        if ml<target_len: lo=mid
        else: hi=mid
    th=scores[(lo+hi)//2]
    out=[]; cur=txt[0]
    for a,b in zip(txt,txt[1:]):
        if pmi(a,b)<th: out.append(cur); cur=b
        else: cur+=b
    out.append(cur)
    return out
def rep_ratio(words):
    ty=collections.Counter(words); T=len(words)
    same=sum(1 for a,b in zip(words,words[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return same, exp, (same/exp if exp else 0)
def stats(words, label, n=4000):
    w=words[:n]
    ty=collections.Counter(w)
    ln=[len(x) for x in w]; mu=sum(ln)/len(ln)
    s,e,r=rep_ratio(w)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {label:34s} токенов {len(w):5d}  ед./слово {mu:4.2f}  TTR {len(ty)/len(w):.3f}  "
          f"хапаксы {hap:.3f}  повторы {r:5.3f}× ({s} при ожид. {e:.1f})")
    return dict(ttr=len(ty)/len(w), hapax=hap, rep=r, mu=mu)
print("="*104)
print("КИТАЙСКИЙ И ЯПОНСКИЙ: то, что переносится без порождающей модели")
print("="*104)
ja=open("ref/wiki_ja.clean").read(); zh=open("ref/wiki_zh.clean").read()
R={}
R["японский (по границам письма)"]=stats(seg_ja(ja), "японский (по границам письма)")
R["китайский (сегментация по PMI)"]=stats(seg_zh_pmi(zh), "китайский (сегментация по PMI)")
R["китайский (по знакам)"]=stats(list(zh.replace(" ","")), "китайский (по знакам)")
print()
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
R["Войнич"]=stats(VOY,"Войнич")
for tag,lab in (("ar","арабский"),("he","иврит"),("sa","санскрит"),("it","итальянский")):
    try: R[lab]=stats(open(f"ref/wiki_{tag}.clean").read().split(), lab)
    except FileNotFoundError: pass
R["латынь"]=stats(open("ref/latin.clean").read().split(),"латынь")
R["английский"]=stats(open("ref/english.clean").read().split(),"английский")
print("\n"+"="*104)
print("ГЛАВНАЯ СРАВНИМАЯ МЕРА — повторы соседних слов относительно случайного ожидания")
print("="*104)
for k,v in sorted(R.items(), key=lambda kv:-kv[1]["rep"]):
    bar="█"*int(v["rep"]*24)
    print(f"  {k:34s} {v['rep']:6.3f}×  {bar}")
