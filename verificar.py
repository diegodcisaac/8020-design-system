# -*- coding: utf-8 -*-
"""
verificar.py: le o HTML de uma peca do 8020-DS 4.0 e aponta o que a regra proibe.
Cobre estrutura, acessibilidade, momentos, dado, limites de texto e editorial;
a geometria do slide fica com verificar-geometria.js, que roda no Playwright.
Sem dependencia: so a biblioteca padrao do Python 3.

  python3 verificar.py templates/deck/padrao/deck.html
  python3 verificar.py --pasta templates/book/padrao
  python3 verificar.py --so-erros --json peca.html
  python3 verificar.py --regras

Sai com codigo 1 quando houver erro. Aviso nao bloqueia: le-se e decide-se.
As regras estao em RULES.md; cada achado aponta a sua.
"""
import argparse, json, os, re, sys, unicodedata
from html.parser import HTMLParser

VERSAO = "4.0"

# ------------------------------------------------------------------ arvore
VAZIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
          "param", "source", "track", "wbr",
          "path", "rect", "circle", "line", "polyline", "polygon", "ellipse", "use", "stop", "image"}
INVISIVEIS = {"script", "style", "head", "template"}


class No:
    __slots__ = ("tag", "attrs", "filhos", "pai", "linha", "texto")

    def __init__(self, tag, attrs=None, linha=0, texto=None):
        self.tag, self.attrs, self.linha, self.texto = tag, attrs or {}, linha, texto
        self.filhos, self.pai = [], None

    # --- consultas
    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def tem(self, *cs):
        c = self.classes
        return all(x in c for x in cs)

    def desc(self, tags=None, classe=None):
        """todos os descendentes que casam com tag e/ou classe"""
        for f in self.filhos:
            if f.tag:
                if (tags is None or f.tag in tags) and (classe is None or classe in f.classes):
                    yield f
                yield from f.desc(tags, classe)

    def um(self, tags=None, classe=None):
        return next(self.desc(tags, classe), None)

    def ancestral(self, tags=None, classe=None):
        p = self.pai
        while p is not None:
            if (tags is None or p.tag in tags) and (classe is None or classe in p.classes):
                return p
            p = p.pai
        return None

    def isento(self):
        """contraexemplo declarado: o no, ou um ancestral, traz data-antipadrao"""
        p = self
        while p is not None:
            if "data-antipadrao" in p.attrs:
                return True
            p = p.pai
        return False

    def dentro_de(self, *classes):
        p = self
        while p is not None:
            if p.classes & set(classes):
                return True
            p = p.pai
        return False

    def txt(self, visivel=True):
        """texto concatenado, com os espacos normalizados"""
        out = []

        def anda(n):
            if n.tag is None:
                out.append(n.texto)
            elif not (visivel and n.tag in INVISIVEIS):
                for f in n.filhos:
                    anda(f)
        anda(self)
        return re.sub(r"\s+", " ", "".join(out)).strip()

    def __repr__(self):
        return f"<{self.tag} .{'.'.join(sorted(self.classes))} l{self.linha}>"


class Arvore(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = No("#raiz")
        self.pilha = [self.raiz]

    def _abre(self, tag, attrs, fecha):
        n = No(tag, dict(attrs), self.getpos()[0])
        n.pai = self.pilha[-1]
        self.pilha[-1].filhos.append(n)
        if not fecha and tag not in VAZIOS:
            self.pilha.append(n)
        return n

    def handle_starttag(self, tag, attrs):
        self._abre(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._abre(tag, attrs, True)

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[i].tag == tag:
                del self.pilha[i:]
                return

    def handle_data(self, d):
        if d.strip() or " " in d:
            n = No(None, linha=self.getpos()[0], texto=d)
            n.pai = self.pilha[-1]
            self.pilha[-1].filhos.append(n)


def ler(caminho):
    a = Arvore()
    a.feed(open(caminho, encoding="utf-8").read())
    return a.raiz


# ------------------------------------------------------------------ achados
class Achado:
    def __init__(self, codigo, nivel, ref, onde, msg, linha):
        self.codigo, self.nivel, self.ref = codigo, nivel, ref
        self.onde, self.msg, self.linha = onde, msg, linha

    def dic(self):
        return dict(codigo=self.codigo, nivel=self.nivel, regra=self.ref,
                    onde=self.onde, mensagem=self.msg, linha=self.linha)


CHECAGENS = []


TODOS = ("deck", "parte", "hub", "pagina", "catalogo")


def checagem(codigo, nivel, ref, escopos=TODOS):
    def deco(f):
        CHECAGENS.append((codigo, nivel, ref, set(escopos), f))
        return f
    return deco


# ------------------------------------------------------------------ contexto
class Peca:
    """o documento mais o que o verificador precisa saber sobre ele"""

    def __init__(self, caminho, tipo=None):
        self.caminho = caminho
        self.raiz = ler(caminho)
        self.body = self.raiz.um(("body",)) or self.raiz
        self.deck = self.raiz.um(classe="deck")
        catalogo = any("_catalogo.css" in (l.attrs.get("href") or "") for l in self.raiz.desc(("link",)))
        if tipo:
            self.escopo = tipo
        elif catalogo:
            # pagina de documentacao: mostra slides de demonstracao, mas nao e peca
            self.escopo = "catalogo"
        elif self.deck is not None and self.deck.attrs.get("data-marca"):
            self.escopo = "deck"
        elif "book" in self.body.classes:
            self.escopo = "hub" if self.raiz.um(classe="hub") else "parte"
        else:
            self.escopo = "pagina"
        if self.escopo != "deck":
            self.deck = self.deck if self.escopo == "catalogo" else None
        self.slides = ([f for f in self.deck.filhos if f.tag and "slide" in f.classes]
                       if self.deck is not None and self.escopo == "deck" else [])
        self.caps = self._capitulos()
        self.contextos = self._contextos()
        bruto = " ".join(n.txt(visivel=False) for n in self.raiz.desc(("style",)))
        # bloco declarado como contraexemplo sai da checagem, entre os dois marcadores
        self.estilo = re.sub(r"/\*\s*antipadr(?:ão|ao)\b.*?/\*\s*fim do antipadr(?:ão|ao)\s*\*/", " ", bruto, flags=re.S)

    def _capitulos(self):
        """o capitulo de cada slide; o slide sem marcador herda o do anterior"""
        mapa, atual = {}, None
        for s in self.slides:
            c = capitulo_do_slide(s)
            if c:
                atual = c
            mapa[id(s)] = atual
        return mapa

    def cap(self, s):
        return self.caps.get(id(s)) or "(sem capítulo)"

    @staticmethod
    def e_contracapa(s):
        return s.um(classe="enderecos") is not None

    def _contextos(self):
        """mapeia no -> rotulo do slide ou da secao a que ele pertence"""
        mapa = {}
        if self.escopo == "deck":
            for i, s in enumerate(self.slides, 1):
                self.marcar(mapa, s, f"{i:02d}  {titulo_do_slide(s)}")
        else:
            for s in self.raiz.desc(("section", "article", "header", "footer", "nav")):
                if s.ancestral(("section", "article")) is not None:
                    continue
                rot = s.attrs.get("data-titulo") or (s.um(("h1", "h2")).txt() if s.um(("h1", "h2")) else "") or s.attrs.get("id") or s.tag
                self.marcar(mapa, s, rot[:56])
        return mapa

    @staticmethod
    def marcar(mapa, no, rot):
        mapa[id(no)] = rot
        for d in no.desc():
            mapa.setdefault(id(d), rot)

    def onde(self, no):
        p = no
        while p is not None:
            if id(p) in self.contextos:
                return self.contextos[id(p)]
            p = p.pai
        return "(peça)"

    def capitulo(self, no):
        """o capitulo do slide a que o no pertence, ou None"""
        s = no if no in self.slides else no.ancestral(classe="slide")
        return capitulo_do_slide(s) if s is not None else None


def titulo_do_slide(s):
    for t in ("h2", "h1"):
        n = s.um((t,))
        if n is not None:
            return n.txt()[:44]
    for c in ("statement", "citacao"):
        n = s.um(classe=c)
        if n is not None:
            return n.txt()[:44]
    return "(sem título)"


def capitulo_do_slide(s):
    """so o marcador canonico: <b>Capitulo N</b> dentro do .cap da faixa"""
    cap = s.um(classe="cap")
    if cap is not None:
        b = cap.um(("b",))
        if b is not None and b.txt():
            return b.txt()
    return None


# ------------------------------------------------------------------ apoio
def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def textos_visiveis(peca):
    """(no, texto) de todo texto que o leitor ve, inclusive nos atributos humanos"""
    for n in peca.raiz.desc():
        if n.tag in INVISIVEIS or n.dentro_de("codigo", "arvore") or n.isento():
            continue
        # trecho citado nao e prosa da peca: o <pre> e o <code> saem, com os filhos
        if n.tag in ("code", "pre") or n.ancestral(("code", "pre")) is not None:
            continue
        proprio = "".join(f.texto for f in n.filhos if f.tag is None).strip()
        if proprio:
            yield n, re.sub(r"\s+", " ", proprio)
        for a in ("alt", "aria-label", "title", "data-leitura", "data-t"):
            if n.attrs.get(a):
                yield n, n.attrs[a]


HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
PALETA = {"#fa4616", "#d63a10", "#ffffff", "#fff", "#0a0a0a", "#15110d", "#1d1611",
          "#faf7f2", "#f3ede4", "#1a140f", "#2a201a", "#120e0b", "#000", "#000000"}

ANGLICISMOS = ["insight", "insights", "briefing", "kickoff", "kick-off", "target", "budget",
               "deadline", "feedback", "benchmark", "brainstorm", "core", "engagement",
               "know-how", "mindset", "player", "players", "stakeholder", "stakeholders",
               "timing", "trend", "trends", "workshop", "awareness", "branding", "compliance",
               "dashboard", "framework", "growth", "learnings", "mainstream", "offline",
               "online", "performance", "pitch", "storytelling", "touchpoint", "tracking",
               "call", "meeting", "share of", "top of mind"]

FIGURAS = ["espinha dorsal", "zona cinzenta", "matéria-prima", "ponta do iceberg",
           "virada de chave", "divisor de águas", "raio-x", "raio x", "guardião", "guardiã",
           "anatomia", "ecossistema", "alavancar", "potencializar", "termômetro", "bússola",
           "coração do", "coração da", "palco", "terreno fértil", "pano de fundo",
           "peça-chave", "carro-chefe", "chave de leitura", "dar o tom"]

DIFICEIS = ["declarada", "declarado", "declaradas", "declarados", "eleitos", "eleitas",
            "exitoso", "outrossim", "destarte", "hodierno", "paradigma", "sinergia",
            "holístico", "robusto", "mitigar", "viabilizar", "otimizar", "maximizar",
            "empoderar", "disruptivo", "escalável", "acionável"]

AUTORREFERENCIA = ["neste documento", "nesta apresentação", "neste deck", "neste material",
                   "este material", "esta apresentação", "o presente documento",
                   "a seguir veremos", "como veremos", "no próximo slide",
                   "nas próximas páginas", "ao longo deste", "ao longo desta"]

ACENTOS = """nao sao voce tambem atraves ate ja apos alem area publico publicos
estrategia comunicacao informacao informacoes decisao decisoes versao relatorio negocio
negocios servico servicos mes tres proximo proximos ultimo ultimos historia analise
criterio criterios periodo numero numeros grafico graficos indice pagina paginas unico
unica minimo maximo possivel disponivel nivel niveis orcamento acao acoes atencao
producao execucao direcao regiao regioes opiniao gestao missao visao padrao sera tera
fara havera referencia referencias experiencia audiencia frequencia agencia presenca
comeco financas saude conteudo usuario usuarios video videos municipio municipios
territorio calendario diagnostico obvio credito debito preco precos metrica metricas
midia midias veiculo veiculos tatica taticas estrategico estrategica tecnico tecnica
especifico generico proprio propria memoria ciencia consciencia inicio series""".split()
ACENTOS_RE = re.compile(r"\b(" + "|".join(ACENTOS) + r")\b", re.I)
# endereco de correio, endereco da rede e nome de arquivo nao levam acento: saem da checagem
ENDERECO_RE = re.compile(r"\S+@\S+|https?://\S+|\S*/\S*|"
                          r"\b[\w.-]+\.(?:com|br|org|net|gov|html|css|js|svg|jpg|png|json|py|md)\b", re.I)

DIAGRAMAS = {"esquema", "fluxo", "atores-mapa", "matriz", "diagrama", "rede"}

LIMITES = [("cap", 30, "capítulo mais rótulo"), ("frase", 110, "frase central"),
           ("statement", 70, "statement"), ("citacao", 120, "citação"),
           ("legenda", 120, "legenda de foto"), ("notas", 300, "nota do apresentador")]


# ------------------------------------------------------------------ marca e superficie
@checagem("cor-crua", "erro", 13, escopos=("deck", "parte", "hub", "pagina"))
def c_cor_crua(p):
    for n in p.raiz.desc():
        if "--8020-" in (n.attrs.get("style") or ""):
            yield n, "A peça usa a cor crua `--8020-*` no atributo style. Só papel semântico (`--ink`, `--accent`) atravessa as camadas."
    if "--8020-" in p.estilo:
        yield p.body, "O `<style>` da peça usa a cor crua `--8020-*`. Só papel semântico atravessa as camadas."


@checagem("cor-fora-da-paleta", "erro", 6, escopos=("deck", "parte", "hub", "pagina"))
def c_paleta(p):
    vistos = set()
    for n in p.raiz.desc():
        for h in HEX.findall(n.attrs.get("style") or ""):
            if h.lower() not in PALETA and h.lower() not in vistos:
                vistos.add(h.lower())
                yield n, f"A cor {h} não está na paleta fechada. Use um papel semântico."
    for h in HEX.findall(p.estilo):
        if h.lower() not in PALETA and h.lower() not in vistos:
            vistos.add(h.lower())
            yield p.body, f"O `<style>` da peça traz a cor {h}, fora da paleta fechada."


@checagem("gradiente", "erro", 4)
def c_gradiente(p):
    alvos = [(n, n.attrs.get("style") or "") for n in p.raiz.desc()] + [(p.body, p.estilo)]
    for n, s in alvos:
        if "gradient(" in s and "repeating-linear-gradient" not in s:
            yield n, "Gradiente na peça. A 4.0 tirou o gradiente do sistema: a superfície é chapada."


@checagem("sombra", "erro", "8b")
def c_sombra(p):
    for n in p.raiz.desc():
        if "box-shadow" in (n.attrs.get("style") or ""):
            yield n, "A peça usa `box-shadow`. A profundidade vem do filete de 1 px, nunca de sombra."
    if "box-shadow" in p.estilo:
        yield p.body, "O `<style>` da peça usa `box-shadow`. A profundidade vem do filete de 1 px."


@checagem("raio", "aviso", 31)
def c_raio(p):
    for m in re.finditer(r"border-radius:\s*([^;}\n]+)", p.estilo):
        v = m.group(1).strip()
        if v not in ("0", "0px", "var(--r-0)", "var(--r-media)"):
            yield p.body, f"`border-radius: {v}` no estilo da peça. O raio do sistema é zero, e 6 px só em mídia de book."


# ------------------------------------------------------------------ momentos
def tema(no):
    c = no.classes
    return "laranja" if "tema-laranja" in c else ("escuro" if "tema-escuro" in c else None)


@checagem("momentos-seguidos", "erro", "6a", escopos=("deck",))
def c_momentos_seguidos(p):
    for a, b in zip(p.slides, p.slides[1:]):
        if tema(a) and tema(b) and "s-cheio" in a.classes and "s-cheio" in b.classes and not p.e_contracapa(b):
            yield b, "Dois momentos de página inteira em slides seguidos. O teto da regra 6a é um por capítulo, nunca colados."


@checagem("momento-repetido-no-capitulo", "erro", "6a", escopos=("deck",))
def c_momento_por_capitulo(p):
    conta = {}
    for s in p.slides:
        if tema(s) and "s-cheio" in s.classes and not p.e_contracapa(s):
            conta.setdefault(p.cap(s), []).append(s)
    for cap, ss in conta.items():
        for s in ss[1:]:
            yield s, f"Segundo momento de página inteira em {cap}. O teto é um por capítulo."


@checagem("faixa-laranja-repetida", "erro", "6a", escopos=("deck",))
def c_faixa_laranja(p):
    conta = {}
    for s in p.slides:
        f = s.um(classe="faixa")
        if f is not None and "laranja" in f.classes:
            conta.setdefault(p.caps.get(id(s)) or "(capa)", []).append(s)
    for cap, ss in conta.items():
        for s in ss[1:]:
            yield s, f"Segunda faixa laranja em {cap}. A separatriz laranja é uma por capítulo."


@checagem("momento-por-parte", "erro", "6a", escopos=("parte", "hub", "pagina"))
def c_momento_parte(p):
    ms = [n for n in p.raiz.desc(("section",)) if "momento" in n.classes]
    for m in ms[1:]:
        yield m, "Segundo momento de página inteira nesta página. O teto é um por parte."


@checagem("acentos-acima-do-teto", "aviso", 6, escopos=("deck", "parte", "hub", "pagina"))
def c_acentos(p):
    funcional = {"quadrado", "o20", "agora", "atual", "is-error", "atencao", "tique", "d1", "d2", "d3", "d4"}
    blocos = p.slides if p.escopo == "deck" else [p.body]
    for b in blocos:
        n = 0
        for d in b.desc():
            if d.classes & funcional or d.dentro_de("grafico", "legenda-rampa"):
                continue
            if tema(d) or ("faixa" in d.classes and "laranja" in d.classes):
                n += 1
            elif "var(--accent)" in (d.attrs.get("style") or ""):
                n += 1
        if n > 3:
            yield b, f"{n} momentos de acento. O teto da regra 6 é três; o laranja funcional e o 20 do dado não contam."


# ------------------------------------------------------------------ dado e acessibilidade
@checagem("barra-em-div", "erro", 8)
def c_barra_em_div(p):
    for g in p.raiz.desc(classe="grafico"):
        for d in g.desc():
            if d.tag in ("div", "span", "li") and re.search(r"width:\s*[\d.]+%", d.attrs.get("style") or ""):
                yield d, "Barra feita com `div` e largura em porcentagem. Gráfico é SVG real."


@checagem("svg-fill-em-texto", "erro", "8c")
def c_fill_texto(p):
    for t in p.raiz.desc(("text", "tspan")):
        if "fill" in t.attrs:
            yield t, "`<text>` com o atributo `fill`. A cor de texto em SVG vai por `style` ou por classe, senão a regra de CSS ganha e o texto some."


@checagem("dado-sem-papel", "erro", 10)
def c_dado_papel(p):
    for g in p.raiz.desc(classe="grafico"):
        for s in g.desc(("svg",)):
            if s.ancestral(("svg",)) is not None:
                continue
            if s.attrs.get("role") != "img":
                yield s, "SVG de dado sem `role=\"img\"`."
            elif not s.attrs.get("aria-label"):
                yield s, "SVG de dado sem `aria-label` descritivo."


@checagem("dado-sem-titulo", "erro", 10)
def c_dado_titulo(p):
    for g in p.raiz.desc(classe="grafico"):
        for s in g.desc(("svg",)):
            if s.ancestral(("svg",)) is None and s.attrs.get("role") == "img" and s.um(("title",)) is None:
                yield s, "SVG de dado sem `<title>` interno."


@checagem("svg-decorativo-exposto", "aviso", 10)
def c_svg_decorativo(p):
    for s in p.raiz.desc(("svg",)):
        if s.ancestral(("svg",)) is not None:
            continue
        if not s.attrs.get("role") and s.attrs.get("aria-hidden") != "true":
            yield s, "SVG sem `role=\"img\"` e sem `aria-hidden=\"true\"`. Decorativo se esconde; de dado se descreve."


@checagem("seta-sem-marcador", "aviso", 9)
def c_seta(p):
    for s in p.raiz.desc(("svg",)):
        if s.um(("marker",)) is not None:
            continue
        for pg in s.desc(("polygon",)):
            pts = (pg.attrs.get("points") or "").replace(",", " ").split()
            if len(pts) == 6:
                yield pg, "Triângulo de três pontos em um SVG sem `<marker>`. Seta vem de um marcador em `<defs>`."
                break


@checagem("dado-sem-razao", "erro", 42, escopos=("parte", "hub", "pagina"))
def c_razao(p):
    for f in p.raiz.desc(classe="figura"):
        if f.um(classe="grafico") is None:
            continue
        if f.um(("details",)) is None and f.um(classe="tabela") is None:
            yield f, "Figura de dado sem livro-razão. A tabela sob a figura, dentro de um `details`, é obrigatória."


@checagem("dado-sem-leitura", "aviso", 42, escopos=("parte", "hub", "pagina"))
def c_leitura(p):
    for f in p.raiz.desc(classe="figura"):
        if f.um(classe="grafico") is not None and f.um(classe="leitura") is None:
            yield f, "Figura de dado sem a leitura em palavras. A página tem de informar parada."


@checagem("dado-sem-fonte", "aviso", 23, escopos=("deck",))
def c_fonte(p):
    for s in p.slides:
        g = s.um(classe="grafico")
        if g is not None and not (g.classes & DIAGRAMAS) and s.um(classe="fonte") is None:
            yield s, "Slide com gráfico e sem a fonte ao pé."


@checagem("imagem-sem-alt", "erro", 10)
def c_alt(p):
    for i in p.raiz.desc(("img",)):
        if "alt" not in i.attrs:
            yield i, f"`<img>` sem `alt`: {i.attrs.get('src', '')}"


@checagem("imagem-gerada-sem-marca", "aviso", 3, escopos=("deck", "parte", "hub", "pagina"))
def c_imagem_marcada(p):
    texto = p.raiz.txt().lower()
    if p.raiz.um(("img",)) is not None and "ilustrativa" not in texto and "ilustrativas" not in texto:
        yield p.body, "A peça tem imagem e não diz em lugar nenhum que a imagem é ilustrativa. Toda imagem gerada é marcada."


@checagem("movimento-sem-guarda", "aviso", 11)
def c_movimento(p):
    if "prefers-reduced-motion" in p.estilo:
        return
    for m in re.finditer(r"\b(?:animation|transition):\s*([^;}\n]+)", p.estilo):
        d = m.group(1)
        if "var(--dur" in d:
            continue   # o token ja cai para 1 ms quando o leitor pede menos movimento
        yield p.body, f"`{m.group(0)[:60]}` anima com duração fixa e sem `prefers-reduced-motion`. Use `var(--dur)` ou escreva a guarda."


# ------------------------------------------------------------------ hierarquia e numero
@checagem("heading-fora-de-ordem", "erro", 12)
def c_headings(p):
    ultimo = 0
    for h in p.raiz.desc(("h1", "h2", "h3", "h4", "h5", "h6")):
        n = int(h.tag[1])
        if ultimo and n > ultimo + 1:
            yield h, f"`{h.tag}` depois de `h{ultimo}`: a hierarquia pulou um nível."
        ultimo = n


@checagem("h1-repetido", "erro", 12)
def c_h1(p):
    hs = list(p.raiz.desc(("h1",)))
    for h in hs[1:]:
        yield h, "Segundo `h1` na página. Um por página."


@checagem("numero-sem-frase", "erro", 14)
def c_numero(p):
    for bloco in p.raiz.desc(classe="numeros"):
        for par in bloco.desc(("p", "div", "li")):
            forte = par.um(("strong", "b"))
            if forte is None:
                continue
            resto = par.txt().replace(forte.txt(), "").strip()
            if len(resto) < 12:
                yield par, f"O número \"{forte.txt()}\" aparece sem a frase que diz o que se mede e por que importa."


# ------------------------------------------------------------------ deck
@checagem("deck-sem-script", "erro", 39, escopos=("deck",))
def c_deck_script(p):
    if not any("deck.js" in (s.attrs.get("src") or "") for s in p.raiz.desc(("script",))):
        yield p.body, "O deck não carrega `assets/deck.js`. Sem ele o sistema não escreve contador, trilho nem moldura."


@checagem("faixa-sem-frase", "erro", 38, escopos=("deck",))
def c_faixa_frase(p):
    for s in p.slides:
        f = s.um(classe="faixa")
        if f is not None and f.um(classe="frase") is None:
            yield s, "Faixa sem frase central. A frase é obrigatória e é onde o achado do slide aparece."


@checagem("faixa-sem-titulo", "erro", 38, escopos=("deck",))
def c_faixa_titulo(p):
    for s in p.slides:
        f = s.um(classe="faixa")
        if f is not None and f.um(("h1", "h2")) is None and "s-cheio" not in s.classes:
            yield s, "Faixa sem título descritivo."


@checagem("slide-sem-notas", "aviso", "8f", escopos=("deck",))
def c_notas(p):
    for s in p.slides:
        if s.um(classe="notas") is None:
            yield s, "Slide sem `<aside class=\"notas\">`. A visão do apresentador fica vazia neste slide."


@checagem("deck-sem-sumario", "erro", 29, escopos=("deck",))
def c_sumario(p):
    if p.raiz.um(classe="sumario-slide") is None:
        yield p.body, "O deck não tem sumário. A regra 29 pede sumário no início."


@checagem("deck-sem-esquema", "erro", 29, escopos=("deck",))
def c_esquema(p):
    if p.raiz.um(classe="esquema") is None:
        yield p.body, "O deck não tem o esquema de fechamento com a estratégia inteira em uma página."


@checagem("deck-sem-contracapa", "erro", 29, escopos=("deck",))
def c_contracapa(p):
    if p.slides and p.slides[-1].um(classe="enderecos") is None:
        yield p.slides[-1], "O último slide não é a contracapa com a logo e os três endereços."


def capitulos_do_deck(p):
    caps = []
    for s in p.slides:
        c = p.caps.get(id(s))
        if c and c.lower().startswith("capítulo") and c not in caps:
            caps.append(c)
    return caps


@checagem("capitulo-sem-separatriz", "erro", 29, escopos=("deck",))
def c_separatriz(p):
    com = {p.cap(s) for s in p.slides if s.um(classe="separatriz") is not None}
    for c in capitulos_do_deck(p):
        if c not in com:
            yield p.body, f"{c} não tem separatriz numerada."


@checagem("capitulo-sem-recap", "erro", 28, escopos=("deck",))
def c_recap(p):
    com = {p.cap(s) for s in p.slides if s.um(classe="recap") is not None}
    for c in capitulos_do_deck(p):
        if c not in com:
            yield p.body, f"{c} não fecha com \"O que aprendemos no capítulo\"."


@checagem("tabela-larga", "erro", 49, escopos=("deck",))
def c_tabela(p):
    for s in p.slides:
        if "s-topo" not in s.classes and "s-faixa" not in s.classes:
            continue
        for t in s.desc(("table",)):
            tr = t.um(("tr",))
            if tr is None:
                continue
            cols = len([c for c in tr.filhos if c.tag in ("th", "td")])
            teto = 6 if "s-topo" in s.classes else 4
            if cols > teto:
                yield t, f"Tabela com {cols} colunas; o teto do registro é {teto}."


# ------------------------------------------------------------------ book
@checagem("book-sem-chave", "erro", 30, escopos=("parte", "hub"))
def c_chave(p):
    if not p.body.attrs.get("data-book"):
        yield p.body, "O `body` não tem `data-book`. Sem a chave, o book não guarda onde o leitor parou."


@checagem("passo-sem-estado", "erro", 30, escopos=("parte", "hub", "pagina"))
def c_passo(p):
    for passo in p.raiz.desc(classe="passo-m"):
        falta = [a for a in ("data-estado", "data-leitura") if not passo.attrs.get(a)]
        if falta:
            yield passo, f"Passo de scrollytelling sem {' e sem '.join('`' + a + '`' for a in falta)}."


@checagem("nota-sem-ancora", "erro", 30, escopos=("parte", "hub", "pagina"))
def c_nota(p):
    ids = {n.attrs["id"] for n in p.raiz.desc() if n.attrs.get("id")}
    for nota in p.raiz.desc(classe="nota-m"):
        ref = nota.attrs.get("data-ref")
        if ref and ref not in ids:
            yield nota, f"A nota da margem aponta para `{ref}`, que não existe na página."
    for ch in p.raiz.desc(classe="chamada"):
        alvo = (ch.attrs.get("href") or "")[1:]
        if alvo and alvo not in ids:
            yield ch, f"A chamada aponta para `#{alvo}`, que não existe na página."


# ------------------------------------------------------------------ limites de texto
@checagem("limite-de-texto", "erro", 48, escopos=("deck",))
def c_limites(p):
    for classe, teto, nome in LIMITES:
        for n in p.raiz.desc(classe=classe):
            if n.um(classe=classe) is not None:
                continue
            t = n.txt()
            if len(t) > teto:
                yield n, f"{nome.capitalize()} com {len(t)} caracteres; o teto é {teto}. Começa em \"{t[:44]}…\""
    for s in p.slides:
        alvo = s.um(classe="faixa")
        teto, nome = (48, "título da faixa") if alvo is not None else (60, "título de slide quieto")
        h = (alvo or s).um(("h2",))
        if h is not None and len(h.txt()) > teto:
            yield h, f"{nome.capitalize()} com {len(h.txt())} caracteres; o teto é {teto}."
    for c in p.raiz.desc(("td", "th")):
        if len(c.txt()) > 40:
            yield c, f"Célula com {len(c.txt())} caracteres; o teto é 40."


# ------------------------------------------------------------------ editorial
@checagem("travessao", "erro", 19)
def c_travessao(p):
    for n, t in textos_visiveis(p):
        if "—" in t or "–" in t:
            yield n, f"Travessão no texto: \"{t[:60]}\". No lugar dele: dois-pontos, vírgula, parênteses ou ponto."


@checagem("sem-acento", "erro", 18)
def c_acento(p):
    vistas = set()
    for n, t in textos_visiveis(p):
        t = ENDERECO_RE.sub(" ", t)
        for m in ACENTOS_RE.finditer(t):
            w = m.group(1)
            if w.lower() in vistas:
                continue
            vistas.add(w.lower())
            yield n, f"\"{w}\" sem acento. Acentuação correta sempre, inclusive em caixa alta e em atributo."


@checagem("anglicismo", "aviso", 20)
def c_anglicismo(p):
    vistas = set()
    for n, t in textos_visiveis(p):
        b = t.lower()
        for a in ANGLICISMOS:
            if re.search(r"\b" + re.escape(a) + r"\b", b) and a not in vistas:
                vistas.add(a)
                yield n, f"\"{a}\" é anglicismo evitável."


@checagem("figura-de-linguagem", "aviso", 25)
def c_figura(p):
    vistas = set()
    for n, t in textos_visiveis(p):
        b = t.lower()
        for f in FIGURAS:
            if f in b and f not in vistas:
                vistas.add(f)
                yield n, f"\"{f}\" é figura de linguagem. Dizer o que é, literalmente."


@checagem("palavra-dificil", "aviso", 27)
def c_dificil(p):
    vistas = set()
    for n, t in textos_visiveis(p):
        b = t.lower()
        for d in DIFICEIS:
            if re.search(r"\b" + re.escape(d) + r"\b", b) and d not in vistas:
                vistas.add(d)
                yield n, f"\"{d}\" é palavra difícil ou pouco usada. Troque pela palavra do dia a dia."


@checagem("autorreferencia", "aviso", 22)
def c_autorreferencia(p):
    vistas = set()
    for n, t in textos_visiveis(p):
        b = t.lower()
        for a in AUTORREFERENCIA:
            if a in b and a not in vistas:
                vistas.add(a)
                yield n, f"\"{a}\": o texto lidera pelo assunto, não pelo veículo."


@checagem("titulo-com-achado", "aviso", 21, escopos=("deck", "parte", "hub", "pagina"))
def c_titulo_achado(p):
    for h in p.raiz.desc(("h1", "h2", "h3")):
        t = h.txt()
        if re.search(r"\d+\s*%|R\$|\b\d+\s*(pontos|mil|milhões|vezes)\b", t):
            yield h, f"O título carrega o achado: \"{t[:56]}\". O achado vai na frase central."


@checagem("titulo-com-contagem", "aviso", 21, escopos=("deck", "parte", "hub", "pagina"))
def c_titulo_contagem(p):
    num = r"(dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|\d+)"
    for h in p.raiz.desc(("h1", "h2", "h3")):
        t = h.txt()
        if re.match(r"^(os|as)\s+" + num + r"\b", t, re.I) or re.match(r"^" + num + r"\s+\w+", t, re.I):
            yield h, f"Título que inventaria: \"{t[:56]}\". O título afirma o aprendizado, não conta os itens."


@checagem("marca-no-texto", "aviso", 24, escopos=("deck", "parte", "hub", "pagina"))
def c_marca(p):
    for n, t in textos_visiveis(p):
        if n.dentro_de("marca", "logo", "enderecos", "rodape", "rodape-slide", "topo") or n.tag in ("title",) or "logo" in n.classes:
            continue
        if re.search(r"\b(80\s?20|8020)\b", t) and "8020-DS" not in t:
            yield n, f"O nome da 80 20 no texto: \"{t[:56]}\". Em peça cliente a marca aparece na logo, na capa e na contracapa."


# ------------------------------------------------------------------ execucao
def verificar(caminho, tipo=None):
    p = Peca(caminho, tipo)
    achados = []
    for codigo, nivel, ref, escopos, f in CHECAGENS:
        if p.escopo not in escopos:
            continue
        for r in f(p):
            no, msg = r[0], r[1]
            if no.isento():
                continue
            achados.append(Achado(codigo, r[2] if len(r) > 2 else nivel, ref, p.onde(no), msg, no.linha))
    achados.sort(key=lambda a: (a.onde, 0 if a.nivel == "erro" else 1, a.linha))
    return p, achados


CORES = {"erro": "\033[31m", "aviso": "\033[33m", "off": "\033[0m", "dim": "\033[2m"}


def imprimir(p, achados, so_erros, cor):
    C = CORES if cor else {k: "" for k in CORES}
    rel = os.path.relpath(p.caminho)
    mostrar = [a for a in achados if not (so_erros and a.nivel == "aviso")]
    erros = sum(1 for a in achados if a.nivel == "erro")
    avisos = len(achados) - erros
    print(f"\n{rel}  {C['dim']}({p.escopo}, {len(p.slides) or len(set(p.contextos.values()))} "
          f"{'slides' if p.escopo == 'deck' else 'seções'}){C['off']}")
    onde = None
    for a in mostrar:
        if a.onde != onde:
            onde = a.onde
            print(f"  {C['dim']}{onde}{C['off']}")
        print(f"    {C[a.nivel]}{a.nivel.upper():5}{C['off']} {a.codigo:28} {a.msg}  "
              f"{C['dim']}(regra {a.ref}, linha {a.linha}){C['off']}")
    if not mostrar:
        print(f"  {C['dim']}nada a apontar{C['off']}" if not achados else f"  {C['dim']}{avisos} avisos escondidos{C['off']}")
    print(f"  {C['erro'] if erros else C['dim']}{erros} erros{C['off']}, {avisos} avisos")
    return erros


def main():
    ap = argparse.ArgumentParser(description=f"Verificador do 8020-DS {VERSAO}: le a peca e aponta o que a regra proibe.")
    ap.add_argument("arquivos", nargs="*", help="um ou mais .html")
    ap.add_argument("--pasta", help="verifica todo .html da pasta, recursivo")
    ap.add_argument("--so-erros", action="store_true", help="esconde os avisos")
    ap.add_argument("--json", action="store_true", help="saida legivel por maquina")
    ap.add_argument("--regras", action="store_true", help="lista as checagens e sai")
    ap.add_argument("--tipo", choices=TODOS, help="forca o escopo em vez de deduzir do arquivo")
    ap.add_argument("--sem-cor", action="store_true")
    a = ap.parse_args()

    if a.regras:
        print(f"{'código':30}{'nível':8}{'regra':8}escopo")
        for codigo, nivel, ref, escopos, _ in sorted(CHECAGENS, key=lambda x: x[0]):
            print(f"{codigo:30}{nivel:8}{str(ref):8}{', '.join(sorted(escopos))}")
        return 0

    alvos = list(a.arquivos)
    if a.pasta:
        for raiz, _, arqs in os.walk(a.pasta):
            alvos += [os.path.join(raiz, f) for f in sorted(arqs) if f.endswith(".html")]
    if not alvos:
        ap.print_help()
        return 2

    cor = not a.sem_cor and sys.stdout.isatty()
    total, saida = 0, []
    for c in sorted(set(alvos)):
        p, achados = verificar(c, a.tipo)
        if a.json:
            saida.append(dict(arquivo=os.path.relpath(c), escopo=p.escopo,
                              slides=len(p.slides), achados=[x.dic() for x in achados]))
            total += sum(1 for x in achados if x.nivel == "erro")
        else:
            total += imprimir(p, achados, a.so_erros, cor)
    if a.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    elif len(alvos) > 1:
        print(f"\n{total} erros em {len(set(alvos))} arquivos.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
