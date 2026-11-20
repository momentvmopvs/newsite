"""
Gera a página de cores de uma linha de catálogo (ex.: catalogos/gold-madeiras.html)
a partir de ferramentas/catalogos/<slug>.json.

Uso (na raiz do site):
    python ferramentas/gerar_catalogo.py gold-madeiras            # só o HTML
    python ferramentas/gerar_catalogo.py gold-madeiras --imagens  # extrai as imagens do PDF também

As imagens das cores vão para images/catalogos/<slug>/ (uma grande para ampliar
e uma miniatura para a grade). O cabeçalho e o rodapé são copiados de catalogos.html,
então mudanças no menu feitas lá entram na próxima geração.

Requer: pymupdf e Pillow (pip install pymupdf pillow) apenas para --imagens.
"""

import html
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

RAIZ = Path(__file__).resolve().parent.parent
SITE = "https://momentvmopvs.com"


def slugify(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def ident(cor):
    """Identificador da cor: código, nome ou os dois."""
    return " ".join(p for p in (cor.get("nome", ""), cor.get("codigo", "")) if p)


def cor_id(cor):
    return slugify(ident(cor))


def nome_arquivo(dados, cor):
    return f"{dados.get('prefixo_arquivo', 'adesivo')}-{dados['slug']}-{cor_id(cor)}-{slugify(dados['fabricante'])}"


def titulo_cor(dados, cor):
    """Nome completo da cor, ex.: 'Gold Madeiras MD 1804' ou 'Kroma Forma Fendi 977KF23'."""
    prefixo = dados.get("prefixo_titulo", dados["linha"])
    return " ".join(p for p in (prefixo, ident(cor)) if p)


def numerar_cartoes(doc):
    """Cartões de cor visíveis, na ordem da página (de cima para baixo, da esquerda
    para a direita). Em cada posição vale a imagem desenhada por último (a que aparece)."""
    cartoes = []
    for pagina in doc:
        topo = {}
        for info in pagina.get_image_info(xrefs=True):
            bb = tuple(round(v) for v in info["bbox"])
            if info["width"] < 300 or bb[2] - bb[0] > 300:
                continue  # ícones, capas e fundos
            topo[bb] = info["xref"]
        cartoes += [topo[bb] for bb in sorted(topo, key=lambda r: (r[1], r[0]))]
    return {i + 1: x for i, x in enumerate(cartoes)}


def extrair_imagens(dados):
    import pymupdf
    from PIL import Image

    pasta = RAIZ / "images" / "catalogos" / dados["slug"]
    pasta.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(RAIZ / dados["pdf"])

    if dados.get("numeracao") == "cartoes":
        numeradas = numerar_cartoes(doc)
    else:
        # Numera as imagens na ordem do PDF: página a página, de cima para baixo,
        # da esquerda para a direita (a mesma numeração usada no campo "img" do JSON)
        numeradas, vistos = {}, set()
        for pagina in doc:
            infos = sorted(pagina.get_image_info(xrefs=True),
                           key=lambda i: (round(i["bbox"][1]), i["bbox"][0]))
            for info in infos:
                if info["xref"] in vistos:
                    continue
                vistos.add(info["xref"])
                numeradas[len(numeradas) + 1] = info["xref"]

    corte = dados.get("corte", "legenda-embaixo")
    for cor in dados["cores"]:
        pix = pymupdf.Pixmap(doc, numeradas[cor["img"]])
        if pix.alpha:
            pix = pymupdf.Pixmap(pix, 0)
        if pix.n >= 4 or pix.colorspace.n != 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        w, h = im.size
        if corte == "legenda-embaixo":
            # Corta a faixa de legenda do PDF: fica só a amostra, quadrada
            lado = int(h * 0.895)
        else:
            lado = min(w, h)
        x0 = (w - lado) // 2
        im = im.crop((x0, 0, x0 + lado, lado))
        if im.width > 600:
            im = im.resize((600, 600), Image.LANCZOS)
        base = nome_arquivo(dados, cor)
        im.save(pasta / f"{base}.webp", "WEBP", quality=82, method=6)
        im.resize((300, 300), Image.LANCZOS).save(pasta / f"{base}-300.webp", "WEBP", quality=78, method=6)
    print(f"{len(dados['cores'])} cores extraídas em {pasta.relative_to(RAIZ)}")


UI = {
    "pt": {
        "lang": "pt-BR", "modelo": "catalogos.html", "base": "", "rel": "../",
        "catalogos": "Catálogos Virtuais", "trilha": "Você está em", "cores": "cores",
        "filtrar": "Filtrar", "todas": "Todas", "cod": "Cód.", "secao": "Cores disponíveis",
        "adesivo": "Adesivo", "ampliar": "Ampliar", "saiba": "Saiba mais",
        "lista": "Cores do adesivo", "escolheu": "Escolheu a cor?",
        "final": "Clique na cor e use o botão de orçamento: o código já vai preenchido. "
                 "Se preferir, a gente leva as amostras físicas para você comparar no local.",
        "orcamento": "Solicite um orçamento", "outros": "Ver outros catálogos",
        "lb": "Cor ampliada", "fechar": "Fechar", "anterior": "Cor anterior", "proxima": "Próxima cor",
        "pedir": "Pedir orçamento com esta cor", "copiar": "Copiar link da cor", "copiado": "Link copiado!",
        "servicos": {},
    },
    "en": {
        "lang": "en", "modelo": "en/catalogos.html", "base": "/en", "rel": "../../",
        "catalogos": "Virtual Catalogues", "trilha": "You are here", "cores": "colors",
        "filtrar": "Filter", "todas": "All", "cod": "Code", "secao": "Available colors",
        "adesivo": "Vinyl", "ampliar": "Enlarge", "saiba": "Learn more",
        "lista": "Colors of the", "escolheu": "Found your color?",
        "final": "Click the color and use the quote button: the code is filled in for you. "
                 "If you prefer, we bring the physical samples so you can compare them on site.",
        "orcamento": "Request a quote", "outros": "See other catalogues",
        "lb": "Enlarged color", "fechar": "Close", "anterior": "Previous color", "proxima": "Next color",
        "pedir": "Request a quote with this color", "copiar": "Copy color link", "copiado": "Link copied!",
        # opções do formulário de orçamento em inglês (en/servicos.html)
        "servicos": {
            "Envelopamento (móveis, portas, veículos)": "Wrapping (furniture, doors, vehicles)",
            "Envelopamento arquitetônico": "Architectural wrapping",
            "Papel de Parede": "Wallpaper",
            "Sinalização / Comunicação Visual Corporativa": "Signage / Corporate Visual Communication",
            "Fachada em ACM": "ACM Facade",
        },
    },
}


def blocos_do_modelo(t):
    modelo = (RAIZ / t["modelo"]).read_text(encoding="utf-8")
    cabecalho = modelo[modelo.index('<body id="topo">'):modelo.index("<main")]
    rodape = modelo[modelo.index("</main>") + len("</main>"):modelo.index('<script type="application/ld+json">')]
    # A página fica um nível abaixo do modelo (catalogos/), então os caminhos relativos
    # ganham um "../" a mais
    def descer(trecho):
        return trecho.replace('"../', '"@@SOBE@@').replace('"./', '"../').replace('"@@SOBE@@', '"../../')
    return descer(cabecalho), descer(rodape)


def url_pagina(slug, lang):
    return f"{SITE}{UI[lang]['base']}/catalogos/{slug}.html"


def gerar_html(dados, lang="pt"):
    e = html.escape
    t = UI[lang]
    # Textos da página: em inglês vêm do bloco "en" do JSON
    txt = dados if lang == "pt" else {**dados, **dados["en"]}
    # Textos da interface que a linha pode trocar (ex.: "Chapa de ACM" no lugar de "Adesivo")
    t = {**t, **txt.get("ui", {})}
    slug, linha, fab = dados["slug"], dados["linha"], dados["fabricante"]
    url = url_pagina(slug, lang)
    rel = t["rel"]
    cabecalho, rodape = blocos_do_modelo(t)
    filtros_txt = txt["filtros"]
    rotulos = dict(filtros_txt)
    img_dir = f"images/catalogos/{slug}"
    servico = t["servicos"].get(dados["servico_formulario"], dados["servico_formulario"])
    form = f"{t['base']}/servicos.html?servico={quote_plus(servico)}"

    filtros = "\n".join(
        f'      <button type="button" class="cores-filtro" data-filtro="{k}">{e(v)}</button>'
        for k, v in filtros_txt
    )
    bloco_filtros = (f'''      <div class="cores-filtros" role="group" aria-label="{t['filtrar']}">
      <button type="button" class="cores-filtro ativo" data-filtro="todas" aria-pressed="true">{t['todas']}</button>
{filtros}
      </div>''' if filtros_txt else "")

    def desc_de(cor):
        return cor.get("desc", "") if lang == "pt" else cor.get("desc_en", "")

    cards = []
    for cor in dados["cores"]:
        base = nome_arquivo(dados, cor)
        cid = cor_id(cor)
        nome = titulo_cor(dados, cor)
        desc = desc_de(cor)
        alt = f"{t['adesivo']} {nome} {fab}" + (f": {desc}" if desc else "")
        material = quote_plus(f"{nome} ({fab})")
        orc = f"{form}&amp;material={material}#orcamento-form"
        principal = cor.get("nome") or cor["codigo"]
        linhas = []
        if desc:
            linhas.append(f'<span class="cor-desc">{e(desc[0].upper() + desc[1:])}</span>')
        if cor.get("nome") and cor.get("codigo"):
            linhas.append(f'<span class="cor-codigo">{t["cod"]} {e(cor["codigo"])}</span>')
        if filtros_txt:
            linhas.append(f'<span class="cor-tom">{e(rotulos[cor["tom"]])}</span>')
        if cor.get("pantone"):
            linhas.append(f'<span class="cor-pantone">Pantone® {e(cor["pantone"])}</span>')
        extra = "\n          ".join(linhas)
        cards.append(f'''      <figure class="cor-card" id="{cid}" data-tom="{cor.get('tom', '')}">
        <button type="button" class="cor-ampliar" data-full="{rel}{img_dir}/{base}.webp" data-titulo="{e(nome)}" data-orcamento="{orc}" aria-label="{t['ampliar']} {e(nome)}">
          <img src="{rel}{img_dir}/{base}-300.webp" width="300" height="300" loading="lazy" decoding="async" alt="{e(alt)}">
        </button>
        <figcaption>
          <strong>{e(principal)}</strong>
          {extra}
        </figcaption>
      </figure>''')

    usos = "\n".join(
        f'''      <div class="cores-uso-item">
        <h3>{e(a)}</h3>
        <p>{e(p)} <a href="{l}">{t['saiba']}</a></p>
      </div>''' for a, p, l in txt["uso"])

    intro = "\n".join(f'    <p class="texto-geral">{e(p)}</p>' for p in txt["intro"])
    onde = txt["onde"] if "onde" in txt else f"Onde aplicar {dados.get('artigo_linha', 'o ' + linha)}"

    itens_ld = []
    for i, cor in enumerate(dados["cores"], 1):
        base = nome_arquivo(dados, cor)
        desc = desc_de(cor)
        itens_ld.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "ImageObject",
                "@id": f"{url}#{cor_id(cor)}",
                "name": f"{t['adesivo']} {titulo_cor(dados, cor)} {fab}",
                "caption": titulo_cor(dados, cor) + (f": {desc}" if desc else "") + (f" (Pantone {cor['pantone']})" if cor.get("pantone") else ""),
                "contentUrl": f"{SITE}/{img_dir}/{base}.webp",
                "thumbnailUrl": f"{SITE}/{img_dir}/{base}-300.webp",
                "creditText": dados.get("credito", fab),
            },
        })
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": url,
                "url": url,
                "name": txt["titulo"],
                "description": txt["meta_descricao"],
                "inLanguage": t["lang"],
                "isPartOf": {"@type": "WebSite", "name": "Momentvm Opvs", "url": SITE},
                "publisher": {"@id": f"{SITE}#organization"},
                "mainEntity": {
                    "@type": "ItemList",
                    "name": f"{t['lista']} {linha} {fab}",
                    "numberOfItems": len(dados["cores"]),
                    "itemListElement": itens_ld,
                },
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}{t['base']}/"},
                    {"@type": "ListItem", "position": 2, "name": t["catalogos"], "item": f"{SITE}{t['base']}/catalogos.html"},
                    {"@type": "ListItem", "position": 3, "name": linha, "item": url},
                ],
            },
            {
                "@type": "Organization",
                "@id": f"{SITE}#organization",
                "name": "Momentvm Opvs",
                "url": SITE,
                "logo": f"{SITE}/images/mo-logo-header.svg",
            },
        ],
    }

    og_img = f"{SITE}/{dados['capa']}"
    url_pt, url_en = url_pagina(slug, "pt"), url_pagina(slug, "en")
    pagina = f'''<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
  <!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-PBQXH9WZ');</script>
<!-- End Google Tag Manager -->
<!-- Página gerada por ferramentas/gerar_catalogo.py a partir de ferramentas/catalogos/{slug}.json.
     Para mudar cores ou textos, edite o JSON e gere de novo. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow, max-image-preview:large">
<title>{e(txt['titulo'])} | Momentvm Opvs</title>
<meta name="description" content="{e(txt['meta_descricao'])}">

<meta property="og:title" content="{e(txt['titulo'])} | Momentvm Opvs">
<meta property="og:description" content="{e(txt['meta_descricao'])}">
<meta property="og:image" content="{og_img}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(txt['titulo'])} | Momentvm Opvs">
<meta name="twitter:description" content="{e(txt['meta_descricao'])}">
<meta name="twitter:image" content="{og_img}">

<link rel="alternate" hreflang="pt-BR" href="{url_pt}" />
<link rel="alternate" hreflang="en" href="{url_en}" />
<link rel="alternate" hreflang="x-default" href="{url_pt}" />

<link rel="canonical" href="{url}">
<link rel="icon" href="{rel}images/mo-icon-32x32.png" type="image/png">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inconsolata:wght@200..900&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
<script src="{rel}conteudo/js/header.js" defer></script>
<script src="{rel}conteudo/js/last-updated.js" defer></script>
<script src="{rel}conteudo/js/catalogo-cores.js" defer></script>

<link rel="stylesheet" href="{rel}conteudo/css/estilo.css">
<link rel="stylesheet" href="{rel}conteudo/css/header.css">
<link rel="stylesheet" href="{rel}conteudo/css/footer.css">
<link rel="stylesheet" href="{rel}conteudo/css/paginas-servicos.css">
<link rel="stylesheet" href="{rel}conteudo/css/catalogo-cores.css">
<link rel="stylesheet" href="{rel}conteudo/css/responsive.css">
</head>
{cabecalho}<main class="sem-recuo">

<section class="catalogos-hero">
  <div class="container catalogos-hero-container">
    <nav class="cores-trilha" aria-label="{t['trilha']}">
      <a href="{t['base']}/catalogos.html">{t['catalogos']}</a> <span aria-hidden="true">›</span> {e(linha)}
    </nav>
    <span class="titulo-linha"></span>
    <h1>{e(txt['h1'])} <span class="cores-fabricante">{e(dados.get("fabricante_exibido", fab))}</span></h1>
{intro}
  </div>
</section>

<section class="cores-secao" aria-label="{t['secao']}">
  <div class="container">
    <div class="cores-barra">
      <p class="cores-contagem"><strong id="cores-total">{len(dados['cores'])}</strong> {t['cores']}</p>
{bloco_filtros}
    </div>

    <div class="cores-grid">
{chr(10).join(cards)}
    </div>

    <p class="cores-aviso">{e(txt['aviso'])}</p>
  </div>
</section>

<section class="cores-uso">
  <div class="container">
    <span class="titulo-linha"></span>
    <h2>{e(onde)}</h2>
    <div class="cores-uso-grid">
{usos}
    </div>
  </div>
</section>

<section class="final servicos-final">
  <div class="container servicos-final-container">
    <span class="titulo-linha"></span>
    <h2>{t['escolheu']}</h2>
    <p class="texto-geral">
      {t['final']}
    </p>
    <div class="servicos-final-acoes">
      <a href="{form}#orcamento-form" class="servicos-final-botao servicos-final-botao-principal">{t['orcamento']}</a>
      <a href="{t['base']}/catalogos.html" class="servicos-final-botao servicos-final-botao-secundario">{t['outros']}</a>
    </div>
  </div>
</section>

</main>

<dialog class="cor-lightbox" aria-label="{t['lb']}" data-copiar="{t['copiar']}" data-copiado="{t['copiado']}">
  <div class="cor-lightbox-conteudo">
    <button type="button" class="cor-lightbox-fechar" aria-label="{t['fechar']}">&times;</button>
    <button type="button" class="cor-lightbox-nav cor-lightbox-anterior" aria-label="{t['anterior']}">&#8249;</button>
    <img src="" alt="">
    <button type="button" class="cor-lightbox-nav cor-lightbox-proxima" aria-label="{t['proxima']}">&#8250;</button>
    <div class="cor-lightbox-legenda">
      <p class="cor-lightbox-titulo"></p>
      <p class="cor-lightbox-desc"></p>
      <div class="cor-lightbox-acoes">
        <a class="cor-lightbox-orcamento" href="#">{t['pedir']}</a>
        <button type="button" class="cor-lightbox-copiar">{t['copiar']}</button>
      </div>
    </div>
  </div>
</dialog>
{rodape}<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</body>
</html>
'''
    pasta = RAIZ / ("catalogos" if lang == "pt" else "en/catalogos")
    pasta.mkdir(exist_ok=True)
    destino = pasta / f"{slug}.html"
    destino.write_text(pagina, encoding="utf-8", newline="\n")
    print(f"Página gerada: {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    dados = json.loads((RAIZ / "ferramentas" / "catalogos" / f"{sys.argv[1]}.json").read_text(encoding="utf-8"))
    if "--imagens" in sys.argv:
        if dados.get("amostras"):
            # Linha sem PDF: as amostras são desenhadas (ver amostras.py)
            from amostras import gerar_amostras
            gerar_amostras(dados, RAIZ, nome_arquivo)
        else:
            extrair_imagens(dados)
    gerar_html(dados, "pt")
    if "en" in dados:
        gerar_html(dados, "en")
