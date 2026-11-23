"""
Atualiza o que depende das datas dos artigos do blog (PT e EN):

  1. No topo de cada artigo: data de publicação e tempo de leitura.
  2. Na lista do blog (blog.html, en/blog.html): cartões da mais recente para a mais
     antiga, com data, tempo de leitura e o selo "Mais recente" no primeiro.
  3. Na página inicial (index.html, en/index.html): seção "Do blog" com os 3 últimos.

A data vem do "datePublished" do JSON-LD de cada artigo; o tempo de leitura é
calculado pelo número de palavras do texto (200 palavras por minuto).

Ao publicar um artigo novo: crie a página em articles/ (e en/articles/), coloque o
cartão dele em qualquer posição da lista do blog e rode, na raiz do site:
    python ferramentas/atualizar_blog.py
"""

import html
import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PALAVRAS_POR_MINUTO = 200
NA_HOME = 3

MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
            "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_EN = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]

IDIOMAS = {
    "pt": {
        "pasta": "articles", "blog": "blog.html", "home": "index.html",
        "data": lambda a, m, d: f"{d} de {MESES_PT[m - 1]} de {a}",
        "leitura": "min de leitura", "recente": "Mais recente",
        "do_blog": "Do blog", "ler": "Ler artigo →", "todos": "Ver todos os artigos",
        "link_blog": "/blog.html", "rotulo_secao": "Artigos mais recentes do blog",
    },
    "en": {
        "pasta": "en/articles", "blog": "en/blog.html", "home": "en/index.html",
        "data": lambda a, m, d: f"{MESES_EN[m - 1]} {d}, {a}",
        "leitura": "min read", "recente": "Latest",
        "do_blog": "From the blog", "ler": "Read article →", "todos": "See all articles",
        "link_blog": "/en/blog.html", "rotulo_secao": "Latest blog articles",
    },
}

RE_META = re.compile(r'\n[ \t]*<p class="artigo-meta">.*?</p>', re.S)


def texto_puro(trecho):
    trecho = re.sub(r"<(script|style)\b.*?</\1>", " ", trecho, flags=re.S)
    trecho = re.sub(r"<!--.*?-->", " ", trecho, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", trecho))


def dados_artigo(arquivo):
    s = arquivo.read_text(encoding="utf-8")
    data = re.search(r'"datePublished":\s*"(\d{4})-(\d{2})-(\d{2})', s)
    if not data:
        raise SystemExit(f"{arquivo}: sem datePublished no JSON-LD")
    ini = s.index("<h1")
    fim = s.find('class="parceiro-final"', ini)
    if fim < 0:
        fim = s.index("</main>", ini)
    palavras = len(texto_puro(RE_META.sub("", s[ini:fim])).split())
    a, m, d = (int(x) for x in data.groups())
    return {
        "arquivo": arquivo,
        "iso": f"{a:04d}-{m:02d}-{d:02d}",
        "amd": (a, m, d),
        "minutos": max(1, math.ceil(palavras / PALAVRAS_POR_MINUTO)),
    }


def meta_html(art, t, recente=False):
    a, m, d = art["amd"]
    selo = f'<span class="selo-linha"><span class="selo-recente">{t["recente"]}</span></span> ' if recente else ""
    return (f'<p class="artigo-meta">{selo}<time datetime="{art["iso"]}">{t["data"](a, m, d)}</time>'
            f' <span class="artigo-meta-leitura"><span aria-hidden="true">·</span> {art["minutos"]} {t["leitura"]}</span></p>')


def atualizar_artigo(art, t):
    s = art["arquivo"].read_text(encoding="utf-8")
    s = RE_META.sub("", s)
    fim_h1 = s.index("</h1>") + len("</h1>")
    s = s[:fim_h1] + "\n\n      " + meta_html(art, t) + s[fim_h1:]
    art["arquivo"].write_text(s, encoding="utf-8")


def cartoes_do_blog(t, artigos):
    """Lê a lista do blog, ordena por data e devolve (página, início, fim, cartões)."""
    arq = RAIZ / t["blog"]
    s = arq.read_text(encoding="utf-8")
    abre = '<section class="sobre-servicos blog-lista">\n'
    i = s.index(abre) + len(abre)
    j = s.index("</section>", i)
    partes = re.split(r'(?m)^[ \t]*(?=<div class="container sobre-flex">)', s[i:j])
    if partes[0].strip():
        raise SystemExit(f"{arq}: conteúdo inesperado antes do primeiro cartão")
    cartoes = []
    for k, c in enumerate(partes[1:]):
        slug = re.search(r'articles/([^"/]+)\.html" class="botao-blog', c).group(1)
        if slug not in artigos:
            raise SystemExit(f"{arq}: cartão aponta para artigo inexistente ({slug})")
        cartoes.append({"slug": slug, "html": "  " + RE_META.sub("", c).rstrip() + "\n", "ordem": k})
    faltando = set(artigos) - {c["slug"] for c in cartoes}
    if faltando:
        raise SystemExit(f"{arq}: artigos sem cartão na lista do blog: {', '.join(sorted(faltando))}")
    # Mais recente primeiro; na mesma data, mantém a ordem que já estava
    cartoes.sort(key=lambda c: (tuple(-x for x in artigos[c["slug"]]["amd"]), c["ordem"]))
    return arq, s, i, j, cartoes


def atualizar_blog(t, artigos):
    arq, s, i, j, cartoes = cartoes_do_blog(t, artigos)
    novos = []
    for n, c in enumerate(cartoes):
        meta = meta_html(artigos[c["slug"]], t, recente=(n == 0))
        h = re.sub(r'(\n)([ \t]*)(<h2 class="especialblog[^"]*">)', lambda m: f"{m[1]}      {meta}\n{m[2]}{m[3]}", c["html"], count=1)
        if h == c["html"]:
            raise SystemExit(f"{arq}: cartão de {c['slug']} sem <h2 class=\"especialblog\">")
        novos.append(h)
    arq.write_text(s[:i] + "".join(novos) + s[j:], encoding="utf-8")
    return cartoes


def secao_home(t, cartoes, artigos):
    itens = []
    for c in cartoes[:NA_HOME]:
        h = c["html"]
        titulo = re.sub(r"\s+", " ", texto_puro(re.search(r'<h2 class="especialblog[^"]*">(.*?)</h2>', h, re.S)[1])).strip()
        desc = re.sub(r"\s+", " ", texto_puro(re.search(r'<p class="parceiro">(.*?)</p>', h, re.S)[1])).strip()
        link = re.search(r'<a href="([^"]+)" class="botao-blog', h)[1]
        img = re.search(r'<img\b(.*?)>', h, re.S)[1]
        src = re.search(r'src="([^"]+)"', img)[1]
        alt = re.search(r'alt="([^"]*)"', img)[1]
        # Versão menor da imagem, se existir (ex.: -640x360.webp ao lado da -1170x658.webp)
        menor = src.replace("-1170x658.", "-640x360.")
        pasta_rel = RAIZ / t["home"]
        if menor != src and (pasta_rel.parent / menor).resolve().exists():
            src = menor
        e = html.escape
        itens.append(f'''      <article class="blog-recente-card">
        <a class="blog-recente-imagem" href="{link}" tabindex="-1" aria-hidden="true">
          <img src="{src}" width="640" height="360" loading="lazy" decoding="async" alt="{alt}">
        </a>
        {meta_html(artigos[c["slug"]], t)}
        <h3><a href="{link}">{e(titulo)}</a></h3>
        <p class="blog-recente-resumo">{e(desc)}</p>
        <p class="blog-recente-ler"><a href="{link}">{t["ler"]}</a></p>
      </article>''')
    return f'''<!-- blog-recentes: gerado por ferramentas/atualizar_blog.py -->
<section class="blog-recentes" aria-label="{t["rotulo_secao"]}">
  <div class="container">
    <div class="titulo-secao">
      <span class="titulo-linha"></span>
      <h2>{t["do_blog"]}</h2>
    </div>
    <div class="blog-recentes-grid">
{chr(10).join(itens)}
    </div>
    <div class="blog-recentes-todos">
      <a href="{t["link_blog"]}" class="botao-blog texto-geral">{t["todos"]}</a>
    </div>
  </div>
</section>
<!-- /blog-recentes -->
'''


def atualizar_home(t, cartoes, artigos):
    arq = RAIZ / t["home"]
    s = arq.read_text(encoding="utf-8")
    secao = secao_home(t, cartoes, artigos)
    existente = re.compile(r"<!-- blog-recentes:.*?<!-- /blog-recentes -->\n", re.S)
    if existente.search(s):
        s = existente.sub(lambda _: secao, s)
    else:
        alvo = '<section class="final">'
        if s.count(alvo) != 1:
            raise SystemExit(f"{arq}: não achei onde colocar a seção do blog")
        s = s.replace(alvo, secao + alvo)
    arq.write_text(s, encoding="utf-8")


def main():
    for lang, t in IDIOMAS.items():
        artigos = {}
        for arq in sorted((RAIZ / t["pasta"]).glob("*.html")):
            art = dados_artigo(arq)
            artigos[arq.stem] = art
            atualizar_artigo(art, t)
        cartoes = atualizar_blog(t, artigos)
        atualizar_home(t, cartoes, artigos)
        print(f"[{lang}] {len(artigos)} artigos; ordem:")
        for c in cartoes:
            art = artigos[c["slug"]]
            print(f"   {art['iso']}  {art['minutos']:>2} min  {c['slug']}")


if __name__ == "__main__":
    main()
