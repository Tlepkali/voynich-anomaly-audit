# -*- coding: utf-8 -*-
"""ГРАММАТИКА ЗАТТЕРЫ (Voynich 2022, Мальта, CEUR Vol-3313 paper10, рис. 4)
реализована буквально по печатному тексту правил. Заявлено автором:
покрывает 62 % ТОКЕНОВ рукописи и 1113 типов (21,6 %), F1 = 0,270 —
лучший результат среди опубликованных грамматик.

Проверяю: воспроизводится ли, и как выглядит на фоне моей наивной модели
(17,5 % токенов, 3,3 % типов).
"""
import sys, collections
sys.path.insert(0,"scripts")
import measures as M

# состояние -> (допустимые глифы, куда можно перейти)
G = {
 "0_d":   ({"d"},            ["4_C","4_S"]),
 "0_q":   ({"q"},            ["1_o"]),
 "0_s":   ({"s"},            ["4_C"]),
 "1_o":   ({"o"},            ["2_r","3_tpkf","4_C","5_TPK","6_eEB","7_d","8_a"]),
 "1_y":   ({"y"},            ["3_tpkf","4_C","4_S"]),
 "2_l":   ({"l"},            ["3_tpkf","4_C","4_S"]),
 "2_r":   ({"r"},            ["8_a"]),
 "3_tpkf":({"t","p","k","f"},["4_C","6_eEB","8_a","8_o","11_y"]),
 "4_C":   ({"ch"},           ["6_eEB","8_a","8_o","10_d","11_y"]),
 "4_S":   ({"sh"},           ["6_eEB","8_o"]),
 "5_TPK": ({"cth","cph","ckh"}, ["6_eEB","8_a","8_o"]),
 "6_eEB": ({"e","ee","eee"}, ["7_s","8_o","10_d","11_y","END"]),
 "7_d":   ({"d"},            ["8_a","8_o"]),
 "7_s":   ({"s"},            ["END"]),
 "8_a":   ({"a"},            ["9_iJ","10_l","10_m","10_n","10_r"]),
 "8_o":   ({"o"},            ["10_d","10_l","10_r","END"]),
 "9_iJ":  ({"i","ii"},       ["10_n","10_r"]),
 "10_d":  ({"d"},            ["11_y","END"]),
 "10_l":  ({"l"},            ["11_y","END"]),
 "10_m":  ({"m"},            ["END"]),
 "10_n":  ({"n"},            ["END"]),
 "10_r":  ({"r"},            ["END"]),
 "11_y":  ({"y"},            ["END"]),
}
START=["0_d","0_q","0_s","1_o","1_y","2_l","2_r","3_tpkf","4_C","4_S","5_TPK","7_d","8_a"]
GLYPHS=sorted({g for v,_ in G.values() for g in v}, key=lambda x:-len(x))

def accepts(w, extra_cfh=False):
    Gl = dict(G)
    if extra_cfh: Gl["5_TPK"]=(Gl["5_TPK"][0]|{"cfh"}, Gl["5_TPK"][1])
    gl = sorted({g for v,_ in Gl.values() for g in v}, key=lambda x:-len(x))
    memo={}
    def go(i, st):
        if (i,st) in memo: return memo[(i,st)]
        ok=False
        if st=="END": ok = (i==len(w))
        else:
            glyphs, nxt = Gl[st]
            for g in gl:
                if g in glyphs and w.startswith(g, i):
                    if any(go(i+len(g), n) for n in nxt): ok=True; break
        memo[(i,st)]=ok; return ok
    return any(go(0,s) for s in START)

VL=M.load(); toks=M.tokens(VL); T=M.types(VL)
cnt=collections.Counter(toks)
for cfh in (False, True):
    good_t={w for w in T if accepts(w, cfh)}
    ntok=sum(cnt[w] for w in good_t)
    lab="с cfh в слоте 5" if cfh else "буквально по правилам (без cfh)"
    print(f"  {lab:>32s}: типов {len(good_t):5d} ({len(good_t)/len(T):5.1%}), "
          f"токенов {ntok:6d} ({ntok/len(toks):5.1%})")
print(f"\n  ЗАЯВЛЕНО АВТОРОМ: 1113 типов (21,6 %) и 62 % токенов")
print(f"  МОЯ НАИВНАЯ МОДЕЛЬ на 12 слотов: 3,3 % типов, 17,5 % токенов")
good_t={w for w in T if accepts(w)}
ranked=[w for w,_ in cnt.most_common()]
first=next((i+1 for i,w in enumerate(ranked) if w not in good_t), None)
print(f"\n  ранг первого НЕ порождаемого слова: {first}")
print(f"  (у поля: Тилтман 19, Фирт 4, ThomasCoon 44, Заттера 89, Стольфи 112)")
print(f"\n  примеры непокрытых частых слов: " + ", ".join(w for w in ranked[:60] if w not in good_t)[:150])

# ── СЛОТОВАЯ МОДЕЛЬ (до отсечки грамматикой) ───────────────────────────────
# Слоты по именам состояний грамматики и рис. 2. Правило Заттеры:
# «за глифом может идти глиф того же или БОЛЬШЕГО слота».
SLOT = {
 0: {"q","s","d"}, 1: {"o","y"}, 2: {"l","r"}, 3: {"t","p","k","f"},
 4: {"ch","sh"},   5: {"cth","cph","ckh","cfh"}, 6: {"e","ee","eee"},
 7: {"d","s"},     8: {"a","o"}, 9: {"i","ii","iii"},
 10:{"d","l","m","n","r"}, 11:{"y"},
}
G2=collections.defaultdict(set)
for k,v in SLOT.items():
    for g in v: G2[g].add(k)
GL=sorted(G2, key=lambda x:-len(x))
def regular(w):
    """разбирается ли слово на глифы с НЕУБЫВАЮЩИМИ слотами"""
    memo={}
    def go(i, lo):
        if i==len(w): return True
        if (i,lo) in memo: return memo[(i,lo)]
        ok=False
        for g in GL:
            if w.startswith(g,i):
                for s in sorted(G2[g]):
                    if s>=lo and go(i+len(g), s): ok=True; break
            if ok: break
        memo[(i,lo)]=ok; return ok
    return go(0,0)
print("\n"+"="*96); print("СЛОТОВАЯ МОДЕЛЬ ЗАТТЕРЫ (12 слотов, неубывающий порядок)"); print("="*96)
reg={w for w in T if regular(w)}
nt=sum(cnt[w] for w in reg)
print(f"  регулярных типов {len(reg)} из {len(T)} = {len(reg)/len(T):.1%}")
print(f"  регулярных ТОКЕНОВ {nt} из {len(toks)} = {nt/len(toks):.1%}   (у автора 86,6 %)")
first=next((i+1 for i,w in enumerate(ranked) if w not in reg), None)
print(f"  ранг первого НЕрегулярного слова: {first}   (у поля для Заттеры: 89)")
print(f"  первые нерегулярные из топ-200: " + ", ".join(w for w in ranked[:200] if w not in reg)[:130])
import random as _r
rnd=_r.Random(5); mp={w:"".join(rnd.sample(w,len(w))) for w in T}
shreg=sum(1 for w in T if regular(mp[w]))
print(f"\n  КОНТРОЛЬ, перемешка знаков в слове: регулярных {shreg/len(T):.1%} типов")
print(f"  отношение {len(reg)/len(T)/max(shreg/len(T),1e-9):.1f}× — вот сила слотовости по мерке поля")
