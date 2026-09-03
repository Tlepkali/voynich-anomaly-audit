import json, collections, sys
sys.path.insert(0,".")
def rep(w):
    ty=collections.Counter(w); T=len(w)
    same=sum(1 for a,b in zip(w,w[1:]) if a==b)
    exp=sum((n/T)**2 for n in ty.values())*(T-1)
    return same, exp, (same/exp if exp else 0)
def ed1(a,b):
    if a==b or abs(len(a)-len(b))>1: return False
    if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
    s,l=(a,b) if len(a)<len(b) else (b,a)
    return any(l[:i]+l[i+1:]==s for i in range(len(l)))
N=4000
def stats(ws, lab):
    w=ws[:N]
    if len(w)<N: print(f"  {lab:34s} мало данных"); return None
    ty=collections.Counter(w); s,e,r=rep(w)
    e1=sum(1 for a,b in zip(w,w[1:]) if ed1(a,b))/(len(w)-1)
    hap=sum(1 for v in ty.values() if v==1)/len(ty)
    print(f"  {lab:34s} TTR {len(ty)/len(w):.3f}  хапаксы {hap:.3f}  "
          f"повторы {r:6.3f}×  отл.1 {e1:.3f}  ср.длина {sum(len(x) for x in w)/len(w):.2f}")
    return r
D=json.load(open("parsed.json")); rows=D["rows"]
VOY=[w for r in rows if r["locus"]=="P" for w in r["words"] if '?' not in w]
print("="*100)
print("СВЯЩЕННЫЕ ТЕКСТЫ ПРОТИВ ОБЫЧНОЙ ПРОЗЫ ТЕХ ЖЕ ЯЗЫКОВ (по 4000 слов)")
print("="*100)
R={}
R["ВОЙНИЧ"]=stats(VOY,"ВОЙНИЧ")
print()
for f,lab in (("ref/scr_vulgata.clean","Вульгата (латынь)"),
              ("ref/latin.clean","  Плиний — обычная латынь"),
              ("ref/scr_quran.clean","Коран (арабский)"),
              ("ref/wiki_ar.clean","  арабская Википедия"),
              ("ref/scr_tanakh.clean","Танах (иврит)"),
              ("ref/wiki_he.clean","  ивритская Википедия")):
    try: R[lab]=stats(open(f).read().split(), lab)
    except FileNotFoundError: print(f"  {lab}: нет файла")
print("\n" + "="*100)
print("ПОВТОРЫ СОСЕДНИХ СЛОВ — упорядоченно")
print("="*100)
for k,v in sorted([(k,v) for k,v in R.items() if v is not None], key=lambda kv:-kv[1]):
    print(f"  {k:34s} {v:6.3f}×  {'█'*int(min(v,2)*30)}")
