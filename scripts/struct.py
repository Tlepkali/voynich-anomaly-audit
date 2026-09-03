import json, math, collections
D = json.load(open("parsed.json")); rows, pages = D["rows"], D["pages"]
voy = [w for r in rows for w in r["words"] if '?' not in w]
lat = open("ref/latin.clean").read().split()[:len(voy)]
eng = open("ref/english.clean").read().split()[:len(voy)]

def posclass(w, i):
    if len(w)==1: return "один"
    return "начало" if i==0 else ("конец" if i==len(w)-1 else "середина")

def mi_glyph_position(words):
    """взаимная информация между буквой и её позицией в слове: мера «слотовости»"""
    joint = collections.Counter()
    for w in words:
        for i,c in enumerate(w): joint[(c, posclass(w,i))] += 1
    T = sum(joint.values())
    pg = collections.Counter(); pp = collections.Counter()
    for (g,p),n in joint.items(): pg[g]+=n; pp[p]+=n
    return sum(n/T*math.log2((n/T)/((pg[g]/T)*(pp[p]/T))) for (g,p),n in joint.items())

print("="*66)
print("ЖЁСТКОСТЬ ПОЗИЦИЙ: сколько бит о позиции в слове несёт сама буква")
print("="*66)
for name, ws in (("Войнич",voy),("латынь",lat),("английский",eng)):
    print(f"  {name:14s} I(буква; позиция) = {mi_glyph_position(ws):.3f} бит")

print("\nбуквы Войнича, жёстче всего привязанные к позиции:")
tab = collections.defaultdict(collections.Counter)
for w in voy:
    for i,c in enumerate(w): tab[c][posclass(w,i)] += 1
for c, cnt in sorted(tab.items(), key=lambda kv: -sum(kv[1].values()))[:14]:
    tot = sum(cnt.values())
    if tot < 300: continue
    b, m, e = cnt['начало']/tot, cnt['середина']/tot, cnt['конец']/tot
    print(f"   {c}  всего {tot:6d}   начало {b:5.0%}  середина {m:5.0%}  конец {e:5.0%}")

print("\n" + "="*66)
print("ПОВТОРЫ СОСЕДНИХ СЛОВ")
print("="*66)
def repeats(words, label):
    same = sum(1 for a,b in zip(words, words[1:]) if a==b)
    freq = collections.Counter(words); T=len(words)
    exp  = sum((n/T)**2 for n in freq.values()) * (T-1)     # ожидание при независимости
    def ed1(a,b):
        if abs(len(a)-len(b))>1: return False
        if a==b: return False
        if len(a)==len(b): return sum(x!=y for x,y in zip(a,b))==1
        s,l = (a,b) if len(a)<len(b) else (b,a)
        return any(l[:i]+l[i+1:]==s for i in range(len(l)))
    near = sum(1 for a,b in zip(words, words[1:]) if ed1(a,b))
    print(f"  {label:14s} точных повторов {same:5d} (ожидалось {exp:6.0f}, ×{same/exp:4.1f})   "
          f"отличие в 1 знак {near:5d} ({near/(len(words)-1):4.1%})")
for name, ws in (("Войнич",voy),("латынь",lat),("английский",eng)): repeats(ws, name)

print("\n" + "="*66)
print("ЗАКОН КАРРИЕРА: первое слово строки отличается от остальных?")
print("="*66)
first = [r["words"][0] for r in rows if r["words"] and '?' not in r["words"][0]]
rest  = [w for r in rows for w in r["words"][1:] if '?' not in w]
last  = [r["words"][-1] for r in rows if r["words"] and '?' not in r["words"][-1]]
def firstchar_dist(ws):
    c = collections.Counter(w[0] for w in ws); T=sum(c.values())
    return {k: v/T for k,v in c.items()}, T
fd,_ = firstchar_dist(first); rd,_ = firstchar_dist(rest); ld,_ = firstchar_dist(last)
print(f"  слов в начале строк {len(first)}, прочих {len(rest)}")
print(f"  {'буква':6s} {'нач.строки':>11s} {'прочие':>9s} {'отношение':>10s}")
for c in sorted(set(fd)|set(rd), key=lambda c: -(rd.get(c,0))):
    if rd.get(c,0) < 0.02 and fd.get(c,0) < 0.02: continue
    r = fd.get(c,0)/rd.get(c,1e-9)
    print(f"  {c:6s} {fd.get(c,0):10.1%} {rd.get(c,0):9.1%} {r:9.2f}×")
