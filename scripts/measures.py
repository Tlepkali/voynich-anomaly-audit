# -*- coding: utf-8 -*-
"""КАНОНИЧЕСКИЕ МЕРЫ. Одно определение каждой величины на весь проект.

Заведён после сверки 03.09.2026, где выяснилось, что жёсткость слотов живёт
в тексте в четырёх видах (20,86 / 20,9 / 21,00 / 21,29) — не потому, что она
шумит, а потому, что её считали четыре скрипта своими копиями оценщика.

Правила модуля:
  * у всякой стохастической меры зерно и число повторов стоят В СИГНАТУРЕ
    со значением по умолчанию; менять их можно только явно;
  * функция ничего не печатает и ничего не грузит с диска, кроме loader'ов;
  * если мера считается ещё где-то в scripts/, ЭТОТ файл главный.

Проверка соответствия опубликованному: scripts/paper_numbers.py
"""
import json, collections, math, random, statistics as st, os

# ── загрузка ────────────────────────────────────────────────────────────────

def load(code="ZL3b-n", locus="P", minlen=3):
    """Строки сплошного текста транскрипции: список списков слов."""
    d = json.load(open(f"data/parsed_{code}.json"))
    L = [[w for w in r["words"] if "?" not in w] for r in d["rows"] if r["locus"] == locus]
    return [l for l in L if len(l) >= minlen]

def cut_to_lines(words, lens):
    """Нарезать поток слов на строки тех же длин — так эталон сравним по строкам."""
    out, p = [], 0
    for n in lens:
        if p + n > len(words): break
        out.append(words[p:p + n]); p += n
    return out

def ref(name, ntokens=None):
    """Эталонный корпус из ref/ как плоский список слов, при желании обрезанный."""
    w = open(f"ref/{name}", encoding="utf-8", errors="ignore").read().split()
    return w[:ntokens] if ntokens else w

def ref_lines(name, lens):
    """Эталонный корпус, нарезанный на строки длин lens."""
    return cut_to_lines(ref(name), lens)

def types(L):
    return sorted({w for l in L for w in l})

def tokens(L):
    return [w for l in L for w in l]

# ── окрестность на расстоянии одной правки ──────────────────────────────────

def nbrs(T):
    """Соседи на расстоянии одной правки, через хеш удалений."""
    idx = collections.defaultdict(set)
    for w in T:
        idx[w].add(w)
        for i in range(len(w)): idx[w[:i] + w[i + 1:]].add(w)
    nb = collections.defaultdict(set)
    for _, ws in idx.items():
        ws = list(ws)
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                if abs(len(a) - len(b)) <= 1: nb[a].add(b); nb[b].add(a)
    return nb

def density(T):
    """Среднее число соседей на тип."""
    T = list(T); nb = nbrs(set(T))
    return st.mean(len(nb.get(w, ())) for w in T)

def has_neighbour(T):
    """Доля типов, у которых сосед есть хоть один."""
    T = list(T); nb = nbrs(set(T))
    return sum(1 for w in T if nb.get(w)) / len(T)

def shape(T, minn=15):
    """Профиль плотности по длине: соседей на длине 5, делённое на длину 3.
    У языков падает с длиной, у рукописи почти плоский."""
    T = set(T); nb = nbrs(T)
    def m(d):
        g = [len(nb.get(w, ())) for w in T if len(w) == d]
        return st.mean(g) if len(g) >= minn else float("nan")
    a, b = m(3), m(5)
    return b / a if a == a and b == b and a > 0 else float("nan")

# ── взаимная информация знак-позиция (жёсткость слотов) ─────────────────────

def mi_at(seq, n=4, minn=150):
    """Сырая ВИ между знаком и его позицией, на словах длины ровно n."""
    sub = [w for w in seq if len(w) == n]
    if len(sub) < minn: return float("nan")
    j = collections.Counter()
    for w in sub:
        for i, c in enumerate(w): j[(c, i)] += 1
    N = sum(j.values()); pg = collections.Counter(); pp = collections.Counter()
    for (g, i), c in j.items(): pg[g] += c; pp[i] += c
    return sum(c / N * math.log2((c / N) / ((pg[g] / N) * (pp[i] / N))) for (g, i), c in j.items())

def slot_rigidity(seq, n=4, B=10, seed=50):
    """ЖЁСТКОСТЬ СЛОТОВ: избыток ВИ знак-позиция над перемешиванием знаков
    ВНУТРИ слова. B перемешиваний с зёрнами seed..seed+B-1, среднее.
    На типах рукописи (ZL3b, длина 4) даёт 20,86; на латыни 8,59."""
    o = mi_at(seq, n)
    if o != o: return float("nan")
    v = []
    for s in range(B):
        r = random.Random(seed + s)
        sh = []
        for w in seq:
            c = list(w); r.shuffle(c); sh.append("".join(c))
        x = mi_at(sh, n)
        if x == x: v.append(x)
    return o / st.mean(v) if v else float("nan")

# ── условная энтропия ───────────────────────────────────────────────────────

def h2_at(seq, n=4, minn=150):
    """Условная энтропия знака по предыдущему, на словах длины ровно n."""
    sub = [w for w in seq if len(w) == n]
    if len(sub) < minn: return float("nan")
    ch = []
    for w in sub: ch.extend(list(w))
    u = collections.Counter(ch); T = len(ch)
    h1 = -sum(c / T * math.log2(c / T) for c in u.values())
    bi = collections.Counter(zip(ch, ch[1:])); M = sum(bi.values())
    return -sum(c / M * math.log2(c / M) for c in bi.values()) - h1

def h2_stream(L, sep=" "):
    """h2 знакового потока всего текста, с пробелом как знаком."""
    s = []
    for l in L:
        for w in l: s += list(w) + [sep]
    c2 = collections.Counter(zip(s, s[1:])); c3 = collections.Counter(zip(s, s[1:], s[2:]))
    n = sum(c3.values())
    return -sum((k / n) * math.log2(k / c2[t[:2]]) for t, k in c3.items())

# ── стык слов ───────────────────────────────────────────────────────────────

def _mi_pairs(pairs):
    j = collections.Counter(pairs)
    a = collections.Counter(x for x, _ in pairs); b = collections.Counter(y for _, y in pairs)
    n = len(pairs)
    return sum(c / n * math.log2((c / n) / ((a[x] / n) * (b[y] / n))) for (x, y), c in j.items())

def junction(L, k=1, B=5, seed=9):
    """СТЫК: избыток ВИ между k последними знаками слова и k первыми следующего
    над перемешиванием ПОРЯДКА СЛОВ внутри строк. B перемешиваний.
    k=1 на рукописи даёт 0,194, на латыни 0,047."""
    pr = lambda LL: [(x[-k:], y[:k]) for l in LL for x, y in zip(l, l[1:])]
    o = _mi_pairs(pr(L))
    f = [w for l in L for w in l]; rnd = random.Random(seed); s = 0.0
    for _ in range(B):
        sh = f[:]; rnd.shuffle(sh); i = 0; SH = []
        for l in L: SH.append(sh[i:i + len(l)]); i += len(l)
        s += _mi_pairs(pr(SH)) / B
    return o - s

# ── марковская цепь по знакам и перерождение словаря ────────────────────────

def markov(types_, order=2, seed=0, guard=200):
    """Породить словарь того же объёма и того же распределения длин
    цепью порядка order, обученной на types_."""
    rnd = random.Random(seed)
    tr = collections.defaultdict(collections.Counter)
    for w in types_:
        s = "^" * order + w + "$"
        for i in range(order, len(s)): tr[s[i - order:i]][s[i]] += 1
    pools = {k: [c for c, n in v.items() for _ in range(n)] for k, v in tr.items()}
    want = collections.Counter(len(w) for w in types_)
    out, got, g = set(), collections.Counter(), 0
    while len(out) < len(types_) and g < len(types_) * guard:
        g += 1
        ctx = "^" * order; w = ""
        while True:
            p_ = pools.get(ctx)
            if not p_: break
            c = p_[rnd.randrange(len(p_))]
            if c == "$": break
            w += c; ctx = (ctx + c)[-order:]
            if len(w) > 25: break      # отсечка как в density_null2: меняет поток случайных чисел
        if w and got[len(w)] < want.get(len(w), 0):
            if w not in out: out.add(w); got[len(w)] += 1
    return sorted(out)

def regeneration(types_, order=2, seed=0):
    """ДОЛЯ ПЕРЕРОЖДЕНИЯ: сколько порождённых цепью слов совпало с настоящими.
    На рукописи (цепь 2) даёт около 28,8 %; величина стохастична,
    разброс по 20 зёрнам 28,2-29,5 %, поэтому усреднять — см. regeneration_mean."""
    M = markov(types_, order, seed)
    if not M: return float("nan")
    return len(set(M) & set(types_)) / len(M)

def regeneration_mean(types_, order=2, seeds=range(5)):
    v = [regeneration(types_, order, s) for s in seeds]
    return st.mean(v), min(v), max(v)

# ── выравнивание словарей (две защищаемые процедуры, см. запись A6b) ────────

def match_mean_length(T, n, target_mean, seed=0, tol=0.25, tries=400, cap=3):
    """Выравнивание А: случайная выборка n типов, у которой СРЕДНЯЯ длина
    попадает в tol от целевой. Слова длиннее int(target_mean)+cap отброшены."""
    pool = [w for w in T if len(w) <= int(target_mean) + cap]
    rnd = random.Random(seed); best = None
    for _ in range(tries):
        s = rnd.sample(pool, min(n, len(pool)))
        m = st.mean(len(w) for w in s)
        if abs(m - target_mean) < tol: return sorted(s)
        if best is None or abs(m - target_mean) < best[0]: best = (abs(m - target_mean), s)
    return sorted(best[1])

def match_length_dist(T, target_lens, n, seed=0):
    """Выравнивание Б: из каждой полосы длин взять ту же долю, что у цели —
    совпадает ВСЁ распределение длин, а не только среднее."""
    rnd = random.Random(seed)
    byl = collections.defaultdict(list)
    for w in T: byl[len(w)].append(w)
    for k in byl: rnd.shuffle(byl[k])
    want = collections.Counter(target_lens)
    scale = n / max(sum(want.values()), 1)
    out = []
    for L, c in want.items():
        out += byl.get(L, [])[:int(round(c * scale))]
    return sorted(set(out))

# ── подписи последовательности ──────────────────────────────────────────────

def rank_corr(L, ranks=None):
    """Корреляция логарифмов частотных рангов соседних слов.
    У языков отрицательна, у рукописи +0,0797. Ранги считаются ОДИН РАЗ
    по всему корпусу — пересчёт на подвыборке смещает оценку."""
    tk = tokens(L)
    if ranks is None:
        c = collections.Counter(tk)
        ranks = {w: i + 1 for i, (w, _) in enumerate(c.most_common())}
    xs, ys = [], []
    for l in L:
        for a, b in zip(l, l[1:]):
            if a in ranks and b in ranks:
                xs.append(math.log(ranks[a])); ys.append(math.log(ranks[b]))
    if len(xs) < 2: return float("nan")
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs)); dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float("nan")

def len_autocorr(L, lag=1):
    """Автокорреляция длины слова на расстоянии lag."""
    a, b = [], []
    for l in L:
        for i in range(len(l) - lag):
            a.append(len(l[i])); b.append(len(l[i + lag]))
    if len(a) < 2: return float("nan")
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a)); db = math.sqrt(sum((y - mb) ** 2 for y in b))
    return num / (da * db) if da and db else float("nan")

def recurrence_profile(L, maxd=60, B=3, seed=5):
    """Профиль возврата: для каждого расстояния d — во сколько раз чаще слово
    возвращается через d, чем при перемешивании потока. Считаются ТОЛЬКО
    расстояния до СЛЕДУЮЩЕГО вхождения, ожидание берётся перемешиванием
    (B раз), а не закрытой формулой: закрытая форма для этой величины
    расходится с перестановкой, см. урок сессии 31.08."""
    f = tokens(L)
    pos = collections.defaultdict(list)
    for i, w in enumerate(f): pos[w].append(i)
    obs = collections.Counter()
    for v in pos.values():
        for a, b in zip(v, v[1:]):
            if b - a <= maxd: obs[b - a] += 1
    rnd = random.Random(seed); exp = collections.Counter()
    for _ in range(B):
        g = f[:]; rnd.shuffle(g); p2 = collections.defaultdict(list)
        for i, w in enumerate(g): p2[w].append(i)
        for v in p2.values():
            for a, b in zip(v, v[1:]):
                if b - a <= maxd: exp[b - a] += 1 / B
    return {d: (obs[d] / exp[d] if exp[d] > 0.5 else float("nan")) for d in range(1, maxd + 1)}

def recurrence(L, lo=1, hi=5, **kw):
    """Среднее превышение возврата на расстояниях lo..hi. На рукописи d1-5 даёт
    2,44, d6-20 — 1,86."""
    r = recurrence_profile(L, **kw)
    v = [r[d] for d in range(lo, hi + 1) if r.get(d, float("nan")) == r.get(d, float("nan"))]
    return st.mean(v) if v else float("nan")

def recurrence_decay(L, thr=1.05, maxd=60, **kw):
    """Расстояние, на котором профиль возврата выходит на единицу."""
    r = recurrence_profile(L, maxd=maxd, **kw)
    tail = [d for d in range(5, maxd + 1) if r.get(d, float("nan")) == r.get(d, float("nan")) and r[d] < thr]
    return tail[0] if tail else maxd

# ── разложение по аффиксам (алгоритм 1 статьи) ──────────────────────────────

def affix_decompose(words, cap=None, k=15, minrem=2, maxaff=3):
    """АЛГОРИТМ 1: тип выведен, если он равен аффикс + ДРУГОЙ ТИП СЛОВАРЯ.
    cap=None — весь словарь (настройка таблицы §3.2); cap=5000 — потолок
    в 5000 частых типов (настройка, описанная в §3.1). Настройка меняет
    результат: 57,2 % против 59,0 % и сдвиг плотности −0,33 против −0,19,
    см. запись A3b инвентаря.
    Возвращает (доля выведенных, доля сводящихся дважды и более, корни)."""
    cnt = collections.Counter(words)
    T = [w for w, _ in cnt.most_common(cap)] if cap else sorted(set(words))
    S = set(T)
    pre = collections.Counter(); suf = collections.Counter()
    for w in T:
        for L in range(1, maxaff + 1):
            if len(w) > L: pre[w[:L]] += 1; suf[w[-L:]] += 1
    P = [a for a, _ in pre.most_common(k)]; U = [a for a, _ in suf.most_common(k)]
    derived = {}
    for w in sorted(S, key=len):
        for a in P:
            if w.startswith(a) and w[len(a):] in S and len(w[len(a):]) >= minrem:
                derived[w] = w[len(a):]; break
        if w in derived: continue
        for a in U:
            if w.endswith(a) and w[:-len(a)] in S and len(w[:-len(a)]) >= minrem:
                derived[w] = w[:-len(a)]; break
    def core(w):
        seen = set()
        while w in derived and w not in seen: seen.add(w); w = derived[w]
        return w
    twice = 0
    for w in S:
        x, d, seen = w, 0, set()
        while x in derived and x not in seen: seen.add(x); x = derived[x]; d += 1
        if d >= 2: twice += 1
    return len(derived) / len(S), twice / len(S), {w: core(w) for w in S}

def strip_text(L, root):
    """Переписать текст корнями разложения."""
    return [[root.get(w, w) for w in l] for l in L]
