import urllib.request, urllib.parse, json, re
ARTS=["Maxwell's_equations","Schrödinger_equation","Navier–Stokes_equations","Riemann_zeta_function",
      "Fourier_transform","General_relativity","Quantum_field_theory","Lie_algebra","Fourier_series",
      "Partial_differential_equation","Matrix_(mathematics)","Eigenvalues_and_eigenvectors",
      "Gaussian_integral","Bessel_function","Laplace_transform","Tensor","Hilbert_space",
      "Dirac_equation","Noether's_theorem","Green's_function","Bayes'_theorem","Central_limit_theorem",
      "Stokes'_theorem","Taylor_series","Euler–Lagrange_equation","Hamiltonian_mechanics"]
out=[]
for a in ARTS:
    q=urllib.parse.urlencode({"action":"parse","page":a,"prop":"wikitext","format":"json","formatversion":"2"})
    try:
        req=urllib.request.Request(f"https://en.wikipedia.org/w/api.php?{q}", headers={"User-Agent":"research/1.0"})
        d=json.load(urllib.request.urlopen(req, timeout=25))
        t=d["parse"]["wikitext"]
    except Exception: continue
    out += re.findall(r"<math[^>]*>(.*?)</math>", t, re.S)
    out += re.findall(r":\s*<math[^>]*>(.*?)</math>", t, re.S)
tex="\n".join(out)
open("ref/latex_math.raw","w").write(tex)
print(f"  формул извлечено: {len(out)}, знаков: {len(tex):,}")
print("  пример:", out[5][:120] if len(out)>5 else "—")
