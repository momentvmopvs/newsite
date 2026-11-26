"""
Monta as páginas de um artigo do blog (PT e EN) a partir de um arquivo de conteúdo.

O conteúdo fica em ferramentas/artigos/<nome>.py, num dicionário ARTIGO com as
chaves "data", "pt" e "en" (veja os arquivos que já existem lá como exemplo).
O visual, o cabeçalho, o rodapé e os dados estruturados vêm do artigo-modelo.

Uso, na raiz do site:
    python ferramentas/novo_artigo.py ferramentas/artigos/<nome>.py
    python ferramentas/atualizar_blog.py

Marcação aceita nos textos:
    **negrito**          [texto do link](/endereco.html)
    um bloco que começa com "- " em cada linha vira lista
"""

import html
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atualizar_blog import IDIOMAS, RAIZ, SITE, miniatura  # noqa: E402

MODELO = {"pt": "articles/adesivo-jateado-em-escritorios.html",
          "en": "en/articles/frosted-glass-film-for-offices.html"}

TXT = {
    "pt": {"assinatura": "Momentvm Opvs — Comunicação Visual e Decoração<br>\n      30 anos de experiência profissional.<br>\n      São Paulo — SP",
           "frase": "Você imagina, nós tornamos realidade.", "leia": "Leia também", "rotulo": "Artigos relacionados"},
    "en": {"assinatura": "Momentvm Opvs — Visual Communication and Decoration<br>\n      30 years of professional experience.<br>\n      São Paulo — SP",
           "frase": "You imagine it, we make it real.", "leia": "Read also", "rotulo": "Related articles"},
}


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"\[(.+?)\]\((.+?)\)", r'<a class="link-artigo" href="\2">\1</a>', t)


def blocos(itens, ind):
    saida = []
    for b in itens:
        linhas = b.strip().split("\n")
        if all(l.startswith("- ") for l in linhas):
            li = "\n".join(f"{ind}  <li>{inline(l[2:])}</li>" for l in linhas)
            saida.append(f'{ind}<ul class="parceiro-bullet">\n{li}\n{ind}</ul>')
        else:
            saida.append(f'{ind}<p class="parceiro">\n{ind}  {inline(" ".join(linhas))}\n{ind}</p>')
    return "\n\n".join(saida)


def figura(img, alt, rel, eager=False):
    nome = f"{img}.webp" if "." not in img else img
    srcset = ""
    if nome.endswith("-1170x658.webp"):
        menor = miniatura(nome)
        srcset = (f'\n        srcset="{rel}images/{menor} 640w, {rel}images/{nome} 1170w"'
                  '\n        sizes="(max-width: 768px) 100vw, 50vw"\n        width="1170"\n        height="658"')
    return (f'<img\n        src="{rel}images/{nome}"{srcset}\n        loading="{"eager" if eager else "lazy"}"'
            f'\n        decoding="async"\n        alt="{html.escape(alt)}"\n      >')


def corpo(a, lang, rel):
    t = TXT[lang]
    partes = [f'''<section class="sobre-servicos">
  <div class="container sobre-flex">
    <div class="intro-texto">
      <h1 class="especialh1">{html.escape(a["h1"], quote=False)}</h1>

{blocos(a["intro"], "      ")}<br>
    </div>

    <div class="sobre-imagem">
      {figura(a["imagem"][0], a["imagem"][1], rel, eager=True)}
    </div>
  </div>
''']
    for s in a["secoes"]:
        titulo = html.escape(s["titulo"], quote=False)
        if "imagem" in s:
            partes.append(f'''
  <div class="container sobre-flex">
    <div class="intro-texto" style="padding-top: 30px;">
      <span class="titulo-linha"></span>

      <h2 style="font-size: 2rem;">{titulo}</h2>
{blocos(s["texto"], "      ")}
    </div>

    <div class="sobre-imagem">
      {figura(s["imagem"][0], s["imagem"][1], rel)}
    </div>
  </div>
''')
        else:
            partes.append(f'''
  <div class="intro-texto" style="padding-top: 30px;">
    <span class="titulo-linha"></span>

    <h2 style="font-size: 2rem;">{titulo}</h2>
{blocos(s["texto"], "    ")}
  </div>
''')
    leia = "\n".join(f'        <li><a href="{h}"><strong>{html.escape(n, quote=False)}</strong></a></li>' for n, h in a["leia"])
    partes.append(f'''
  <div class="parceiro-final">
    <p class="parceiro-assinatura" style="font-size: 2rem; padding-top:20px;">
      {t["assinatura"]}
    </p>
    <p class="parceiro" style="margin-top: 16px;"><strong>{t["frase"]}</strong></p>
    <div class="conteudo-blog" style="margin-top: 20px;">
      <a href="{a["botao"][1]}" class="botao-blog texto-geral">{html.escape(a["botao"][0], quote=False)}</a>
    </div>
  </div>
</section>
<section class="servico-artigos-section" aria-label="{t["rotulo"]}">
  <div class="container">
    <div class="titulo-secao">
      <span class="titulo-linha"></span>
      <h2>{t["leia"]}</h2>
    </div>
    <ul class="servico-artigos-lista">
{leia}
    </ul>
  </div>
</section>
''')
    return "".join(partes)


def trocar(s, padrao, novo):
    s, n = re.subn(padrao, lambda m: m[1] + novo + m[2], s)
    if n != 1:
        raise SystemExit(f"modelo: esperava 1 ocorrência de {padrao!r}, achei {n}")
    return s


def montar(art, lang, urls):
    a, t = art[lang], IDIOMAS[lang]
    if a["assunto"] not in t["assuntos"].values():
        raise SystemExit(f'[{lang}] assunto "{a["assunto"]}" não existe em IDIOMAS (atualizar_blog.py)')
    rel = "../" if lang == "pt" else "../../"
    m = (RAIZ / MODELO[lang]).read_text(encoding="utf-8")
    ini = m.index('<section class="sobre-servicos">')
    fim = m.index("</section>", m.index('class="servico-artigos-section"')) + len("</section>\n")
    s = m[:ini] + corpo(a, lang, rel) + m[fim:]

    url = urls[lang]
    img = f'{SITE}/images/{a["imagem"][0]}{"" if "." in a["imagem"][0] else ".webp"}'
    e = lambda x: html.escape(x)  # noqa: E731
    j = lambda x: json.dumps(x, ensure_ascii=False)[1:-1]  # noqa: E731
    for padrao, novo in [
        (r"(<title>).*?( \| Momentvm Opvs</title>)", e(a["titulo"])),
        (r'(<meta name="description" content=")[^"]*(")', e(a["descricao"])),
        (r'(<meta name="keywords" content=")[^"]*(")', e(a["palavras"])),
        (r'(<meta property="og:title" content=")[^"]*(")', e(a["titulo"]) + " | Momentvm Opvs"),
        (r'(<meta property="og:description" content=")[^"]*(")', e(a["descricao"])),
        (r'(<meta property="og:image" content=")[^"]*(")', img),
        (r'(<meta property="og:url" content=")[^"]*(")', url),
        (r'(<meta name="twitter:title" content=")[^"]*(")', e(a["titulo_curto"]) + " | Momentvm Opvs"),
        (r'(<meta name="twitter:description" content=")[^"]*(")', e(a["descricao"])),
        (r'(<meta name="twitter:image" content=")[^"]*(")', img),
        (r'(<link rel="alternate" hreflang="pt-BR" href=")[^"]*(")', urls["pt"]),
        (r'(<link rel="alternate" hreflang="en" href=")[^"]*(")', urls["en"]),
        (r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', urls["pt"]),
        (r'(<link rel="canonical" href=")[^"]*(")', url),
        (r'("@type": "BlogPosting",\s*"headline": ")[^"]*(")', j(a["h1"])),
        (r'("@type": "BlogPosting",\s*"headline": "[^"]*",\s*"description": ")[^"]*(")', j(a["descricao"])),
        (r'("@type": "BlogPosting",(?:[^{}]|\{[^{}]*\})*?"image": ")[^"]*(")', img),
        (r'("mainEntityOfPage": \{\s*"@type": "WebPage",\s*"@id": ")[^"]*(")', url),
        (r'("articleSection": ")[^"]*(")', a["assunto"]),
        (r'("datePublished": ")[^"]*(")', art["data"]),
        (r'("dateModified": ")[^"]*(")', art["data"]),
    ]:
        s = trocar(s, padrao, novo)
    velho = re.search(r'<link rel="canonical" href="([^"]+)"', m)[1]
    if velho in s:
        raise SystemExit(f"[{lang}] sobrou o endereço do modelo ({velho})")
    destino = RAIZ / f'{t["pasta"]}/{a["slug"]}.html'
    destino.write_text(s, encoding="utf-8")
    print(f"ok {destino.relative_to(RAIZ)}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    spec = importlib.util.spec_from_file_location("artigo", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    art = mod.ARTIGO
    urls = {lang: f'{SITE}/{IDIOMAS[lang]["pasta"]}/{art[lang]["slug"]}.html' for lang in ("pt", "en")}
    for lang in ("pt", "en"):
        montar(art, lang, urls)


if __name__ == "__main__":
    main()
