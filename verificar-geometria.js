/* ============================================================
   verificar-geometria.js  ·  8020-DS 4.0
   A segunda passada do verificador: o que so a renderizacao mostra.
   Cobra as regras 47 e 49 do RULES.md.

     - caixa fora dos 1280 por 720 do slide
     - texto sobre texto
     - rotulo de SVG cruzando traco ou saindo da propria caixa
     - piso de fonte efetivo (texto de SVG vezes a escala do viewBox)
     - altura da faixa e folga na base do conteudo
     - imagem que nao carregou
     - na pagina: rolagem horizontal e piso de 11,5 px

   Elemento com data-antipadrao, e tudo dentro dele, sai das duas medicoes:
   e contraexemplo declarado, como na pagina patterns/proibido.html.

   Como rodar. O Playwright nao abre file://, entao a peca precisa estar
   num servidor local (basta um python3 -m http.server na pasta da peca).
   Trocar __URL__ pelo endereco da peca e __DIR__ pela pasta das capturas,
   e passar o arquivo inteiro para browser_run_code_unsafe.

   Devolve uma linha por slide (ou uma por secao, na pagina) e o resumo.
   Zero erro e a condicao de saida da peca.
   ============================================================ */
async (page) => {
  const DIR = '__DIR__';
  const URL = '__URL__';
  const SL_W = 1280, SL_H = 720;
  const PISO_SLIDE = 14, PISO_PAGINA = 11.5;

  await page.setViewportSize({ width: 1328, height: 856 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto(URL, { waitUntil: 'load' });
  await page.waitForFunction(() => document.fonts.status === 'loaded');
  await page.waitForTimeout(400);

  /* deck de verdade traz data-marca no .deck; pagina de catalogo so mostra slides de demonstracao */
  const ehDeck = await page.evaluate(() => !!document.querySelector('.deck[data-marca] > .slide'));

  /* ---------------------------------------------------------------- pagina */
  if (!ehDeck) {
    const r = await page.evaluate((PISO) => {
      const out = { rolagem: document.documentElement.scrollWidth > window.innerWidth + 1, pequenos: [], quebradas: [], svgFora: [] };
      document.querySelectorAll('*').forEach((el) => {
        if (el.closest('[data-antipadrao]')) return;   // contraexemplo declarado
        const cx = getComputedStyle(el);
        if (cx.display === 'none' || cx.visibility === 'hidden') return;
        const proprio = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
        if (proprio) {
          const svg = el.ownerSVGElement;
          let esc = 1;
          if (svg && svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) esc = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
          const fs = parseFloat(cx.fontSize) * esc;
          if (fs < PISO - 0.05) out.pequenos.push(`${+fs.toFixed(1)}px "${el.textContent.trim().slice(0, 28)}"`);
        }
        if (el.tagName === 'IMG' && !(el.complete && el.naturalWidth > 0)) out.quebradas.push(el.getAttribute('src'));
      });
      document.querySelectorAll('svg').forEach((svg) => {
        const S = svg.getBoundingClientRect();
        svg.querySelectorAll('text').forEach((t) => {
          const q = t.getBoundingClientRect();
          if (q.right > S.right + 0.5 || q.left < S.left - 0.5 || q.bottom > S.bottom + 0.5 || q.top < S.top - 0.5)
            out.svgFora.push(`"${t.textContent.trim().slice(0, 24)}"`);
        });
      });
      return out;
    }, PISO_PAGINA);
    await page.screenshot({ path: `${DIR}/pagina-1328.png`, fullPage: true });
    const linhas = [];
    if (r.rolagem) linhas.push('ROLAGEM HORIZONTAL na largura de 1328');
    if (r.pequenos.length) linhas.push(`FONTE abaixo de ${PISO_PAGINA}px: ${r.pequenos.slice(0, 12).join(' | ')}`);
    if (r.quebradas.length) linhas.push(`IMAGEM que nao carregou: ${r.quebradas.join(', ')}`);
    if (r.svgFora.length) linhas.push(`TEXTO fora da caixa do SVG: ${r.svgFora.slice(0, 12).join(' | ')}`);
    return (linhas.length ? linhas.join('\n') : 'pagina: nada a apontar') + `\n${linhas.length} achados`;
  }

  /* ------------------------------------------------------------------ deck */
  await page.goto(URL + '#1', { waitUntil: 'load' });
  await page.waitForTimeout(300);
  const N = await page.evaluate(() => document.querySelectorAll('.deck > .slide').length);
  const out = [];

  for (let k = 1; k <= N; k++) {
    await page.evaluate((k) => { location.hash = '#' + k; }, k);
    await page.waitForTimeout(150);
    const m = await page.evaluate(([SL_W, SL_H, PISO]) => {
      const deck = document.querySelector('.deck');
      const s = deck.querySelector('.slide.atual') || deck.children[0];
      const R = s.getBoundingClientRect(); const sc = R.width / SL_W;
      const rel = (r) => ({ l: (r.left - R.left) / sc, t: (r.top - R.top) / sc, r: (r.right - R.left) / sc, b: (r.bottom - R.top) / sc });
      const rd = (x) => Math.round(x);
      const tit = s.querySelector('h2, .statement, .citacao');
      const res = { titulo: tit ? tit.textContent.trim().replace(/\s+/g, ' ').slice(0, 40) : '(sem título)',
                    fora: [], sobrepostos: [], svg: [], menorFonte: 99, imagens: [], faixaH: null, sobra: null };

      const escalaSVG = (el) => {
        const svg = el.ownerSVGElement; if (!svg) return 1;
        const vb = svg.viewBox && svg.viewBox.baseVal; if (!vb || !vb.width) return 1;
        return (svg.getBoundingClientRect().width / sc) / vb.width;
      };

      const textos = [];
      s.querySelectorAll('*').forEach((el) => {
        if (el.closest('.notas') || el.closest('defs') || el.tagName === 'DEFS') return;
        if (el.closest('[data-antipadrao]')) return;   // contraexemplo declarado
        const r = el.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return;
        const q = rel(r);
        const tag = el.tagName.toLowerCase(), cls = el.getAttribute('class') || '';
        const txt = (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 30);
        if (q.r > SL_W + 0.5 || q.b > SL_H + 0.5 || q.l < -0.5 || q.t < -0.5)
          res.fora.push({ tag, cls, txt, caixa: [rd(q.l), rd(q.t), rd(q.r), rd(q.b)] });
        if (tag === 'img' && !(el.complete && el.naturalWidth > 0)) res.imagens.push(el.getAttribute('src'));
        const proprio = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
        if (proprio) {
          const fs = parseFloat(getComputedStyle(el).fontSize) * escalaSVG(el);
          res.menorFonte = Math.min(res.menorFonte, +fs.toFixed(1));
          textos.push({ el, txt, q });
        }
      });

      /* texto sobre texto: dois blocos de texto que se cruzam sem um conter o outro */
      for (let i = 0; i < textos.length; i++) for (let j = i + 1; j < textos.length; j++) {
        const a = textos[i], b = textos[j];
        if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
        if (a.el.closest('.duas-colunas') && b.el.closest('.duas-colunas')) continue;
        const iw = Math.min(a.q.r, b.q.r) - Math.max(a.q.l, b.q.l);
        const ih = Math.min(a.q.b, b.q.b) - Math.max(a.q.t, b.q.t);
        if (iw > 2 && ih > 2) res.sobrepostos.push(`${a.txt} x ${b.txt} (${rd(iw)}x${rd(ih)})`);
      }

      /* rotulo de SVG: fora da caixa, cruzando borda de rect ou cruzando traco */
      const cruza = (x1, y1, x2, y2, T) => {
        const dentro = (x, y) => x > T.l && x < T.r && y > T.t && y < T.b;
        if (dentro(x1, y1) || dentro(x2, y2)) return true;
        const seg = (ax, ay, bx, by, cx, cy, dx, dy) => {
          const d = (bx - ax) * (dy - cy) - (by - ay) * (dx - cx); if (!d) return false;
          const u = ((cx - ax) * (dy - cy) - (cy - ay) * (dx - cx)) / d;
          const v = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / d;
          return u > 0 && u < 1 && v > 0 && v < 1;
        };
        return seg(x1, y1, x2, y2, T.l, T.t, T.r, T.t) || seg(x1, y1, x2, y2, T.r, T.t, T.r, T.b)
            || seg(x1, y1, x2, y2, T.l, T.b, T.r, T.b) || seg(x1, y1, x2, y2, T.l, T.t, T.l, T.b);
      };
      s.querySelectorAll('svg').forEach((svg) => {
        const S = rel(svg.getBoundingClientRect());
        Array.from(svg.querySelectorAll('text')).forEach((t) => {
          const q = rel(t.getBoundingClientRect());
          const txt = t.textContent.trim().slice(0, 24);
          const T = { l: q.l + 1, t: q.t + 1, r: q.r - 1, b: q.b - 1 };
          if (q.r > S.r + 0.5 || q.b > S.b + 0.5 || q.l < S.l - 0.5 || q.t < S.t - 0.5)
            res.svg.push(`fora do SVG: "${txt}"`);
          svg.querySelectorAll('rect').forEach((rc) => {
            if (rc.closest('pattern')) return;
            const q2 = rel(rc.getBoundingClientRect());
            const toca = Math.min(T.r, q2.r) > Math.max(T.l, q2.l) && Math.min(T.b, q2.b) > Math.max(T.t, q2.t);
            if (!toca) return;
            const contido = T.l >= q2.l + 1 && T.r <= q2.r - 1 && T.t >= q2.t + 1 && T.b <= q2.b - 1;
            if (!contido) res.svg.push(`"${txt}" cruza a borda de um rect`);
          });
          svg.querySelectorAll('line, polyline').forEach((ln) => {
            let pts = [];
            if (ln.tagName === 'line') pts = [[+ln.getAttribute('x1'), +ln.getAttribute('y1')], [+ln.getAttribute('x2'), +ln.getAttribute('y2')]];
            else pts = ln.getAttribute('points').trim().split(/[\s,]+/).map(Number)
                        .reduce((a, v, i, arr) => (i % 2 ? a : a.concat([[v, arr[i + 1]]])), []);
            const M = svg.getScreenCTM();
            const paraRel = (p) => { const pt = svg.createSVGPoint(); pt.x = p[0]; pt.y = p[1]; const g = pt.matrixTransform(M); return [(g.x - R.left) / sc, (g.y - R.top) / sc]; };
            const P = pts.map(paraRel);
            for (let i = 0; i + 1 < P.length; i++)
              if (cruza(P[i][0], P[i][1], P[i + 1][0], P[i + 1][1], T)) { res.svg.push(`"${txt}" cruza um ${ln.tagName}`); break; }
          });
        });
      });

      const fx = s.querySelector('.faixa');
      if (fx) { const q = rel(fx.getBoundingClientRect()); res.faixaH = rd(q.b - q.t); }
      const ct = s.querySelector('.conteudo');
      if (ct) {
        const q = rel(ct.getBoundingClientRect()); const cs = getComputedStyle(ct);
        let base = 0; ct.querySelectorAll('*').forEach((el) => { const r = el.getBoundingClientRect(); if (r.width || r.height) base = Math.max(base, rel(r).b); });
        res.sobra = rd(q.b - parseFloat(cs.paddingBottom) - base);
      }
      return res;
    }, [SL_W, SL_H, PISO_SLIDE]);

    m.n = k;
    await page.locator('.deck').screenshot({ path: `${DIR}/slide-${String(k).padStart(2, '0')}.png` });
    out.push(m);
  }

  const problema = (m) => m.fora.length + m.sobrepostos.length + m.svg.length + m.imagens.length + (m.menorFonte < PISO_SLIDE ? 1 : 0);
  const total = out.reduce((a, m) => a + problema(m), 0);
  return out.map((m) => `${String(m.n).padStart(2, '0')} ${m.titulo.padEnd(40)} faixa=${m.faixaH} sobra=${m.sobra} menorFonte=${m.menorFonte}`
    + (m.fora.length ? `\n   FORA DO SLIDE: ${JSON.stringify(m.fora)}` : '')
    + (m.sobrepostos.length ? `\n   TEXTO SOBRE TEXTO: ${m.sobrepostos.join(' | ')}` : '')
    + (m.svg.length ? `\n   SVG: ${m.svg.join(' | ')}` : '')
    + (m.imagens.length ? `\n   IMAGEM: ${m.imagens.join(', ')}` : '')
    + (m.menorFonte < PISO_SLIDE ? `\n   FONTE abaixo de ${PISO_SLIDE}px: ${m.menorFonte}px` : '')
  ).join('\n') + `\n\n${N} slides, ${total} achados.`;
}
