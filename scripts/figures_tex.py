# -*- coding: utf-8 -*-
"""ТЕ ЖЕ ШЕСТЬ ФИГУР, НО НАТИВНЫМ TikZ — для подачи на arXiv.

Почему не конвертация SVG: конвертера на машине нет, а PDF/EPS в пакете это
внешние двоичные файлы, которые ни прогон, ни рецензент проверить не могут.
TikZ собирается тем же LaTeX'ом, что и текст, и числа берутся ИЗ ТОГО ЖЕ
МАНИФЕСТА, что у scripts/figures.py, — значит check_paper.py продолжает
держать фигуру и абзац в согласии.

Числа вне манифеста помечены именем скрипта, который их посчитал (решёточные
прогоны, в манифест не влезающие по времени) — ровно как в figures.py.

Пишет arxiv/fig/figN.tex, каждый — самостоятельная tikzpicture.
"""
import json, os, sys

OUT = "arxiv/fig"
os.makedirs(OUT, exist_ok=True)
NUM = {}
if os.path.exists("data/paper_numbers.json"):
    NUM = {r["key"]: r["value"] for r in json.load(open("data/paper_numbers.json", encoding="utf-8"))}
def n(key, fallback):
    if key in NUM: return NUM[key]
    print(f"  ! {key} нет в манифесте, беру запасное {fallback}", file=sys.stderr)
    return fallback

HEAD = r"""%% автогенерация: scripts/figures_tex.py — руками не править
\begin{tikzpicture}[x=1mm,y=1mm,font=\sffamily\scriptsize]
\definecolor{ink}{HTML}{1A1A1A}\definecolor{inkii}{HTML}{5A5A5A}
\definecolor{inkiii}{HTML}{8A8A8A}\definecolor{rule}{HTML}{D0D0D0}
\definecolor{fill}{HTML}{2B2B2B}\definecolor{fillii}{HTML}{9A9A9A}
\definecolor{filliii}{HTML}{C8C8C8}
"""
TAIL = "\\end{tikzpicture}\n"

def save(name, body):
    open(f"{OUT}/{name}.tex", "w", encoding="utf-8").write(HEAD + body + TAIL)

def hbars(rows, mx, w, title, sub, note, ticks, fmt="{:.1f}\\%", lab_w=34):
    """горизонтальные полосы; rows = (подпись, значение, второе значение или None)"""
    o = [f"\\node[anchor=west,font=\\sffamily\\small\\bfseries,text=ink] at (0,{len(rows)*11+13}) {{{title}}};",
         f"\\node[anchor=west,text=inkii] at (0,{len(rows)*11+8}) {{{sub}}};"]
    for t in ticks:
        x = lab_w + w * t / mx
        col = "ink" if t == 0 else "rule"
        o.append(f"\\draw[{col}] ({x},{len(rows)*11+3}) -- ({x},1);")
        o.append(f"\\node[below,text=inkiii] at ({x},1) {{{t}\\%}};")
    for i, (lab, a, b) in enumerate(rows):
        y = (len(rows) - i) * 11 - 5
        o.append(f"\\node[anchor=east,text=ink] at ({lab_w-2},{y+1.5}) {{{lab}}};")
        if b is None:
            o.append(f"\\fill[fill] ({lab_w},{y}) rectangle ({lab_w+w*a/mx},{y+5});")
            o.append(f"\\node[anchor=west,font=\\sffamily\\scriptsize\\bfseries,text=ink] at ({lab_w+w*a/mx+1.5},{y+2.5}) {{{fmt.format(a)}}};")
        else:
            o.append(f"\\fill[fillii] ({lab_w},{y+3}) rectangle ({lab_w+w*a/mx},{y+6});")
            o.append(f"\\fill[filliii] ({lab_w},{y-1}) rectangle ({lab_w+w*b/mx},{y+2});")
            o.append(f"\\node[anchor=west,text=inkii] at ({lab_w+w*a/mx+1.5},{y+4.5}) {{{fmt.format(a)}}};")
            o.append(f"\\node[anchor=west,text=inkii] at ({lab_w+w*b/mx+1.5},{y+0.5}) {{{fmt.format(b)}}};")
    o.append(f"\\node[anchor=west,text=inkiii,align=left] at (0,-7) {{{note}}};")
    return "\n".join(o) + "\n"

# ── фиг. 1 ──────────────────────────────────────────────────────────────────
save("fig1", hbars(
    [("Voynichese", n("regen_voy_head", 28.8), None),
     ("Italian", n("regen_ita_meanlen", 5.9), n("regen_ita_lendist", 6.6)),
     ("Spanish", n("regen_spa_meanlen", 2.6), n("regen_spa_lendist", 5.7)),
     ("Latin",   n("regen_lat_meanlen", 1.7), n("regen_lat_lendist", 3.5))],
    mx=32.0, w=80, ticks=(0, 10, 20, 30),
    title="Chain regeneration of the vocabulary",
    sub="share of words from a second-order character chain that are real types",
    note=r"Upper bar: matched on mean type length. Lower bar: matched on the whole length"
         r"\\distribution. All sub-vocabularies are 7,205 types; the gap is 4--17$\times$"
         r"\\depending on the matching."))

# ── фиг. 4 ──────────────────────────────────────────────────────────────────
# scripts/construct*.py, scripts/threshold.py — решёточные прогоны, вне манифеста
save("fig4", hbars(
    [("selection of whole words", 26, None),
     ("hybrid: memory ignores the boundary", 41, None),
     ("memory filtered for legality", 55, None),
     ("memory weighted by transition frequency", 82, None)],
    mx=100.0, w=70, ticks=(0, 25, 50, 75, 100), fmt="{:.0f}\\%", lab_w=54,
    title="Reaching the word-boundary information",
    sub="best three-character junction attained while the other three signatures are held",
    note=r"Filtering preserves which boundary transitions are possible; weighting preserves"
         r"\\their frequencies. The junction lives in the distribution, not in its support ---"
         r"\\which is what the 55 $\to$ 82 step shows."))

# ── фиг. 2: типы против токенов по длине слова ─────────────────────────────
# scripts/typetoken2.py
def fig2():
    L=[3,4,5,6,7]; tok=[2.03,4.52,5.76,4.50,3.20]; typ=[2.48,2.43,1.55,1.98,1.60]
    x0,y0,w,h,mx=14,8,78,42,6.0
    px=lambda i: x0+w*i/(len(L)-1); py=lambda v: y0+h*(v-1)/(mx-1)
    o=[r"\node[anchor=west,font=\sffamily\small\bfseries,text=ink] at (0,%.1f) {Slot rigidity: the gap with Latin depends on the unit};"%(y0+h+11),
       r"\node[anchor=west,text=inkii] at (0,%.1f) {excess of glyph--position mutual information over a within-word shuffle, Voynichese $\div$ Latin};"%(y0+h+6)]
    for v in range(1,7):
        o.append(f"\\draw[{'rule' if v>1 else 'ink'}] ({x0},{py(v):.2f}) -- ({x0+w},{py(v):.2f});")
        o.append(f"\\node[anchor=east,text=inkiii] at ({x0-1.5},{py(v):.2f}) {{{v}$\\times$}};")
    for i,v in enumerate(L):
        o.append(f"\\node[below,text=inkii] at ({px(i):.2f},{y0-1}) {{{v}}};")
    o.append(f"\\node[below,text=inkiii] at ({x0+w/2},{y0-5}) {{word length (characters)}};")
    o.append(r"\draw[fill,line width=.5pt] "+" -- ".join(f"({px(i):.2f},{py(v):.2f})" for i,v in enumerate(tok))+";")
    o.append(r"\draw[inkiii,line width=.5pt,dashed] "+" -- ".join(f"({px(i):.2f},{py(v):.2f})" for i,v in enumerate(typ))+";")
    for i,v in enumerate(tok): o.append(f"\\fill[fill] ({px(i):.2f},{py(v):.2f}) circle (.9);")
    for i,v in enumerate(typ): o.append(f"\\fill[inkiii] ({px(i):.2f},{py(v):.2f}) circle (.9);")
    o.append(f"\\node[anchor=west,font=\\sffamily\\scriptsize\\bfseries,text=ink] at ({px(3)+2:.2f},{py(tok[3])+3:.2f}) {{measured on tokens}};")
    o.append(f"\\node[anchor=west,text=inkii] at ({px(3)+2:.2f},{py(typ[3])-3:.2f}) {{measured on types}};")
    o.append(f"\\draw[inkiii,dotted] ({px(0):.2f},{py(typ[0])+2:.2f}) -- ({px(0):.2f},{py(tok[0])-2:.2f});")
    o.append(f"\\node[anchor=west,text=inkiii,align=left] at ({px(0)+2:.2f},{y0+h-4:.2f}) {{at length 3\\\\the order reverses}};")
    return "\n".join(o)+"\n"
save("fig2", fig2())

# ── фиг. 3: одна величина, три алгоритма ───────────────────────────────────
# scripts/one_instrument.py, scripts/morf_spread.py
def fig3():
    rows=[("1\\ \\ affix + vocabulary word",-15.83,None),
          ("2\\ \\ Goldsmith signatures",-1.02,None),
          ("3\\ \\ Morfessor Baseline",-10.82,(-11.26,-10.18))]
    x0,w,lo,hi=52,60,-18.0,1.0
    px=lambda v: x0+w*(v-lo)/(hi-lo)
    o=[r"\node[anchor=west,font=\sffamily\small\bfseries,text=ink] at (0,46) {One quantity, three decompositions};",
       r"\node[anchor=west,text=inkii] at (0,41) {shift in type-level slot rigidity after stripping affixes (ZL3b, length 4)};"]
    for v in (-15,-10,-5,0):
        o.append(f"\\draw[{'ink' if v==0 else 'rule'}] ({px(v):.2f},36) -- ({px(v):.2f},8);")
        o.append(f"\\node[below,text=inkiii] at ({px(v):.2f},8) {{${v}$}};")
    for i,(lab,v,sp) in enumerate(rows):
        y=32-i*8
        o.append(f"\\node[anchor=east,text=ink] at ({x0-2},{y}) {{{lab}}};")
        if sp:
            o.append(f"\\fill[filliii] ({px(sp[0]):.2f},{y-2}) rectangle ({px(sp[1]):.2f},{y+2});")
        o.append(f"\\draw[fill,line width=.7pt] ({px(0):.2f},{y}) -- ({px(v):.2f},{y});")
        o.append(f"\\fill[fill] ({px(v):.2f},{y}) circle (1);")
        side="west" if px(v)<x0+w*0.25 else "east"
        dx=2 if side=="west" else -2
        o.append(f"\\node[anchor={side},font=\\sffamily\\scriptsize\\bfseries,text=ink] at ({px(v)+dx:.2f},{y+3.4}) {{${v:+.2f}$}};")
    o.append(f"\\fill[filliii] ({x0},3) rectangle ({x0+6},6);")
    o.append(f"\\node[anchor=west,text=inkiii] at ({x0+7.5},4.5) {{spread over five seeds}};")
    o.append(r"\node[anchor=west,text=inkiii,align=left] at (0,-4) {Morfessor has no seed of its own; its row is a mean of five runs, and Latin's own"
             r"\\shift changes sign between them. The spread between algorithms is the finding: no"
             r"\\single number should be quoted without the procedure.};")
    return "\n".join(o)+"\n"
save("fig3", fig3())

# ── фиг. 5: порог был несущим ──────────────────────────────────────────────
# scripts/threshold.py
def fig5():
    th=[(65,23),(70,18),(75,6),(80,2),(85,0)]
    x0,y0,w,h,mx=12,10,76,36,24
    o=[r"\node[anchor=west,font=\sffamily\small\bfseries,text=ink] at (0,%d) {The threshold was load-bearing};"%(y0+h+11),
       r"\node[anchor=west,text=inkii] at (0,%d) {configurations of 54 reaching all four signatures, by the threshold called ``reached''};"%(y0+h+6)]
    for v in (0,6,12,18,24):
        y=y0+h*v/mx
        o.append(f"\\draw[{'rule' if v else 'ink'}] ({x0},{y:.2f}) -- ({x0+w},{y:.2f});")
        o.append(f"\\node[anchor=east,text=inkiii] at ({x0-1.5},{y:.2f}) {{{v}}};")
    bw=w/len(th)*0.46
    for i,(t,c) in enumerate(th):
        cx=x0+w*(i+0.5)/len(th); hh=h*c/mx
        col="fill" if t==70 else "fillii"
        if c: o.append(f"\\fill[{col}] ({cx-bw/2:.2f},{y0}) rectangle ({cx+bw/2:.2f},{y0+hh:.2f});")
        bold="\\bfseries" if t==70 else ""
        o.append(f"\\node[above,font=\\sffamily\\scriptsize{bold},text=ink] at ({cx:.2f},{y0+hh:.2f}) {{{c}}};")
        o.append(f"\\node[below,font=\\sffamily\\scriptsize{bold},text={'ink' if t==70 else 'inkii'}] at ({cx:.2f},{y0-1}) {{{t}\\%}};")
    o.append(f"\\node[below,text=inkiii] at ({x0+w/2},{y0-5}) {{threshold declared in advance}};")
    o.append(r"\node[anchor=west,text=inkiii,align=left] at (0,-1) {Stated without a threshold: the best worst-of-four ratio anywhere on the grid is"
             r"\\82\%, with a median of 58\%.};")
    return "\n".join(o)+"\n"
save("fig5", fig5())

# ── фиг. 6: расхождение начала строки по знакам ────────────────────────────
# scripts/line_residual.py, scripts/line_null2.py
def fig6():
    data=[("d",15.4,8.4,12.7),("s",14.7,11.7,11.8),("y",14.7,3.5,8.2),
          ("o",13.6,21.4,17.9),("q",13.0,15.9,15.8),("t",9.7,1.9,5.3),
          ("p",9.3,0.5,3.9),("c",3.7,20.4,12.2),("a",0.4,6.0,3.7)]
    x0,y0,w,h,mx=12,14,84,36,23.0
    cw=w/len(data)
    o=[r"\node[anchor=west,font=\sffamily\small\bfseries,text=ink] at (0,%d) {What prepending does not account for at the line start};"%(y0+h+14),
       r"\node[anchor=west,text=inkii] at (0,%d) {first character of the first word of a line, against mid-line words and against a};"%(y0+h+9),
       r"\node[anchor=west,text=inkii] at (0,%d) {prepending-only model at the rate the observed length gain implies ($p=0.40$)};"%(y0+h+5)]
    for v in (0,5,10,15,20):
        y=y0+h*v/mx
        o.append(f"\\draw[{'rule' if v else 'ink'}] ({x0},{y:.2f}) -- ({x0+w},{y:.2f});")
        o.append(f"\\node[anchor=east,text=inkiii] at ({x0-1.5},{y:.2f}) {{{v}\\%}};")
    for i,(ch,obs,mid,pred) in enumerate(data):
        cx=x0+cw*(i+0.5)
        o.append(f"\\fill[fill] ({cx-2.6:.2f},{y0}) rectangle ({cx-0.3:.2f},{y0+h*obs/mx:.2f});")
        o.append(f"\\fill[filliii] ({cx+0.3:.2f},{y0}) rectangle ({cx+2.6:.2f},{y0+h*mid/mx:.2f});")
        yp=y0+h*pred/mx
        o.append(f"\\draw[ink,line width=.5pt,dashed] ({cx-3.2:.2f},{yp:.2f}) -- ({cx+3.2:.2f},{yp:.2f});")
        o.append(f"\\node[below,font=\\ttfamily\\scriptsize,text=ink] at ({cx:.2f},{y0-1}) {{{ch}}};")
        r=obs-pred
        if abs(r)>=4: o.append(f"\\node[below,text=inkii] at ({cx:.2f},{y0-4.6}) {{${r:+.0f}$}};")
    o.append(f"\\node[anchor=east,text=inkiii] at ({x0-1.5},{y0-6}) {{residual}};")
    o.append(f"\\fill[fill] ({x0},2) rectangle ({x0+4},5);")
    o.append(f"\\node[anchor=west,text=inkii] at ({x0+5.5},3.5) {{line-initial}};")
    o.append(f"\\fill[filliii] ({x0+26},2) rectangle ({x0+30},5);")
    o.append(f"\\node[anchor=west,text=inkii] at ({x0+31.5},3.5) {{mid-line}};")
    o.append(f"\\draw[ink,line width=.5pt,dashed] ({x0+48},3.5) -- ({x0+54},3.5);")
    o.append(f"\\node[anchor=west,text=inkii] at ({x0+55.5},3.5) {{predicted by prepending alone}};")
    o.append(r"\node[anchor=west,text=inkiii,align=left] at (0,-3) {Prepending at the rate its own length signature implies produces a divergence of"
             r"\\0.186 against the observed 0.385.};")
    return "\n".join(o)+"\n"
save("fig6", fig6())
print(f"собрано {len(os.listdir(OUT))} фигур в {OUT}/")
