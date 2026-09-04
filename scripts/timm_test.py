# -*- coding: utf-8 -*-
"""ЧЕТЫРЕ ПОДПИСИ НА ОПУБЛИКОВАННОМ ВЫХОДЕ ГЕНЕРАТОРА ТИММА И ШИННЕРА.

Тимм и Шиннер (Cryptologia 44(1), 1-19, 2020) предложили механизм САМОЦИТИРОВАНИЯ:
писец берёт слово из уже написанного (предпочтительно с той же страницы, с
вероятностью 28 % — с той же позиции предыдущей строки) и меняет его одной из
операций: добавить/убрать знак (20 %), склеить/разделить (30 %), заменить знак
(50 %), при ограничении «какой знак может следовать за каким» ВНУТРИ слова.
Плюс «подсказки», удерживающие доли -in/-ol/-dy выше порогов.

То есть у них ЧЕТЫРЕ мои памяти: сосед (источник + морфинг), позиционная,
страничная локальность, класс частоты. Ограничения ЧЕРЕЗ ГРАНИЦУ СЛОВА нет.

ПРЕДСКАЗАНИЕ, ОБЪЯВЛЕНО ДО ЗАМЕРА: возврат, автокорреляцию длины и
ранг-корреляцию их текст возьмёт, а СТЫК провалит — это центральное
утверждение моей генеративной статьи применительно к их алгоритму.

Текст взят из их репозитория (executable/generate/generated_text.txt),
ничего не запускалось.
"""
import sys, statistics as st
sys.path.insert(0,"scripts")
import measures as M

SP="/private/tmp/claude-501/-Users-tlep-oxima/f4011fbf-75d7-4aa8-97c3-a63629ac967f/scratchpad"
raw=open(f"{SP}/timm/executable/generate/generated_text.txt",encoding="utf-8",errors="ignore").read()
T=[l.split() for l in raw.split("\n") if l.strip() and not l.startswith("#")]
T=[l for l in T if len(l)>=3]
VL=M.load()
# рукопись, выровненная по объёму: те же длины строк, столько же строк
lens=[len(l) for l in T]
flat=M.tokens(VL); V=[]; p=0
for k in lens:
    if p+k>len(flat): break
    V.append(flat[p:p+k]); p+=k

def battery(L):
    return dict(rec=M.recurrence(L,1,5), d620=M.recurrence(L,6,20),
                la=M.len_autocorr(L), rc=M.rank_corr(L), j=M.junction(L,1))
tm=battery(T); ms=battery(V); full=battery(VL)
print("="*104); print("ЧЕТЫРЕ ПОДПИСИ: ГЕНЕРАТОР ТИММА И ШИННЕРА ПРОТИВ РУКОПИСИ"); print("="*104)
print(f"  их текст: строк {len(T)}, токенов {sum(len(l) for l in T)}, типов {len({w for l in T for w in l})}")
print(f"  рукопись выровнена: строк {len(V)}, токенов {sum(len(l) for l in V)}, типов {len({w for l in V for w in l})}")
print(f"\n  {'подпись':>26s} {'рукопись (выровн.)':>18s} {'Тимм-Шиннер':>13s} {'доля':>7s} {'рукопись целиком':>17s}")
for k,lab in [("rec","возврат d1-5"),("d620","возврат d6-20"),("la","автокорр. длины"),
              ("rc","ранг-корреляция"),("j","стык по 1 знаку")]:
    a,b,c=ms[k],tm[k],full[k]
    sh=b/a if abs(a)>1e-9 else float("nan")
    flag=""
    if k=="j": flag="   ← ПРЕДСКАЗАНО: провал"
    print(f"  {lab:>26s} {a:18.4f} {b:13.4f} {sh:6.0%} {c:17.4f}{flag}")
print("\n"+"="*104); print("СЛОВАРНЫЕ МЕРЫ ДЛЯ ПОЛНОТЫ"); print("="*104)
TT=sorted({w for l in T for w in l}); VV=sorted({w for l in V for w in l})
print(f"  {'мера':>26s} {'рукопись (выровн.)':>18s} {'Тимм-Шиннер':>13s}")
for lab,fn in [("соседей на тип", M.density),("профиль дл5/дл3", M.shape),
               ("доля типов с соседом", lambda X: M.has_neighbour(X)*100),
               ("жёсткость слотов", M.slot_rigidity)]:
    print(f"  {lab:>26s} {fn(VV):18.2f} {fn(TT):13.2f}")
ov=len(set(TT)&set(M.types(VL)))/len(TT)
print(f"\n  доля их типов, совпадающих со словарём рукописи: {ov:.1%}")
