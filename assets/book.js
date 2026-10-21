/* ============================================================
   8020-DS 4.1, assets/book.js
   A margem viva do book: progresso de leitura, trilha com o capítulo
   visível, notas de rodapé alinhadas ao parágrafo que as chama,
   scrollytelling dirigido pela margem (o passo do meio da tela troca o
   estado da figura e a leitura em palavras), reveal só em figura,
   atalhos (j, k, h, ?). Nada fica guardado no navegador: a peça não
   lembra onde o leitor parou (regra 22a).
   Nenhum conteúdo nasce aqui. Vanilla, zero dependência.
   Capítulos são [data-titulo]; o hub é #hub; as partes declaram
   data-hub no body para a tecla h.
   ============================================================ */
(function () {
  "use strict";
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- progresso de leitura ---- */
  var barra = document.getElementById("progresso") || document.querySelector(".progresso-leitura");
  function progresso() { if (!barra) return; var h = document.documentElement; var max = h.scrollHeight - h.clientHeight; var p = max > 0 ? h.scrollTop / max : 0; barra.style.width = (Math.max(0, Math.min(1, p)) * 100) + "%"; }
  window.addEventListener("scroll", progresso, { passive: true }); progresso();

  var hubHref = document.body.getAttribute("data-hub") || "";

  /* ---- trilha: o capítulo visível no topo ---- */
  var caps = document.querySelectorAll("[data-titulo]"), trilha = document.getElementById("trilha-atual");
  var atualId = null;
  if ("IntersectionObserver" in window && caps.length) {
    var obs = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { atualId = e.target.id; if (trilha) trilha.textContent = e.target.getAttribute("data-titulo"); } }); }, { rootMargin: "-30% 0px -60% 0px" });
    caps.forEach(function (c) { obs.observe(c); });
    var hub = document.getElementById("hub");
    if (hub) { var hubObs = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { if (trilha) trilha.textContent = "Início"; atualId = null; } }); }, { rootMargin: "-30% 0px -60% 0px" }); hubObs.observe(hub); }
  }

  /* ---- notas na margem, alinhadas ao parágrafo que as chama ---- */
  function posicionar() {
    document.querySelectorAll(".folha.com-notas").forEach(function (folha) {
      var margem = folha.querySelector(":scope > .margem"); if (!margem) return; var notas = margem.querySelectorAll(".nota-m");
      if (window.innerWidth < 900) { notas.forEach(function (n) { n.classList.remove("posta"); n.style.top = ""; }); margem.style.minHeight = ""; return; }
      var base = folha.getBoundingClientRect().top, ultimo = -1e9, fim = 0;
      notas.forEach(function (n) {
        var ref = document.getElementById(n.getAttribute("data-ref")); if (!ref) return;
        var alvo = ref.getBoundingClientRect().top - base; var top = Math.max(alvo, ultimo + 16);
        n.classList.add("posta"); n.style.top = top + "px"; ultimo = top + n.offsetHeight; fim = Math.max(fim, ultimo);
      });
      margem.style.minHeight = fim + "px";
    });
  }
  window.addEventListener("resize", posicionar);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(posicionar); else posicionar();
  document.querySelectorAll("img").forEach(function (im) { im.addEventListener("load", posicionar); });
  setTimeout(posicionar, 600);

  /* ---- scrollytelling na margem: o passo ativo dirige a figura ----
     Cada .passo-m pode trazer data-estado (vai para o data-estado do .fixo,
     para o CSS da página reagir), data-leitura (HTML para a .leitura) e
     data-alvo no .scrolly (id de um svg com rect.move, tratado pelo dado.js).
     A página também recebe um evento "passo" com {indice, passo, scrolly}. */
  document.querySelectorAll(".scrolly").forEach(function (sc) {
    var passos = sc.querySelectorAll(".passo-m"), fixo = sc.querySelector(".fixo"), leitura = sc.querySelector(".leitura"); if (!passos.length) return;
    var ativo = -1;
    function ativar(k) {
      if (k === ativo) return; ativo = k; var p = passos[k];
      passos.forEach(function (x, j) { x.classList.toggle("ativo", j === k); });
      if (fixo && p.hasAttribute("data-estado")) fixo.setAttribute("data-estado", p.getAttribute("data-estado"));
      if (leitura && p.hasAttribute("data-leitura")) leitura.innerHTML = p.getAttribute("data-leitura");
      sc.dispatchEvent(new CustomEvent("passo", { detail: { indice: k, passo: p, scrolly: sc } }));
    }
    sc.ativarPasso = ativar;
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) ativar(Array.prototype.indexOf.call(passos, e.target)); }); }, { rootMargin: "-45% 0px -45% 0px" });
      passos.forEach(function (p) { io.observe(p); });
    }
    if (window.innerWidth < 900) { var fim = sc.hasAttribute("data-estado-estreito") ? parseInt(sc.getAttribute("data-estado-estreito"), 10) : passos.length - 1; ativar(fim); passos.forEach(function (p) { p.classList.add("ativo"); }); }
    if (ativo < 0) ativar(0);
  });

  /* ---- reveal só em figura, gráfico e diagrama ---- */
  var revs = document.querySelectorAll(".reveal");
  if (revs.length && "IntersectionObserver" in window && !reduz) {
    var ro = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-visible"); ro.unobserve(e.target); } }); }, { threshold: .15 });
    revs.forEach(function (r) { ro.observe(r); });
  } else revs.forEach(function (r) { r.classList.add("is-visible"); });

  /* ---- atalhos: j e k trocam de capítulo, h volta ao hub, ? abre a lista ---- */
  var dlg = document.getElementById("atalhos");
  function alternar(sim) { if (!dlg) return; dlg.hidden = sim === undefined ? !dlg.hidden : !sim; if (!dlg.hidden) { var f = document.getElementById("fechar-atalhos"); if (f) f.focus(); } }
  var ab = document.getElementById("abrir-atalhos"), fe = document.getElementById("fechar-atalhos");
  if (ab) ab.addEventListener("click", function () { alternar(true); });
  if (fe) fe.addEventListener("click", function () { alternar(false); });
  if (dlg) dlg.addEventListener("click", function (e) { if (e.target === dlg) alternar(false); });
  var ordem = ["hub"].concat(Array.prototype.map.call(caps, function (c) { return c.id; })).filter(function (id) { return document.getElementById(id); });
  document.addEventListener("keydown", function (e) {
    if (e.target.matches("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "?") { e.preventDefault(); alternar(); return; }
    if (e.key === "Escape") { alternar(false); return; }
    if (dlg && !dlg.hidden) return;
    if (e.key === "h") { if (document.getElementById("hub")) location.hash = "#hub"; else location.href = hubHref || "#hub"; return; }
    if (e.key === "j" || e.key === "k") {
      var at = ordem.indexOf(atualId || ordem[0]); var n = e.key === "j" ? Math.min(ordem.length - 1, at + 1) : Math.max(0, at - 1);
      var alvo = document.getElementById(ordem[n]); if (alvo) alvo.scrollIntoView({ behavior: reduz ? "auto" : "smooth" });
    }
  });
})();
