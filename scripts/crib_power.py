# -*- coding: utf-8 -*-
"""ЕСТЬ ЛИ У КРИБОВОЙ ПОДГОНКИ РАЗРЕШАЮЩАЯ СПОСОБНОСТЬ.

ЧТО ДЕЛАЮТ В ПОЛЕ. У аптечных страниц (f88-f102) нарисованы части растений и
проставлены подписи — 194 штуки на 15 страницах. Крибовый ход: опознать
растение по рисунку, принять подпись за название, вывести соответствия
«знак -> буква» и распространить на весь текст. Так сделано множество разборов,
ни один не принят.

ЧТО ПРОВЕРЯЕМ. НЕ «какое растение на f88r» — определений у нас нет, они спорны,
и от них ничего не зависит. Проверяем САМ МЕТОД: способна ли подгонка отличить
правильную цель от произвольной. Если подписи с равным успехом читаются как
названия трав, как латынь и как случайные буквы, удачная подгонка НЕ ЕСТЬ
ДОВОД — и это показывается без единого определения растения.

ДВЕ СТЕПЕНИ СВОБОДЫ, КОТОРЫМИ ПОЛЬЗУЮТСЯ НА ДЕЛЕ, обе воспроизведены:
  1. отображение — какой знак какой буквой читать, включая право читать знак
     как пустоту;
  2. цель — у растения много названий (латынь, греческий, народные,
     разнописания), поэтому подпись сравнивается с ЛУЧШИМ словом набора.

НАБОРЫ, выровнены по распределению длин подписей:
  A названия трав (сверены с травником Калпепера)  B латынь
  C английский                                     D случайные буквы (пол шкалы)

ПОЛОЖИТЕЛЬНЫЙ КОНТРОЛЬ. Подписи заменяются на названия из A, зашифрованные
ИЗВЕСТНОЙ подстановкой. Подгонщик обязан их восстановить: без этого
отрицательный итог означал бы негодный прибор, а не отсутствие явления (урок
зодиака, и первый заход этого опыта на нём же и провалился — слабый
оптимизатор давал 0,60 при достижимой 1,00).

КРИТЕРИЙ, НАЗНАЧЕН ДО ЗАПУСКА. Разрешающая способность есть, только если на
настоящих подписях преимущество A над лучшим из B и C составляет хотя бы
ПОЛОВИНУ преимущества, показанного на положительном контроле.
"""
import re, random, collections, statistics as st
from functools import lru_cache

def clean(t):
    t = re.sub(r"<[^>]*>", "", t)                      # <!119>, <-> — разметка IVTFF
    t = re.sub(r"\[([^\]:.]+)[:.][^\]]*\]", r"\1", t)
    t = re.sub(r"\{[^}]*\}", "", t); t = re.sub(r"@\d+;", "", t)
    return t.replace("?", "")

LAB = []
for ln in open("ZL3b-n.txt", encoding="utf-8", errors="ignore"):
    m = re.match(r"<f\d+[rv]\d*\.\d+,[@&+*]Lf>\s*(.*)", ln)
    if m:
        w = "".join(x for x in re.split(r"[.,]", clean(m.group(1).strip())) if x)
        if w: LAB.append(w)
GL = collections.Counter(g for w in LAB for g in w)
print("=" * 92); print("ПОДПИСИ АПТЕЧНОГО РАЗДЕЛА"); print("=" * 92)
print(f"   {len(LAB)} подписей, средняя длина {st.mean(map(len,LAB)):.2f}, знаков {len(GL)}")
print(f"   {' '.join(LAB[:14])} …")

HERBS = """agrimony alkanet angelica anise arnica asparagus avens balm barberry basil
betony bilberry bistort borage bramble bugloss burdock burnet calamint caraway
carrot catmint celandine celery centaury chamomile chervil chicory cinquefoil
cleavers clover coltsfoot columbine comfrey coriander cowslip cress cudweed
cumin daisy dandelion darnel dill dodder elder elecampane endive eyebright
fennel fenugreek fern feverfew figwort flax fleabane fumitory garlic gentian
germander goldenrod gromwell groundsel hawkweed hawthorn hazel hellebore
hemlock henbane holly honeysuckle horehound horsetail houseleek hyssop juniper
knapweed knotgrass lavender leek lettuce lily liquorice liverwort lovage
lungwort madder maidenhair mallow mandrake marigold marjoram meadowsweet
melilot mercury mint mistletoe motherwort mugwort mullein mustard nettle
nightshade nutmeg onion orach orpine parsley parsnip pellitory pennyroyal
peony periwinkle pimpernel plantain polypody poppy primrose privet purslane
radish ragwort rampion rhubarb rocket rose rosemary rue saffron sage samphire
sanicle savory saxifrage scabious selfheal senna sorrel southernwood spearmint
speedwell spikenard spleenwort strawberry sundew tansy tarragon teasel thistle
thyme toadflax tormentil trefoil valerian vervain vine violet wallflower walnut
watercress willow woad wormwood woundwort yarrow""".split()
CULP = set(open("ref/g_herbal.clean", encoding="utf-8", errors="ignore").read().split())
print(f"   набор A: {len(HERBS)} названий, в травнике Калпепера {sum(1 for h in HERBS if h in CULP)}")

AL = "abcdefghijklmnopqrstuvwxyz"; TGT = AL + " "
rnd = random.Random(11); LENS = [len(w) for w in LAB]; K = 100
def wpool(fn):
    return sorted({w for w in open(f"ref/{fn}", encoding="utf-8", errors="ignore").read().split()
                   if w.isalpha() and 2 < len(w) < 14})
def match_len(pool, k):
    by = collections.defaultdict(list)
    for w in pool: by[len(w)].append(w)
    out = []
    for L in [rnd.choice(LENS) for _ in range(k)]:
        c = [l for l in sorted(by) if by[l]]
        b = min(c, key=lambda x: abs(x - L))
        out.append(by[b].pop(rnd.randrange(len(by[b]))))
    return out
POOLS = {"A травы": match_len(HERBS*3, K), "B латынь": match_len(wpool("latin.clean"), K),
         "C английский": match_len(wpool("english.clean"), K),
         "D случайные буквы": ["".join(rnd.choice(AL) for _ in range(rnd.choice(LENS))) for _ in range(K)]}

@lru_cache(maxsize=None)
def sim(a, b):
    if not a or not b: return 0.0
    prev = [0]*(len(b)+1)
    for x in a:
        cur = [0]*(len(b)+1)
        for j, y in enumerate(b, 1): cur[j] = prev[j-1]+1 if x == y else max(prev[j], cur[j-1])
        prev = cur
    return prev[-1]/max(len(a), len(b))

def lcs_ratio(a, b):
    prev = [0]*(len(b)+1)
    for x in a:
        cur = [0]*(len(b)+1)
        for k, y in enumerate(b, 1): cur[k] = prev[k-1]+1 if x == y else max(prev[k], cur[k-1])
        prev = cur
    return prev[-1]/max(len(a), len(b))

def fit(labs, pool, restarts=3, seed=0):
    """ПОКООРДИНАТНЫЙ ПОДЪЁМ: для каждого знака перебираются ВСЕ 27 значений.
    Ускорение: кеш по ОТОБРАЖЁННОЙ строке + отсечение по верхней границе LCS
    (размер пересечения мультимножеств) — полный LCS считается только там,
    где кандидат в принципе способен побить текущий максимум."""
    r = random.Random(seed); gl = sorted({g for w in labs for g in w})
    hits = {g: [i for i, w in enumerate(labs) if g in w] for g in gl}
    PC = [(p_, collections.Counter(p_), len(p_)) for p_ in pool]
    memo = {}
    def one(m, w):
        s_ = "".join(m.get(g, "") for g in w).replace(" ", "")
        v = memo.get(s_)
        if v is not None: return v
        if not s_: memo[s_] = 0.0; return 0.0
        cs = collections.Counter(s_); ls = len(s_); b = 0.0
        for p_, cp, lp in PC:
            mx = ls if ls > lp else lp
            ub = 0
            for ch, n in cs.items():
                o = cp.get(ch)
                if o: ub += n if n < o else o
            if ub <= b*mx: continue
            x = lcs_ratio(s_, p_)
            if x > b: b = x
        memo[s_] = b; return b
    best, bm = -1.0, None
    for _ in range(restarts):
        m = {g: r.choice(TGT) for g in gl}
        per = [one(m, w) for w in labs]; cur = sum(per)/len(per)
        for _ in range(6):
            moved = False
            for g in gl:
                keep, kv, kper = m[g], cur, None
                base = sum(per) - sum(per[i] for i in hits[g])
                for t in TGT:
                    if t == m[g]: continue
                    old = m[g]; m[g] = t
                    upd = {i: one(m, labs[i]) for i in hits[g]}
                    s2 = (base + sum(upd.values()))/len(per)
                    m[g] = old
                    if s2 > kv: keep, kv, kper = t, s2, upd
                if kper is not None:
                    m[g] = keep; cur = kv
                    for i, v in kper.items(): per[i] = v
                    moved = True
            if not moved: break
        if cur > best: best, bm = cur, dict(m)
    return best, bm

# ── ПОЛОЖИТЕЛЬНЫЙ КОНТРОЛЬ ──────────────────────────────────────────────────
print("\n" + "=" * 92)
print("ПОЛОЖИТЕЛЬНЫЙ КОНТРОЛЬ: подписи = названия трав под ИЗВЕСТНОЙ подстановкой")
print("=" * 92)
rc = random.Random(5); keys = list(AL); rc.shuffle(keys); ciph = dict(zip(AL, keys))
FAKE = ["".join(ciph[c] for c in w) for w in POOLS["A травы"]][:len(LAB)]
ctl = {}
for nm in ("A травы", "B латынь", "C английский", "D случайные буквы"):
    v, _ = fit(FAKE, POOLS[nm], seed=1); ctl[nm] = v
    print(f"   против набора {nm:>18s}:  {v:.4f}")
gap_ctl = ctl["A травы"] - max(ctl["B латынь"], ctl["C английский"])
print(f"   ПРЕИМУЩЕСТВО ПРАВИЛЬНОЙ ЦЕЛИ: {gap_ctl:+.4f}"
      f"   -> прибор {'ГОДЕН' if gap_ctl > 0.15 else 'НЕГОДЕН'}")

# ── НАСТОЯЩИЕ ПОДПИСИ ───────────────────────────────────────────────────────
print("\n" + "=" * 92)
print("НАСТОЯЩИЕ ПОДПИСИ ПРОТИВ ЧЕТЫРЁХ НАБОРОВ (тот же бюджет)")
print("=" * 92)
res = {}
for nm, pool in POOLS.items():
    v, m = fit(LAB, pool, seed=2); res[nm] = v
    rd = " ".join(f"{g}{'_' if m[g]==' ' else m[g]}" for g in sorted(m)[:12])
    print(f"   {nm:>18s}  подгонка {v:.4f}   чтение: {rd}")

gap_real = res["A травы"] - max(res["B латынь"], res["C английский"])
print("\n" + "=" * 92); print("ИТОГ ПО КРИТЕРИЮ, ОБЪЯВЛЕННОМУ ДО ЗАПУСКА"); print("=" * 92)
print(f"   преимущество трав над лучшим из латыни/английского : {gap_real:+.4f}")
print(f"   то же на положительном контроле                    : {gap_ctl:+.4f}")
print(f"   требуется не меньше половины                       : {gap_ctl/2:+.4f}")
print(f"\n   У КРИБОВОЙ ПОДГОНКИ ЕСТЬ РАЗРЕШАЮЩАЯ СПОСОБНОСТЬ: "
      f"{'ДА' if (gap_ctl > 0.15 and gap_real >= gap_ctl/2) else 'НЕТ'}")
