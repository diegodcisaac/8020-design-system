/* ============================================================
   8020-DS 4.0, assets/deck.js
   O visualizador de deck (regra 8f): monta a moldura em chumbo com
   todo controle fora do slide, escreve o contador e o trilho de cada
   faixa (o autor não numera slide à mão), abre as miniaturas na tecla
   o, a tela cheia em f, a lista de atalhos em ?, a visão do
   apresentador em p (janela própria, sincronizada por BroadcastChannel),
   guarda o slide no endereço (#12) e prepara a impressão.
   Nenhum conteúdo nasce aqui. Sem JavaScript os slides empilham.
   O deck é o elemento .deck, com os slides como filhos diretos:
     <div class="deck" data-marca="Cliente" data-peca="Nome da peça, mês de 2026">
   Atributos opcionais: data-canal (nome do canal de sincronização),
   data-logo (caminho da logo branca; o padrão é assets/logos/).
   ============================================================ */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var deck = document.querySelector(".deck"); if (!deck) return;
  var slides = Array.prototype.slice.call(deck.querySelectorAll(":scope > .slide")); var N = slides.length; if (!N) return;
  var params = new URLSearchParams(location.search);
  var apresentador = params.has("apresentador");
  var reduz = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var script = document.currentScript; var base = script && script.src ? script.src.replace(/deck\.js(\?.*)?$/, "") : "";
  var logo = deck.getAttribute("data-logo") || (base + "logos/logo-8020-branco.svg");
  var marca = deck.getAttribute("data-marca") || "";
  var peca = deck.getAttribute("data-peca") || document.title;
  var canalNome = deck.getAttribute("data-canal") || ("deck-8020-" + location.pathname.replace(/[^a-z0-9]+/gi, "-"));
  var i = 0;

  function dois(n) { return String(n).padStart(2, "0"); }
  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html !== undefined) e.innerHTML = html; return e; }

  /* ---- 1. o cromo de cada slide: contador, trilho e a cascata, escritos pelo sistema ---- */
  slides.forEach(function (s, k) {
    var n = k + 1, topo = s.classList.contains("s-topo");
    var fx = s.querySelector(":scope > .faixa");
    if (fx) {
      var pe = fx.querySelector(".pe"); if (!pe) { pe = el("div", "pe"); fx.appendChild(pe); }
      var ct = pe.querySelector(".contador"); if (!ct) { ct = el("div", "contador"); pe.insertBefore(ct, pe.firstChild); }
      var b = ct.querySelector("b");
      if (topo) {
        var sp = ct.querySelector("span:not(.quando)"); if (!sp) { sp = el("span"); ct.appendChild(sp); }
        sp.textContent = dois(n) + " de " + N;
      } else if (b) {
        b.textContent = dois(n); var s2 = b.nextElementSibling; if (!s2) { s2 = el("span"); ct.appendChild(s2); } s2.textContent = "de " + N;
      } else {
        var alvo = ct.querySelector("span:not(.quando)"); if (!alvo) { alvo = el("span"); ct.appendChild(alvo); }
        alvo.textContent = dois(n) + " de " + N;
      }
      var tr = pe.querySelector(".trilho"); if (!tr) { tr = el("div", "trilho"); tr.appendChild(el("span")); pe.appendChild(tr); }
      var trs = tr.querySelector("span"); if (!trs) { trs = el("span"); tr.appendChild(trs); } trs.style.width = (n / N * 100) + "%";
    }
    var cromo = s.querySelector(":scope > .cromo");
    if (cromo) {
      var v = cromo.querySelector(".vertical"); if (!v) { v = el("div", "vertical", "<span></span>"); v.setAttribute("aria-hidden", "true"); cromo.appendChild(v); }
      var vs = v.querySelector("span"); if (!vs) { vs = el("span"); v.appendChild(vs); } vs.style.height = (n / N * 100) + "%";
      var cc = cromo.querySelector(".contador"); if (!cc) { cc = el("div", "contador"); cromo.appendChild(cc); }
      cc.innerHTML = "<b>" + dois(n) + "</b>de " + N;
    }
    if (s.classList.contains("s-cheio")) {
      var rd = s.querySelector(".rodape-slide");
      if (!rd) { rd = el("div", "rodape-slide", "<span></span>"); var alvoRd = s.querySelector(".sobre") || s; alvoRd.appendChild(rd); }
      var tab = rd.querySelector(".tab"); if (!tab) { tab = el("span", "tab"); rd.appendChild(tab); }
      tab.textContent = dois(n) + " de " + N;
    }
    var blocos = s.querySelectorAll(":scope > .conteudo > *"); blocos.forEach(function (x, j) { x.style.setProperty("--i", j); });
    if (s.classList.contains("s-cheio")) { var raiz = s.querySelector(".sobre") || s; Array.prototype.forEach.call(raiz.children, function (x, j) { x.style.setProperty("--i", j); }); }
    s.querySelectorAll("svg.cresce-y rect, svg.cresce-x rect").forEach(function (r, j) { r.style.setProperty("--j", j); });
    s.querySelectorAll(".fase").forEach(function (f, j) { f.style.setProperty("--i", j); });
  });

  function capituloDe(s) {
    var c = s.querySelector(".faixa .cap"); if (c) return c.textContent.replace(/\s+/g, " ").trim();
    var q = s.querySelector(".cromo .capitulo"); if (q) return q.childNodes[0].textContent.trim();
    var r = s.querySelector(".rodape-slide span"); if (r) { var t = r.textContent.replace(/\s+/g, " ").trim(); if (t) return t; }
    /* sem rótulo escrito: a capa é o primeiro slide, a contracapa é o último */
    var k = slides.indexOf(s); return k === 0 ? "Capa" : k === N - 1 ? "Contracapa" : "";
  }
  function tituloDe(s) {
    var h = s.querySelector("h2"); if (h) return h.textContent.trim();
    var st = s.querySelector(".statement, .citacao"); if (st) return st.textContent.trim().slice(0, 60);
    return "";
  }

  /* ---- 2. a moldura, as miniaturas, os atalhos e a mesa do apresentador ---- */
  var hachura = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs><pattern id="hachura-laranja" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)"><rect width="6" height="6" fill="#fa4616"/><line x1="0" y1="0" x2="0" y2="6" stroke="#1a140f" stroke-width="1.2"/></pattern></defs></svg>';
  if (!document.getElementById("hachura-laranja")) document.body.insertAdjacentHTML("afterbegin", hachura);
  var marcaHtml = '<div class="marca"><img src="' + logo + '" alt="80 20"><span>' + marca + "</span></div>";
  var moldura = el("div", "moldura"); moldura.id = "moldura";
  moldura.innerHTML =
    '<div class="cromo-topo">' + marcaHtml + '<span class="peca">' + peca + '</span><span class="capitulo" id="cap-atual"></span></div>' +
    '<div class="palco-vivo" id="palco-vivo"></div>' +
    '<div class="cromo-base"><span class="contador" id="contador"></span>' +
    '<div class="teclas"><button class="tecla" type="button" id="b-mini" title="Miniaturas">o</button><button class="tecla" type="button" id="b-cheia" title="Tela cheia">f</button><button class="tecla" type="button" id="b-apres" title="Visão do apresentador">p</button><button class="tecla" type="button" id="b-atalhos" title="Atalhos">?</button></div>' +
    '<div class="setas"><button class="seta" type="button" id="b-ant">Anterior</button><button class="seta" type="button" id="b-prox">Próximo</button></div>' +
    '<div class="progresso-deck"><span id="progresso"></span></div></div>';
  deck.parentNode.insertBefore(moldura, deck);
  moldura.querySelector("#palco-vivo").appendChild(deck);

  var minis = el("div", "miniaturas"); minis.id = "miniaturas"; minis.hidden = true;
  minis.innerHTML = '<div class="folha-m"><div class="grade" id="grade-mini"></div><aside class="margem-m"><span class="n">' + N + ' slides</span><p>Clique num slide para ir até ele. A tecla <kbd class="tecla">o</kbd> fecha.</p><ol id="mini-capitulos"></ol><button class="seta fechar" type="button" id="b-mini-fechar">Fechar</button></aside></div>';
  document.body.appendChild(minis);

  var atalhos = el("div", "atalhos"); atalhos.id = "atalhos"; atalhos.hidden = true; atalhos.setAttribute("role", "dialog"); atalhos.setAttribute("aria-modal", "true"); atalhos.setAttribute("aria-label", "Atalhos de teclado");
  atalhos.innerHTML = '<div class="caixa"><h2>Atalhos</h2><dl>' +
    "<dt><kbd>→</kbd><kbd>↓</kbd><kbd>espaço</kbd></dt><dd>Próximo slide</dd><dt><kbd>←</kbd><kbd>↑</kbd></dt><dd>Slide anterior</dd>" +
    "<dt><kbd>Home</kbd><kbd>End</kbd></dt><dd>Primeiro e último</dd><dt><kbd>o</kbd></dt><dd>Miniaturas de todos os slides</dd>" +
    "<dt><kbd>f</kbd></dt><dd>Tela cheia</dd><dt><kbd>p</kbd></dt><dd>Visão do apresentador, em janela própria e sincronizada</dd>" +
    "<dt><kbd>t</kbd></dt><dd>Zerar o tempo, na visão do apresentador</dd><dt><kbd>?</kbd></dt><dd>Abrir e fechar esta lista</dd><dt><kbd>Esc</kbd></dt><dd>Fechar</dd>" +
    '</dl><button class="filete" type="button" id="b-atalhos-fechar">Fechar</button></div>';
  document.body.appendChild(atalhos);

  var mesa = el("div", "mesa"); mesa.id = "mesa"; mesa.hidden = true;
  mesa.innerHTML = '<div class="cromo-topo">' + marcaHtml + '<span class="peca">Visão do apresentador</span><span class="capitulo" id="cap-atual-a"></span></div>' +
    '<div class="atual-a"><div class="palco-a" id="palco-a"></div><div class="notas-a" id="notas-a"><b>Notas</b><span id="notas-texto"></span></div></div>' +
    '<div class="lado-a"><div class="tempo" id="tempo">00:00<small>tempo decorrido, <kbd class="tecla" style="font-size:11px">t</kbd> zera</small></div>' +
    '<div class="contador-a" id="contador-a"></div><div class="proximo-a"><span>Próximo</span><div class="quadro" id="proximo-a"></div><span id="proximo-titulo"></span></div>' +
    '<div class="setas"><button class="seta" type="button" id="a-ant">Anterior</button><button class="seta" type="button" id="a-prox">Próximo</button></div>' +
    '<div class="margem-a">A janela do deck e esta ficam no mesmo slide. Avance daqui ou de lá.</div></div>';
  document.body.appendChild(mesa);

  /* ---- 3. escala do palco ---- */
  var palco = document.getElementById("palco-vivo");
  function escalar() { if (apresentador) return; var w = palco.clientWidth - 48, h = palco.clientHeight - 24; deck.style.setProperty("--escala", Math.min(w / 1280, h / 720)); }
  window.addEventListener("resize", escalar);

  /* ---- 4. navegação, com o canal entre as janelas ---- */
  var canal = null; try { canal = new BroadcastChannel(canalNome); } catch (e) {}
  function ir(n, emitir) {
    n = Math.max(0, Math.min(N - 1, n)); i = n;
    slides.forEach(function (s, k) { s.classList.toggle("atual", k === i); if (k !== i) s.classList.remove("entra"); });
    if (!reduz && !apresentador) { slides[i].classList.remove("entra"); void slides[i].offsetWidth; slides[i].classList.add("entra"); }
    document.getElementById("contador").innerHTML = dois(i + 1) + " <small>de " + N + "</small>";
    document.getElementById("cap-atual").innerHTML = (capituloDe(slides[i]) || "Capa") + "<small>" + tituloDe(slides[i]) + "</small>";
    document.getElementById("progresso").style.transform = "scaleX(" + ((i + 1) / N) + ")";
    document.getElementById("b-ant").disabled = i === 0; document.getElementById("b-prox").disabled = i === N - 1;
    history.replaceState(null, "", "#" + (i + 1));
    if (apresentador) atualizarMesa();
    if (emitir !== false && canal) canal.postMessage({ i: i });
    document.querySelectorAll(".mini").forEach(function (m, k) { m.classList.toggle("atual", k === i); });
  }
  if (canal) canal.onmessage = function (e) { if (e.data && typeof e.data.i === "number" && e.data.i !== i) ir(e.data.i, false); };

  /* ---- 5. miniaturas ---- */
  var grade = document.getElementById("grade-mini");
  function montarMinis() {
    if (grade.children.length) return;
    slides.forEach(function (s, k) {
      var b = el("button", "mini" + (k === i ? " atual" : "")); b.type = "button";
      var q = el("div", "quadro"); var c = s.cloneNode(true); c.classList.remove("atual", "entra"); c.removeAttribute("id"); q.appendChild(c);
      var t = el("span", "", '<span class="n">' + dois(k + 1) + "</span>" + tituloDe(s));
      b.appendChild(q); b.appendChild(t); b.addEventListener("click", function () { ir(k); alternarMinis(false); });
      grade.appendChild(b);
    });
    var caps = {}, lista = document.getElementById("mini-capitulos");
    slides.forEach(function (s, k) { var c = capituloDe(s).split(" ").slice(0, 2).join(" "); if (!/^(Capítulo \d+|Sumário|Fechamento)$/.test(c)) return; if (c && !caps[c]) { caps[c] = k + 1; var li = el("li", "", "<b>" + dois(k + 1) + "</b><span>" + c + "</span>"); lista.appendChild(li); } });
    escalarMinis();
  }
  function escalarMinis() { grade.querySelectorAll(".quadro").forEach(function (q) { var s = q.firstElementChild; s.style.transform = "scale(" + (q.clientWidth / 1280) + ")"; }); }
  window.addEventListener("resize", escalarMinis);
  function alternarMinis(sim) { if (sim === undefined) sim = minis.hidden; minis.hidden = !sim; if (sim) { montarMinis(); escalarMinis(); var a = grade.querySelector(".mini.atual"); if (a) a.focus(); } }

  /* ---- 6. atalhos, tela cheia ---- */
  function alternarAtalhos(sim) { if (sim === undefined) sim = atalhos.hidden; atalhos.hidden = !sim; if (sim) document.getElementById("b-atalhos-fechar").focus(); }
  function telaCheia() { var d = document.documentElement; if (!document.fullscreenElement) { if (d.requestFullscreen) d.requestFullscreen(); } else if (document.exitFullscreen) document.exitFullscreen(); }

  /* ---- 7. visão do apresentador ---- */
  var t0 = Date.now(), tempoEl = document.getElementById("tempo");
  function abrirApresentador() { window.open(location.pathname + "?apresentador=1#" + (i + 1), "apresentador-8020", "width=1280,height=800"); }
  function clonar(k, alvo, prop) {
    alvo.innerHTML = ""; var c = slides[k].cloneNode(true); c.classList.add("atual"); c.classList.remove("entra"); c.removeAttribute("id");
    var d = el("div", "deck"); d.appendChild(c); alvo.appendChild(d); d.style.setProperty(prop, alvo.clientWidth / 1280);
  }
  function atualizarMesa() {
    clonar(i, document.getElementById("palco-a"), "--escala-a");
    var pp = document.getElementById("proximo-a");
    if (i + 1 < N) { clonar(i + 1, pp, "--escala-p"); document.getElementById("proximo-titulo").textContent = dois(i + 2) + " " + tituloDe(slides[i + 1]); }
    else { pp.innerHTML = ""; document.getElementById("proximo-titulo").textContent = "Fim do deck"; }
    var notas = slides[i].querySelector(".notas"); document.getElementById("notas-texto").textContent = notas ? notas.textContent.trim() : "Sem notas para este slide.";
    document.getElementById("contador-a").innerHTML = dois(i + 1) + " <small>de " + N + "</small>";
    document.getElementById("cap-atual-a").textContent = capituloDe(slides[i]) || "Capa";
  }
  function relogio() { var s = Math.floor((Date.now() - t0) / 1000); tempoEl.firstChild.textContent = dois(Math.floor(s / 60)) + ":" + dois(s % 60); }

  /* ---- 8. teclado e botões ---- */
  document.addEventListener("keydown", function (e) {
    if (e.target.matches("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;
    if (k === "?") { e.preventDefault(); alternarAtalhos(); return; }
    if (k === "Escape") { alternarAtalhos(false); alternarMinis(false); return; }
    if (!atalhos.hidden) return;
    if (k === "ArrowRight" || k === "ArrowDown" || k === "PageDown" || k === " ") { e.preventDefault(); ir(i + 1); }
    else if (k === "ArrowLeft" || k === "ArrowUp" || k === "PageUp") { e.preventDefault(); ir(i - 1); }
    else if (k === "Home") { ir(0); } else if (k === "End") { ir(N - 1); }
    else if (k === "o" || k === "O") { alternarMinis(); }
    else if (k === "f" || k === "F") { telaCheia(); }
    else if ((k === "p" || k === "P") && !apresentador) { abrirApresentador(); }
    else if ((k === "t" || k === "T") && apresentador) { t0 = Date.now(); relogio(); }
  });
  var liga = function (id, fn) { var b = document.getElementById(id); if (b) b.addEventListener("click", fn); };
  liga("b-ant", function () { ir(i - 1); }); liga("b-prox", function () { ir(i + 1); });
  liga("b-mini", function () { alternarMinis(); }); liga("b-mini-fechar", function () { alternarMinis(false); });
  liga("b-cheia", telaCheia); liga("b-apres", abrirApresentador);
  liga("b-atalhos", function () { alternarAtalhos(); }); liga("b-atalhos-fechar", function () { alternarAtalhos(false); });
  liga("a-ant", function () { ir(i - 1); }); liga("a-prox", function () { ir(i + 1); });

  /* ---- 9. modo, endereço e impressão ---- */
  var inicial = parseInt((location.hash || "#1").slice(1), 10); if (isNaN(inicial)) inicial = 1;
  if (apresentador) {
    document.body.classList.add("apresentador"); moldura.hidden = true; mesa.hidden = false;
    setInterval(relogio, 1000); ir(inicial - 1, false); window.addEventListener("resize", atualizarMesa);
  } else {
    document.body.classList.add("visor"); escalar(); ir(inicial - 1, false);
  }
  window.addEventListener("hashchange", function () { var n = parseInt(location.hash.slice(1), 10); if (!isNaN(n) && n - 1 !== i) ir(n - 1); });
  window.addEventListener("beforeprint", function () { slides.forEach(function (s) { s.classList.add("atual"); s.classList.remove("entra"); }); });
  window.addEventListener("afterprint", function () { slides.forEach(function (s, k) { s.classList.toggle("atual", k === i); }); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(escalar);
})();
