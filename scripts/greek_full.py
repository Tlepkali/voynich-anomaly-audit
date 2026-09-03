import json, collections, sys
sys.path.insert(0,"."); import metrics
D=json.load(open("parsed.json")); rows=D["rows"]
VL=[[w for w in r["words"] if '?' not in w] for r in rows if r["locus"]=="P"]
VL=[l for l in VL if len(l)>=3]
LENS=[]; tot=0
for l in VL:
    if tot>=4000: break
    LENS.append(len(l)); tot+=len(l)
N=tot; VOY=[w for l in VL for w in l][:N]
def lay(ws):
    o=[];k=0
    for n in LENS:
        if k+n>len(ws): break
        o.append(ws[k:k+n]); k+=n
    return o
def M(ws):
    L=lay(ws); return metrics.all_metrics([w for l in L for w in l], L)
def skel(w, v):
    if len(w)<=3: return w
    core="".join(c for c in w[1:-1] if c not in v)
    return (w[0]+core+w[-1])[:7] or w
GV="αεηιουω"; LV="aeiou"
el=open("ref/wiki_el.clean").read().split()
la=open("ref/latin.clean").read().split()
CORP=[("РУКОПИСЬ ВОЙНИЧА",VOY),
      ("греческий как есть",el),
      ("греческий, снят гласные",[skel(w,GV) for w in el]),
      ("латынь как есть",la),
      ("латынь, снят гласные",[skel(w,LV) for w in la])]
KEYS=[("mean_len","ср.длина"),("cv","CV длин"),("h1","h1"),("h2","h2"),
      ("mi_pos","слотовость"),("ttr","TTR"),("hapax","хапаксы"),
      ("wh2","H(слово|пред)"),("zipf","Ципф"),("rep_ratio","повторы ×"),
      ("ed1","отл. в 1 знак"),("line_div","эффект строки")]
res={}
for lab,ws in CORP:
    if len(ws)<N: print(f"  {lab}: мало"); continue
    res[lab]=M(ws)
mv=res["РУКОПИСЬ ВОЙНИЧА"]
print("="*112)
print("ГРЕЧЕСКИЙ БЕЗ ГЛАСНЫХ — ПОЛНАЯ ПАНЕЛЬ (ранжирование шло только по TTR и слотовости)")
print("="*112)
hdr=list(res)
print(f"  {'мера':16s}" + "".join(f"{h[:20]:>22s}" for h in hdr))
print("  "+"-"*(16+22*len(hdr)))
for k,lab in KEYS:
    row=f"  {lab:16s}"
    for h in hdr:
        v=res[h][k]
        if h=="РУКОПИСЬ ВОЙНИЧА": row+=f"{v:22.3f}"
        else:
            e=abs(v-mv[k])/max(abs(mv[k]),1e-9)
            row+=f"{v:15.3f} {('✓' if e<=0.15 else f'{e:.0%}'):>6s}"
    print(row)
print("  "+"-"*(16+22*len(hdr)))
for h in hdr[1:]:
    hits=sum(1 for k,_ in KEYS if abs(res[h][k]-mv[k])/max(abs(mv[k]),1e-9)<=0.15)
    print(f"  {h:34s} попаданий {hits:2d} из {len(KEYS)}")
