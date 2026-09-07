# -*- coding: utf-8 -*-
"""
gerar-brand.py: escreve tokens/brand.json a partir de tokens/8020.css.
Lê os tokens da base e dos dois momentos, compõe cada rgba sobre o papel
do momento, mede o contraste WCAG de todo par de texto e fundo e a
separação dos degraus da rampa, e grava as três camadas (primitivos,
semânticos, componentes) mais a matriz de contraste com o uso permitido.
Rodar de dentro de v4/tokens: python3 gerar-brand.py
"""
import json, math, os, re
AQUI = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(AQUI, "8020.css"), encoding="utf-8").read()

def bloco(seletor):
    m = re.search(re.escape(seletor) + r"\s*\{(.*?)\n\}", CSS, re.S); return m.group(1)
def tokens(txt):
    out = {}
    for m in re.finditer(r"--([a-z0-9-]+)\s*:\s*([^;]+);", txt): out[m.group(1)] = m.group(2).strip()
    return out
RAIZ = tokens(bloco(":root")); LARANJA = tokens(bloco(".tema-laranja")); ESCURO = tokens(bloco(".tema-escuro"))

def resolver(v, ctx, prof=0):
    v = v.strip()
    m = re.fullmatch(r"var\(--([a-z0-9-]+)\)", v)
    if m and prof < 8: return resolver(ctx.get(m.group(1), RAIZ.get(m.group(1), v)), ctx, prof + 1)
    return v
def cor(v):
    """devolve (r, g, b, a) em 0 a 1 ou None"""
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-f]{6})", v, re.I)
    if m: h = m.group(1); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4)) + (1.0,)
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+))?\s*\)", v)
    if m: return (int(m.group(1)) / 255, int(m.group(2)) / 255, int(m.group(3)) / 255, float(m.group(4) or 1))
    return None
def compor(fg, bg): a = fg[3]; return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))
def hexa(rgb): return "#" + "".join("%02x" % round(c * 255) for c in rgb)
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum(rgb): l = [lin(c) for c in rgb]; return 0.2126 * l[0] + 0.7152 * l[1] + 0.0722 * l[2]
def contraste(a, b): x, y = lum(a), lum(b); return (max(x, y) + 0.05) / (min(x, y) + 0.05)
def oklab(rgb):
    l_ = [lin(c) for c in rgb]
    l = (0.4122214708 * l_[0] + 0.5363325363 * l_[1] + 0.0514459929 * l_[2]) ** (1/3)
    m = (0.2119034982 * l_[0] + 0.6806995451 * l_[1] + 0.1073969566 * l_[2]) ** (1/3)
    s = (0.0883024619 * l_[0] + 0.2817188376 * l_[1] + 0.6299787005 * l_[2]) ** (1/3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s, 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s, 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)
def dE(a, b): p, q = oklab(a), oklab(b); return 100 * math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(3)))

MOMENTOS = [("papel", {}), ("laranja", LARANJA), ("escuro", ESCURO)]
PAPEIS_TEXTO = ["ink", "ink-body", "ink-soft", "muted", "meta", "accent"]
FUNDOS = ["paper", "surface", "surface-2"]

def valor(nome, ctx): return resolver(ctx.get(nome, RAIZ.get(nome, "")), {**RAIZ, **ctx})

semanticos, matriz, rampas = {}, [], {}
for nome, ctx in MOMENTOS:
    chao = cor(valor("paper", ctx))
    sem = {}
    for k in ["paper", "surface", "surface-2", "ink", "ink-body", "ink-soft", "muted", "meta", "rule", "rule-strong", "hairline", "accent", "accent-ink", "floor", "floor-ink", "focus", "negative", "dado-1", "dado-2", "dado-3", "dado-4", "dado-0"]:
        v = valor(k, ctx); c = cor(v)
        sem[k] = {"valor": v, "composto_sobre_papel": hexa(compor(c, chao)) if c else None}
    semanticos[nome] = sem
    for fundo in FUNDOS:
        bg = compor(cor(valor(fundo, ctx)), chao)
        for papel in PAPEIS_TEXTO:
            if papel == "accent" and nome != "papel": continue
            fg = compor(cor(valor(papel, ctx)), bg); r = contraste(fg, bg)
            nivel = "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA-grande" if r >= 3 else "reprova"
            uso = {"AAA": "qualquer texto", "AA": "qualquer texto a partir de 11,5 px", "AA-grande": "só texto de 24 px, ou 19 px em peso 700 ou mais", "reprova": "não usar para texto"}[nivel]
            matriz.append({"momento": nome, "fg": papel, "bg": fundo, "fg_hex": hexa(fg), "bg_hex": hexa(bg), "ratio": round(r, 2), "nivel": nivel, "uso": uso})
    # branco sobre o acento e o chão
    if nome == "papel":
        for fg_n, bg_n in [("accent-ink", "accent"), ("floor-ink", "floor"), ("paper", "ink")]:
            fg = compor(cor(valor(fg_n, ctx)), chao); bg = compor(cor(valor(bg_n, ctx)), chao); r = contraste(fg, bg)
            nivel = "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA-grande" if r >= 3 else "reprova"
            matriz.append({"momento": nome, "fg": fg_n, "bg": bg_n, "fg_hex": hexa(fg), "bg_hex": hexa(bg), "ratio": round(r, 2), "nivel": nivel, "uso": {"AAA": "qualquer texto", "AA": "qualquer texto", "AA-grande": "só texto de 24 px, ou 19 px em peso 700 ou mais", "reprova": "não usar para texto"}[nivel]})
    # rampa
    degraus = [compor(cor(valor("dado-%d" % i, ctx)), chao) for i in (1, 2, 3, 4)]
    o20 = compor(cor(valor("accent", ctx)), chao)
    rampas[nome] = {"degraus": [hexa(d) for d in degraus], "contraste_com_o_chao": [round(contraste(d, chao), 2) for d in degraus],
                    "separacao_oklab_adjacente": [round(dE(degraus[i], degraus[i + 1]), 1) for i in range(3)],
                    "separacao_para_o_20": [round(dE(d, o20), 1) for d in degraus], "o20": hexa(o20)}

brand = {
  "system": "8020-DS", "version": "4.0", "candidato": True, "gerado_por": "tokens/gerar-brand.py a partir de tokens/8020.css", "data": "2026-09-07",
  "primitivos": {
    "cores": {k: RAIZ[k] for k in RAIZ if k.startswith("8020-")},
    "fonte": {"familia": "Montserrat", "variavel": True, "licenca": "OFL", "servida_de": "assets/fonts/", "pesos": {"fino": 300, "corpo": 400, "medio": 500, "rotulo": 600, "titulo": 700, "display": 800}},
    "escala_tipo": {k: RAIZ[k] for k in RAIZ if k.startswith("t-")},
    "entrelinha": {k: RAIZ[k] for k in RAIZ if k.startswith("lh-")},
    "escala_espaco": {k: RAIZ[k] for k in RAIZ if k.startswith("s-")},
    "medidas": {k: RAIZ[k] for k in ("measure", "max", "max-prose", "gutter", "sl-w", "sl-h")},
    "forma": {k: RAIZ[k] for k in ("r-0", "r-media", "registro")},
    "movimento": {k: RAIZ[k] for k in ("ease-out", "dur-fast", "dur", "dur-slow")},
  },
  "semanticos": semanticos,
  "componentes": {
    "filete": ["ink", "rule-strong", "accent", "meta"], "tinta": ["ink", "paper", "accent (momento laranja: branco)"], "quieta": ["muted", "ink"],
    "peso": ["ink-soft", "ink", "meta"], "campo": ["ink", "rule-strong", "accent (cursor e erro)", "meta"], "marca-opcao": ["ink", "rule"],
    "segmentos": ["ink", "paper", "surface-2"], "interruptor": ["ink", "paper", "muted", "rule-strong"], "aviso": ["ink", "rule", "accent (atenção)"],
    "progresso": ["rule-strong", "ink"], "tabela": ["ink", "muted", "rule", "surface-2", "ink-body"], "estado": ["ink", "accent", "rule-strong"],
    "faixa": ["ink (fundo)", "accent (fundo, abertura de capítulo)", "branco", "preto (texto pequeno no laranja)"],
    "cromo do slide quieto": ["rule", "rule-strong", "ink", "muted"], "moldura do visualizador": ["8020-chumbo", "branco", "accent (miniatura atual)"],
    "grafico": ["dado-1 a dado-4", "dado-0", "accent (o 20)", "rule-strong (eixo)", "hairline (grade)", "ink", "ink-body", "meta"],
    "mapa": ["dado-1 a dado-4", "dado-0", "accent", "paper (traço entre municípios)", "ink (guia e alfinete)"],
    "margem viva": ["ink (filete e numeral)", "muted", "accent (quadrado)"],
  },
  "dado": {
    "regra": "uma tonalidade, a tinta do contexto, em quatro degraus (100, 64, 40 e 20 %); até três séries usam 100, 55 e 25 %; a partir da quinta série, pequenos múltiplos ou 'outros'. O laranja é o 20: um elemento por gráfico, o que a leitura em palavras nomeia. Degrau abaixo de 3:1 contra o chão exige rótulo direto na marca ou livro-razão. No momento laranja a rampa é de preto e o 20 é branco. Na impressão o laranja vira hachura.",
    "rampas": rampas,
    "tres_series": ["100%", "55%", "25%"], "quatro_series": ["100%", "64%", "40%", "20%"],
    "marcas": {"barra": "até 24 px, reta, 2 px de papel entre segmentos", "linha": "2 px", "ponto": "8 px com anel de papel de 2 px", "no_de_rede": "quadrado de 8 px", "banda_de_fluxo": "reta, 1 px de papel entre bandas"},
    "proibido": ["pizza e rosca", "eixo duplo", "radar", "gradiente em dado", "laranja como série", "tooltip flutuante (a leitura em palavras substitui)", "legenda em caixa (rótulo direto)"]
  },
  "contrast_matrix": matriz,
  "forbidden_pairs": [
    {"fg": "branco", "bg": "laranja", "context": "texto abaixo de 24 px (ou 19 px em 700)", "motivo": "3,5:1: só passa como texto grande"},
    {"fg": "laranja", "bg": "papel", "context": "texto abaixo de 24 px", "motivo": "3,3:1: o laranja é acento de título, momento, ação e estado, nunca corpo"},
    {"fg": "qualquer cor fora dos seis primitivos", "bg": "qualquer", "motivo": "a paleta é fechada"},
    {"fg": "laranja", "bg": "laranja", "motivo": "sem contraste; dentro do momento laranja o acento é o branco"}
  ],
  "hard_rules": [
    {"id": "paleta-fechada", "regra": "só os seis primitivos e os papéis derivados deles", "check": "nenhuma cor fora de --8020-* no CSS e no SVG"},
    {"id": "papel-substrato", "regra": "o papel é o fundo de toda peça; laranja e escuro entram como momento", "check": "--paper da base é #faf7f2"},
    {"id": "raio-zero", "regra": "0 em bloco, tabela, controle e foto de slide; 6 só em mídia de book", "check": "border-radius fora de --r-media só na moldura do visualizador"},
    {"id": "sem-sombra", "regra": "nada de box-shadow nem drop-shadow; profundidade vem de cor e filete", "check": "nenhum box-shadow"},
    {"id": "sem-moldura", "regra": "sem barra lateral colorida, sem caixa de ícone, sem pílula de conteúdo, sem hover que desloca; cartão só para coleção, sem borda", "check": "nenhum border-left colorido, nenhum translateY em hover"},
    {"id": "filete-vivo", "regra": "todo controle textual mora sobre uma linha que conta o estado; estado nunca é só cor", "check": "todo .filete, .tinta, .campo tem os estados escritos"},
    {"id": "peso-como-estado", "regra": "navegação, aba e sumário mudam de peso, não de cor; largura reservada no peso máximo", "check": ".peso com data-t"},
    {"id": "um-icone", "regra": "o quadrado de 8 px é o único ícone: tinta, laranja, contorno, meta", "check": "nenhuma biblioteca de ícones"},
    {"id": "acento-escasso", "regra": "no máximo três momentos de acento por página ou slide; o laranja funcional (erro, atenção, passo atual, cursor, o 20 do dado) é tabelado e não conta", "check": "contagem por página"},
    {"id": "faixa", "regra": "no deck, a faixa carrega capítulo, título descritivo, frase central e contador; a frase é obrigatória e o título nunca carrega o achado", "check": "toda .faixa tem h2 e .frase"},
    {"id": "faixa-laranja", "regra": "uma por capítulo, nunca em dois slides seguidos; o texto pequeno da faixa laranja é preto", "check": "verificador"},
    {"id": "svg-real", "regra": "gráfico e diagrama em SVG real com role=img, aria-label, title e livro-razão; decorativo com aria-hidden", "check": "nenhuma barra em div com width em porcentagem"},
    {"id": "angulo-reto", "regra": "conector de diagrama em segmento reto com dobra em ângulo reto, seta por marker", "check": "nenhum C, Q ou S em path de conector"},
    {"id": "piso-de-fonte", "regra": "11,5 px na página, 14 px efetivos no slide; --meta é a cor mais clara permitida para texto", "check": "medir-deck.js"},
    {"id": "foco-visivel", "regra": "anel de 2 px em --focus com 2 px de afastamento em tudo que recebe teclado", "check": ":focus-visible nunca removido"},
    {"id": "movimento", "regra": "só transform e opacidade em página; a transição de dado move a marca em 480 ms; tudo desliga com prefers-reduced-motion e na impressão", "check": "@media reduce presente"},
    {"id": "montserrat", "regra": "só Montserrat, servida localmente", "check": "font-family resolve para Montserrat"},
    {"id": "logo-intacta", "regra": "logo 80 20 nunca recolorida: branca nos momentos e na moldura, invertida para escura sobre o papel", "check": "--logo-invert"}
  ]
}
saida = os.path.join(AQUI, "brand.json")
open(saida, "w", encoding="utf-8").write(json.dumps(brand, ensure_ascii=False, indent=2) + "\n")
reprovados = [m for m in matriz if m["nivel"] == "reprova"]
print("brand.json:", len(matriz), "pares medidos;", len(reprovados), "reprovados;", "AA-grande:", sum(1 for m in matriz if m["nivel"] == "AA-grande"))
for m in matriz:
    if m["nivel"] in ("reprova", "AA-grande"): print("  ", m["momento"], m["fg"], "sobre", m["bg"], m["ratio"], m["nivel"])
for nome, r in rampas.items(): print("  rampa", nome, r["contraste_com_o_chao"], "ΔE", r["separacao_oklab_adjacente"], "para o 20", r["separacao_para_o_20"])
