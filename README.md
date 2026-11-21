# WasteLens Guwahati

Photograph an item. Find out how Guwahati disposes of it. Find the nearest scrap
dealer or e-waste point. Track how much you diverted.

Built for **Arbiter Hacks V1 — Theme Track: Rethinking Waste**.

## The problem

Guwahati generates roughly 600+ tonnes of solid waste a day, and a large share of
it is mixed at source. Residents are unsure which bin a packet, battery or
banana leaf goes into, so recyclables land in the dump and wet waste is
contaminated by plastic. There is no cheap, offline way to answer: *"What do I do
with this?"*

## What it does

- **Classify** — point the camera at an item. MobileNet (TensorFlow.js) runs
  entirely on-device; the prediction is mapped to one of Guwahati's four
  disposal streams.
- **Explain** — each result tells you *why* and what to do, in plain language.
- **Locate** — a direct link to find the nearest scrap dealer / e-waste point.
- **Measure** — every scan is logged locally with an estimated weight, so the
  required impact measurement is a real number, not a guess.

## Waste streams

| Stream | Examples | Where it goes |
|---|---|---|
| Dry recyclable | bottles, cans, paper, cardboard, metal, cloth | scrap dealer / dry-waste bin |
| Wet / compostable | food scraps, banana leaves, peels, wood | home compost / wet-waste collector |
| Hazardous / e-waste | batteries, phones, cables, bulbs, paint | e-waste or battery collection point |
| Landfill (residual) | chips packets, polythene, diapers, thermocol | residual waste — avoid |

## Privacy

No account, no server, no analytics. Images are classified in the browser and
never uploaded. The impact log lives in `localStorage` on the device.

## Run it

```bash
cd wastelens
python3 -m http.server 9000
# open http://127.0.0.1:9000/
```

Any static host works — it is three files.

## Tech

- Vanilla HTML/CSS/JS (three files, no build step)
- TensorFlow.js 4.x + MobileNet v2 (client-side inference)
- OpenStreetMap / Overpass for disposal points

## Measurement

Each scan is assigned a per-category average weight (dry 0.05 kg, wet 0.3 kg,
hazardous 0.4 kg, landfill 0.2 kg). Summing the log gives an estimated kilograms
diverted from landfill. The next iteration replaces these averages with a
trained classifier (TrashNet / local dataset) and a ward-level leaderboard.

## License

MIT
