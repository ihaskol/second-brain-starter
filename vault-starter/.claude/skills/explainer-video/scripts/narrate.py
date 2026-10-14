"""Narrate a script with Kokoro (local, offline) and write the timing every engine reads.

    python narrate.py script.json out_dir --kokoro <dir with kokoro-v1.0.onnx + voices-v1.0.bin>

script.json:
{ "voice": "af_heart", "speed": 1.05,
  "say": {"0.98": "zero point nine eight"},          # spoken-only replacements (captions keep the original)
  "preset": "whiteboard" | "crayon",                  # pacing defaults (below); any key can be overridden
  "scenes": [ {"title": "1. Hook", "label": "MONDAY", "lines": ["First sentence.", "Second sentence."]}, ... ] }

Writes out_dir/voice.wav (24 kHz mono), out_dir/timing.json and out_dir/captions.vtt.
timing.json = {"total": s, "scenes": [{"title","label","start","end","seg":[{"t","d","text"}]}]}
Needs: pip install kokoro-onnx soundfile numpy espeakng-loader (Python 3.11 venv recommended)."""
import argparse, json, shutil
from pathlib import Path
import numpy as np, soundfile as sf, espeakng_loader
from kokoro_onnx import Kokoro, EspeakConfig
PRESETS = {"whiteboard": {"lead": 0.8, "gap": 0.45, "scene_gap": 0.9, "min_scene": 0.0, "tail": 1.5},
           "crayon": {"lead": 0.5, "gap": 0.45, "scene_gap": 1.3, "min_scene": 4.2, "tail": 1.0}}
ap = argparse.ArgumentParser(); ap.add_argument("script"); ap.add_argument("out"); ap.add_argument("--kokoro", required=True)
a = ap.parse_args(); S = json.loads(Path(a.script).read_text()); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
P = dict(PRESETS[S.get("preset", "whiteboard")], **{k: S[k] for k in ("lead", "gap", "scene_gap", "min_scene", "tail") if k in S})
esd = Path("/tmp/esd/espeak-ng-data")            # espeak-ng needs a path without spaces
if not esd.exists(): shutil.copytree(espeakng_loader.get_data_path(), esd)
K = Path(a.kokoro)
kok = Kokoro(str(K / "kokoro-v1.0.onnx"), str(K / "voices-v1.0.bin"), espeak_config=EspeakConfig(data_path=str(esd), lib_path=espeakng_loader.get_library_path()))
def spoken(s):
    for x, y in S.get("say", {}).items(): s = s.replace(x, y)
    return s
SR = 24000; parts = []; t = P["lead"]; scenes = []
for sc in S["scenes"]:
    start = max(0.0, t - 0.3); seg = []
    for line in sc["lines"]:
        au = kok.create(spoken(line), voice=S.get("voice", "af_heart"), speed=S.get("speed", 1.05), lang="en-us")[0].astype(np.float32)
        d = len(au) / SR; seg.append({"t": round(t, 3), "d": round(d, 3), "text": line}); parts.append((t, au)); t += d + P["gap"]
    t = max(t - P["gap"] + P["scene_gap"], start + P["min_scene"])
    scenes.append({"title": sc.get("title", ""), "label": sc.get("label", ""), "start": round(start, 3), "end": round(t - 0.2, 3), "seg": seg})
total = round(t + P["tail"], 3)
v = np.zeros(int(total * SR) + SR, np.float32)
for s, au in parts: i = int(s * SR); v[i:i + len(au)] += au
sf.write(out / "voice.wav", v, SR)
(out / "timing.json").write_text(json.dumps({"total": total, "scenes": scenes}, indent=1))
f = lambda x: "%02d:%02d.%03d" % (int(x) // 60, int(x) % 60, int(round((x % 1) * 1000)) % 1000)
vtt = ["WEBVTT", ""]; n = 0
for sc in scenes:
    for g in sc["seg"]: n += 1; vtt += [str(n), "%s --> %s" % (f(g["t"]), f(g["t"] + g["d"] + 0.3)), g["text"], ""]
(out / "captions.vtt").write_text("\n".join(vtt))
print(len(scenes), "scenes;", total, "s")
