/* ============================================================
   8020-DS 4.0, assets/pagina.js
   O mínimo de uma página do catálogo ou de uma peça longa que não é
   book: o item atual do topo acompanha a seção visível (peso como
   estado), os botões .copiar copiam o código do alvo, as abas movem o
   trilho, o toast desce e sobe. Vanilla, zero dependência.
   ============================================================ */
(function () {
  "use strict";
  /* item atual do topo conforme a seção visível */
  var links = document.querySelectorAll(".topo nav .peso[href^='#']");
  if ("IntersectionObserver" in window && links.length) {
    var mapa = {}; links.forEach(function (a) { mapa[a.getAttribute("href").slice(1)] = a; });
    var obs = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { links.forEach(function (a) { a.removeAttribute("aria-current"); }); var a = mapa[en.target.id]; if (a) a.setAttribute("aria-current", "true"); } }); }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(mapa).forEach(function (id) { var s = document.getElementById(id); if (s) obs.observe(s); });
  }
  /* copiar código */
  document.querySelectorAll(".copiar[data-alvo]").forEach(function (b) {
    b.addEventListener("click", function () {
      var c = document.getElementById(b.getAttribute("data-alvo")); if (!c) return;
      var texto = c.textContent, ok = function () { b.textContent = "Copiado"; setTimeout(function () { b.textContent = "Copiar"; }, 1600); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(texto).then(ok, ok); else ok();
    });
  });
  /* abas: o trilho que se move */
  document.querySelectorAll(".abas").forEach(function (abas) {
    var trilho = abas.querySelector(".trilho"); if (!trilho) return;
    function mover(aba) { if (!aba) return; trilho.style.transform = "translateX(" + aba.offsetLeft + "px) scaleX(" + aba.offsetWidth + ")"; }
    var atual = abas.querySelector('[aria-selected="true"]');
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { mover(atual); }); else mover(atual);
    abas.addEventListener("click", function (e) {
      var aba = e.target.closest('[role="tab"]'); if (!aba) return;
      abas.querySelectorAll('[role="tab"]').forEach(function (x) { var sim = x === aba; x.setAttribute("aria-selected", sim ? "true" : "false"); if (sim) x.setAttribute("aria-current", "true"); else x.removeAttribute("aria-current"); });
      mover(aba);
      var painel = abas.parentNode.querySelector(".painel-aba"); if (painel && aba.hasAttribute("data-painel")) painel.innerHTML = aba.getAttribute("data-painel");
    });
    window.addEventListener("resize", function () { mover(abas.querySelector('[aria-selected="true"]')); });
  });
  /* toast: uma linha que desce, fica quatro segundos e sobe */
  var toast = document.querySelector(".toast"), timer;
  window.toast8020 = function (html, atencao) {
    if (!toast) return; clearTimeout(timer);
    var t = toast.querySelector("[data-texto]") || toast.firstElementChild; toast.classList.toggle("atencao", !!atencao); t.innerHTML = html; toast.classList.add("visivel");
    timer = setTimeout(function () { toast.classList.remove("visivel"); }, 4000);
  };
  if (toast) { var f = toast.querySelector("[data-fechar]"); if (f) f.addEventListener("click", function () { clearTimeout(timer); toast.classList.remove("visivel"); }); }
})();
