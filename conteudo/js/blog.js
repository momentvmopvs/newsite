/* Página do blog: filtro por assunto e "mostrar mais artigos".
   O assunto escolhido vai no endereço (ex.: /blog.html#fachadas), então o link pode ser
   compartilhado. Sem JavaScript, a lista aparece inteira. */
(function () {
  var POR_VEZ = 12;
  var filtros = document.querySelector(".blog-filtros");
  var mais = document.getElementById("blog-mais");
  if (!filtros || !mais) return;

  var botoes = Array.prototype.slice.call(filtros.querySelectorAll(".blog-filtro"));
  var cartoes = Array.prototype.slice.call(document.querySelectorAll(".blog-lista .blog-recente-card"));
  var assunto = "";
  var limite = POR_VEZ;

  function mostrar() {
    var achados = cartoes.filter(function (c) {
      return !assunto || c.dataset.assunto === assunto;
    });
    cartoes.forEach(function (c) {
      var n = achados.indexOf(c);
      c.hidden = n < 0 || n >= limite;
    });
    botoes.forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.assunto === assunto));
    });
    mais.hidden = achados.length <= limite;
  }

  function lerEndereco() {
    var pedido = decodeURIComponent(location.hash.slice(1));
    var existe = botoes.some(function (b) { return b.dataset.assunto === pedido; });
    assunto = existe ? pedido : "";
    limite = POR_VEZ;
    mostrar();
  }

  filtros.addEventListener("click", function (ev) {
    var b = ev.target.closest(".blog-filtro");
    if (!b) return;
    assunto = b.dataset.assunto;
    limite = POR_VEZ;
    history.replaceState(null, "", assunto ? "#" + assunto : location.pathname + location.search);
    mostrar();
  });

  mais.querySelector("button").addEventListener("click", function () {
    var primeiroNovo = limite;
    limite += POR_VEZ;
    mostrar();
    var visiveis = cartoes.filter(function (c) { return !c.hidden; });
    var link = visiveis[primeiroNovo] && visiveis[primeiroNovo].querySelector("h2 a");
    if (link) link.focus({ preventScroll: true });
  });

  window.addEventListener("hashchange", lerEndereco);
  filtros.hidden = false;
  lerEndereco();
})();
