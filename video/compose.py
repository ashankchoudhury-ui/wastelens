#!/usr/bin/env python3
"""Build the WasteLens demo video: title card + bottle demo + leaf demo + end card."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/bryan/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
W, H = 900, 1500

TITLE = r"""from PIL import Image, ImageDraw
img = Image.new("RGB", (900, 1500), (10, 10, 10))
d = ImageDraw.Draw(img)
def f(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        from PIL import ImageFont
        return ImageFont.truetype(p, sz)
    except Exception:
        from PIL import ImageFont
        return ImageFont.load_default()
d.text((70, 560), "WasteLens", font=f(96), fill=(247, 245, 240))
d.text((74, 690), "GUWAHATI", font=f(34), fill=(150, 150, 150))
d.text((74, 780), "Photograph it. Know your bin.", font=f(30, False), fill=(220, 220, 220))
d.text((74, 830), "Find the buyer.", font=f(30, False), fill=(220, 220, 220))
d.line([(74, 900), (826, 900)], fill=(60, 60, 60), width=2)
d.text((74, 940), "On-device waste classification.", font=f(26, False), fill=(180, 180, 180))
d.text((74, 1330), "github.com/ashankchoudhary-ui/wastelens", font=f(22, False), fill=(120, 120, 120))
img.save("card-title.png")
"""

END = r"""from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGB", (900, 1500), (10, 10, 10))
d = ImageDraw.Draw(img)
def f(sz, bold=True):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
    try:
        return ImageFont.truetype(p, sz)
    except Exception:
        return ImageFont.load_default()
d.text((70, 500), "WasteLens", font=f(80), fill=(247, 245, 240))
d.text((74, 620), "Guwahati", font=f(32), fill=(150, 150, 150))
d.line([(74, 700), (826, 700)], fill=(60, 60, 60), width=2)
d.text((74, 760), "Runs fully on-device.", font=f(30, False), fill=(220, 220, 220))
d.text((74, 812), "No image ever leaves the phone.", font=f(30, False), fill=(220, 220, 220))
d.text((74, 900), "github.com/ashankchoudhary-ui/wastelens", font=f(26, False), fill=(180, 180, 180))
d.text((74, 1330), "Built for Arbiter Hacks V1", font=f(24, False), fill=(120, 120, 120))
img.save("card-end.png")
"""


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True)


def card(script, out):
    path = os.path.join(HERE, "_card_gen.py")
    with open(path, "w") as f:
        f.write(script)
    r = sh("python3 _card_gen.py")
    if r.returncode != 0:
        print("card failed:", r.stderr[-500:])


def still(img, secs, out):
    r = sh(f'{FF} -y -loop 1 -i {img} -t {secs} -c:v libx264 -preset veryfast '
           f'-pix_fmt yuv420p -vf "scale={W}:{H}:force_original_aspect_ratio=decrease,'
           f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2" {out}')
    if r.returncode != 0:
        print("still failed:", r.stderr[-800:])


def trim(src, secs, out):
    r = sh(f'{FF} -y -i {src} -t {secs} -c:v libx264 -preset veryfast -pix_fmt yuv420p {out}')
    if r.returncode != 0:
        print("trim failed:", r.stderr[-800:])


def main():
    card(TITLE, "card-title.png")
    card(END, "card-end.png")
    still("card-title.png", 5, "seg-title.mp4")
    trim("raw-bottle.mp4", 52, "seg-bottle.mp4")
    trim("raw-leaf2.mp4", 50, "seg-leaf.mp4")
    still("card-end.png", 6, "seg-end.mp4")

    with open(os.path.join(HERE, "concat.txt"), "w") as f:
        for s in ["seg-title.mp4", "seg-bottle.mp4", "seg-leaf.mp4", "seg-end.mp4"]:
            f.write(f"file '{s}'\n")
    r = sh(f"{FF} -y -f concat -safe 0 -i concat.txt -c copy WasteLens-demo.mp4")
    if r.returncode != 0:
        print("concat failed, re-encoding:", r.stderr[-800:])
        sh(f"{FF} -y -f concat -safe 0 -i concat.txt -c:v libx264 -preset veryfast "
           f"-pix_fmt yuv420p WasteLens-demo.mp4")
    print("done:", os.path.getsize(os.path.join(HERE, "WasteLens-demo.mp4")))


if __name__ == "__main__":
    main()
