"""
Desenha amostras digitais de cor (para linhas sem catálogo em PDF, como o ACM).

Cada cor do JSON precisa de "amostra": {"tipo": ..., "hex": "#rrggbb"} e,
nas madeiras, "hex2" (tom dos veios). Tipos:
    fosco, brilho, metalico, escovado, espelhado, madeira

Gera images/catalogos/<slug>/<arquivo>.webp (600 px) e -300.webp, e a capa
(1170 x 658) indicada em "capa", com uma grade das próprias amostras.
Usa só o Pillow.
"""

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

LADO = 600


def _rgb(hexa):
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def _diagonal(lado, rot=-45):
    """Gradiente em diagonal (claro no canto superior esquerdo), modo L."""
    g = Image.linear_gradient("L").resize((lado * 2, lado * 2))
    g = g.rotate(rot, resample=Image.BICUBIC)
    m = lado // 2
    return g.crop((m, m, m + lado, m + lado))


def _ruido(lado, sigma, semente):
    random.seed(semente)
    return Image.effect_noise((lado, lado), sigma).convert("L")


def _luz(img, intensidade):
    """Clareia o canto superior esquerdo e escurece o oposto (efeito de chapa iluminada)."""
    g = _diagonal(img.width).point(lambda v: 255 - v)
    claro = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), intensidade)
    escuro = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), intensidade)
    meio = Image.composite(claro, escuro, g)
    return meio


def _textura(img, mascara, quanto):
    """Mistura um ruído (mascara L) por cima da cor, clareando e escurecendo."""
    ruido_rgb = Image.merge("RGB", (mascara, mascara, mascara))
    sobre = ImageChops.overlay(img, ruido_rgb)
    return Image.blend(img, sobre, quanto)


def _reflexo(img, largura, forca, posicao=0.32):
    """Faixa de brilho diagonal, suave, como reflexo de luz em superfície lisa."""
    lado = img.width
    faixa = Image.new("L", (lado * 2, lado * 2), 0)
    d = ImageDraw.Draw(faixa)
    y = int(lado * 2 * posicao)
    d.rectangle((0, y, lado * 2, y + int(lado * largura)), fill=int(255 * forca))
    faixa = faixa.filter(ImageFilter.GaussianBlur(lado * largura * 0.6))
    faixa = faixa.rotate(-35, resample=Image.BICUBIC)
    m = lado // 2
    faixa = faixa.crop((m, m, m + lado, m + lado))
    return Image.composite(Image.new("RGB", img.size, (255, 255, 255)), img, faixa)


def fosco(cor, semente):
    img = Image.new("RGB", (LADO, LADO), cor)
    img = _luz(img, 0.05)
    return _textura(img, _ruido(LADO, 18, semente), 0.10)


def brilho(cor, semente):
    img = Image.new("RGB", (LADO, LADO), cor)
    img = _luz(img, 0.10)
    img = _reflexo(img, 0.16, 0.30)
    return _reflexo(img, 0.04, 0.20, posicao=0.52)


def metalico(cor, semente):
    img = Image.new("RGB", (LADO, LADO), cor)
    img = _luz(img, 0.16)
    flocos = _ruido(LADO, 70, semente)
    img = _textura(img, flocos, 0.32)
    return _reflexo(img, 0.22, 0.12)


def escovado(cor, semente):
    img = Image.new("RGB", (LADO, LADO), cor)
    img = _luz(img, 0.12)
    # Riscos horizontais: ruído esticado na horizontal
    riscos = _ruido(LADO, 80, semente).resize((12, LADO), Image.BILINEAR).resize((LADO, LADO), Image.BILINEAR)
    finos = _ruido(LADO, 60, semente + 1).resize((40, LADO)).resize((LADO, LADO), Image.BICUBIC)
    img = _textura(img, riscos, 0.45)
    img = _textura(img, finos, 0.30)
    return _reflexo(img, 0.30, 0.10)


def espelhado(cor, semente):
    """Reflexo de espelho: faixas largas de claro e escuro, levemente inclinadas."""
    alto = LADO * 2
    coluna = Image.new("L", (1, alto))
    vals = []
    for y in range(alto):
        t = y / alto
        v = (0.55 + 0.30 * math.sin(t * 7.0 + 0.6) + 0.15 * math.sin(t * 19.0 + 1.3))
        vals.append(max(0, min(255, int(v * 255))))
    coluna.putdata(vals)
    faixas = coluna.resize((alto, alto)).rotate(-18, resample=Image.BICUBIC)
    m = (alto - LADO) // 2
    faixas = faixas.crop((m, m, m + LADO, m + LADO))
    claro = tuple(min(255, int(c + (255 - c) * 0.6)) for c in cor)
    escuro = tuple(int(c * 0.40) for c in cor)
    img = Image.composite(Image.new("RGB", (LADO, LADO), claro), Image.new("RGB", (LADO, LADO), escuro), faixas)
    img = Image.blend(img, Image.new("RGB", (LADO, LADO), cor), 0.25)
    return _reflexo(img, 0.05, 0.45, posicao=0.45)


def madeira(cor, veio, semente):
    """Madeira: veios longos e irregulares na horizontal, feitos com ruído esticado
    em várias escalas, levemente ondulados."""
    def faixas(colunas, linhas, sigma, s):
        return _ruido(max(colunas, linhas), sigma, s).crop((0, 0, colunas, linhas))             .resize((LADO, LADO), Image.BICUBIC)
    largas = faixas(5, 70, 90, semente)
    medias = faixas(9, 180, 90, semente + 7)
    finas = faixas(24, 600, 70, semente + 13)
    mistura = Image.blend(Image.blend(largas, medias, 0.45), finas, 0.30)
    # contraste: veios escuros mais marcados
    mistura = mistura.point(lambda v: max(0, min(255, int((v - 128) * 2.6 + 128))))
    # ondulação suave das fibras
    rnd = random.Random(semente)
    f1, f2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    ondulada = Image.new("L", (LADO, LADO))
    for x in range(0, LADO, 4):
        dy = int(6 * math.sin(x / 140 + f1) + 3 * math.sin(x / 47 + f2))
        tira = mistura.crop((x, 0, x + 4, LADO))
        ondulada.paste(tira, (x, dy))
        if dy > 0:
            ondulada.paste(mistura.crop((x, LADO - dy, x + 4, LADO)), (x, 0))
        elif dy < 0:
            ondulada.paste(mistura.crop((x, 0, x + 4, -dy)), (x, LADO + dy))
    ondulada = ondulada.filter(ImageFilter.GaussianBlur(0.8))
    img = Image.composite(Image.new("RGB", (LADO, LADO), cor), Image.new("RGB", (LADO, LADO), veio), ondulada)
    poros = _ruido(LADO, 40, semente + 3).resize((90, LADO)).resize((LADO, LADO), Image.BICUBIC)
    img = _textura(img, poros, 0.22)
    return _luz(img, 0.06)


def desenhar(amostra, semente=1):
    tipo, cor = amostra["tipo"], _rgb(amostra["hex"])
    if tipo == "madeira":
        return madeira(cor, _rgb(amostra["hex2"]), semente)
    return {"fosco": fosco, "brilho": brilho, "metalico": metalico,
            "escovado": escovado, "espelhado": espelhado}[tipo](cor, semente)


def capa(imagens, destino, largura=1170, altura=658, colunas=7, linhas=4, vao=10):
    lado = min((largura - 60 - vao * (colunas - 1)) // colunas, (altura - 60 - vao * (linhas - 1)) // linhas)
    tela = Image.new("RGB", (largura, altura), (245, 245, 248))
    x0 = (largura - (lado * colunas + vao * (colunas - 1))) // 2
    y0 = (altura - (lado * linhas + vao * (linhas - 1))) // 2
    for i, im in enumerate(imagens[:colunas * linhas]):
        lin, col = divmod(i, colunas)
        miniatura = im.resize((lado, lado), Image.LANCZOS)
        tela.paste(miniatura, (x0 + col * (lado + vao), y0 + lin * (lado + vao)))
    tela.save(destino, "WEBP", quality=84, method=6)


def gerar_amostras(dados, raiz, nome_arquivo):
    pasta = raiz / "images" / "catalogos" / dados["slug"]
    pasta.mkdir(parents=True, exist_ok=True)
    feitas = []
    for i, cor in enumerate(dados["cores"], 1):
        im = desenhar(cor["amostra"], semente=i)
        base = nome_arquivo(dados, cor)
        im.save(pasta / f"{base}.webp", "WEBP", quality=86, method=6)
        im.resize((300, 300), Image.LANCZOS).save(pasta / f"{base}-300.webp", "WEBP", quality=82, method=6)
        feitas.append(im)
    ordem = dados.get("ordem_capa")
    if ordem:
        feitas = [feitas[n - 1] for n in ordem]
    capa(feitas, raiz / dados["capa"])
    print(f"{len(dados['cores'])} amostras desenhadas em {pasta.relative_to(raiz)} + capa {dados['capa']}")
