import json, math, collections
D = json.load(open("parsed.json"))
rows, pages = D["rows"], D["pages"]

def ok(w): return '?' not in w
toks = [w for r in rows for w in r["words"] if ok(w)]
types = collections.Counter(toks)

print("="*62)
print("БАЗОВЫЕ ВЕЛИЧИНЫ")
print("="*62)
print(f"токенов (слов)            {len(toks):>8,}")
print(f"типов (уникальных слов)   {len(types):>8,}")
print(f"отношение типы/токены     {len(types)/len(toks):>8.3f}")
hapax = sum(1 for w,n in types.items() if n==1)
print(f"хапаксов (встретились 1×) {hapax:>8,}  ({hapax/len(types):.0%} словаря)")

print("\nсамые частые слова:")
for w,n in types.most_common(15):
    print(f"   {w:12s} {n:5d}  {n/len(toks):6.2%}")

print("\n" + "="*62)
print("ДЛИНЫ СЛОВ")
print("="*62)
L = collections.Counter(len(w) for w in toks)
mean = sum(len(w) for w in toks)/len(toks)
var  = sum((len(w)-mean)**2 for w in toks)/len(toks)
print(f"средняя {mean:.2f}, дисперсия {var:.2f}, ст.откл {var**0.5:.2f}")
mx = max(L)
for i in range(1, mx+1):
    n = L.get(i,0)
    print(f"   {i:2d} │{'█'*int(60*n/max(L.values())):60s}│ {n:5d} {n/len(toks):6.2%}")

# энтропия по символам, пробел как символ
def entropies(seqs, label):
    text = " ".join(seqs)
    uni = collections.Counter(text)
    N = len(text)
    h1 = -sum(n/N*math.log2(n/N) for n in uni.values())
    bi = collections.Counter(text[i:i+2] for i in range(N-1))
    M = sum(bi.values())
    h12 = -sum(n/M*math.log2(n/M) for n in bi.values())
    h2 = h12 - h1
    h0 = math.log2(len(uni))
    print(f"{label:22s} алфавит {len(uni):3d}  h0={h0:5.2f}  h1={h1:5.2f}  h2={h2:5.2f}")
    return h0,h1,h2

print("\n" + "="*62)
print("ЭНТРОПИЯ (бит/символ, пробел учитывается как символ)")
print("="*62)
print("h0 = log2(алфавит), h1 = по одиночным, h2 = условная H(c|предыдущий)")
entropies(toks, "Войнич, весь текст")

# язык Карриера
for lang in ("A","B"):
    t = [w for r in rows for w in r["words"] if ok(w) and pages.get(r["page"],{}).get("L")==lang]
    if t: entropies(t, f"  Карриер {lang} ({len(t):,} тк)")
