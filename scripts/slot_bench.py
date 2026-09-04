# -*- coding: utf-8 -*-
"""Мерка ПОЛЯ для слотовых моделей: ранг самого частого слова, которое модель
НЕ порождает. Зандберген (voynich.nu, a3_para) сводит их в таблицу:
Тилтман 1967 — 19, Роу — раньше, Фирт — 4 (на языке B), Стольфи — 112,
ThomasCoon — 44, Заттера 2022 — 89. Все однознаковые системы на 12 слотов.

У меня запись A1 «слова строятся из упорядоченных позиционных слотов» стоит
ОСЛАБЛЕННОЙ по совсем другой мере: доля «упорядоченных» слов 88 % против 81 %
у перемешивания внутри слова = 1,09×. Если модель на 12 слотов покрывает топ-88,
эти два измерения выглядят несовместимо. Проверяю, кто из них негоден.
"""
import sys, collections, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

VL=M.load(); toks=M.tokens(VL)
cnt=collections.Counter(toks)
ranked=[w for w,_ in cnt.most_common()]

def build_order(tokens):
    """порядок знаков по средней ОТНОСИТЕЛЬНОЙ позиции в слове"""
    pos=collections.defaultdict(list)
    for w in tokens:
        if len(w)<2: continue
        for i,c in enumerate(w): pos[c].append(i/(len(w)-1))
    return {c: st.mean(v) for c,v in pos.items() if len(v)>=20}

def ordered_frac(tokens, order):
    """доля слов, чьи знаки идут в неубывающем порядке рангов"""
    ok=n=0
    for w in tokens:
        if len(w)<2: continue
        r=[order.get(c) for c in w]
        if any(x is None for x in r): continue
        n+=1
        if all(r[i]<=r[i+1] for i in range(len(r)-1)): ok+=1
    return ok/max(n,1), n

ORD=build_order(toks)
a,na=ordered_frac(toks,ORD)
rnd=random.Random(5)
TV=sorted(set(toks)); mp={w:"".join(rnd.sample(w,len(w))) for w in TV}
sh=[mp[w] for w in toks]
b,nb=ordered_frac(sh,ORD)
print("="*96); print("МОЯ МЕРА (доля слов с неубывающим порядком рангов знаков)"); print("="*96)
print(f"  настоящий текст   {a:.1%} (n={na})")
print(f"  перемешка в слове {b:.1%} (n={nb})")
print(f"  отношение {a/b:.2f}×   ← в записи A1 стоит 1,09×")

print("\n"+"="*96); print("МЕРКА ПОЛЯ: строим слотовую модель и ищем ранг первого непокрытого слова"); print("="*96)
def slot_model(tokens, nslots=12, minf=20):
    """каждому знаку — слот по средней относительной позиции, разбитой на nslots"""
    o=build_order(tokens)
    lo,hi=min(o.values()),max(o.values())
    slot={c:min(nslots-1,int((v-lo)/(hi-lo+1e-9)*nslots)) for c,v in o.items()}
    return slot
def covered(w, slot):
    s=[slot.get(c) for c in w]
    if any(x is None for x in s): return False
    return all(s[i]<s[i+1] for i in range(len(s)-1))     # строго по возрастанию слотов
for nslots in (12,16,20):
    slot=slot_model(toks,nslots)
    first=None; cov=0
    for i,w in enumerate(ranked):
        if covered(w,slot): cov+=1
        elif first is None: first=i+1
    tot=sum(1 for w in toks if covered(w,slot))/len(toks)
    print(f"  слотов {nslots:2d}: первое непокрытое слово ранга {first}, покрыто типов "
          f"{cov}/{len(ranked)} = {cov/len(ranked):.1%}, токенов {tot:.1%}")
print("\n  для сверки, у поля: Тилтман 19, Фирт 4 (яз. B), ThomasCoon 44, Заттера 89, Стольфи 112")
print("\n"+"="*96); print("ЧТО ПОКАЗЫВАЕТ РАСХОЖДЕНИЕ"); print("="*96)
slot=slot_model(toks,12)
print(f"  доля ТОКЕНОВ, покрытых моделью на 12 слотов: {sum(1 for w in toks if covered(w,slot))/len(toks):.1%}")
shc=sum(1 for w in sh if covered(w,slot))/len(sh)
print(f"  то же у ПЕРЕМЕШКИ внутри слова:              {shc:.1%}")
print(f"  отношение {sum(1 for w in toks if covered(w,slot))/len(toks)/max(shc,1e-9):.1f}×  ← вот это и есть сила слотовости")
print("\n  моя мера «неубывающий порядок рангов» ДОПУСКАЕТ повторы и равенства,")
print("  поэтому почти всякое слово её проходит и различает она плохо;")
print("  мерка поля требует СТРОГО возрастающих слотов и различает резко")
