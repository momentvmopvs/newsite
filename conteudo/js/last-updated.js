// Mostra no rodapé a data da última publicação real do site.
// A data vem do Cloudflare (worker.js -> /ultima-atualizacao.json) e muda
// só quando uma nova versão do site é publicada (merge na main).
(function () {
  const el = document.getElementById("last-updated");
  if (!el) return;

  fetch("/ultima-atualizacao.json")
    .then((r) => (r.ok ? r.json() : null))
    .then((info) => {
      if (!info || !info.data) return;
      const data = new Date(info.data);
      if (isNaN(data)) return;

      el.textContent = data
        .toLocaleString("pt-BR", {
          day: "2-digit",
          month: "2-digit",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          timeZone: "America/Sao_Paulo",
        })
        .replace(",", " |");
    })
    .catch(() => {});
})();
