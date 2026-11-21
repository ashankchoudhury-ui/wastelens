#!/usr/bin/env python3
"""Rebuild the WasteLens demo video (tight, with voiceover) and produce thumbnail + product images."""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/home/bryan/.hermes/tools/ffmpeg-9.0.1-linux-x64/bin/ffmpeg"
W, H = 900, 1500


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=HERE, capture_output=True, text=True)


def still(img, secs, out):
    r = sh(f'{FF} -y -loop 1 -i {img} -t {secs} -c:v libx264 -preset veryfast '
           f'-pix_fmt yuv420p -vf "scale={W}:{H}:force_original_aspect_ratio=decrease,'
           f'pad={W}:{H}:(ow-iw)/2:(oh-ih)/2" {out}')
    if r.returncode != 0:
        print("still failed:", r.stderr[-600:])


def cut(src, start, secs, out):
    r = sh(f'{FF} -y -ss {start} -i {src} -t {secs} -c:v libx264 -preset veryfast '
           f'-pix_fmt yuv420p {out}')
    if r.returncode != 0:
        print("cut failed:", r.stderr[-600:])


def main():
    # --- video segments timed to the 46s voiceover ---
    still("card-title.png", 6, "v-title.mp4")
    cut("raw-bottle.mp4", 3, 16, "v-bottle.mp4")
    cut("raw-leaf2.mp4", 3, 16, "v-leaf.mp4")
    still("card-end.png", 8, "v-end.mp4")

    with open(os.path.join(HERE, "concat.txt"), "w") as f:
        for s in ["v-title.mp4", "v-bottle.mp4", "v-leaf.mp4", "v-end.mp4"]:
            f.write(f"file '{s}'\n")

    sh(f"{FF} -y -f concat -safe 0 -i concat.txt -c:v libx264 -preset veryfast "
       f"-pix_fmt yuv420p -r 20 vsilent.mp4")
    sh(f"{FF} -y -i vsilent.mp4 -i voiceover.ogg -c:v libx264 -preset veryfast "
       f"-pix_fmt yuv420p -c:a aac -b:a 128k -shortest WasteLens-demo.mp4")
    r = sh(f"{FF} -i WasteLens-demo.mp4 2>&1 | grep -oE 'Duration: [0-9:.]+'")
    print("final:", r.stdout.strip())

    # --- product images ---
    gen_images()


def gen_images():
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=True):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            return ImageFont.load_default()

    def fit(path, maxw, maxh):
        im = Image.open(path).convert("RGB")
        im.thumbnail((maxw, maxh))
        return im

    # thumbnail 1280x720
    th = Image.new("RGB", (1280, 720), (10, 10, 10))
    d = ImageDraw.Draw(th)
    shot = fit("c18.png", 360, 640)
    frame = Image.new("RGB", (shot.width + 16, shot.height + 16), (24, 24, 24))
    frame.paste(shot, (8, 8))
    th.paste(frame, (860, 40))
    d.text((80, 150), "WasteLens", font=font(116), fill=(247, 245, 240))
    d.text((84, 296), "GUWAHATI", font=font(30), fill=(150, 150, 150))
    d.line([(84, 346), (760, 346)], fill=(60, 60, 60), width=3)
    d.text((84, 386), "Point your phone.", font=font(40, False), fill=(235, 235, 235))
    d.text((84, 440), "Know your bin.", font=font(40, False), fill=(235, 235, 235))
    d.text((84, 560), "On-device waste classification.", font=font(26, False), fill=(170, 170, 170))
    th.save(os.path.join(HERE, "thumbnail.png"))

    # product shots
    for src, out in [("c18.png", "product-bottle.png"), ("l20.png", "product-leaf.png")]:
        shot = fit(src, 420, 720)
        im = Image.new("RGB", (1280, 720), (12, 12, 12))
        dd = ImageDraw.Draw(im)
        frame = Image.new("RGB", (shot.width + 16, shot.height + 16), (26, 26, 26))
        frame.paste(shot, (8, 8))
        im.paste(frame, (430, 0))
        dd.text((70, 300), "WasteLens", font=font(64), fill=(247, 245, 240))
        dd.text((72, 386), "Guwahati", font=font(26), fill=(150, 150, 150))
        dd.line([(72, 424), (520, 424)], fill=(60, 60, 60), width=2)
        dd.text((72, 452), "Know your bin.", font=font(30, False), fill=(210, 210, 210))
        im.save(os.path.join(HERE, out))
    print("images done")


if __name__ == "__main__":
    main()
