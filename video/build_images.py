#!/usr/bin/env python3
"""WasteLens thumbnail + product images: clean app captures, tight layout."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME_H = 150  # browser chrome height in the raw captures


def font(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()


def cover(path, w, h, blur=0, dark=0.0):
    im = Image.open(path).convert("RGB")
    scale = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)))
    im = im.crop(((im.width - w) // 2, (im.height - h) // 2,
                  (im.width - w) // 2 + w, (im.height - h) // 2 + h))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if dark:
        im = ImageEnhance.Brightness(im).enhance(1 - dark)
    return im


def clean(path):
    im = Image.open(path).convert("RGB")
    return im.crop((0, CHROME_H, im.width, im.height))


def frame(im, pad=10, colour=(32, 32, 32)):
    f = Image.new("RGB", (im.width + pad * 2, im.height + pad * 2), colour)
    f.paste(im, (pad, pad))
    return f


def thumbnail():
    W, H = 1280, 720
    bg = cover(os.path.join(HERE, "../test-bottle.png"), W, H, blur=8, dark=0.62)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((56, 76, 700, 644), radius=20, fill=(10, 10, 10))
    d.text((92, 132), "WasteLens", font=font(98), fill=(247, 245, 240))
    d.text((96, 252), "GUWAHATI", font=font(26), fill=(165, 165, 165))
    d.line([(96, 300), (580, 300)], fill=(75, 75, 75), width=3)
    d.text((96, 334), "Point your phone.", font=font(42, False), fill=(240, 240, 240))
    d.text((96, 390), "Know your bin.", font=font(42, False), fill=(240, 240, 240))
    d.text((96, 548), "On-device waste classification.\nNo image ever leaves the phone.",
           font=font(24, False), fill=(180, 180, 180))

    shot = clean(os.path.join(HERE, "shot-bottle.png"))
    shot.thumbnail((330, 660))
    bg.paste(frame(shot), (820, 30))
    bg.save(os.path.join(HERE, "thumbnail.png"))


def product(photo, shot, out, title, sub):
    W, H = 1280, 720
    bg = Image.new("RGB", (W, H), (12, 12, 12))
    bg.paste(cover(photo, 620, H), (0, 0))
    d = ImageDraw.Draw(bg)
    d.text((52, 58), "YOU HOLD THIS", font=font(21), fill=(215, 215, 215))

    app = clean(shot)
    card = app.crop((46, 655, 856, 950))
    card.thumbnail((600, 400))
    bg.paste(frame(card, 8), (656, 96))
    d = ImageDraw.Draw(bg)
    d.text((656, 46), "THE APP ANSWERS", font=font(21), fill=(215, 215, 215))
    d.text((656, 500), title, font=font(40), fill=(242, 242, 242))
    d.text((656, 560), sub, font=font(23, False), fill=(165, 165, 165))
    d.line([(656, 640), (1220, 640)], fill=(60, 60, 60), width=2)
    d.text((656, 660), "WasteLens · Guwahati", font=font(19, False), fill=(120, 120, 120))
    bg.save(os.path.join(HERE, out))


def how_it_works():
    W, H = 1280, 720
    bg = Image.new("RGB", (W, H), (12, 12, 12))
    d = ImageDraw.Draw(bg)
    d.text((64, 56), "How it works", font=font(56), fill=(247, 245, 240))
    d.line([(66, 138), (1216, 138)], fill=(70, 70, 70), width=3)

    steps = [
        ("1", "Photograph", "Point at any\nhousehold item."),
        ("2", "Classify on-device", "MobileNet runs\nlocally. No upload."),
        ("3", "Know your stream", "Dry, wet, hazardous\nor landfill."),
        ("4", "Find the buyer", "Nearest scrap dealer\non the map."),
    ]
    x = 64
    for n, t, s in steps:
        d.rounded_rectangle((x, 200, x + 272, 600), radius=18, fill=(20, 20, 20))
        d.text((x + 26, 232), n, font=font(42), fill=(247, 245, 240))
        d.text((x + 26, 300), t, font=font(21), fill=(235, 235, 235))
        d.text((x + 26, 384), s, font=font(19, False), fill=(160, 160, 160))
        x += 296
    d.text((64, 654), "No account.  No server.  No analytics.",
           font=font(22, False), fill=(125, 125, 125))
    bg.save(os.path.join(HERE, "product-how.png"))


if __name__ == "__main__":
    thumbnail()
    product(os.path.join(HERE, "../test-bottle.png"), os.path.join(HERE, "shot-bottle.png"),
            "product-bottle.png", "Dry recyclable", "Sell to a scrap dealer, or use the dry-waste bin.")
    product(os.path.join(HERE, "../test-leaf.png"), os.path.join(HERE, "shot-leaf.png"),
            "product-leaf.png", "Wet / compostable", "Compost at home, or hand to the wet-waste collector.")
    how_it_works()
    print("images rebuilt")
