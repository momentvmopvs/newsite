"""
Atualiza o que depende dos artigos do blog (PT e EN):

  1. No topo de cada artigo: assunto, data de publicação e tempo de leitura.
  2. Na lista do blog (blog.html, en/blog.html): filtro por assunto e cartões da mais
     recente para a mais antiga, com o selo "Mais recente" no primeiro.
  3. Na página inicial (index.html, en/index.html): seção "Do blog" com os 3 últimos.
  4. No sitemap.xml: inclui os artigos novos e atualiza as datas dos artigos, do blog e da home.

A data vem do "datePublished" e o assunto do "articleSection" do JSON-LD de cada artigo
(os assuntos válidos estão em IDIOMAS, abaixo). O tempo de leitura é calculado pelo
número de palavras (200 por minuto).

Ao publicar um artigo novo: crie a página em articles/ (e en/articles/) e rode, na raiz:
    python ferramentas/atualizar_blog.py
O cartão é criado com o título, a descrição e a imagem do JSON-LD; depois disso, o título
e o resumo podem ser editados na própria lista. A miniatura 640x360 também é criada.
"""

import html
import json
import math
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PALAVRAS_POR_MINUTO = 200
NA_HOME = 3
SITE = "https://momentvmopvs.com"

MESES_PT = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
            "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_EN = ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]

IDIOMAS = {
    "pt": {
        "pasta": "articles", "blog": "blog.html", "home": "index.html",
        "data": lambda a, m, d: f"{d} de {MESES_PT[m - 1]} de {a}",
        "leitura": "min de leitura", "recente": "Mais recente",
        "do_blog": "Do blog", "todos": "Ver todos os artigos",
        "link_blog": "/blog.html", "rotulo_secao": "Artigos mais recentes do blog",
        "todos_assuntos": "Todos", "filtrar": "Filtrar artigos por assunto",
        "mais": "Mostrar mais artigos", "rotulo_lista": "Artigos do blog",
        "assuntos": {
            "fachadas": "Fachadas em ACM", "letras": "Letras e Sinalização",
            "envelopamento": "Envelopamento", "peliculas": "Películas e Jateados",
            "impressao-3d": "Impressão 3D", "comunicacao-visual": "Comunicação Visual",
            "especiais": "Projetos Especiais",
        },
    },
    "en": {
        "pasta": "en/articles", "blog": "en/blog.html", "home": "en/index.html",
        "data": lambda a, m, d: f"{MESES_EN[m - 1]} {d}, {a}",
        "leitura": "min read", "recente": "Latest",
        "do_blog": "From the blog", "todos": "See all articles",
        "link_blog": "/en/blog.html", "rotulo_secao": "Latest blog articles",
        "todos_assuntos": "All", "filtrar": "Filter articles by topic",
        "mais": "Show more articles", "rotulo_lista": "Blog articles",
        "assuntos": {
            "fachadas": "ACM Facades", "letras": "Letters and Signage",
            "envelopamento": "Wrapping", "peliculas": "Window and Frosted Films",
            "impressao-3d": "3D Printing", "comunicacao-visual": "Visual Communication",
            "especiais": "Special Projects",
        },
    },
}

RE_META = re.compile(r'\n[ \t]*<p class="artigo-meta">.*?</p>', re.S)


def texto_puro(trecho):
    trecho = re.sub(r"<(script|style)\b.*?</\1>", " ", trecho, flags=re.S)
    trecho = re.sub(r"<!--.*?-->", " ", trecho, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", trecho))


def dados_artigo(arquivo, t):
    s = arquivo.read_text(encoding="utf-8")
    data = re.search(r'"datePublished":\s*"(\d{4})-(\d{2})-(\d{2})', s)
    if not data:
        raise SystemExit(f"{arquivo}: sem datePublished no JSON-LD")
    secao = re.search(r'"articleSection":\s*"([^"]+)"', s)
    nome = secao[1] if secao else ""
    por_nome = {v: k for k, v in t["assuntos"].items()}
    if nome not in por_nome:
        raise SystemExit(f'{arquivo}: "articleSection" no JSON-LD deve ser um destes: {", ".join(por_nome)}')
    ini = s.index("<h1")
    fim = s.find('class="parceiro-final"', ini)
    if fim < 0:
        fim = s.index("</main>", ini)
    palavras = len(texto_puro(RE_META.sub("", s[ini:fim])).split())
    a, m, d = (int(x) for x in data.groups())
    return {
        "arquivo": arquivo,
        "iso": f"{a:04d}-{m:02d}-{d:02d}",
        "modificado": max([f"{a:04d}-{m:02d}-{d:02d}"] + re.findall(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})', s)),
        "amd": (a, m, d),
        "assunto": por_nome[nome],
        "assunto_nome": nome,
        "minutos": max(1, math.ceil(palavras / PALAVRAS_POR_MINUTO)),
    }


RELOGIO = ('<svg class="icone-relogio" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">'
           '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
           'd="M9 2h6M12 2v3M12 9v4.5l3 1.8M18.5 6.5l1.2 1.2M12 5a8.5 8.5 0 1 0 0 17 8.5 8.5 0 0 0 0-17Z"/></svg>')


def data_html(art, t):
    return f'<time datetime="{art["iso"]}">{t["data"](*art["amd"])}</time>'


def leitura_html(art, t, classe):
    return f'<span class="{classe}">{RELOGIO}{art["minutos"]} {t["leitura"]}</span>'


def atualizar_artigo(art, t):
    """Assunto, data e tempo de leitura logo abaixo do título do artigo."""
    s = art["arquivo"].read_text(encoding="utf-8")
    s = RE_META.sub("", s)
    meta = (f'<p class="artigo-meta"><a class="artigo-assunto" href="{t["link_blog"]}#{art["assunto"]}">'
            f'{html.escape(art["assunto_nome"])}</a> {data_html(art, t)} '
            f'{leitura_html(art, t, "artigo-meta-leitura")}</p>')
    fim_h1 = s.index("</h1>") + len("</h1>")
    s = s[:fim_h1] + "\n\n      " + meta + "\n\n" + s[fim_h1:].lstrip("\n")
    art["arquivo"].write_text(s, encoding="utf-8")


def miniatura(src):
    """Nome da versão 640x360 da imagem (criada em images/ se ainda não existir)."""
    nome = src.rsplit("/", 1)[-1]
    base = re.sub(r"-(1170x658|640x360)$", "", nome.rsplit(".", 1)[0])
    menor = RAIZ / "images" / f"{base}-640x360.webp"
    if not menor.exists():
        from PIL import Image, ImageOps
        with Image.open(RAIZ / "images" / nome) as im:
            ImageOps.fit(im.convert("RGB"), (640, 360), Image.LANCZOS).save(menor, quality=80, method=6)
        print(f"   miniatura criada: {menor.name}")
    return menor.name


def cartao_do_artigo(slug, art):
    """Cartão inicial de um artigo que ainda não está na lista, com os dados do JSON-LD."""
    s = art["arquivo"].read_text(encoding="utf-8")
    ld = s[s.index('"BlogPosting"'):]
    titulo = json.loads(re.search(r'"headline":\s*("(?:[^"\\]|\\.)*")', ld)[1])
    resumo = json.loads(re.search(r'"description":\s*("(?:[^"\\]|\\.)*")', ld)[1])
    img = re.search(r'"image":\s*"([^"]+)"', ld)[1].rsplit("/", 1)[-1]
    alt = titulo
    for tag in re.findall(r"<img\b.*?>", s, re.S):
        a = re.search(r'alt="([^"]+)"', tag)
        if img in tag and a:
            alt = html.unescape(a[1])
            break
    return {"slug": slug, "titulo": titulo, "resumo": resumo, "img": img, "alt": alt, "ordem": -1}


def ler_cartoes(t, artigos):
    """Lê os cartões da lista do blog, acrescenta os artigos novos e ordena por data."""
    s = (RAIZ / t["blog"]).read_text(encoding="utf-8")
    cartoes = []
    for k, c in enumerate(re.findall(r'<article class="blog-recente-card".*?</article>', s, re.S)):
        um = lambda padrao: html.unescape(re.sub(r"\s+", " ", re.search(padrao, c, re.S)[1]).strip())
        slug = um(r'href="[^"]*articles/([^"/]+)\.html"')
        if slug not in artigos:
            raise SystemExit(f"{t['blog']}: cartão aponta para artigo inexistente ({slug})")
        cartoes.append({"slug": slug, "titulo": um(r"<h2><a[^>]*>(.*?)</a></h2>"),
                        "resumo": um(r'<p class="blog-recente-resumo">(.*?)</p>'),
                        "img": um(r'<img src="([^"]+)"'), "alt": um(r'alt="([^"]*)"'), "ordem": k})
    ja = {c["slug"] for c in cartoes}
    for slug, art in artigos.items():
        if slug not in ja:
            print(f"   cartão novo: {slug}")
            cartoes.append(cartao_do_artigo(slug, art))
    # Mais recente primeiro; na mesma data, mantém a ordem que já estava
    cartoes.sort(key=lambda c: (tuple(-x for x in artigos[c["slug"]]["amd"]), c["ordem"]))
    return cartoes


def cartao_html(c, art, t, nivel, recente=False):
    e = html.escape
    link = f'/{t["pasta"]}/{c["slug"]}.html'
    selo = f'\n          <span class="selo-recente">{t["recente"]}</span>' if recente else ""
    return f"""      <article class="blog-recente-card" data-assunto="{art["assunto"]}">
        <a class="blog-recente-imagem" href="{link}" tabindex="-1">
          <img src="/images/{miniatura(c["img"])}" width="640" height="360" loading="lazy" decoding="async" alt="{e(c["alt"])}">{selo}
          {leitura_html(art, t, "blog-recente-leitura")}
        </a>
        <span class="titulo-linha"></span>
        <p class="blog-recente-assunto">{e(art["assunto_nome"])}</p>
        <{nivel}><a href="{link}">{e(c["titulo"], quote=False)}</a></{nivel}>
        <p class="blog-recente-resumo">{e(c["resumo"], quote=False)}</p>
        <p class="blog-recente-data">{data_html(art, t)}</p>
      </article>"""


def trocar_bloco(arq, conteudo):
    s = arq.read_text(encoding="utf-8")
    bloco = re.compile(r"<!-- blog-recentes:.*?<!-- /blog-recentes -->\n", re.S)
    if len(bloco.findall(s)) != 1:
        raise SystemExit(f"{arq}: não achei o bloco <!-- blog-recentes: -->")
    novo = ("<!-- blog-recentes: gerado por ferramentas/atualizar_blog.py -->\n"
            + conteudo + "<!-- /blog-recentes -->\n")
    arq.write_text(bloco.sub(lambda _: novo, s), encoding="utf-8")


def atualizar_blog(t, artigos):
    cartoes = ler_cartoes(t, artigos)
    quantos = {}
    for a in artigos.values():
        quantos[a["assunto"]] = quantos.get(a["assunto"], 0) + 1
    botoes = [f'      <button type="button" class="blog-filtro" data-assunto="" aria-pressed="true">'
              f'{t["todos_assuntos"]} <span>{len(artigos)}</span></button>']
    for slug, nome in t["assuntos"].items():
        if slug in quantos:  # só aparecem os assuntos que já têm artigo
            botoes.append(f'      <button type="button" class="blog-filtro" data-assunto="{slug}" aria-pressed="false">'
                          f'{html.escape(nome)} <span>{quantos[slug]}</span></button>')
    grade = "\n".join(cartao_html(c, artigos[c["slug"]], t, "h2", n == 0) for n, c in enumerate(cartoes))
    trocar_bloco(RAIZ / t["blog"], f"""<section class="blog-recentes blog-lista" aria-label="{t["rotulo_lista"]}">
  <div class="container">
    <div class="blog-filtros" role="group" aria-label="{t["filtrar"]}" hidden>
{chr(10).join(botoes)}
    </div>
    <div class="blog-recentes-grid">
{grade}
    </div>
    <div class="blog-recentes-todos" id="blog-mais" hidden>
      <button type="button" class="botao-blog texto-geral">{t["mais"]}</button>
    </div>
  </div>
</section>
""")
    return cartoes


def atualizar_home(t, cartoes, artigos):
    grade = "\n".join(cartao_html(c, artigos[c["slug"]], t, "h3") for c in cartoes[:NA_HOME])
    trocar_bloco(RAIZ / t["home"], f"""<section class="blog-recentes" aria-label="{t["rotulo_secao"]}">
  <div class="container">
    <div class="titulo-secao">
      <span class="titulo-linha"></span>
      <h2>{t["do_blog"]}</h2>
    </div>
    <div class="blog-recentes-grid">
{grade}
    </div>
    <div class="blog-recentes-todos">
      <a href="{t["link_blog"]}" class="botao-blog texto-geral">{t["todos"]}</a>
    </div>
  </div>
</section>
""")


def lastmod_sitemap(s, url, data):
    """Põe a data no endereço, sem nunca voltar para uma data anterior."""
    padrao = re.compile(r"(<loc>" + re.escape(url) + r"</loc>\s*<lastmod>)([^<]+)")
    if not padrao.search(s):
        raise SystemExit(f"sitemap.xml: não achei {url} com <lastmod>")
    return padrao.sub(lambda m: m[1] + max(m[2], data), s)


def atualizar_sitemap(por_idioma):
    """Inclui os artigos novos e atualiza as datas dos artigos, do blog e da home."""
    arq = RAIZ / "sitemap.xml"
    s = arq.read_text(encoding="utf-8")
    for t, artigos in por_idioma:
        base = "/en/" if t["pasta"].startswith("en/") else "/"
        for slug, art in artigos.items():
            url = f'{SITE}/{t["pasta"]}/{slug}.html'
            if f"<loc>{url}</loc>" not in s:
                novo = (f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{art['modificado']}</lastmod>\n"
                        "    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n")
                s = s.replace("  <!-- Artigos -->\n", "  <!-- Artigos -->\n" + novo, 1)
                if novo not in s:
                    raise SystemExit("sitemap.xml: não achei o comentário <!-- Artigos -->")
                print(f"   sitemap: incluído {url}")
            s = lastmod_sitemap(s, url, art["modificado"])
        ultimo = max(art["iso"] for art in artigos.values())
        s = lastmod_sitemap(s, SITE + t["link_blog"], ultimo)
        s = lastmod_sitemap(s, SITE + base, ultimo)
    arq.write_text(s, encoding="utf-8")


def main():
    por_idioma = []
    for lang, t in IDIOMAS.items():
        artigos = {}
        for arq in sorted((RAIZ / t["pasta"]).glob("*.html")):
            art = dados_artigo(arq, t)
            artigos[arq.stem] = art
            atualizar_artigo(art, t)
        cartoes = atualizar_blog(t, artigos)
        atualizar_home(t, cartoes, artigos)
        por_idioma.append((t, artigos))
        print(f"[{lang}] {len(artigos)} artigos; ordem:")
        for c in cartoes:
            art = artigos[c["slug"]]
            print(f"   {art['iso']}  {art['minutos']:>2} min  {c['slug']}")
    atualizar_sitemap(por_idioma)


if __name__ == "__main__":
    main()
