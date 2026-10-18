import re
from pathlib import Path

src = Path(r"D:\Git\LLM\deepdive_7xTGNNLPyMI.en-orig.srt")
dst = Path(r"D:\Git\LLM\deepdive_transcript.txt")
raw = src.read_text(encoding="utf-8-sig")
out = []
for block in re.split(r"\n\s*\n", raw.strip()):
    lines = [x.strip() for x in block.splitlines() if x.strip()]
    idx = next((i for i, x in enumerate(lines) if "-->" in x), None)
    if idx is None:
        continue
    ts = lines[idx].split("-->")[0].strip().replace(",", ".")
    text = " ".join(lines[idx + 1:])
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        out.append(f"[{ts}] {text}")
dst.write_text("\n".join(out), encoding="utf-8")
print(dst, len(out), dst.stat().st_size)
