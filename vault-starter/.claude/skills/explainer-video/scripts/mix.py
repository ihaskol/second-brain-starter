"""Mix narration and background music (explainer-video skill).
- Voice: high-pass 80 Hz (rumble), gentle +2 dB presence around 3 kHz (intelligibility band 1–4 kHz).
- Music: a licensed (ideally CC0) track, low-passed at 6 kHz, -5 dB dip around 2.5 kHz so it stays out of the speech band,
  looped with crossfades if the video is longer than the track.
- Level: while the narrator speaks, music RMS sits >= 20 dB below speech RMS (WCAG 1.4.7 benchmark); in pauses longer
  than 1.2 s it rises by 5 dB with 0.6 s ramps. Final loudness normalised to -16 LUFS (online video).
Usage: python mix.py voice.wav music.wav out.m4a [total_seconds]
Music: use a track whose licence you have checked (CC0 recommended) and record its source next to the project."""
import subprocess, sys, tempfile, numpy as np, soundfile as sf
from pathlib import Path
HERE = Path(__file__).resolve().parent; SR = 48000
voice_in, music_in, out = sys.argv[1], sys.argv[2], sys.argv[3]
tmp = Path(tempfile.mkdtemp())
def ff(*a): subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *a], check=True)
ff("-i", voice_in, "-af", "highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=2,aresample=48000", "-ac", "1", str(tmp / "v.wav"))
ff("-i", music_in, "-af", "lowpass=f=6000,equalizer=f=2500:t=q:w=1.0:g=-5,aresample=48000", "-ac", "2", str(tmp / "m.wav"))
v, _ = sf.read(tmp / "v.wav"); m, _ = sf.read(tmp / "m.wav")
n = len(v) if len(sys.argv) < 5 else int(float(sys.argv[4]) * SR); v = np.pad(v, (0, max(0, n - len(v))))[:n]
# loop music with 4 s crossfades
xf = 4 * SR; music = m.copy()
while len(music) < n:
    r = np.linspace(0, 1, xf)[:, None]; music = np.concatenate([music[:-xf], music[-xf:] * (1 - r) + m[:xf] * r, m[xf:]])
music = music[:n]
# speech activity (20 ms frames)
fr = int(0.02 * SR); env = np.sqrt(np.convolve(v ** 2, np.ones(fr) / fr, mode="same"))
active = env > 0.01
# pauses longer than 1.2 s are "open"
gain_db = np.zeros(n); i = 0
idx = np.flatnonzero(active)
speech_rms = np.sqrt(np.mean(v[active] ** 2)); music_rms = np.sqrt(np.mean(music ** 2))
base_db = 20 * np.log10(speech_rms / music_rms) - 26          # 26 dB under speech while talking (20 dB is the WCAG 1.4.7 minimum; 26 sounded calmer in testing)
open_mask = np.zeros(n, bool); prev = 0
for a, b in zip(np.r_[0, idx[np.flatnonzero(np.diff(idx) > 1) + 1]], np.r_[idx[np.flatnonzero(np.diff(idx) > 1)], idx[-1]]):
    if a - prev > 1.2 * SR: open_mask[prev + int(0.3 * SR):a - int(0.3 * SR)] = True
    prev = b
if n - prev > 1.2 * SR: open_mask[prev + int(0.3 * SR):] = True
target = base_db + 5 * open_mask
k = int(0.6 * SR); smooth = np.convolve(target, np.ones(k) / k, mode="same")
g = 10 ** (smooth / 20)
mix = np.stack([v, v], 1) + music * g[:, None]
fade = int(1.5 * SR); mix[:fade] *= np.linspace(0, 1, fade)[:, None]; mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
sf.write(tmp / "mix.wav", mix.astype(np.float32), SR)
ff("-i", str(tmp / "mix.wav"), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", out)
# report the speech-to-music gap actually achieved while talking
gap = 20 * np.log10(np.sqrt(np.mean(v[active] ** 2)) / np.sqrt(np.mean((music * g[:, None])[active] ** 2)))
print(f"speech-to-music gap while talking: {gap:.1f} dB; open (music-up) share: {open_mask.mean():.0%}")
