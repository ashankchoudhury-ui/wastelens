#!/usr/bin/env python3
"""Fetch a few real Creative-Commons photos from Wikimedia Commons for the WasteLens demo."""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "WasteLens-demo-build/1.0 (hackathon demo; contact: user@example.com)"}
OUT = os.path.dirname(os.path.abspath(__file__))

QUERIES = [
    ("bottle", "plastic bottle", ["bottle", "bottles", "plastic"]),
    ("leaf", "banana leaf", ["banana", "leaf", "leaves"]),
    ("can", "aluminium can", ["can", "aluminium", "aluminum"]),
]


def search(q):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": q + " filetype:bitmap",
        "gsrlimit": 12,
        "gsrnamespace": 6,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": 900,
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pick(data, wanted):
    pages = (data.get("query", {}) or {}).get("pages", {}) or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        title = p.get("title", "")
        lic = ((ii.get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "?")
        w = ii.get("width", 0) or 0
        h = ii.get("height", 0) or 0
        low = title.lower()
        if any(x in low for x in ("svg", "logo", "diagram", "icon", "map", "qr", "stamp")):
            continue
        if w < 400 or h < 400:
            continue
        thumb = ii.get("thumburl") or ii.get("url")
        if not thumb:
            continue
        out.append((title, lic, thumb))
    return out


def main():
    for name, q, _ in QUERIES:
        try:
            data = search(q)
        except Exception as e:
            print(f"{name}: search failed: {e}")
            continue
        hits = pick(data, name)
        print(f"=== {name} ({q}) -> {len(hits)} candidates ===")
        for title, lic, url in hits[:6]:
            print(f"  {lic:<28} {title}\n      {url}")
        if hits:
            title, lic, url = hits[0]
            dest = os.path.join(OUT, f"photo-{name}.jpg")
            try:
                req = urllib.request.Request(url, headers=UA)
                with urllib.request.urlopen(req, timeout=40) as r, open(dest, "wb") as f:
                    f.write(r.read())
                print(f"  DOWNLOADED -> {dest} ({os.path.getsize(dest)} bytes)  [{lic}]  {title}")
            except Exception as e:
                print(f"  download failed: {e}")


if __name__ == "__main__":
    main()
