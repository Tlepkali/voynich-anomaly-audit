import json, sys
sys.path.insert(0,".")
import metrics, gens, gens2
T=json.load(open("target.json"))
KEYS=[("mean_len","ср.длина"),("h1","h1"),("cv","CV длин"),("h2","h2"),("h2_merged","h2 склеен"),
      ("mi_pos","слотовость"),("mi_pos_merged","слот. склеен"),("rep_ratio","повторы ×"),
      ("ed1","отл. в 1 знак"),("ttr","TTR"),("hapax","хапаксы"),("wh2","H(слово|пред)"),
      ("zipf","наклон Ципфа"),("line_div","эффект строки")]

# подбор p_rep/p_mut для составной процедуры — по повторам и отличиям в 1 знак
best=None
for pr in [0.004,0.006,0.008,0.012]:
    for pm in [0.02,0.04,0.06,0.09]:
        L=gens2.gen_composite(pr,pm); ws=[w for l in L for w in l]
        m=metrics.all_metrics(ws,L)
        e=abs(m['rep_ratio']-T['rep_ratio'])/T['rep_ratio']+abs(m['ed1']-T['ed1'])/T['ed1']
        if best is None or e<best[0]: best=(e,pr,pm,m)
_,PR,PM,mE = best
print(f"составная процедура настроена: p_rep={PR}  p_mut={PM}\n")

L2=gens2.gen_slot_big(); mA2=metrics.all_metrics([w for l in L2 for w in l], L2)
cands=[("A2. большая таблица", mA2), ("E. три слоя", mE)]
print(f"{'показатель':17s}{'ЦЕЛЬ':>10s}" + "".join(f"{n[:18]:>20s}" for n,_ in cands))
print("-"*70)
for k,label in KEYS:
    row=f"{label:17s}{T[k]:10.3f}"
    for _,m in cands: row+=f"{m[k]:20.3f}"
    print(row)
print()
for n,m in cands:
    errs=[abs(m[k]-T[k])/max(abs(T[k]),1e-9) for k,_ in KEYS]
    hits=sum(1 for e in errs if e<=0.15)
    print(f"  {n:22s} попаданий {hits:2d}/14   медианное отклонение {sorted(errs)[len(errs)//2]:6.1%}")
