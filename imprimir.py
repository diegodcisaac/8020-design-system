# -*- coding: utf-8 -*-
"""
imprimir.py: gera o PDF de uma peca do 8020-DS pelo Chrome headless e confere o
que saiu. O deck vira um slide por pagina em 1280 por 720; o book imprime o hub
e cada parte na ordem dos links do hub e junta tudo num PDF so. Depois de
imprimir, le o PDF e confere paginas, tamanho da pagina, fonte embutida, texto
sobre texto e pagina em branco; no deck, tambem se o deck.js montou.
Sem dependencia: so a biblioteca padrao do Python 3 e um Chrome instalado.

  python3 imprimir.py templates/deck/padrao/deck.html
  python3 imprimir.py templates/book/padrao/index.html --saida entrega/
  python3 imprimir.py deck.html --saida entrega/deck-cliente.pdf --previa
  CHROME=/caminho/do/chrome python3 imprimir.py deck.html

Sem --saida, o PDF nasce ao lado do HTML (deck.html vira deck.pdf; o hub
index.html vira book.pdf). --saida aceita pasta ou caminho terminado em .pdf.
O Chrome sai da variavel CHROME ou dos caminhos comuns do macOS, Linux e
Windows. Para juntar o book usa o que houver, nesta ordem: pypdf, qpdf,
pdfunite, gs; sem nenhum, deixa um PDF por pagina do book e avisa.
--previa gera um PNG por pagina numa pasta ao lado do PDF (pdftoppm, mutool,
gs ou, no macOS, o PDFKit do sistema).

Sai com codigo 1 quando houver erro. Aviso nao bloqueia: le-se e decide-se.
"""
import argparse, json, os, re, shutil, signal, subprocess, sys, tempfile, time, zlib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import url2pathname

VERSAO = "4.1"
FAMILIA = "Montserrat"          # a fonte da marca; --fonte acrescenta outras
DECK_PT = (960.0, 540.0)        # 1280 por 720 px, a 0,75 pt por px
FOLGA_PT = 1.5                  # o Chrome arredonda o papel para a unidade do dispositivo
ESPERA_MS = 20000               # tempo virtual para script, fonte e imagem
LIMITE_S = 180                  # tempo real maximo de uma impressao
CORES = {"erro": "\033[31m", "aviso": "\033[33m", "off": "\033[0m", "dim": "\033[2m"}

VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
          "param", "source", "track", "wbr",
          "path", "rect", "circle", "line", "polyline", "polygon", "ellipse", "use", "stop", "image"}


# ------------------------------------------------------------------ achados
class Achado:
    def __init__(self, nivel, codigo, msg):
        self.nivel, self.codigo, self.msg = nivel, codigo, msg

    def dic(self):
        return dict(nivel=self.nivel, codigo=self.codigo, mensagem=self.msg)


def pl(n, um, varios):
    return f"{n} {um if n == 1 else varios}"


def num(x, casas=1):
    """numero em pt-BR: 1,5 e nao 1.5"""
    return f"{x:.{casas}f}".replace(".", ",")


def rel(p):
    try:
        return os.path.relpath(p)
    except ValueError:  # outro disco, no Windows
        return p


# ------------------------------------------------------------------ html
class LeitorHTML(HTMLParser):
    """o minimo do documento que a impressao precisa: tipo, slides, partes, recursos"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha = []                      # (tag, classes) dos elementos abertos
        self.html_classes, self.body, self.base, self.titulo = set(), {}, None, ""
        self.links, self.estilos, self.blocos, self.scripts, self.recursos = [], [], [], [], []
        self.ids = set()
        self.deck_nivel, self.tem_deck, self.slides = None, False, 0
        self.capitulos, self.hub, self.o20 = 0, False, 0
        self._style, self._titulo = None, None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        cls = set(a.get("class", "").split())
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.html_classes = cls
        elif tag == "body":
            self.body = a
        elif tag == "base" and a.get("href") and self.base is None:
            self.base = a["href"]
        elif tag == "title":
            self._titulo = []
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "link" and "stylesheet" in a.get("rel", "").lower().split() and a.get("href"):
            self.estilos.append((a["href"], a.get("media", "")))
            self.recursos.append(a["href"])
        elif tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
            self.recursos.append(a["src"])
        elif tag == "style":
            self._style = [a.get("media", "")]
        if tag in ("img", "source", "video", "audio", "image", "use", "embed", "iframe", "object"):
            for k in ("src", "poster", "href", "xlink:href", "data"):
                if a.get(k) and not a[k].startswith("#"):
                    self.recursos.append(a[k])
            for k in ("srcset",):
                for parte in a.get(k, "").split(","):
                    if parte.strip():
                        self.recursos.append(parte.split()[0])
        # o deck: os slides sao filhos diretos do primeiro .deck
        nivel = len(self.pilha)
        if "deck" in cls and not self.tem_deck:
            self.tem_deck, self.deck_nivel = True, nivel
        elif self.deck_nivel is not None and nivel == self.deck_nivel + 1 and "slide" in cls:
            self.slides += 1
        if "capitulo" in cls:
            self.capitulos += 1
        if "hub" in cls:
            self.hub = True
        if "o20" in cls and any(c & {"grafico", "mapa"} for _, c in self.pilha):
            self.o20 += 1
        if tag not in VAZIOS:
            self.pilha.append((tag, cls))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VAZIOS and self.pilha and self.pilha[-1][0] == tag:
            self.pilha.pop()

    def handle_endtag(self, tag):
        if tag == "style" and self._style is not None:
            self.blocos.append((self._style[0], "".join(self._style[1:])))
            self._style = None
        if tag == "title" and self._titulo is not None:
            self.titulo, self._titulo = " ".join("".join(self._titulo).split()), None
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break
        if self.deck_nivel is not None and len(self.pilha) <= self.deck_nivel:
            self.deck_nivel = None   # o deck fechou; slide de outro lugar nao conta

    def handle_data(self, data):
        if self._style is not None:
            self._style.append(data)
        if self._titulo is not None:
            self._titulo.append(data)


def ler_html(texto):
    h = LeitorHTML()
    h.feed(texto)
    h.close()
    return h


def caminho_local(url, base_dir):
    """url de recurso para caminho no disco; None quando nao e arquivo local"""
    url = url.strip()
    if not url or url.startswith(("#", "data:", "blob:", "about:", "javascript:", "mailto:", "tel:")):
        return None
    if re.match(r"[A-Za-z]:[\\/]", url):     # caminho absoluto do Windows
        return os.path.normpath(url)
    sp = urlsplit(url)
    if sp.scheme == "file":
        return url2pathname(unquote(sp.path))
    if sp.scheme:                             # http, https e afins: nao e disco
        return None
    caminho = unquote(sp.path)
    if not caminho:
        return None
    return os.path.normpath(os.path.join(base_dir, caminho))


def pasta_base(arquivo, doc):
    """a pasta contra a qual os caminhos relativos do HTML resolvem (respeita <base>)"""
    raiz = os.path.dirname(os.path.abspath(arquivo))
    if doc.base:
        b = caminho_local(doc.base, raiz)
        if b is None:
            return None                      # base remota: nao da para conferir no disco
        return b if doc.base.endswith(("/", "\\")) or os.path.isdir(b) else os.path.dirname(b)
    return raiz


# ------------------------------------------------------------------ css
def sem_comentario(css):
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def folhas(arquivo, doc):
    """os CSS da pagina na ordem da cascata: [(origem, texto)], seguindo @import"""
    base = pasta_base(arquivo, doc)
    saida, vistos = [], set()

    def carregar(caminho, media, profundidade=0):
        if not caminho or caminho in vistos or profundidade > 5 or not os.path.isfile(caminho):
            return
        if media and "print" not in media and "all" not in media:
            return
        vistos.add(caminho)
        try:
            texto = sem_comentario(open(caminho, encoding="utf-8", errors="replace").read())
        except OSError:
            return
        for m in re.finditer(r"@import\s+(?:url\()?\s*['\"]?([^'\")\s;]+)['\"]?\s*\)?\s*([^;]*);", texto):
            carregar(caminho_local(m.group(1), os.path.dirname(caminho)), m.group(2).strip(), profundidade + 1)
        saida.append((caminho, texto))

    if base is not None:
        for href, media in doc.estilos:
            carregar(caminho_local(href, base), media)
    for media, texto in doc.blocos:
        if not media or "print" in media or "all" in media:
            saida.append((arquivo, sem_comentario(texto)))
    return saida


def regras_page(css):
    """corpos dos @page sem seletor, fora de @media so de tela"""
    pilha, achados, inicio = [], [], 0
    for m in re.finditer(r"[{};]", css):
        c = m.group()
        if c == "{":
            pilha.append((css[inicio:m.start()].strip(), m.end()))
        elif c == "}" and pilha:
            prel, ini = pilha.pop()
            if re.fullmatch(r"@page\s*", prel):
                midias = [p for p, _ in pilha if p.startswith("@media")]
                if not any("screen" in p and "print" not in p for p in midias):
                    achados.append(css[ini:m.start()])
        inicio = m.end()
    return achados


PAPEL_MM = {"a5": (148, 210), "a4": (210, 297), "a3": (297, 420), "b5": (176, 250), "b4": (250, 353),
            "jis-b5": (182, 257), "jis-b4": (257, 364)}
PAPEL_IN = {"letter": (8.5, 11), "legal": (8.5, 14), "ledger": (11, 17)}
UNIDADE_PT = {"pt": 1, "px": 0.75, "in": 72, "cm": 72 / 2.54, "mm": 72 / 25.4, "q": 72 / 101.6, "pc": 12}


def tamanho_css(valor):
    """valor de size: do @page para (largura, altura) em pt; None quando e auto"""
    v = valor.lower().replace("!important", "").split()
    if not v or v[0] == "auto":
        return None
    w = h = None
    orient = next((x for x in v if x in ("portrait", "landscape")), None)
    nomes = [x for x in v if x not in ("portrait", "landscape")]
    medidas = [re.fullmatch(r"([\d.]+)(px|pt|in|cm|mm|q|pc)", x) for x in nomes]
    if nomes and all(medidas):
        w = float(medidas[0].group(1)) * UNIDADE_PT[medidas[0].group(2)]
        h = float(medidas[-1].group(1)) * UNIDADE_PT[medidas[-1].group(2)]
    elif nomes and nomes[0] in PAPEL_MM:
        w, h = (x * 72 / 25.4 for x in PAPEL_MM[nomes[0]])
    elif nomes and nomes[0] in PAPEL_IN:
        w, h = (x * 72 for x in PAPEL_IN[nomes[0]])
    elif not nomes and orient:
        w, h = 612.0, 792.0               # so a orientacao: o papel padrao do Chrome
    else:
        return None
    if orient == "landscape" and w < h or orient == "portrait" and w > h:
        w, h = h, w
    return (w, h)


def page_declarado(arquivo, doc):
    """o size do ultimo @page da cascata: ((w, h) em pt, texto, origem) ou None"""
    achado = None
    for origem, css in folhas(arquivo, doc):
        for corpo in regras_page(css):
            for m in re.finditer(r"(?:^|[;\s])size\s*:\s*([^;}]+)", corpo):
                t = tamanho_css(m.group(1))
                if t:
                    achado = (t, m.group(1).strip(), origem)
    return achado


def recursos_ausentes(arquivo, doc):
    """arquivo local citado pelo HTML ou pelos CSS que nao existe no disco"""
    base = pasta_base(arquivo, doc)
    if base is None:
        return []
    faltam = []
    for url in doc.recursos:
        p = caminho_local(url, base)
        if p and not os.path.exists(p):
            faltam.append((url, arquivo))
    for origem, css in folhas(arquivo, doc):
        pasta = base if origem == arquivo else os.path.dirname(origem)   # <style> resolve como o HTML
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+?)['\"]?\s*\)", css):
            p = caminho_local(m.group(1), pasta)
            if p and not os.path.exists(p):
                faltam.append((m.group(1), origem))
    vistos, saida = set(), []
    for url, origem in faltam:
        if url not in vistos:
            vistos.add(url)
            saida.append((url, origem))
    return saida


# ------------------------------------------------------------------ pdf
RE_OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")
RE_INI_STREAM = re.compile(rb">>\s*stream\r?\n")
RE_REF = re.compile(rb"(\d+)\s+\d+\s+R")
RE_TOK = re.compile(rb"\((?:\\.|[^\\)])*\)|<<|>>|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]<>(){}%]+"
                    rb"|[+-]?(?:\d+\.?\d*|\.\d+)|[A-Za-z'\"*]+|%[^\r\n]*")


def mult(m, n):
    """produto de matrizes do PDF [a b c d e f]"""
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, e * A + f * C + E, e * B + f * D + F)


def ponto(m, x, y):
    return (x * m[0] + y * m[2] + m[4], x * m[1] + y * m[3] + m[5])


class LeitorPDF:
    """le o PDF com a biblioteca padrao: objetos, fluxos de objeto, paginas e fontes"""

    def __init__(self, caminho):
        self.d = open(caminho, "rb").read()
        self.objs = {}                       # numero -> (dicionario, (ini, fim) do fluxo ou None)
        self._ler()

    def _ler(self):
        d, pos = self.d, 0
        while True:
            m = RE_OBJ.search(d, pos)
            if not m:
                break
            ini = m.end()
            fim = d.find(b"endobj", ini)
            if fim < 0:
                break
            s = RE_INI_STREAM.search(d, ini, fim)
            if s:
                dic = d[ini:s.start() + 2]
                ds = s.end()
                ln = re.search(rb"/Length\s+(\d+)(?!\s+\d+\s+R)", dic)
                if ln and d[ds + int(ln.group(1)):ds + int(ln.group(1)) + 12].lstrip().startswith(b"endstream"):
                    de = ds + int(ln.group(1))
                else:
                    de = d.find(b"endstream", ds)
                    de = de if de >= 0 else fim
                fim = d.find(b"endobj", de)
                fim = fim if fim >= 0 else len(d)
                self.objs[int(m.group(1))] = (dic, (ds, de))
            else:
                self.objs[int(m.group(1))] = (d[ini:fim], None)
            pos = fim + 6
        # objetos comprimidos dentro de /ObjStm (gs e outros escrevem assim)
        for n, (dic, fl) in list(self.objs.items()):
            if fl and re.search(rb"/Type\s*/ObjStm", dic):
                dados = self.fluxo(n)
                cab = re.search(rb"/First\s+(\d+)", dic)
                qt = re.search(rb"/N\s+(\d+)", dic)
                if not dados or not cab or not qt:
                    continue
                primeiro = int(cab.group(1))
                pares = [int(x) for x in dados[:primeiro].split()]
                pares = list(zip(pares[0::2], pares[1::2]))[:int(qt.group(1))]
                for k, (on, off) in enumerate(pares):
                    fim = primeiro + pares[k + 1][1] if k + 1 < len(pares) else len(dados)
                    self.objs.setdefault(on, (dados[primeiro + off:fim], None))

    def dic(self, n):
        return self.objs.get(n, (b"", None))[0]

    def fluxo(self, n):
        dic, fl = self.objs.get(n, (b"", None))
        if not fl:
            return b""
        bruto = self.d[fl[0]:fl[1]]
        if re.search(rb"/Filter\s*(?:\[\s*)?/FlateDecode", dic):
            try:
                return zlib.decompress(bruto)
            except zlib.error:
                try:
                    return zlib.decompressobj().decompress(bruto)
                except zlib.error:
                    return b""
        if re.search(rb"/Filter", dic):
            return b""
        return bruto

    def _caixa(self, dic):
        for chave in (rb"/CropBox", rb"/MediaBox"):
            m = re.search(chave + rb"\s*\[([^\]]*)\]", dic)
            if not m:
                r = re.search(chave + rb"\s+(\d+)\s+\d+\s+R", dic)
                if r:
                    m = re.search(rb"\[([^\]]*)\]", self.dic(int(r.group(1))))
            if m:
                v = [float(x) for x in m.group(1).split()]
                if len(v) == 4:
                    return (abs(v[2] - v[0]), abs(v[3] - v[1]))
        return None

    def paginas(self):
        """lista de paginas na ordem da arvore: dict(n, w, h, conteudo)"""
        saida = []
        cat = [n for n, (dic, _) in self.objs.items() if re.search(rb"/Type\s*/Catalog\b", dic)]
        raiz = None
        if cat:
            r = re.search(rb"/Pages\s+(\d+)\s+\d+\s+R", self.dic(max(cat)))
            raiz = int(r.group(1)) if r else None

        def andar(n, caixa, giro, vistos):
            if n in vistos or n not in self.objs:
                return
            vistos.add(n)
            dic = self.dic(n)
            caixa = self._caixa(dic) or caixa
            g = re.search(rb"/Rotate\s+(-?\d+)", dic)
            giro = int(g.group(1)) if g else giro
            if re.search(rb"/Type\s*/Pages\b", dic):
                k = re.search(rb"/Kids\s*\[([^\]]*)\]", dic)
                for f in RE_REF.findall(k.group(1) if k else b""):
                    andar(int(f), caixa, giro, vistos)
            elif re.search(rb"/Type\s*/Page\b", dic):
                w, h = caixa or (0.0, 0.0)
                if giro % 180:
                    w, h = h, w
                saida.append(dict(n=n, w=w, h=h, dic=dic))

        if raiz is not None:
            andar(raiz, None, 0, set())
        if not saida:   # arvore ilegivel: cai para a ordem dos objetos
            for n in sorted(self.objs):
                dic = self.dic(n)
                if re.search(rb"/Type\s*/Page\b", dic) and not re.search(rb"/Type\s*/Pages\b", dic):
                    w, h = self._caixa(dic) or (0.0, 0.0)
                    saida.append(dict(n=n, w=w, h=h, dic=dic))
        return saida

    def conteudo(self, pagina):
        """os operadores da pagina, descomprimidos"""
        dic = pagina["dic"]
        m = re.search(rb"/Contents\s*(\[[^\]]*\]|\d+\s+\d+\s+R)", dic)
        if not m:
            return b""
        return b"\n".join(self.fluxo(int(r)) for r in RE_REF.findall(m.group(1)))

    def ocupacao(self, pagina):
        """o que a pagina desenha: (textos, imagens, faixa vertical ocupada em pt, glifos)
        glifos e a lista (x, y, corpo) da origem de cada texto, em pt"""
        ident = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        ctm, pilha, tm, tlm, entrelinha, corpo = ident, [], ident, ident, 0.0, 0.0
        nums, ys, glifos, textos, imagens = [], [], [], 0, 0
        for t in RE_TOK.finditer(self.conteudo(pagina)):
            s = t.group()
            if s[:1] in b"+-.0123456789":
                try:
                    nums.append(float(s))
                except ValueError:
                    nums = []
                continue
            if s[:1] in b"(<[]/%>":
                continue                      # operando que nao e numero
            if s == b"q":
                pilha.append(ctm)
            elif s == b"Q":
                ctm = pilha.pop() if pilha else ctm
            elif s == b"cm" and len(nums) >= 6:
                ctm = mult(tuple(nums[-6:]), ctm)
            elif s == b"BT":
                tm = tlm = ident
            elif s == b"Tm" and len(nums) >= 6:
                tm = tlm = tuple(nums[-6:])
            elif s in (b"Td", b"TD") and len(nums) >= 2:
                if s == b"TD":
                    entrelinha = -nums[-1]
                tm = tlm = mult((1.0, 0.0, 0.0, 1.0, nums[-2], nums[-1]), tlm)
            elif s == b"TL" and nums:
                entrelinha = nums[-1]
            elif s == b"Tf" and nums:
                corpo = nums[-1]
            elif s in (b"T*", b"'", b'"'):
                tm = tlm = mult((1.0, 0.0, 0.0, 1.0, 0.0, -entrelinha), tlm)
            if s in (b"Tj", b"TJ", b"'", b'"'):
                textos += 1
                m = mult(tm, ctm)
                x, y = ponto(m, 0, 0)
                ys.append(y)
                glifos.append((x, y, abs(corpo) * abs(m[0] * m[3] - m[1] * m[2]) ** 0.5))
            elif s == b"Do":
                imagens += 1
                ys += [ponto(ctm, x, y)[1] for x, y in ((0, 0), (1, 0), (0, 1), (1, 1))]
            nums = []
        ys = [min(max(y, 0.0), pagina["h"]) for y in ys]
        return textos, imagens, (max(ys) - min(ys)) if ys else 0.0, glifos

    def fontes(self):
        """[(nome sem prefixo de subconjunto, subtipo, embutida)]"""
        saida = []
        for n, (dic, _) in self.objs.items():
            if not re.search(rb"/Type\s*/Font\b", dic):
                continue
            sub = re.search(rb"/Subtype\s*/(\w+)", dic)
            sub = sub.group(1).decode() if sub else "?"
            if sub.startswith("CIDFontType"):
                continue                      # entra pela fonte Type0 que a usa
            desc = re.search(rb"/FontDescriptor\s+(\d+)\s+\d+\s+R", dic)
            if not desc:
                filha = re.search(rb"/DescendantFonts\s*(?:\[\s*)?(\d+)\s+\d+\s+R", dic)
                if filha:
                    desc = re.search(rb"/FontDescriptor\s+(\d+)\s+\d+\s+R", self.dic(int(filha.group(1))))
            ddic = self.dic(int(desc.group(1))) if desc else b""
            nome = re.search(rb"/FontName\s*/([^\s/\[\]<>()]+)", ddic) or re.search(rb"/BaseFont\s*/([^\s/\[\]<>()]+)", dic)
            nome = nome.group(1).decode("latin-1") if nome else "(sem nome)"
            nome = re.sub(r"#([0-9A-Fa-f]{2})", lambda x: chr(int(x.group(1), 16)), nome)
            nome = re.sub(r"^[A-Z]{6}\+", "", nome)
            nome = re.sub(r"-Identity-[HV]$", "", nome)
            embutida = sub == "Type3" or bool(re.search(rb"/FontFile[23]?\b", ddic))
            saida.append((nome, sub, embutida))
        return saida


def pdf_inteiro(caminho):
    try:
        with open(caminho, "rb") as f:
            f.seek(0, 2)
            t = f.tell()
            f.seek(max(0, t - 2048))
            return t > 0 and b"%%EOF" in f.read()
    except OSError:
        return False


PAPEIS = [("A4", 595.28, 841.89), ("A3", 841.89, 1190.55), ("A5", 419.53, 595.28),
          ("Carta", 612, 792), ("Ofício", 612, 1008), ("1280 x 720 px", 960, 540)]


def nome_papel(w, h):
    for nome, a, b in PAPEIS:
        if abs(w - a) <= FOLGA_PT and abs(h - b) <= FOLGA_PT:
            return nome
        if abs(w - b) <= FOLGA_PT and abs(h - a) <= FOLGA_PT:
            return nome + " deitado"
    return ""


def papel(w, h):
    n = nome_papel(w, h)
    return f"{w:.0f} x {h:.0f} pt" + (f" ({n})" if n else "")


PESOS = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]


def ordem_estilo(estilo):
    base = estilo.replace("Italic", "") or "Regular"
    return (PESOS.index(base) if base in PESOS else 99, "Italic" in estilo, estilo)


def normal(nome):
    return re.sub(r"[^a-z0-9]", "", nome.lower())


# ------------------------------------------------------------------ chrome
def achar_chrome():
    """o Chrome da variavel CHROME ou dos caminhos comuns; (caminho, None) ou (None, motivo)"""
    env = os.environ.get("CHROME", "").strip()
    if env:
        achado = env if os.path.isfile(env) else shutil.which(env)
        return (achado, None) if achado else (None, f"a variável CHROME aponta para {env}, que não existe")
    cands = []
    if sys.platform == "darwin":
        for raiz in ("/Applications", os.path.expanduser("~/Applications")):
            cands += [f"{raiz}/Google Chrome.app/Contents/MacOS/Google Chrome",
                      f"{raiz}/Chromium.app/Contents/MacOS/Chromium",
                      f"{raiz}/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
                      f"{raiz}/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                      f"{raiz}/Brave Browser.app/Contents/MacOS/Brave Browser"]
    elif os.name == "nt":
        for var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            raiz = os.environ.get(var)
            if raiz:
                cands += [os.path.join(raiz, "Google", "Chrome", "Application", "chrome.exe"),
                          os.path.join(raiz, "Chromium", "Application", "chrome.exe"),
                          os.path.join(raiz, "Microsoft", "Edge", "Application", "msedge.exe"),
                          os.path.join(raiz, "BraveSoftware", "Brave-Browser", "Application", "brave.exe")]
    else:
        cands += ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/opt/google/chrome/chrome",
                  "/usr/bin/chromium", "/usr/bin/chromium-browser", "/snap/bin/chromium",
                  "/usr/bin/microsoft-edge", "/usr/bin/brave-browser"]
    for c in cands:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c, None
    for nome in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
                 "microsoft-edge", "msedge", "brave-browser"):
        w = shutil.which(nome)
        if w:
            return w, None
    return None, "nenhum Chrome encontrado; instale o Google Chrome ou aponte a variável CHROME para ele"


def versao_chrome(chrome):
    try:
        r = subprocess.run([chrome, "--version"], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() or "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


def matar(proc):
    """fecha o Chrome e os processos filhos dele (renderizador, GPU), que nao morrem sozinhos"""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True, timeout=30)
        else:
            os.killpg(proc.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError):
        pass
    try:
        proc.kill()
    except OSError:
        pass


def rodar_chrome(chrome, html, pdf, espera):
    """imprime o HTML em pdf e devolve o DOM depois dos scripts: dict(ok, dom, erro, s)"""
    perfil = tempfile.mkdtemp(prefix="imprimir-chrome-")
    args = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
            "--no-first-run", "--no-default-browser-check", "--disable-extensions", "--disable-sync",
            "--disable-background-networking", "--disable-component-update",
            f"--user-data-dir={perfil}", "--window-size=1440,900",
            # cor e texto deterministas: o laranja sai #fa4616 e a metrica nao depende do sistema
            "--force-color-profile=srgb", "--font-render-hinting=none",
            # fonte, imagem e script locais carregam antes de imprimir
            "--allow-file-access-from-files", "--run-all-compositor-stages-before-draw",
            f"--virtual-time-budget={espera}",
            # papel limpo: sem cabecalho do navegador, com marcadores a partir dos titulos
            "--no-pdf-header-footer", "--print-to-pdf-no-header", "--generate-pdf-document-outline",
            "--dump-dom", f"--print-to-pdf={pdf}", Path(os.path.abspath(html)).as_uri()]
    if sys.platform.startswith("linux") and hasattr(os, "geteuid") and os.geteuid() == 0:
        args.insert(1, "--no-sandbox")       # o Chrome recusa rodar como root sem isso
    t0 = time.time()
    saida = dict(ok=False, dom="", erro="", s=0.0)
    try:
        grupo = dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else dict(start_new_session=True)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **grupo)
    except OSError as e:
        shutil.rmtree(perfil, ignore_errors=True)
        saida["erro"] = f"o Chrome não abriu: {e}"
        return saida
    out, err, pronto_desde = b"", b"", None
    try:
        while True:
            try:
                out, err = proc.communicate(timeout=1)
                break
            except subprocess.TimeoutExpired:
                # o Chrome as vezes fica no ar depois de escrever o PDF: espera 5 s e fecha
                if pdf_inteiro(pdf):
                    pronto_desde = pronto_desde or time.time()
                    if time.time() - pronto_desde > 5:
                        matar(proc)
                        out, err = proc.communicate()
                        break
                if time.time() - t0 > LIMITE_S:
                    matar(proc)
                    out, err = proc.communicate()
                    saida["erro"] = f"o Chrome passou de {LIMITE_S} s sem terminar"
                    break
    finally:
        if proc.poll() is None:
            matar(proc)
        shutil.rmtree(perfil, ignore_errors=True)
    saida["s"] = time.time() - t0
    saida["dom"] = out.decode("utf-8", errors="replace")
    if pdf_inteiro(pdf):
        saida["ok"] = True
    elif not saida["erro"]:
        ruido = ("cv_display_link", "task_policy_set", "allocator", "DevTools listening", "bytes written")
        linhas = [l for l in err.decode("utf-8", errors="replace").splitlines()
                  if l.strip() and not any(r in l for r in ruido)]
        saida["erro"] = "o Chrome não escreveu o PDF" + (f": {linhas[-1].strip()[:160]}" if linhas else "")
    return saida


# ------------------------------------------------------------------ juntar e previa
def juntar(pdfs, destino, titulo=""):
    """junta os PDFs na ordem; devolve o nome da ferramenta ou None"""
    try:
        import pypdf
        w = pypdf.PdfWriter()
        for p in pdfs:
            w.append(p)
        if titulo:
            w.add_metadata({"/Title": titulo})
        with open(destino, "wb") as f:
            w.write(f)
        if pdf_inteiro(destino):
            return "pypdf"
    except Exception:   # pypdf ausente ou falhou: tenta a proxima
        pass
    tentativas = []
    if shutil.which("qpdf"):
        # o primeiro arquivo e o principal: o titulo e os marcadores do hub ficam
        tentativas.append(("qpdf", [shutil.which("qpdf"), pdfs[0], "--pages", ".", *pdfs[1:], "--", destino], (0, 3)))
    if shutil.which("pdfunite"):
        tentativas.append(("pdfunite", [shutil.which("pdfunite"), *pdfs, destino], (0,)))
    gs = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
    if gs:
        tentativas.append(("gs", [gs, "-q", "-dBATCH", "-dNOPAUSE", "-dSAFER", "-sDEVICE=pdfwrite",
                                  "-dAutoRotatePages=/None", f"-sOutputFile={destino}", *pdfs], (0,)))
    for nome, cmd, oks in tentativas:
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=300)
            if r.returncode in oks and pdf_inteiro(destino):
                return nome
        except (OSError, subprocess.SubprocessError):
            pass
    return None


JXA_PDFKIT = r"""
ObjC.import('PDFKit'); ObjC.import('AppKit');
function run(argv) {
  var doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[0]));
  if (!doc || doc.isNil()) return 0;
  var n = doc.pageCount, escala = parseFloat(argv[2]) / 72;
  for (var i = 0; i < n; i++) {
    var pg = doc.pageAtIndex(i), cx = pg.boundsForBox(0);
    var img = pg.thumbnailOfSizeForBox($.NSMakeSize(Math.round(cx.size.width * escala), Math.round(cx.size.height * escala)), 0);
    var rep = $.NSBitmapImageRep.imageRepWithData(img.TIFFRepresentation);
    var png = rep.representationUsingTypeProperties(4, $({}));
    png.writeToFileAtomically(argv[1] + '/p-' + (i + 1) + '.png', true);
  }
  return n;
}
"""


def previa(pdf, pasta, dpi):
    """um PNG por pagina em pasta/pagina-NN.png; devolve (quantos, ferramenta, aviso)"""
    tmp = tempfile.mkdtemp(prefix=".previa-", dir=os.path.dirname(os.path.abspath(pasta)))

    def limpar():   # tentativa que falhou no meio nao deixa PNG para a seguinte
        for f in os.listdir(tmp):
            os.remove(os.path.join(tmp, f))

    try:
        usado = None
        if shutil.which("pdftoppm"):
            r = subprocess.run([shutil.which("pdftoppm"), "-png", "-r", str(dpi), pdf, os.path.join(tmp, "p")],
                               capture_output=True, timeout=600)
            usado = "pdftoppm" if r.returncode == 0 else None
        if not usado and shutil.which("mutool"):
            limpar()
            r = subprocess.run([shutil.which("mutool"), "draw", "-q", "-r", str(dpi), "-o",
                                os.path.join(tmp, "p-%d.png"), pdf], capture_output=True, timeout=600)
            usado = "mutool" if r.returncode == 0 else None
        gs = shutil.which("gs") or shutil.which("gswin64c") or shutil.which("gswin32c")
        if not usado and gs:
            limpar()
            r = subprocess.run([gs, "-q", "-dBATCH", "-dNOPAUSE", "-dSAFER", "-sDEVICE=png16m", f"-r{dpi}",
                                "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4",
                                f"-sOutputFile={os.path.join(tmp, 'p-%d.png')}", pdf], capture_output=True, timeout=600)
            usado = "gs" if r.returncode == 0 else None
        if not usado and sys.platform == "darwin" and shutil.which("osascript"):
            limpar()
            r = subprocess.run(["osascript", "-l", "JavaScript", "-e", JXA_PDFKIT, os.path.abspath(pdf), tmp, str(dpi)],
                               capture_output=True, timeout=600)
            usado = "PDFKit do macOS" if r.returncode == 0 and os.listdir(tmp) else None
        aviso = None
        if not usado and sys.platform == "darwin" and shutil.which("sips"):
            limpar()
            r = subprocess.run(["sips", "-s", "format", "png", pdf, "--out", os.path.join(tmp, "p-1.png")],
                               capture_output=True, timeout=120)
            if r.returncode == 0:
                usado, aviso = "sips", "o sips só desenha a primeira página; instale o poppler (pdftoppm) para ver todas"
        if not usado:
            return 0, None, "sem ferramenta de prévia: instale o poppler (pdftoppm) ou o ghostscript (gs)"
        # nomes iguais em qualquer ferramenta: pagina-01.png; a previa velha sai antes
        os.makedirs(pasta, exist_ok=True)
        for f in os.listdir(pasta):
            if re.fullmatch(r"pagina-\d+\.png", f):
                os.remove(os.path.join(pasta, f))
        feitos = sorted((int(re.search(r"(\d+)\.png$", f).group(1)), f) for f in os.listdir(tmp) if f.endswith(".png"))
        larg = max(2, len(str(len(feitos))))
        for n, f in feitos:
            os.replace(os.path.join(tmp, f), os.path.join(pasta, f"pagina-{n:0{larg}d}.png"))
        return len(feitos), usado, aviso
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ a peca
def ler(caminho):
    return open(caminho, encoding="utf-8", errors="replace").read()


def tipo_de(doc):
    if doc.tem_deck or any(s.split("?")[0].endswith("deck.js") for s in doc.scripts):
        return "deck"
    if doc.body.get("data-hub"):
        return "parte"
    return "book" if doc.hub or partes_do_hub(None, doc) else "pagina"


def partes_do_hub(hub, doc):
    """as partes na ordem do primeiro link do hub: [caminho absoluto]"""
    base = pasta_base(hub, doc) if hub else None
    saida = []
    for href in doc.links:
        sp = urlsplit(href)
        if sp.scheme or not sp.path.lower().endswith(".html"):
            continue
        caminho = os.path.normpath(os.path.join(base, unquote(sp.path))) if base else unquote(sp.path)
        if hub and os.path.abspath(caminho) == os.path.abspath(hub):
            continue
        eh_parte = bool(re.search(r"(?:^|/)partes?/parte-\d+\.html$", sp.path))
        if hub and not eh_parte and os.path.isfile(caminho):
            filho = ler_html(ler(caminho))
            alvo = filho.body.get("data-hub")
            eh_parte = bool(alvo) and os.path.abspath(
                caminho_local(alvo, pasta_base(caminho, filho) or os.path.dirname(caminho)) or "") == os.path.abspath(hub)
        if eh_parte and caminho not in saida:
            saida.append(caminho)
    return saida


def destino_pdf(arquivo, tipo, saida, varios):
    nome = Path(arquivo).stem
    if tipo == "book" and nome.lower() == "index":
        nome = "book"
    if saida and saida.lower().endswith(".pdf"):
        if varios:
            return None
        return os.path.abspath(saida)
    pasta = os.path.abspath(saida) if saida else os.path.dirname(os.path.abspath(arquivo))
    return os.path.join(pasta, nome + ".pdf")


def conferir_tamanho(paginas, esperado, rotulo, achados, origem=""):
    fora = [i + 1 for i, p in enumerate(paginas)
            if abs(p["w"] - esperado[0]) > FOLGA_PT or abs(p["h"] - esperado[1]) > FOLGA_PT]
    if fora:
        p = paginas[fora[0] - 1]
        lista = ", ".join(map(str, fora[:8])) + ("..." if len(fora) > 8 else "")
        achados.append(Achado("erro", "tamanho",
                              f"{rotulo}{pl(len(fora), 'página', 'páginas')} fora de {papel(*esperado)}: {lista}; "
                              f"a primeira saiu em {papel(p['w'], p['h'])}{origem}"))


QUASE_VAZIA = 0.08   # conteudo numa faixa menor que isso da altura: linha orfa, rodape sozinho
SOBREPOSTOS = 5      # pares de glifos sobrepostos a partir dos quais a pagina tem texto sobre texto


def sobrepostos(glifos):
    """pares de glifos do mesmo corpo com linhas de base perto demais e a mesma posicao na linha:
    duas linhas de texto uma sobre a outra (no papel, quase sempre bloco partido entre paginas)"""
    gs = sorted(glifos, key=lambda g: g[1])
    pares = 0
    for i, a in enumerate(gs):
        for b in gs[i + 1:]:
            dy = b[1] - a[1]
            if dy > 1.2 * a[2]:
                break
            c = min(a[2], b[2])
            # linhas de base a menos de um corpo uma da outra: a de cima pisa na de baixo
            if 0.1 * c < dy < 0.95 * c and abs(b[0] - a[0]) < 0.5 * c and abs(a[2] - b[2]) <= 0.15 * max(a[2], b[2]):
                pares += 1
    return pares


def conferir_vazias(leitor, paginas, rotulo, achados, desloc=0):
    vazias, quase, sobre = [], [], []
    for i, p in enumerate(paginas):
        textos, imagens, faixa, glifos = leitor.ocupacao(p)
        if not textos and not imagens:
            vazias.append(desloc + i + 1)
        elif p["h"] and faixa < QUASE_VAZIA * p["h"]:
            quase.append(desloc + i + 1)
        if sobrepostos(glifos) >= SOBREPOSTOS:
            sobre.append(desloc + i + 1)
    if sobre:
        achados.append(Achado("erro", "texto-sobre-texto",
                              f"{rotulo}uma linha de texto sobre outra em {pl(len(sobre), 'página', 'páginas')}: "
                              f"{', '.join(map(str, sobre[:8]))} (veja a prévia)"))
    if vazias:
        achados.append(Achado("aviso", "pagina-vazia",
                              f"{rotulo}{pl(len(vazias), 'página', 'páginas')} em branco: "
                              f"{', '.join(map(str, vazias[:8]))}"))
    if quase:
        achados.append(Achado("aviso", "pagina-quase-vazia",
                              f"{rotulo}{pl(len(quase), 'página', 'páginas')} quase vazia{'s' if len(quase) > 1 else ''}, "
                              f"só uma linha ou o rodapé: {', '.join(map(str, quase[:8]))}"))


def conferir_fontes(leitores, aceitas, achados):
    """a fonte da marca tem de estar embutida, e nenhuma outra no lugar dela"""
    fontes = [f for leitor in leitores for f in leitor.fontes()]
    aceitas_n = [normal(a) for a in aceitas]
    marca = [f for f in fontes if any(normal(f[0]).startswith(a) for a in aceitas_n)]
    fora = sorted({f[0] for f in fontes if f not in marca})
    sem = sorted({f[0] for f in marca if not f[2]})
    if not fontes:
        achados.append(Achado("aviso", "sem-texto", "o PDF não tem fonte nenhuma: saiu sem texto?"))
        return []
    if not marca:
        achados.append(Achado("erro", "fonte-ausente",
                              f"nenhuma {' ou '.join(aceitas)} no PDF; o texto saiu em "
                              f"{', '.join(fora) if fora else 'nenhuma fonte'} (a @font-face não carregou?)"))
    elif fora:
        achados.append(Achado("erro", "fonte-fora",
                              f"fonte de sistema no PDF: {', '.join(fora)}; algum texto ou glifo não pegou a "
                              f"{aceitas[0]} (caractere fora da fonte ou família errada no CSS)"))
    if sem:
        achados.append(Achado("erro", "fonte-nao-embutida", f"fonte sem o arquivo embutido: {', '.join(sem)}"))
    familias = {}
    for nome, sub, _ in marca:
        fam, _, estilo = nome.partition("-")
        familias.setdefault(fam, set()).add((estilo or "Regular", sub))
    resumo = []
    for fam, est in sorted(familias.items()):
        estilos = sorted({e for e, _ in est}, key=ordem_estilo)
        tipos = sorted({s.replace("Type", "Type ") if s in ("Type0", "Type1", "Type3") else s for _, s in est})
        resumo.append(f"{fam}: {', '.join(estilos)}" + (f" (embutida como {', '.join(tipos)})" if tipos else ""))
    return resumo


def conferir_dom(dom_txt, doc, tipo, rotulo, achados, tem_deck_js):
    """o DOM depois dos scripts: deck.js montou e o padrao da hachura existe"""
    if not dom_txt.strip():
        if tipo == "deck" and tem_deck_js:
            achados.append(Achado("aviso", "deck-js", f"{rotulo}o Chrome não devolveu o DOM; "
                                                     "a montagem do deck.js não foi conferida"))
        return doc
    dom = ler_html(dom_txt)
    if tipo == "deck" and not tem_deck_js:
        achados.append(Achado("aviso", "deck-js", "o deck não carrega o deck.js: contador, trilho e hachura "
                                                  "não são escritos, e o PDF sai sem eles"))
    if tipo == "deck" and tem_deck_js and not ("js" in dom.html_classes and "hachura-laranja" in dom.ids):
        achados.append(Achado("erro", "deck-js", f"{rotulo}o deck.js não montou antes da impressão "
                                                 "(sem a classe js no html ou sem o padrão da hachura)"))
    if dom.o20 and "hachura-laranja" not in dom.ids:
        achados.append(Achado("erro", "hachura",
                              f"{rotulo}{pl(dom.o20, 'marca laranja', 'marcas laranja')} de dado sem o padrão "
                              "#hachura-laranja na página: no papel a marca some (falta o deck.js ou o dado.js)"))
    return dom


def imprimir_peca(arquivo, a, chrome, varios):
    t0 = time.time()
    achados, info = [], dict(arquivo=rel(arquivo), tipo="?", pdf=None, paginas=0, tamanho=None,
                             fontes=[], juntado_por=None, previa=None, partes=[])
    try:
        doc = ler_html(ler(arquivo))
    except OSError as e:
        achados.append(Achado("erro", "arquivo", f"não deu para ler: {e}"))
        return info, achados, 0.0
    tipo = a.tipo or tipo_de(doc)
    info["tipo"] = tipo
    destino = destino_pdf(arquivo, tipo, a.saida, varios)
    if destino is None:
        achados.append(Achado("erro", "saida", "--saida com .pdf vale para um arquivo só; passe uma pasta"))
        return info, achados, 0.0
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    # o que imprimir: o deck e a pagina sao um HTML; o book e o hub mais as partes
    paginas_html = [arquivo]
    if tipo == "book":
        partes = partes_do_hub(arquivo, doc)
        faltam = [p for p in partes if not os.path.isfile(p)]
        for p in faltam:
            achados.append(Achado("erro", "parte-ausente", f"o hub aponta para {rel(p)}, que não existe"))
        partes = [p for p in partes if p not in faltam]
        if not partes:
            achados.append(Achado("aviso", "book-sem-partes", "o hub não aponta para nenhuma parte; sai só o hub"))
        paginas_html += partes
    elif tipo == "parte":
        hub = caminho_local(doc.body.get("data-hub", ""), pasta_base(arquivo, doc) or os.path.dirname(arquivo))
        achados.append(Achado("aviso", "so-a-parte", f"parte de book: sai só esta parte; para o book inteiro, "
                                                     f"passe o hub ({rel(hub) if hub else 'data-hub'})"))
    docs = {arquivo: doc}
    for p in paginas_html[1:]:
        docs[p] = ler_html(ler(p))

    # antes de imprimir: recurso local que nao existe sai torto no papel
    for p in paginas_html:
        for url, origem in recursos_ausentes(p, docs[p]):
            achados.append(Achado("erro", "recurso-ausente",
                                  f"{rel(origem)} cita {url}, que não existe no disco"))

    tmp = tempfile.mkdtemp(prefix=".imprimir-", dir=os.path.dirname(destino))
    try:
        pdfs = [os.path.join(tmp, f"{k + 1:02d}-{Path(p).stem}.pdf") for k, p in enumerate(paginas_html)]
        with ThreadPoolExecutor(max_workers=min(4, len(pdfs))) as ex:
            rodadas = list(ex.map(lambda par: rodar_chrome(chrome, par[0], par[1], a.espera),
                                  zip(paginas_html, pdfs)))
        falhou = [(p, r) for p, r in zip(paginas_html, rodadas) if not r["ok"]]
        for p, r in falhou:
            achados.append(Achado("erro", "chrome", f"{rel(p)}: {r['erro']}"))
        if falhou:
            return info, achados, time.time() - t0

        # leitura de cada PDF impresso
        lidos, total, sem_page = [], 0, []
        for k, (p, pdf, r) in enumerate(zip(paginas_html, pdfs, rodadas)):
            leitor = LeitorPDF(pdf)
            pags = leitor.paginas()
            curto = os.path.relpath(p, os.path.dirname(arquivo))
            rotulo = f"{curto}: " if tipo == "book" else ""
            d = docs[p]
            dom = conferir_dom(r["dom"], d, tipo, rotulo, achados,
                               any(s.split("?")[0].endswith("deck.js") for s in d.scripts))
            lidos.append((p, leitor, pags))
            total += len(pags)
            info["partes"].append(dict(html=curto, paginas=len(pags), de=total - len(pags) + 1, s=round(r["s"], 1)))
            if not pags:
                achados.append(Achado("erro", "paginas", f"{rotulo}o PDF saiu sem página legível"))
                continue
            if tipo == "deck":
                slides = dom.slides if dom.tem_deck else d.slides
                if dom.tem_deck and dom.slides != d.slides:
                    achados.append(Achado("aviso", "slides", f"o HTML tem {d.slides} slides e o DOM montado, "
                                                             f"{dom.slides}; vale o DOM"))
                info["slides"] = slides
                if len(pags) != slides:
                    achados.append(Achado("erro", "paginas",
                                          f"{pl(slides, 'slide', 'slides')} no deck e "
                                          f"{pl(len(pags), 'página', 'páginas')} no PDF"))
                decl = page_declarado(p, d)
                origem = f"; o CSS declara size: {decl[1]} em {rel(decl[2])}" if decl and (
                    abs(decl[0][0] - DECK_PT[0]) > FOLGA_PT or abs(decl[0][1] - DECK_PT[1]) > FOLGA_PT) else ""
                conferir_tamanho(pags, DECK_PT, "", achados, origem)
            else:
                decl = page_declarado(p, d)
                if decl:
                    conferir_tamanho(pags, decl[0], rotulo, achados,
                                     f"; o CSS declara size: {decl[1]} em {rel(decl[2])}")
                else:
                    sem_page.append((p, pags[0]))
                if tipo in ("book", "parte") and d.capitulos > len(pags):
                    achados.append(Achado("aviso", "quebra", f"{rotulo}{pl(d.capitulos, 'capítulo', 'capítulos')} "
                                                             f"em {pl(len(pags), 'página', 'páginas')}: a quebra "
                                                             "antes do capítulo não aplicou"))
            conferir_vazias(leitor, pags, rotulo, achados, total - len(pags))
        if sem_page:
            quais = "" if len(sem_page) == len(paginas_html) or tipo != "book" else \
                " em " + ", ".join(rel(p) for p, _ in sem_page)
            pg = sem_page[0][1]
            achados.append(Achado("aviso", "papel-padrao",
                                  f"nenhum CSS declara @page {{ size }}{quais}; o Chrome usou o papel padrão dele, "
                                  f"{papel(pg['w'], pg['h'])}, com a margem padrão em branco"))

        # um PDF so: o book junta; o resto ja e um
        finais = []
        if len(pdfs) == 1:
            os.replace(pdfs[0], destino)
            finais = [destino]
        else:
            junto = os.path.join(tmp, "junto.pdf")
            usado = juntar(pdfs, junto, doc.titulo)
            if usado:
                os.replace(junto, destino)
                info["juntado_por"] = usado
                finais = [destino]
                juntos = LeitorPDF(destino).paginas()
                if len(juntos) != total:
                    achados.append(Achado("erro", "juncao", f"as partes somam {total} páginas e o PDF "
                                                            f"juntado pelo {usado} tem {len(juntos)}"))
            else:
                base = destino[:-4]
                for k, pdf in enumerate(pdfs):
                    final = f"{base}-{k + 1:02d}-{Path(paginas_html[k]).stem}.pdf"
                    os.replace(pdf, final)
                    finais.append(final)
                achados.append(Achado("aviso", "sem-juncao", f"sem pypdf, qpdf, pdfunite ou gs para juntar: "
                                                             f"ficou um PDF por página do book ({len(finais)}), e a numeração "
                                                             "dos achados segue o book inteiro"))
        info["pdf"] = [rel(f) for f in finais] if len(finais) > 1 else rel(finais[0])
        info["paginas"] = total
        todas = [pg for _, _, pags in lidos for pg in pags]
        tamanhos = sorted({(round(pg["w"]), round(pg["h"])) for pg in todas})
        info["tamanho"] = [papel(*t) for t in tamanhos]
        if tipo == "book" and len(tamanhos) > 1:
            achados.append(Achado("erro", "tamanho", "o book mistura tamanhos de página: "
                                                     + "; ".join(papel(*t) for t in tamanhos)))
        # a fonte se confere no que o Chrome escreveu: o gs, ao juntar, apaga o nome das fontes Type 3
        info["fontes"] = conferir_fontes([leitor for _, leitor, _ in lidos], [FAMILIA] + list(a.fonte or []), achados)
        info["bytes"] = sum(os.path.getsize(f) for f in finais)

        if a.previa:
            feitas = []
            for f in finais:
                pasta = f[:-4] + "-previa"
                n, usado, aviso = previa(f, pasta, a.dpi)
                if aviso:
                    achados.append(Achado("aviso", "previa", aviso))
                if n:
                    feitas.append(dict(pasta=rel(pasta), png=n, ferramenta=usado))
            info["previa"] = feitas
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return info, achados, time.time() - t0


# ------------------------------------------------------------------ saida
def relatar(info, achados, segundos, so_erros, cor):
    C = CORES if cor else {k: "" for k in CORES}
    erros = sum(1 for x in achados if x.nivel == "erro")
    avisos = len(achados) - erros
    tipo = info["tipo"]
    if tipo == "deck":
        qual = f"deck, {pl(info.get('slides', 0), 'slide', 'slides')}"
    elif tipo == "book":
        qual = f"book: hub e {pl(len(info['partes']) - 1, 'parte', 'partes')}" if info["partes"] else "book"
    else:
        qual = tipo
    print(f"\n{info['arquivo']}  {C['dim']}({qual}){C['off']}")
    if tipo == "book" and len(info["partes"]) > 1:
        larg = max(len(p["html"]) for p in info["partes"])
        for p in info["partes"]:
            faixa = f"{p['de']} a {p['de'] + p['paginas'] - 1}" if p["paginas"] > 1 else str(p["de"])
            print(f"  {C['dim']}{p['html']:{larg}}  {pl(p['paginas'], 'página', 'páginas')} ({faixa}), "
                  f"{num(p['s'])} s{C['off']}")
    if info["pdf"]:
        pdfs = info["pdf"] if isinstance(info["pdf"], list) else [info["pdf"]]
        junto = f", juntado pelo {info['juntado_por']}" if info.get("juntado_por") else ""
        print(f"  pdf     {pdfs[0]}" + "".join(f"\n          {p}" for p in pdfs[1:]))
        mb = info.get("bytes", 0) / 1048576
        print(f"          {pl(info['paginas'], 'página', 'páginas')} em {' e '.join(info['tamanho'])}, "
              f"{num(mb)} MB, {num(segundos)} s{junto}")
        for f in info["fontes"]:
            print(f"  fontes  {f}")
        for pv in info.get("previa") or []:
            print(f"  prévia  {pv['pasta']}/  {C['dim']}({pv['png']} PNG, {pv['ferramenta']}){C['off']}")
    mostrar = [x for x in achados if not (so_erros and x.nivel == "aviso")]
    for x in mostrar:
        print(f"    {C[x.nivel]}{x.nivel.upper():5}{C['off']} {x.codigo:18} {x.msg}")
    if not mostrar and achados:
        print(f"  {C['dim']}{pl(avisos, 'aviso escondido', 'avisos escondidos')}{C['off']}")
    print(f"  {C['erro'] if erros else C['dim']}{pl(erros, 'erro', 'erros')}{C['off']}, {pl(avisos, 'aviso', 'avisos')}")
    return erros


def main():
    ap = argparse.ArgumentParser(description=f"Impressão do 8020-DS {VERSAO}: gera o PDF da peça pelo Chrome "
                                             "headless e confere páginas, tamanho, fonte e texto sobre texto.")
    ap.add_argument("arquivos", nargs="*", help="deck.html, o index.html do book (o hub), uma parte ou uma página")
    ap.add_argument("--saida", help="pasta, ou caminho terminado em .pdf (só com um arquivo)")
    ap.add_argument("--previa", action="store_true", help="gera um PNG por página numa pasta ao lado do PDF")
    ap.add_argument("--dpi", type=int, default=96, help="resolução da prévia; 96 dá o slide em 1280 por 720 (padrão 96)")
    ap.add_argument("--espera", type=int, default=ESPERA_MS,
                    help=f"tempo virtual, em ms, para script, fonte e imagem antes de imprimir (padrão {ESPERA_MS})")
    ap.add_argument("--fonte", action="append", metavar="FAMÍLIA",
                    help=f"família aceita além da {FAMILIA}; repetir para mais de uma")
    ap.add_argument("--tipo", choices=("deck", "book", "parte", "pagina"), help="força o tipo em vez de deduzir")
    ap.add_argument("--so-erros", action="store_true", help="esconde os avisos")
    ap.add_argument("--json", action="store_true", help="saída legível por máquina")
    ap.add_argument("--sem-cor", action="store_true")
    a = ap.parse_args()

    if not a.arquivos:
        ap.print_help()
        return 2
    if a.espera < 1000:
        ap.error("--espera precisa de pelo menos 1000 ms: com menos, o Chrome pode imprimir antes da fonte ou não imprimir")
    chrome, motivo = achar_chrome()
    if not chrome:
        print(f"imprimir.py: {motivo}.", file=sys.stderr)
        return 1
    cor = not a.sem_cor and sys.stdout.isatty() and not a.json
    if not a.json:
        C = CORES if cor else {k: "" for k in CORES}
        print(f"{C['dim']}{versao_chrome(chrome)}: {chrome}{C['off']}")
    alvos = list(dict.fromkeys(os.path.abspath(x) for x in a.arquivos))
    total, saida = 0, []
    for arq in alvos:
        if not os.path.isfile(arq):
            info, achados, s = dict(arquivo=rel(arq), tipo="?", pdf=None, partes=[]), \
                [Achado("erro", "arquivo", "não existe")], 0.0
        else:
            info, achados, s = imprimir_peca(arq, a, chrome, len(alvos) > 1)
        erros = sum(1 for x in achados if x.nivel == "erro")
        total += erros
        if a.json:
            info.update(segundos=round(s, 1), achados=[x.dic() for x in achados])
            saida.append(info)
        else:
            relatar(info, achados, s, a.so_erros, cor)
    if a.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    elif len(alvos) > 1:
        print(f"\n{pl(total, 'erro', 'erros')} em {len(alvos)} arquivos.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
