#!/usr/bin/env python3
"""Four rockstar Rollies: accessories drawn over the real mascot art (no AI redraw), plus the notice mockup."""
import math
from PIL import Image, ImageDraw, ImageFilter

SRC = Image.open('rollie-rock.png')
ANG = 13.67                      # head tilt; accessories are drawn level, then rotated with the head
PT, PS = 260, 60                 # padding above / at the sides so hats and spikes fit
C = (400 + PS, 300 + PT)         # rotation centre in padded coords


def base():
    im = Image.new('RGBA', (SRC.width + 2 * PS, SRC.height + PT), (0, 0, 0, 0))
    im.alpha_composite(SRC, (PS, PT))
    return im


def P(x, y): return (x + PS, y + PT)


def layer(): return Image.new('RGBA', (SRC.width + 2 * PS, SRC.height + PT), (0, 0, 0, 0))


def shades(d):
    for x0, y0, x1, y1 in ((222, 240, 345, 330), (380, 225, 503, 318)):
        d.rounded_rectangle([P(x0, y0), P(x1, y1)], 22, fill=(18, 18, 22, 255), outline=(60, 60, 70, 255), width=6)
        d.line([P(x0 + 22, y0 + 18), P(x0 + 55, y0 + 18)], fill=(255, 255, 255, 170), width=8)
    d.line([P(345, 270), P(380, 262)], fill=(18, 18, 22, 255), width=12)
    d.line([P(185, 270), P(222, 268)], fill=(18, 18, 22, 255), width=10)


def bandana(d):
    d.polygon([P(178, 60), P(578, 60), P(578, 128), P(178, 138)], fill=(206, 28, 36, 255))
    for x in range(200, 570, 42):
        for y in (80, 112):
            d.ellipse([P(x, y), P(x + 9, y + 9)], fill=(255, 240, 230, 255))
    d.polygon([P(182, 90), P(105, 150), P(132, 168), P(186, 120)], fill=(186, 22, 30, 255))
    d.polygon([P(182, 105), P(120, 205), P(148, 210), P(190, 130)], fill=(206, 28, 36, 255))


def mohawk(d):
    n, x0, x1 = 7, 220, 540
    for i in range(n):
        cx = x0 + (x1 - x0) * i / (n - 1)
        h = 150 + 60 * math.sin(math.pi * i / (n - 1))
        lean = (cx - 380) * 0.35
        d.polygon([P(cx - 32, 58), P(cx + 32, 58), P(cx + lean, 58 - h)], fill=(70, 220, 90, 255), outline=(25, 110, 40, 255))
    d.rectangle([P(210, 45), P(550, 62)], fill=(40, 160, 60, 255))


def star(cx, cy, r, rot=0):
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = math.radians(rot - 90 + 36 * k)
        pts.append(P(cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def star_glasses(d):
    for cx, cy in ((285, 290), (442, 272)):
        d.polygon(star(cx, cy, 82), fill=(255, 70, 170, 235), outline=(255, 210, 60, 255), width=7)
    d.line([P(352, 282), P(375, 276)], fill=(255, 210, 60, 255), width=9)
    for cx, cy, r in ((150, 60, 26), (600, 40, 20), (560, 470, 16), (120, 380, 18)):
        d.polygon(star(cx, cy, r), fill=(255, 225, 90, 255))


def top_hat(d):
    hair = (38, 24, 18, 255)
    left = [(160, 45), (235, 45), (232, 150), (222, 260), (230, 360), (205, 440), (175, 455), (185, 380), (160, 300), (170, 200), (150, 120)]
    right = [(540, 45), (625, 70), (640, 180), (628, 280), (648, 380), (620, 450), (598, 400), (590, 300), (575, 200), (560, 120)]
    for poly in (left, right):
        d.polygon([P(x, y) for x, y in poly], fill=hair)
    for x0, y0, x1, y1 in ((185, 90, 175, 380), (210, 80, 205, 330), (590, 110, 610, 400)):
        d.line([P(x0, y0), P(x1, y1)], fill=(80, 54, 40, 255), width=4)
    d.rectangle([P(255, -140), P(505, 40)], fill=(22, 20, 24, 255), outline=(70, 66, 74, 255), width=5)
    d.rectangle([P(255, -10), P(505, 30)], fill=(150, 24, 30, 255))
    d.ellipse([P(140, 15), P(620, 75)], fill=(22, 20, 24, 255), outline=(70, 66, 74, 255), width=5)


def rockstar(*painters):
    im = base()
    for p in painters:
        lay = layer()
        p(ImageDraw.Draw(lay))
        im.alpha_composite(lay.rotate(-ANG, resample=Image.BICUBIC, center=C))
    b = im.getbbox()
    return im.crop((b[0], b[1], b[2], im.height))  # keep the feet on the bottom edge


LOOKS = {
    'rollie-shades.png': (bandana, shades),
    'rollie-mohawk.png': (mohawk,),
    'rollie-glam.png': (star_glasses,),
    'rollie-tophat.png': (top_hat,),
}


def placed(im, body, flip, angle, glow):
    f = body / SRC.height  # same body size whatever sits on the head
    im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    g = Image.new('RGBA', (im.width + 80, im.height + 80), (0, 0, 0, 0))
    col = Image.new('RGBA', im.size, glow + (255,)); col.putalpha(im.split()[3])
    g.alpha_composite(col, (40, 40)); g = g.filter(ImageFilter.GaussianBlur(18))
    g.alpha_composite(im, (40, 40))
    return g


def bake(looks, base_png='notice-base.jpg'):
    """Writes assets/notice/*.png (glow, flip and tilt baked in) and include/notice_layout.hpp for the game."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    out = root / 'assets/notice'; out.mkdir(parents=True, exist_ok=True)
    H, S = 215, 1.5                        # on-screen body height; textures are baked at S x for crispness
    screen = Image.open(base_png).convert('RGBA')
    sprites = []
    spec = (('rock0', 'rollie-shades.png', (125, 355), True, -5, (60, 220, 80)),
            ('rock1', 'rollie-mohawk.png', (125, 705), True, 4, (230, 40, 40)),
            ('rock2', 'rollie-tophat.png', (1155, 355), False, 5, (255, 200, 40)),
            ('rock3', 'rollie-glam.png', (1155, 705), False, -4, (40, 120, 255)))
    for name, look, (cx, feet), flip, ang, glow in spec:
        g = placed(looks[look], H, flip, ang, glow)
        x, y = cx - g.width // 2, feet - g.height + 40
        screen.alpha_composite(g, (x, y))
        big = placed(looks[look], int(H * S), flip, ang, glow)
        assert max(big.size) <= 512, big.size
        big.save(out / f'{name}.png')
        sprites.append((f'notice/{name}.png', x + g.width / 2, y + g.height / 2, g.width, g.height))
    logo = Image.open('/home/brendongl/snp-site/public/logos/sip n play long no cafe.png').convert('RGBA')
    lw = logo.copy(); lw.thumbnail((250, 80), Image.LANCZOS)
    big = logo.copy(); big.thumbnail((500, 160), Image.LANCZOS); big.save(out / 'logo.png')
    screen.alpha_composite(lw, (24, 18))
    sprites.append(('notice/logo.png', 24 + lw.width / 2, 18 + lw.height / 2, lw.width, lw.height))
    with open(root / 'include/notice_layout.hpp', 'w') as f:
        f.write('// Generated by cafe-art/make_rockstars.py. Do not edit by hand.\n#pragma once\nnamespace notice {\n')
        f.write('struct Sprite { const char *file; float cx, cy, w, h; };\n')
        f.write('inline constexpr Sprite sprites[] = {\n')
        for fn, cx, cy, w, h in sprites: f.write(f'    {{"{fn}", {cx:.1f}f, {cy:.1f}f, {w}.0f, {h}.0f}},\n')
        f.write('};\n}\n')
    screen.convert('RGB').save('notice-mockup-v2.png')


if __name__ == '__main__':
    looks = {}
    for name, painters in LOOKS.items():
        looks[name] = rockstar(*painters); looks[name].save(name)
    bake(looks)
