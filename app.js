/* WasteLens Guwahati — client-side waste classification.
 * Model: MobileNet (TensorFlow.js), runs fully on-device.
 * No images leave the phone. No account. No server.
 */
(function () {
  "use strict";

  var CATEGORY = {
    dry: {
      label: "Dry recyclable",
      badge: "dry",
      guidance: "Keep it clean and dry. Sell to a scrap dealer (kabadiwala) or put it in the dry-waste bin. Do not mix with food waste.",
      overpass: "recycling"
    },
    wet: {
      label: "Wet / compostable",
      badge: "wet",
      guidance: "Compost it at home or hand it to the wet-waste collector. Banana leaves and food scraps belong here — never in plastic bags.",
      overpass: "compost"
    },
    haz: {
      label: "Hazardous / e-waste",
      badge: "haz",
      guidance: "Do NOT bin this. Take it to an e-waste or battery collection point. Batteries and electronics leak toxins into soil and the Brahmaputra.",
      overpass: "waste_disposal"
    },
    land: {
      label: "Landfill (residual)",
      badge: "land",
      guidance: "Only if it is truly non-recyclable and non-compostable. Residual waste goes to the dump — try to avoid it.",
      overpass: "landfill"
    }
  };

  // MobileNet class keywords -> Guwahati disposal stream.
  var RULES = [
    { c: "hz", keys: ["battery", "batteries", "cellphone", "mobile phone", "smartphone", "laptop", "computer", "keyboard", "mouse", "remote", "cable", "charger", "circuit", "tv", "television", "monitor", "lamp", "light bulb", "bulb", "thermometer", "paint", "aerosol", "pesticide", "medicine", "pill", "syringe", "needle", "mercury", "printer", "cartridge", "toner", "camera", "radio", "speaker", "headphone", "console", "keyboard"] },
    { c: "dry", keys: ["bottle", "bottles", "can", "cans", "tin", "aluminum", "aluminium", "glass", "jar", "plastic", "paper", "cardboard", "carton", "newspaper", "magazine", "book", "notebook", "envelope", "bag", "packet", "packet", "wrapper", "foil", "tray", "cup", "container", "box", "steel", "metal", "wire", "coin", "cloth", "clothes", "shirt", "trousers", "shoe", "shoes", "toy", "pen", "pencil", "hanger", "comb", "toothbrush", "mirror", "ceramic", "pot", "pan", "utensil", "spoon", "fork", "knife", "straw", "lid", "cap", "tube", "bucket", "mug", "vase", "candle"] },
    { c: "wet", keys: ["banana", "leaf", "leaves", "apple", "orange", "mango", "fruit", "vegetable", "potato", "onion", "tomato", "food", "rice", "bread", "roti", "chapati", "fish", "meat", "chicken", "egg", "shell", "tea", "coffee", "leaf", "plant", "flower", "grass", "wood", "stick", "nut", "coconut", "rice", "grain", "bone", "corn", "peel", "scraps", "leftover", "cooked", "raw"] },
    { c: "land", keys: ["diaper", "sanitary", "napkin", "tissue", "towel", "cigarette", "ash", "dust", "sweepings", "ceramic", "mirror", "pyrex", "styrofoam", "thermocol", "multi-layer", "chip packet", "chocolate wrapper", "biscuit packet", "toffee", "polythene", "plastic bag", "carry bag", "glove", "mask", "sponge", "brush", "toothpaste tube", "razor", "ink", "glue", "tape", "rubber", "tyre", "tube"] }
  ];

  var CONF_FLOOR = 0.04;

  var model = null;
  var modelLoading = null;
  var stream = null;

  var el = {
    video: document.getElementById("view"),
    canvas: document.getElementById("frame"),
    start: document.getElementById("start"),
    snap: document.getElementById("snap"),
    file: document.getElementById("file"),
    status: document.getElementById("status"),
    result: document.getElementById("result"),
    badge: document.getElementById("badge"),
    label: document.getElementById("label"),
    confidence: document.getElementById("confidence"),
    guidance: document.getElementById("guidance"),
    mapLink: document.getElementById("map-link"),
    save: document.getElementById("save"),
    clear: document.getElementById("clear"),
    impactLine: document.getElementById("impact-line")
  };

  function setStatus(msg) { el.status.textContent = msg; }

  function loadModel() {
    if (model) return Promise.resolve(model);
    if (modelLoading) return modelLoading;
    modelLoading = mobilenet.load({ version: 2, alpha: 1.0 })
      .then(function (m) { model = m; setStatus("Model ready. Point at an item and tap Classify."); return m; })
      .catch(function (e) { setStatus("Could not load the model: " + e.message); throw e; });
    return modelLoading;
  }

  function classifyImage(img) {
    return loadModel().then(function (m) { return m.classify(img, 5); });
  }

  function pickCategory(predictions) {
    var best = { c: "land", score: 0, matched: "" };
    var seen = {};
    predictions.forEach(function (p) {
      var name = (p.className || "").toLowerCase();
      for (var i = 0; i < RULES.length; i++) {
        var rule = RULES[i];
        for (var j = 0; j < rule.keys.length; j++) {
          var k = rule.keys[j];
          if (name.indexOf(k) !== -1) {
            var score = p.probability * (1 + (rule.keys.length - j) / 100);
            if (!seen[rule.c]) { seen[rule.c] = score; }
            else { seen[rule.c] = Math.max(seen[rule.c], score); }
            if (seen[rule.c] > best.score) { best = { c: rule.c, score: seen[rule.c], matched: k }; }
            return;
          }
        }
      }
    });
    return best;
  }

  function showResult(predictions) {
    var pick = pickCategory(predictions);
    var cat = CATEGORY[pick.c];
    var top = predictions[0];
    var conf = Math.round((top ? top.probability : 0) * 100);

    el.badge.textContent = cat.label;
    el.badge.className = "badge " + cat.badge;
    el.label.textContent = "Looks like " + (top ? top.className.split(",")[0] : "unknown");
    el.confidence.textContent = "Model confidence " + conf + "% · rule match: " + (pick.matched || "none");
    el.guidance.textContent = cat.guidance;
    el.mapLink.href = overpassUrl(cat.overpass);
    el.result.hidden = false;
    el.result.scrollIntoView({ behavior: "smooth", block: "nearest" });
    renderImpact();
  }

  function overpassUrl(kind) {
    var q = "";
    if (kind === "recycling") q = 'node["amenity"="recycling"](26.1445,91.7362,26.25,91.85);';
    else if (kind === "waste_disposal") q = 'node["amenity"="waste_disposal"](26.1445,91.7362,26.25,91.85);';
    else q = 'node["landuse"="landfill"](26.1445,91.7362,26.25,91.85);';
    return "https://www.openstreetmap.org/search?query=scrap%20dealer%20Guwahati";
  }

  function grabFrame() {
    var v = el.video;
    if (v && v.videoWidth) {
      el.canvas.width = v.videoWidth;
      el.canvas.height = v.videoHeight;
      var ctx = el.canvas.getContext("2d");
      ctx.drawImage(v, 0, 0, v.videoWidth, v.videoHeight);
      return el.canvas;
    }
    return null;
  }

  function renderImpact() {
    var log = JSON.parse(localStorage.getItem("wastelens.log") || "[]");
    if (!log.length) { el.impactLine.textContent = "No scans logged yet."; return; }
    var counts = {};
    var kg = 0;
    log.forEach(function (r) { counts[r.cat] = (counts[r.cat] || 0) + 1; kg += r.kg; });
    var parts = Object.keys(counts).map(function (k) { return counts[k] + " " + CATEGORY[k].label.toLowerCase(); });
    el.impactLine.textContent = log.length + " scans · " + parts.join(", ") + " · ~" + kg.toFixed(1) + " kg diverted.";
  }

  function logScan(cat) {
    var weights = { dry: 0.05, wet: 0.3, haz: 0.4, land: 0.2 };
    var log = JSON.parse(localStorage.getItem("wastelens.log") || "[]");
    log.push({ cat: cat, at: new Date().toISOString(), kg: weights[cat] || 0.1 });
    localStorage.setItem("wastelens.log", JSON.stringify(log));
  }

  // ---- wiring
  el.start.addEventListener("click", function () {
    if (stream) return;
    setStatus("Starting camera…");
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false })
      .then(function (s) { stream = s; el.video.srcObject = s; el.snap.disabled = false; })
      .catch(function (e) { setStatus("Camera unavailable (" + e.name + "). Use Upload a photo instead."); });
  });

  el.snap.addEventListener("click", function () {
    var frame = grabFrame();
    if (!frame) { setStatus("No camera frame yet."); return; }
    setStatus("Classifying…");
    classifyImage(frame).then(showResult).catch(function (e) { setStatus("Classification failed: " + e.message); });
  });

  el.file.addEventListener("change", function () {
    var f = el.file.files && el.file.files[0];
    if (!f) return;
    var img = new Image();
    img.onload = function () { setStatus("Classifying…"); classifyImage(img).then(showResult).catch(function (e) { setStatus("Classification failed: " + e.message); }); };
    img.onerror = function () { setStatus("Could not read that image."); };
    img.src = URL.createObjectURL(f);
  });

  el.save.addEventListener("click", function () {
    var cat = el.badge.className.replace("badge ", "");
    if (!CATEGORY[cat]) return;
    logScan(cat);
    el.save.textContent = "Logged ✓";
    setTimeout(function () { el.save.textContent = "Log this scan"; }, 1500);
  });

  el.clear.addEventListener("click", function () {
    localStorage.removeItem("wastelens.log");
    renderImpact();
  });

  renderImpact();
})();
