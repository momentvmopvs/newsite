// Serve o site estático mantendo as URLs com .html, como no GitHub Pages.
// Roda antes dos arquivos (run_worker_first) para também cuidar dos
// redirecionamentos de domínio: www e http -> https://momentvmopvs.com

const DOMINIO = "momentvmopvs.com";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // www.momentvmopvs.com  e  http://  ->  https://momentvmopvs.com (301)
    if (
      url.hostname === "www." + DOMINIO ||
      (url.hostname === DOMINIO && url.protocol === "http:")
    ) {
      return Response.redirect("https://" + DOMINIO + path + url.search, 301);
    }

    // Data da última publicação do site (rodapé "Site atualizado em")
    if (path === "/ultima-atualizacao.json") {
      return Response.json(
        { data: env.CF_VERSION_METADATA?.timestamp || null },
        { headers: { "Cache-Control": "public, max-age=300" } }
      );
    }

    // Arquivo existente (ex.: /sobre.html, imagens, css): entrega direto
    const direto = await env.ASSETS.fetch(request);
    if (direto.status !== 404) return direto;

    const asset = (p) => env.ASSETS.fetch(new URL(p, url.origin));

    // Pasta com barra final: /  e  /en/  ->  index.html
    if (path.endsWith("/")) {
      const index = await asset(path + "index.html");
      if (index.ok) return index;
    } else if (!path.split("/").pop().includes(".")) {
      // Sem extensão: /sobre -> /sobre.html  e  /en -> /en/
      if ((await asset(path + ".html")).ok) {
        return Response.redirect(url.origin + path + ".html" + url.search, 301);
      }
      if ((await asset(path + "/index.html")).ok) {
        return Response.redirect(url.origin + path + "/" + url.search, 301);
      }
    }

    const notFound = await asset(path.startsWith("/en/") ? "/en/404.html" : "/404.html");
    return new Response(notFound.body, { status: 404, headers: notFound.headers });
  },
};
