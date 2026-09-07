/* ============================================================
   8020-DS 4.0, assets/dado.js
   A interação de dado do sistema, sem tooltip: a leitura em palavras
   (o ponteiro ou o foco sobre uma marca reescreve a .leitura da
   figura), a rede que acende as arestas do nó em foco, a transição
   entre estados (o mesmo rect muda de largura, controlada por um
   .segmentos[data-alvo] ou pelos passos de um .scrolly[data-alvo]),
   a mira da linha do tempo e o desenho da linha ao entrar na tela.
   Nada aqui cria dado: o valor final está no HTML e imprime sem JS.
   ============================================================ */
(function () {
  "use strict";
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- a hachura da impressão: o laranja do dado vira tinta sobre laranja no papel ----
     O padrão precisa existir na página para o fill url(#hachura-laranja) do @media print resolver. */
  if (!document.getElementById("hachura-laranja")) {
    document.body.insertAdjacentHTML("afterbegin", '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><pattern id="hachura-laranja" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)"><rect width="6" height="6" fill="#fa4616"/><line x1="0" y1="0" x2="0" y2="6" stroke="#1a140f" stroke-width="1.2"/></pattern></defs></svg>');
  }
  /* ---- na impressão o livro-razão imprime aberto: a tabela é a única leitura que sobrevive ao papel ---- */
  var abertos = [];
  window.addEventListener("beforeprint", function () { abertos = []; document.querySelectorAll("details.razao:not([open])").forEach(function (d) { d.open = true; abertos.push(d); }); });
  window.addEventListener("afterprint", function () { abertos.forEach(function (d) { d.open = false; }); abertos = []; });

  /* ---- leitura em palavras ---- */
  document.querySelectorAll(".grafico [data-leitura], .figura [data-leitura]").forEach(function (m) {
    var fig = m.closest(".figura"); if (!fig) return;
    var alvo = fig.querySelector(".leitura"); if (!alvo) return;
    if (!alvo.hasAttribute("data-padrao")) alvo.setAttribute("data-padrao", alvo.innerHTML);
    function mostrar() { alvo.innerHTML = m.getAttribute("data-leitura"); }
    function voltar() { alvo.innerHTML = alvo.getAttribute("data-padrao"); }
    m.addEventListener("pointerenter", mostrar); m.addEventListener("pointerleave", voltar);
    m.addEventListener("focus", mostrar); m.addEventListener("blur", voltar);
  });

  /* ---- linha do tempo: a mira assenta no ano mais próximo ---- */
  document.querySelectorAll(".grafico svg[data-mira]").forEach(function (svg) {
    var mira = svg.querySelector(".mira"), alvos = svg.querySelectorAll("[data-x]"); if (!mira || !alvos.length) return;
    var fig = svg.closest(".figura"), leitura = fig && fig.querySelector(".leitura");
    svg.addEventListener("pointermove", function (e) {
      var pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; var p = pt.matrixTransform(svg.getScreenCTM().inverse());
      var melhor = null, d = 1e9; alvos.forEach(function (a) { var dx = Math.abs(+a.getAttribute("data-x") - p.x); if (dx < d) { d = dx; melhor = a; } });
      if (!melhor) return; mira.setAttribute("x1", melhor.getAttribute("data-x")); mira.setAttribute("x2", melhor.getAttribute("data-x")); mira.classList.add("on");
      if (leitura && melhor.hasAttribute("data-leitura")) { if (!leitura.hasAttribute("data-padrao")) leitura.setAttribute("data-padrao", leitura.innerHTML); leitura.innerHTML = melhor.getAttribute("data-leitura"); }
    });
    svg.addEventListener("pointerleave", function () { mira.classList.remove("on"); if (leitura && leitura.hasAttribute("data-padrao")) leitura.innerHTML = leitura.getAttribute("data-padrao"); });
  });

  /* ---- rede: o nó aceso acende as arestas dele ---- */
  document.querySelectorAll(".grafico .no").forEach(function (n) {
    var svg = n.closest("svg"), de = n.getAttribute("data-no"), pub = n.getAttribute("data-pub");
    function liga(sim) { svg.querySelectorAll(".aresta").forEach(function (a) { var bate = de ? a.getAttribute("data-de") === de : a.getAttribute("data-para") === pub; a.classList.toggle("on", sim && bate); }); }
    n.addEventListener("pointerenter", function () { liga(true); }); n.addEventListener("pointerleave", function () { liga(false); });
    n.addEventListener("focus", function () { liga(true); }); n.addEventListener("blur", function () { liga(false); });
  });

  /* ---- transição entre estados: a mesma marca muda de lugar ----
     rect.move e text.move trazem data-a e data-b (largura ou x nos dois
     estados) e text.move traz data-va e data-vb (o valor escrito). */
  function estado(svg, qual) {
    if (!svg) return; svg.setAttribute("data-estado", qual);
    /* o segundo estado é "b", ou o valor declarado em data-estado-b do svg (por exemplo "2026") */
    var b = qual === "b" || qual === (svg.getAttribute("data-estado-b") || "2026");
    var chave = b ? "data-b" : "data-a", vchave = b ? "data-vb" : "data-va";
    svg.querySelectorAll("rect.move").forEach(function (r) { r.style.width = r.getAttribute(chave) + "px"; });
    svg.querySelectorAll("text.move").forEach(function (t) { t.style.x = t.getAttribute(chave) + "px"; t.textContent = t.getAttribute(vchave); });
  }
  window.dado8020 = { estado: estado };
  document.querySelectorAll(".segmentos[data-alvo]").forEach(function (seg) {
    var svg = document.getElementById(seg.getAttribute("data-alvo"));
    seg.querySelectorAll("button").forEach(function (b) { b.addEventListener("click", function () { seg.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); }); estado(svg, b.getAttribute("data-estado")); }); });
  });
  document.querySelectorAll(".scrolly[data-alvo]").forEach(function (sc) {
    var svg = document.getElementById(sc.getAttribute("data-alvo")), passos = sc.querySelectorAll(".passo-m, .passos li"), leitura = sc.querySelector(".leitura");
    function aplicar(p) { if (p.hasAttribute("data-estado")) estado(svg, p.getAttribute("data-estado")); if (leitura && p.hasAttribute("data-leitura")) leitura.innerHTML = p.getAttribute("data-leitura"); passos.forEach(function (x) { x.classList.toggle("atual", x === p); x.classList.toggle("ativo", x === p); }); }
    sc.addEventListener("passo", function (e) { aplicar(e.detail.passo); });
    if (!sc.ativarPasso && "IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) aplicar(en.target); }); }, { rootMargin: "-45% 0px -45% 0px" });
      passos.forEach(function (p) { obs.observe(p); });
    }
  });

  /* ---- desenho da linha ao entrar na tela, uma vez ---- */
  var linhas = document.querySelectorAll("svg[data-desenha]");
  if (linhas.length && "IntersectionObserver" in window && !reduz) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("desenha"); io.unobserve(e.target); } }); }, { threshold: .3 });
    linhas.forEach(function (s) { io.observe(s); });
  }
})();
