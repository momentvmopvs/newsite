"""
Gera a página "Uso das imagens" (catalogos/uso-das-imagens.html e a versão em inglês).

As imagens das cores nos catálogos apontam para ela nos dados estruturados
(campos license e acquireLicensePage, ver gerar_catalogo.py). A lista de
fabricantes e linhas vem de ferramentas/catalogos/*.json, então uma linha nova
entra aqui ao gerar de novo.

Uso (na raiz do site):
    python ferramentas/gerar_uso_imagens.py
"""

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_catalogo import RAIZ, SITE, UI, blocos_do_modelo, slugify  # noqa: E402

SLUG = "uso-das-imagens"
PROPRIA = "Momentvm Opvs"

TXT = {
    "pt": {
        "titulo": "Uso das imagens dos catálogos",
        "descricao": "De quem são as imagens das cores nos catálogos da Momentvm Opvs "
                     "e como pedir autorização para usá-las.",
        "intro": [
            "As imagens das cores nos nossos catálogos virtuais estão aqui para ajudar você "
            "a escolher o acabamento do seu projeto. Elas não estão à venda nem liberadas "
            "para uso fora deste site.",
            "Cada imagem tem um dono diferente. Veja abaixo de quem é e com quem falar "
            "se quiser usá-la em outro lugar.",
        ],
        "titulo_secao": "De quem são as imagens",
        "fab": "As imagens das linhas {linhas} vêm do catálogo da {fab} e pertencem a ela. "
               "Para usá-las fora deste site, peça autorização diretamente à {fab}.",
        "propria": "As amostras digitais do catálogo de chapas {linhas} foram desenhadas pela "
                   "Momentvm Opvs. Para usá-las fora deste site, {fale}.",
        "fale": "fale com a gente",
        "contato": "Fale com a gente",
        "cores_reais": "As cores na tela são uma referência. Antes de fechar o projeto, "
                       "compare com a amostra física: a gente leva até você.",
        "catalogos": "Ver os catálogos",
    },
    "en": {
        "titulo": "Use of catalogue images",
        "descricao": "Who owns the color images in the Momentvm Opvs catalogues "
                     "and how to ask permission to use them.",
        "intro": [
            "The color images in our virtual catalogues are here to help you choose the "
            "finish for your project. They are not for sale and are not licensed for use "
            "outside this site.",
            "Each image has a different owner. See below who owns it and who to contact "
            "if you want to use it elsewhere.",
        ],
        "titulo_secao": "Who owns the images",
        "fab": "The images of the {linhas} lines come from the {fab} catalogue and belong to {fab}. "
               "To use them outside this site, ask {fab} for permission directly.",
        "propria": "The digital samples in the {linhas} panel catalogue were drawn by "
                   "Momentvm Opvs. To use them outside this site, {fale}.",
        "fale": "get in touch with us",
        "contato": "Contact us",
        "cores_reais": "On-screen colors are a reference. Before closing the project, "
                       "compare them with the physical sample: we bring it to you.",
        "catalogos": "See the catalogues",
    },
}


def url_pagina(lang):
    return f"{SITE}{UI[lang]['base']}/catalogos/{SLUG}.html"


def ancora(dono):
    """Âncora do dono das imagens na página (usada também em gerar_catalogo.py)."""
    return slugify(dono)


def donos():
    """{dono: [(slug, linha), ...]} na ordem em que aparecem."""
    grupos = {}
    for f in sorted((RAIZ / "ferramentas" / "catalogos").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        dono = d.get("credito", d["fabricante"])
        grupos.setdefault(dono, []).append((d["slug"], d["linha"]))
    # Fabricantes primeiro, a Momentvm Opvs por último
    return dict(sorted(grupos.items(), key=lambda kv: (kv[0] == PROPRIA, kv[0])))


def lista_linhas(linhas, lang, base):
    e = html.escape
    links = [f'<a href="{base}/catalogos/{s}.html">{e(n)}</a>' for s, n in linhas]
    if len(links) == 1:
        return links[0]
    junta = " e " if lang == "pt" else " and "
    return ", ".join(links[:-1]) + junta + links[-1]


def gerar(lang):
    e = html.escape
    t, x = UI[lang], TXT[lang]
    rel, base = t["rel"], t["base"]
    url = url_pagina(lang)
    cabecalho, rodape = blocos_do_modelo(t)
    form = f"{base}/servicos.html#orcamento-form"

    itens = []
    for dono, linhas in donos().items():
        lst = lista_linhas(linhas, lang, base)
        if dono == PROPRIA:
            texto = x["propria"].format(linhas=lst, fale=f'<a href="{form}">{x["fale"]}</a>')
        else:
            texto = x["fab"].format(linhas=lst, fab=e(dono))
        itens.append(f'''      <div class="cores-uso-item" id="{ancora(dono)}">
        <h3>{e(dono)}</h3>
        <p>{texto}</p>
      </div>''')

    intro = "\n".join(f'    <p class="texto-geral">{e(p)}</p>' for p in x["intro"])
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": url,
                "url": url,
                "name": x["titulo"],
                "description": x["descricao"],
                "inLanguage": t["lang"],
                "isPartOf": {"@type": "WebSite", "name": "Momentvm Opvs", "url": SITE},
                "publisher": {"@id": f"{SITE}#organization"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}{base}/"},
                    {"@type": "ListItem", "position": 2, "name": t["catalogos"], "item": f"{SITE}{base}/catalogos.html"},
                    {"@type": "ListItem", "position": 3, "name": x["titulo"], "item": url},
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

    url_pt, url_en = url_pagina("pt"), url_pagina("en")
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
<!-- Página gerada por ferramentas/gerar_uso_imagens.py. Para mudar os textos, edite o script e gere de novo. -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="index, follow">
<title>{e(x['titulo'])} | Momentvm Opvs</title>
<meta name="description" content="{e(x['descricao'])}">

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
      <a href="{base}/catalogos.html">{t['catalogos']}</a> <span aria-hidden="true">›</span> {e(x['titulo'])}
    </nav>
    <span class="titulo-linha"></span>
    <h1>{e(x['titulo'])}</h1>
{intro}
  </div>
</section>

<section class="cores-uso">
  <div class="container">
    <span class="titulo-linha"></span>
    <h2>{e(x['titulo_secao'])}</h2>
    <div class="cores-uso-grid">
{chr(10).join(itens)}
    </div>
    <p class="cores-aviso">{e(x['cores_reais'])}</p>
  </div>
</section>

<section class="final servicos-final">
  <div class="container servicos-final-container">
    <div class="servicos-final-acoes">
      <a href="{base}/catalogos.html" class="servicos-final-botao servicos-final-botao-principal">{x['catalogos']}</a>
      <a href="{form}" class="servicos-final-botao servicos-final-botao-secundario">{x['contato']}</a>
    </div>
  </div>
</section>

</main>
{rodape}<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
</body>
</html>
'''
    pasta = RAIZ / ("catalogos" if lang == "pt" else "en/catalogos")
    destino = pasta / f"{SLUG}.html"
    destino.write_text(pagina, encoding="utf-8", newline="\n")
    print(f"Página gerada: {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    gerar("pt")
    gerar("en")
