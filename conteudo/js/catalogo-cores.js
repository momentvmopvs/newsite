// Páginas de cores dos catálogos: filtro por tom, ampliação com
// navegação entre cores, link direto para cada cor (#codigo) e
// botão de orçamento com a cor já preenchida.
(function () {
  const cards = Array.from(document.querySelectorAll(".cor-card"));
  const dialog = document.querySelector(".cor-lightbox");
  if (!cards.length || !dialog) return;

  const img = dialog.querySelector("img");
  const titulo = dialog.querySelector(".cor-lightbox-titulo");
  const desc = dialog.querySelector(".cor-lightbox-desc");
  const orcamento = dialog.querySelector(".cor-lightbox-orcamento");
  const copiar = dialog.querySelector(".cor-lightbox-copiar");
  const total = document.getElementById("cores-total");
  let atual = -1;

  /* ---------- Filtros ---------- */
  const filtros = document.querySelectorAll(".cores-filtro");
  filtros.forEach((botao) => {
    botao.addEventListener("click", () => {
      const tom = botao.dataset.filtro;
      filtros.forEach((b) => {
        const ativo = b === botao;
        b.classList.toggle("ativo", ativo);
        b.setAttribute("aria-pressed", ativo ? "true" : "false");
      });
      let n = 0;
      cards.forEach((card) => {
        const mostra = tom === "todas" || card.dataset.tom === tom;
        card.hidden = !mostra;
        if (mostra) n++;
      });
      if (total) total.textContent = n;
    });
  });

  const visiveis = () => cards.filter((c) => !c.hidden);

  /* ---------- Ampliação ---------- */
  function mostrar(card) {
    const botao = card.querySelector(".cor-ampliar");
    const mini = botao.querySelector("img");
    atual = cards.indexOf(card);
    img.src = botao.dataset.full;
    img.alt = mini.alt;
    titulo.textContent = botao.dataset.titulo;
    desc.textContent = Array.from(card.querySelectorAll(".cor-desc, .cor-pantone"))
      .map((el) => el.textContent)
      .join(" · ");
    orcamento.href = botao.dataset.orcamento;
    copiar.textContent = dialog.dataset.copiar || "Copiar link da cor";
    history.replaceState(null, "", "#" + card.id);
  }

  function abrir(card) {
    mostrar(card);
    if (!dialog.open) dialog.showModal();
  }

  function andar(passo) {
    const lista = visiveis();
    let i = lista.indexOf(cards[atual]);
    i = (i + passo + lista.length) % lista.length;
    mostrar(lista[i]);
  }

  cards.forEach((card) =>
    card.querySelector(".cor-ampliar").addEventListener("click", () => abrir(card))
  );
  dialog.querySelector(".cor-lightbox-anterior").addEventListener("click", () => andar(-1));
  dialog.querySelector(".cor-lightbox-proxima").addEventListener("click", () => andar(1));
  dialog.querySelector(".cor-lightbox-fechar").addEventListener("click", () => dialog.close());

  // Fecha ao clicar fora da caixa
  dialog.addEventListener("click", (ev) => {
    if (ev.target === dialog) dialog.close();
  });

  dialog.addEventListener("keydown", (ev) => {
    if (ev.key === "ArrowLeft") andar(-1);
    if (ev.key === "ArrowRight") andar(1);
  });

  // Arrastar para o lado no celular
  let toqueX = null;
  img.addEventListener("touchstart", (ev) => (toqueX = ev.touches[0].clientX), { passive: true });
  img.addEventListener("touchend", (ev) => {
    if (toqueX === null) return;
    const dx = ev.changedTouches[0].clientX - toqueX;
    if (Math.abs(dx) > 40) andar(dx < 0 ? 1 : -1);
    toqueX = null;
  });

  copiar.addEventListener("click", () => {
    const link = location.origin + location.pathname + "#" + cards[atual].id;
    const ok = () => (copiar.textContent = dialog.dataset.copiado || "Link copiado!");
    if (navigator.clipboard) navigator.clipboard.writeText(link).then(ok).catch(() => prompt("Link:", link));
    else prompt("Link:", link);
  });

  // Abrindo a página com #codigo, já mostra a cor
  if (location.hash) {
    const alvo = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (alvo && alvo.classList.contains("cor-card")) {
      alvo.scrollIntoView({ block: "center" });
      setTimeout(() => abrir(alvo), 300);
    }
  }
})();
