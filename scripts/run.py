import json, math, collections, sys, itertools
sys.path.insert(0,".")
import metrics, gens

T = json.load(open("target.json"))

def cheap(lines):
    """только настраиваемые величины: средняя длина и h1 — считается быстро"""
    ws=[w for l in lines for w in l]
    mu=sum(len(w) for w in ws)/len(ws)
    ch=[]
    for w in ws: ch.extend(list(w)); ch.append(" ")
    c=collections.Counter(ch); N=len(ch)
    h1=-sum(n/N*math.log2(n/N) for n in c.values())
    return mu,h1
def loss(lines):
    mu,h1=cheap(lines)
    return abs(mu-T['mean_len'])/T['mean_len'] + abs(h1-T['h1'])/T['h1']

print("НАСТРОЙКА (только по средней длине слова и h1)\n")

best=None
for a in [0.65,0.70,0.75,0.80,0.85,0.90]:
    for pm in [0.2,0.35,0.5,0.65,0.8,0.95]:
        L=loss(gens.gen_slot(a,pm)); 
        if best is None or L<best[0]: best=(L,a,pm)
_,A,PM = best
print(f"  слоты (решётка Кардано):   alpha={A}  p_mid={PM}   невязка {best[0]:.4f}")

best=None
for pc in [0.0,0.05,0.10,0.20,0.30]:
    for W in [5,10,20,50]:
        L=loss(gens.gen_selfcite(pc,W,A,PM))
        if best is None or L<best[0]: best=(L,pc,W)
_,PC,WW = best
print(f"  самоцитирование:           p_copy={PC}  окно={WW}   невязка {best[0]:.4f}")

best=None
for ps in [0.3,0.5,0.7,0.85]:
    for pc in [0.0,0.10,0.20,0.30]:
        L=loss(gens.gen_hybrid(ps,pc,WW,A,PM))
        if best is None or L<best[0]: best=(L,ps,pc)
_,PS,PC2 = best
print(f"  гибрид:                    p_self={PS}  p_copy={PC2}  невязка {best[0]:.4f}")

CAND = [
  ("рукопись Войнича",            None),
  ("A. слоты (решётка)",          gens.gen_slot(A,PM)),
  ("B. самоцитирование",          gens.gen_selfcite(PC,WW,A,PM)),
  ("C. гибрид",                   gens.gen_hybrid(PS,PC2,WW,A,PM)),
  ("C2. гибрид + сброс на строке", gens.gen_hybrid(PS,PC2,WW,A,PM,line_reset=True)),
  ("D. Марков-2 (контроль)",      gens.gen_markov2()),
]
res={}
for name, lines in CAND:
    if lines is None:
        res[name]=T
    else:
        ws=[w for l in lines for w in l]
        res[name]=metrics.all_metrics(ws, lines)
json.dump(res, open("results.json","w"))

KEYS=[("mean_len","ср.длина","T"),("h1","h1","T"),
      ("cv","CV длин",""),("h2","h2",""),("h2_merged","h2 склеен",""),
      ("mi_pos","слотовость",""),("mi_pos_merged","слот. склеен",""),
      ("rep_ratio","повторы ×",""),("ed1","отл. в 1 знак",""),
      ("ttr","TTR",""),("hapax","хапаксы",""),("wh2","H(слово|пред)",""),
      ("zipf","наклон Ципфа",""),("line_div","эффект строки","")]
names=[n for n,_ in CAND]
print("\n" + "="*104)
print("T = величина, по которой шла настройка. Остальные 12 — контрольные.")
print("="*104)
hdr=f"{'':17s}" + "".join(f"{n[:15]:>16s}" for n in names[1:])
print(f"{'показатель':17s}{'ЦЕЛЬ':>10s}" + "".join(f"{n[:14]:>15s}" for n in names[1:]))
print("-"*104)
for k,label,mark in KEYS:
    row=f"{label+(' ('+mark+')' if mark else ''):17s}{T[k]:10.3f}"
    for n in names[1:]:
        v=res[n].get(k)
        row += f"{v:15.3f}" if v is not None else f"{'—':>15s}"
    print(row)

print("\nОТКЛОНЕНИЕ ОТ ЦЕЛИ ПО 12 КОНТРОЛЬНЫМ (доля |откл|/цель, попадание = в пределах 15 %)")
print("-"*104)
ctrl=[k for k,_,m in KEYS if not m]
for n in names[1:]:
    errs=[]; hits=0
    for k in ctrl:
        v=res[n].get(k)
        if v is None: continue
        e=abs(v-T[k])/max(abs(T[k]),1e-9); errs.append(e); hits += e<=0.15
    print(f"  {n:30s} попаданий {hits:2d}/{len(errs):2d}   медианное отклонение {sorted(errs)[len(errs)//2]:6.1%}")
