# Arbiter Hacks V1 — Submission copy (Theme Track: Rethinking Waste)

Project: **WasteLens Guwahati**
Repo: https://github.com/ashankchoudhury-ui/wastelens
Track: Theme Track — Rethinking Waste

---

## What it does

WasteLens is a mobile web app that answers one question a resident of Guwahati
asks every day: **"What do I do with this?"**

You photograph an item. A MobileNet model running entirely in the browser
classifies it and maps it to one of the city's four disposal streams — dry
recyclable, wet/compostable, hazardous/e-waste, or landfill. The app then explains
why, tells you where it should go, links you to the nearest scrap dealer or
e-waste point, and logs the scan with an estimated weight so your diverted
kilograms add up.

No account. No server. No analytics. Images never leave the phone.

## How it was built

- Three files of vanilla HTML/CSS/JS. No build step, no framework, no database.
- TensorFlow.js 4.x with MobileNet v2 for on-device inference — the model runs in
  the browser, so it works offline after first load and costs nothing to serve.
- A keyword-rule layer maps MobileNet's ImageNet classes onto the four local
  disposal streams, because ImageNet has no "kabadiwala" category.
- OpenStreetMap is the backend for locating disposal points, so there is no API
  key to manage and no cost at scale.
- The impact log uses `localStorage`, keeping the app fully client-side.

## What I'd do next

- Replace the keyword mapping with a classifier trained on TrashNet plus ~200
  locally photographed items (polythene, banana leaf, battery, packet), exported
  to TFLite so it runs offline on any phone.
- Replace the per-category average weights with item-specific weights, and add a
  ward-level leaderboard so the city can see which wards divert the most.
- Integrate the Guwahati Municipal Corporation collection schedule so the app
  reminds you which van comes to your ward on which day.

## The specific waste problem, and how I'd measure success

**Problem.** Guwahati's waste is mixed at the source. Residents cannot tell a dry
recyclable from a residual one, so recyclables are buried and wet waste is
contaminated by plastic — which is exactly the fraction that could have been
sold to a scrap dealer or composted.

**Measurement.** The app logs every scan with a per-category average weight
(dry 0.05 kg, wet 0.3 kg, hazardous 0.4 kg, landfill 0.2 kg). Success is measured
three ways:

1. **Diversion estimate** — total kilograms logged into dry/wet/hazardous streams
   rather than landfill.
2. **Classification accuracy** — top-1 accuracy against a hand-labelled test set
   of 15–20 real household items, targeting 85%+.
3. **Behaviour** — share of scans that resolve to a non-landfill stream, which is
   the direct signal that the guidance changed a disposal decision.

The first number is already measurable in the shipped app from the local log.
