# -*- coding: utf-8 -*-
"""Ландини 2001 (Cryptologia 25(4), 275-295): спектральный анализ текста БЕЗ
ПРОБЕЛОВ даёт указание на модальную длину слова, не опираясь на верность
кодировки словоразделов. Это сильнее моего §9, где сегментация проверялась
двумя ПЕРЕразбиениями — то есть всё равно через пробелы.

Простая версия: убираем пробелы, для частых знаков считаем автокорреляцию
индикаторной последовательности по лагам. Если структура слова реальна и не
навязана пробелами, у концесловных знаков должен быть пик на средней длине слова.
"""
import sys, collections, random, statistics as st
sys.path.insert(0,"scripts")
import measures as M

def stream(L): return "".join("".join(l) for l in L)     # БЕЗ пробелов
def autocorr(seq, ch, maxlag=14):
    idx=[i for i,c in enumerate(seq) if c==ch]
    if len(idx)<200: return None
    n=len(seq); p=len(idx)/n
    s=set(idx); out=[]
    for lag in range(1,maxlag+1):
        hit=sum(1 for i in idx if i+lag in s)
        out.append((hit/len(idx))/p)      # во сколько раз чаще случайного
    return out

VL=M.load(); S=stream(VL)
mean_len=st.mean(len(w) for w in M.tokens(VL))
print("="*100); print(f"АВТОКОРРЕЛЯЦИЯ ЗНАКОВ В ПОТОКЕ БЕЗ ПРОБЕЛОВ (средняя длина слова {mean_len:.2f})"); print("="*100)
freq=collections.Counter(S)
print(f"  {'знак':>5s} " + " ".join(f"{l:>5d}" for l in range(1,13)) + "   пик")
peaks=[]
for ch,_ in freq.most_common(8):
    a=autocorr(S,ch)
    if not a: continue
    pk=max(range(len(a)), key=lambda i:a[i])+1
    peaks.append((ch,pk,a[pk-1]))
    print(f"  {ch:>5s} " + " ".join(f"{v:5.2f}" for v in a[:12]) + f"   {pk}")
print("\n  контроль — тот же поток, знаки перемешаны (структуры слова нет):")
rnd=random.Random(7); SH="".join(rnd.sample(S,len(S)))
for ch,_ in freq.most_common(4):
    a=autocorr(SH,ch)
    if a: print(f"  {ch:>5s} " + " ".join(f"{v:5.2f}" for v in a[:12]))
print("\n  контроль — ЛАТЫНЬ без пробелов (средняя длина слова у неё иная):")
LL=M.ref_lines("latin.clean",[len(l) for l in VL]); SL=stream(LL)
ml=st.mean(len(w) for w in M.tokens(LL))
print(f"  (средняя длина латинского слова {ml:.2f})")
for ch,_ in collections.Counter(SL).most_common(4):
    a=autocorr(SL,ch)
    if a:
        pk=max(range(len(a)), key=lambda i:a[i])+1
        print(f"  {ch:>5s} " + " ".join(f"{v:5.2f}" for v in a[:12]) + f"   пик {pk}")
print("\n"+"="*100); print("ВЫВОД"); print("="*100)
good=[p for _,p,_ in peaks if abs(p-mean_len)<=1.5]
print(f"  знаков с пиком в пределах 1,5 от средней длины слова: {len(good)} из {len(peaks)}")
print(f"  пики: " + ", ".join(f"{c}→{p}" for c,p,_ in peaks))
