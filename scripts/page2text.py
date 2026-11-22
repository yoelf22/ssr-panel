#!/usr/bin/env python3
"""Fetch a web page (or read a local .html) and write its visible text, from the
first <h1> to the <footer>, one block per line. Usage: page2text.py <url|file> <out.txt>"""
import sys, re, html, urllib.request
src, out = sys.argv[1], sys.argv[2]
if src.startswith("http"):
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0 (ssr-panel)"})
    s = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
else:
    s = open(src, encoding="utf-8").read()
s = re.sub(r"(?is)<head.*?</head>", "", s)
start = s.find("<h1")
s = s[start if start >= 0 else 0:]
end = s.rfind("<footer")
s = s[:end] if end > 0 else s
s = re.sub(r"(?s)<(script|style|svg|noscript|template)[^>]*>.*?</\1>", "", s)
s = re.sub(r"(?i)<br\s*/?>", "\n", s)
s = re.sub(r"(?i)</(p|h\d|li|div|a|span|td|th|dt|dd)>", "\n", s)
lines = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "", s)).split("\n")]
text = "\n".join(l for l in lines if l)
open(out, "w").write(text)
print(f"{out}: {len(text.split())} words, starts: {text[:80]!r}")
