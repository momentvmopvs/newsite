// Serve o site estático mantendo as URLs com .html, como no GitHub Pages.
// Arquivos que existem (ex.: /sobre.html) são entregues direto pelo Cloudflare,
// sem passar por aqui; este script só trata o que não bate com um arquivo.

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
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
