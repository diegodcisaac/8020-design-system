# -*- coding: utf-8 -*-
"""
conferir.py: confere o sistema contra a propria documentacao.

O verificar.py cuida da peca; este cuida do repositorio. Conta o que existe de
verdade (checagens, paginas, formas, regras, slides, links) e compara com o que
README.md, GUIA.md, llms.txt, RULES.md e index.html afirmam. Numero de documento
envelhece calado, e ja envelheceu duas vezes aqui.

  python3 conferir.py            confere tudo
  python3 conferir.py --contas   so mostra o que existe, sem comparar

Sai com codigo 1 quando alguma afirmacao nao bate ou algum link nao resolve.
"""
import argparse, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
def ler(p): return open(os.path.join(AQUI, p), encoding="utf-8").read()
def existe(p): return os.path.exists(os.path.join(AQUI, p))

UNIDADE = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6,
           "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13,
           "catorze": 14, "quatorze": 14, "quinze": 15, "dezesseis": 16, "dezessete": 17,
           "dezoito": 18, "dezenove": 19}
DEZENA = {"vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60,
          "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100, "cento": 100}


def para_numero(txt):
    """"28", "vinte e oito" e "vinte" viram 28, 28 e 20; o que nao e numero vira None"""
    t = txt.lower().strip(",.;:()")
    if t.isdigit():
        return int(t)
    partes = [x for x in t.replace(" e ", " ").split() if x]
    total, achou = 0, False
    for x in partes:
        if x in DEZENA:
            total += DEZENA[x]; achou = True
        elif x in UNIDADE:
            total += UNIDADE[x]; achou = True
        else:
            return None
    return total if achou else None


# ------------------------------------------------------------------ o que existe
def contar():
    c = {}
    regras = subprocess.run([sys.executable, "verificar.py", "--regras"], cwd=AQUI,
                            capture_output=True, text=True).stdout
    c["checagens"] = len([l for l in regras.split("\n")[1:] if l.strip()])
    c["codigos"] = {l.split()[0] for l in regras.split("\n")[1:] if l.strip()}
    c["paginas de catalogo"] = len([f for f in os.listdir(os.path.join(AQUI, "patterns")) if f.endswith(".html")])
    c["pares de antipadrao"] = ler("patterns/proibido.html").count('class="pilha par"')
    c["formas de dado"] = ler("patterns/dado.html").count('<article class="padrao"')
    dado = ler("patterns/dado.html")
    i, j = dado.find('id="regras"'), dado.find("</section>", dado.find('id="regras"'))
    c["regras de dado"] = dado[i:j].count("<div><strong>")
    c["slides do deck padrao"] = ler("templates/deck/padrao/deck.html").count('class="slide ')
    c["slides do editorial"] = ler("templates/deck/editorial/deck.html").count('class="slide ')
    deck_cat = ler("patterns/deck.html")
    a = deck_cat.find('id="tipos"')
    b = deck_cat.find("<section", a + 10)
    c["tipos de slide"] = deck_cat[a:b if b > 0 else len(deck_cat)].count('class="padrao"')
    rules = ler("RULES.md")
    c["maior regra"] = max(int(m) for m in re.findall(r"^(\d+)[a-z]?\. ", rules, re.M))
    guia = ler("GUIA.md")
    def linhas_tabela(titulo, ate):
        a, b = guia.find(titulo), guia.find(ate)
        return len([l for l in guia[a:b].split("\n") if l.startswith("| ") and "---" not in l]) - 1
    c["tipos no guia"] = linhas_tabela("## A receita de cada tipo de slide", "## A receita de cada seção")
    c["secoes de book no guia"] = linhas_tabela("## A receita de cada seção do book", "## O catálogo")
    c["arquivos"] = sum(len(a) for r, d, a in os.walk(AQUI)
                        if ".git" not in r for a in [a] if True)
    return c


# ------------------------------------------------------------------ o que se afirma
# Cada afirmacao e uma frase exata com {N} no lugar do numero. A frase precisa
# existir e o numero precisa bater. Busca solta deixava uma ocorrencia certa
# mascarar uma errada, que e falso-passa: pior do que nao ter ferramenta.
def afirmacoes(c):
    return [
        ("README.md", "São {N} checagens", c["checagens"]),
        ("README.md", "traz as {N} páginas do catálogo", c["paginas de catalogo"]),
        ("README.md", "que disparam 35 das {N} checagens", c["checagens"]),
        ("README.md", "deck/padrao/     deck.html  CONTRATO.md     {N} slides", c["slides do deck padrao"]),
        ("README.md", "deck/editorial/  deck.html  CONTRATO.md     {N} slides", c["slides do editorial"]),
        ("llms.txt", "disparam 35 das {N} checagens", c["checagens"]),
        ("llms.txt", "deck denso, didático, sequencial, {N} slides", c["slides do deck padrao"]),
        ("llms.txt", "deck de respiro, imagem e statement, {N} slides", c["slides do editorial"]),
        ("GUIA.md", "{N} páginas com os blocos ao vivo", c["paginas de catalogo"]),
        ("index.html", "{N} páginas, cada uma com os blocos ao vivo", c["paginas de catalogo"]),
        ("index.html", "{N} pares de errado ao lado de certo", c["pares de antipadrao"]),
        ("index.html", "os {N} tipos de slide", c["tipos de slide"]),
        ("index.html", "{N} formas em SVG real para copiar", c["formas de dado"]),
        ("index.html", "as {N} regras", c["regras de dado"]),
        ("index.html", "traz as {N} páginas do catálogo", c["paginas de catalogo"]),
        ("patterns/dado.html", "As {N} regras de dado", c["regras de dado"]),
        ("testes/verificador-deve-reprovar.html", "disparam 35 das {N} checagens", c["checagens"]),
    ]


def confere_numero(arquivo, frase, valor):
    """a frase tem de existir, e o numero no lugar de {N} tem de bater"""
    s = re.sub(r"\s+", " ", ler(arquivo))
    padrao = re.escape(frase).replace(r"\{N\}", r"([\wÀ-ÿ]+(?: e [\wÀ-ÿ]+)?)")
    padrao = re.sub(r"(\\ )+", " ", padrao)
    achou = list(re.finditer(padrao, s, re.I))
    if not achou:
        return f'{arquivo}: a frase "{frase}" sumiu. Se o texto mudou, atualize o conferir.py junto.'
    for m in achou:
        n = para_numero(m.group(1))
        if n != valor:
            return f'{arquivo}: "{frase.replace("{N}", m.group(1))}" onde o sistema tem {valor}'
    return None


# ------------------------------------------------------------------ coerencia interna
def checagens_citadas(c):
    """todo codigo citado na tabela do RULES.md existe no verificar.py"""
    citados = set(re.findall(r"`([a-z][a-z0-9-]+)`", ler("RULES.md")))
    inventados = {x for x in citados if "-" in x and x not in c["codigos"]
                  and not x.endswith((".py", ".js", ".css", ".json", ".html", ".md", ".txt"))
                  and not x.startswith(("data-", "aria-", "s-", "d1", "o20", "tema-", "--"))
                  and x in ler("RULES.md").split("## O que o verificador cobra")[-1]}
    return [f"RULES.md cita a checagem `{x}`, que não existe no verificar.py" for x in sorted(inventados)]


def links():
    """todo href, src e link de markdown resolve"""
    ruins = []
    for raiz, dirs, arqs in os.walk(AQUI):
        dirs[:] = [d for d in dirs if d not in ("candidatas", "__pycache__", ".git", "fonte")]
        for f in arqs:
            if not f.endswith((".html", ".md", ".txt")):
                continue
            if f == "verificador-deve-reprovar.html":
                continue   # o teste de regressao aponta de proposito para uma imagem que nao existe
            p = os.path.join(raiz, f)
            s = open(p, encoding="utf-8", errors="replace").read()
            refs = set(re.findall(r'(?:href|src)="([^"#?]+)"', s)) | set(re.findall(r"\]\(([^)#\s]+)\)", s))
            for r in refs:
                if r.startswith(("http", "data:", "#", "mailto:", "//")) or r.count("../") > 2:
                    continue
                if not os.path.exists(os.path.normpath(os.path.join(raiz, r))):
                    ruins.append(f"{os.path.relpath(p, AQUI)} aponta para {r}, que não existe")
    return ruins


def regressao():
    """o exemplo com defeito tem de continuar reprovando"""
    r = subprocess.run([sys.executable, "verificar.py", "--sem-cor", "--so-erros", "testes/verificador-deve-reprovar.html"],
                       cwd=AQUI, capture_output=True, text=True)
    if r.returncode == 0:
        return ["testes/verificador-deve-reprovar.html passou no verificador: o verificador quebrou"]
    return []


def sistema_limpo():
    """as pecas e as paginas do sistema nao podem ter erro"""
    alvos = ["index.html"] + sorted("patterns/" + f for f in os.listdir(os.path.join(AQUI, "patterns")) if f.endswith(".html"))
    alvos += ["templates/deck/padrao/deck.html", "templates/deck/editorial/deck.html",
              "templates/book/padrao/index.html"]
    alvos += sorted("templates/book/padrao/partes/" + f for f in os.listdir(os.path.join(AQUI, "templates/book/padrao/partes")))
    r = subprocess.run([sys.executable, "verificar.py", "--sem-cor", "--so-erros", *alvos],
                       cwd=AQUI, capture_output=True, text=True)
    if r.returncode != 0:
        return ["o verificador achou erro no próprio sistema; rode: python3 verificar.py " + alvos[0] + " ..."]
    return []


def main():
    ap = argparse.ArgumentParser(description="Confere o sistema contra a propria documentacao.")
    ap.add_argument("--contas", action="store_true", help="so mostra o que existe")
    a = ap.parse_args()

    c = contar()
    print("O que o sistema tem")
    for k, v in c.items():
        if k != "codigos":
            print(f"  {str(v):>4}  {k}")
    if a.contas:
        return 0

    problemas = []
    for arquivo, trecho, valor in afirmacoes(c):
        r = confere_numero(arquivo, trecho, valor)
        if r:
            problemas.append(r)
    problemas += checagens_citadas(c) + links() + regressao() + sistema_limpo()

    print()
    if problemas:
        print(f"{len(problemas)} coisas fora do lugar")
        for p in problemas:
            print("  " + p)
        return 1
    print("documentação, links, regressão e sistema: tudo bate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
