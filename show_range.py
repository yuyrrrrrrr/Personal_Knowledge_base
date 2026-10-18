import re
import sys
from pathlib import Path

path = Path(r"D:\Git\LLM\deepdive_transcript.txt")
start, end = sys.argv[1], sys.argv[2]
def sec(t):
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)
a, b = sec(start), sec(end)
for line in path.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\[(\d\d:\d\d:\d\d\.\d+)\]", line)
    if m and a <= sec(m.group(1)) < b:
        print(line)
