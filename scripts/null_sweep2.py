# -*- coding: utf-8 -*-
"""A4: «аффиксы, найденные без подсказки, совпадают с каноническими» — CONFIRM
при контроле «отбор по частоте типов, тот же на всех корпусах». Но канонический
список сообщество тоже выводило, глядя на частые краевые подстроки. Тогда
совпадение гарантировано устройством процедуры, а не морфологией.

НУЛЬ, которого не было: тот же отбор на словаре с ПЕРЕМЕШАННЫМИ ВНУТРИ СЛОВА
знаками. Он сохраняет частоты знаков и длины, но уничтожает всякий порядок,
то есть всякую морфологию. Если и он «находит» канонические аффиксы —
находка есть свойство частот, а не текста.
"""
import sys, collections, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

CANON_PRE={"o","ch","q","qo","s","sh","y","d"}
CANON_SUF={"y","dy","in","iin","ey","edy","ol","ar"}
def affixes(types,k=15,maxaff=3):
    pre=collections.Counter(); suf=collections.Counter()
    for w in types:
        for L in range(1,maxaff+1):
            if len(w)>L: pre[w[:L]]+=1; suf[w[-L:]]+=1
    return [a for a,_ in pre.most_common(k)],[a for a,_ in suf.most_common(k)]

VL=M.load(); TV=M.types(VL)
P,U=affixes(TV)
hit_p=CANON_PRE&set(P); hit_s=CANON_SUF&set(U)
print("="*96); print("A4: СОВПАДЕНИЕ С КАНОНИЧЕСКИМ СПИСКОМ"); print("="*96)
print(f"  найдено приставок (топ-15): {', '.join(P)}")
print(f"  найдено окончаний (топ-15): {', '.join(U)}")
print(f"\n  канонические приставки {sorted(CANON_PRE)}: попало {len(hit_p)}/8 — {sorted(hit_p)}")
print(f"  канонические окончания {sorted(CANON_SUF)}: попало {len(hit_s)}/8 — {sorted(hit_s)}")
print(f"  ИТОГО совпадение {len(hit_p)+len(hit_s)}/16 = {(len(hit_p)+len(hit_s))/16:.0%}")

print("\n"+"="*96); print("НУЛЬ: тот же отбор на словаре с перемешанными В СЛОВЕ знаками"); print("="*96)
res=[]
for seed in range(20):
    rnd=random.Random(seed)
    SH=sorted({"".join(rnd.sample(w,len(w))) for w in TV})
    p2,u2=affixes(SH)
    res.append((len(CANON_PRE&set(p2)), len(CANON_SUF&set(u2))))
mp=st.mean(a for a,_ in res); ms=st.mean(b for _,b in res)
lo=min(a+b for a,b in res); hi=max(a+b for a,b in res)
print(f"  перемешанный словарь, 20 зёрен: приставок {mp:.1f}/8, окончаний {ms:.1f}/8, "
      f"итого {mp+ms:.1f}/16 = {(mp+ms)/16:.0%}  [{lo}; {hi}]")
obs=len(hit_p)+len(hit_s)
ge=sum(1 for a,b in res if a+b>=obs)
print(f"  наблюдённое {obs}/16, нуль даёт не меньше в {ge} случаях из 20  →  p = {(ge+1)/21:.3f}")
print(f"\n  пример «аффиксов», найденных в перемешанном словаре (зерно 0):")
rnd=random.Random(0); SH=sorted({"".join(rnd.sample(w,len(w))) for w in TV})
p2,u2=affixes(SH)
print(f"    приставки: {', '.join(p2)}")
print(f"    окончания: {', '.join(u2)}")

print("\n"+"="*96); print("ПОЛОЖИТЕЛЬНЫЙ КОНТРОЛЬ: та же процедура на латыни"); print("="*96)
TL=M.types(M.ref_lines("latin.clean",[len(l) for l in VL]))
pl,ul=affixes(TL)
LAT_SUF={"s","m","is","um","que","us","rum","tur","ns","es","ae","i","o","a","e"}
print(f"  окончания латыни (топ-15): {', '.join(ul)}")
print(f"  из них настоящих латинских флексий: {len(set(ul)&LAT_SUF)}/15 — {sorted(set(ul)&LAT_SUF)}")
rnd=random.Random(0); SHL=sorted({"".join(rnd.sample(w,len(w))) for w in TL})
_,ul2=affixes(SHL)
print(f"  то же на ПЕРЕМЕШАННОЙ латыни: {len(set(ul2)&LAT_SUF)}/15 — {sorted(set(ul2)&LAT_SUF)}")
