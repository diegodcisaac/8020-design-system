"""
construir.py: transforma a malha municipal do IBGE em base geografica do sistema.

Fonte: API de malhas do IBGE, versao 3, qualidade minima, intrarregiao municipio
  https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf}?formato=image/svg+xml&qualidade=minima&intrarregiao=municipio
  e a lista de municipios https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios?view=nivelado
  baixadas em 2026-09-06 para fonte/.

Saida, por UF: {sigla}-municipios.svg (viewBox 0 0 1000 H, um <path> por municipio com id="m{codigo}"
e data-nome) e {sigla}-municipios.json (codigo -> nome, centroide x e y na mesma grade).
Projecao: equirretangular com a longitude corrigida pelo cosseno da latitude media da UF.
"""
import json, math, re, sys, os
AQUI = os.path.dirname(os.path.abspath(__file__))
UFS = {"50": "ms", "52": "go"}
W = 1000.0

def parse_paths(svg):
    out = []
    for m in re.finditer(r'<path id="(\d+)" d="([^"]+)"', svg):
        code, d = m.group(1), m.group(2)
        subs, cur, x, y = [], [], 0.0, 0.0
        for cmd, args in re.findall(r'([MmLlHhVvZz])([^MmLlHhVvZz]*)', d):
            nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?(?:e-?\d+)?', args)]
            if cmd in 'Mm':
                if cur: subs.append(cur)
                if cmd == 'M' or not cur: x, y = nums[0], nums[1]
                else: x += nums[0]; y += nums[1]
                cur = [(x, y)]
                for i in range(2, len(nums), 2):
                    if cmd == 'M': x, y = nums[i], nums[i+1]
                    else: x += nums[i]; y += nums[i+1]
                    cur.append((x, y))
            elif cmd == 'l':
                for i in range(0, len(nums), 2): x += nums[i]; y += nums[i+1]; cur.append((x, y))
            elif cmd == 'L':
                for i in range(0, len(nums), 2): x, y = nums[i], nums[i+1]; cur.append((x, y))
            elif cmd == 'h':
                for v in nums: x += v; cur.append((x, y))
            elif cmd == 'H':
                for v in nums: x = v; cur.append((x, y))
            elif cmd == 'v':
                for v in nums: y += v; cur.append((x, y))
            elif cmd == 'V':
                for v in nums: y = v; cur.append((x, y))
            elif cmd in 'Zz':
                if cur: subs.append(cur); cur = []
        if cur: subs.append(cur)
        subs = [[(px * 1e-4, py * 1e-4) for px, py in s] for s in subs]  # lon, lat (unidades do IBGE: 1e-4 grau)
        out.append((code, subs))
    return out

def build(uf, sigla):
    svg = open(os.path.join(AQUI, "fonte", f"ibge-{uf}.svg"), encoding="utf-8").read()
    nomes = {str(m["municipio-id"]): m["municipio-nome"] for m in json.load(open(os.path.join(AQUI, "fonte", f"ibge-{uf}-municipios.json"), encoding="utf-8"))}
    paths = parse_paths(svg)
    lons = [p[0] for _, subs in paths for s in subs for p in s]; lats = [p[1] for _, subs in paths for s in subs for p in s]
    lon0, lon1, lat0, lat1 = min(lons), max(lons), min(lats), max(lats)
    k = math.cos(math.radians((lat0 + lat1) / 2))
    escala = W / ((lon1 - lon0) * k)
    H = (lat1 - lat0) * escala
    def proj(lon, lat): return ((lon - lon0) * k * escala, (lat1 - lat) * escala)
    out, cent = [], {}
    for code, subs in paths:
        ds, sx, sy, n = [], 0.0, 0.0, 0
        for s in subs:
            pts = [proj(lon, lat) for lon, lat in s]
            ds.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
            for x, y in pts: sx += x; sy += y; n += 1
        nome = nomes.get(code, code)
        cent[code] = {"nome": nome, "x": round(sx / n, 1), "y": round(sy / n, 1)}
        out.append(f'<path id="m{code}" data-nome="{nome}" d="{"".join(ds)}"/>')
    corpo = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" data-uf="{sigla.upper()}" data-lon0="{lon0:.4f}" data-lat1="{lat1:.4f}" data-escala="{escala:.3f}" data-k="{k:.5f}">\n'
             f'<!-- base geografica do 8020-DS: {len(out)} municipios de {sigla.upper()}, malha IBGE 2022 (qualidade minima), projecao equirretangular. Gerado por construir.py. -->\n'
             f'<g class="municipios">\n' + "\n".join(out) + '\n</g>\n</svg>\n')
    open(os.path.join(AQUI, f"{sigla}-municipios.svg"), "w", encoding="utf-8").write(corpo)
    json.dump(cent, open(os.path.join(AQUI, f"{sigla}-municipios.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(sigla, len(out), "municipios;", f"viewBox 0 0 {W:.0f} {H:.0f};", "lon", round(lon0, 3), round(lon1, 3), "lat", round(lat0, 3), round(lat1, 3), "->", round(os.path.getsize(os.path.join(AQUI, f"{sigla}-municipios.svg")) / 1024), "KB")

if __name__ == "__main__":
    for uf, sigla in UFS.items(): build(uf, sigla)
