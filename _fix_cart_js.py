from pathlib import Path
text = Path("index.html").read_text(encoding="utf-8", errors="replace")

start = text.find("/* Bag — local boutique cart */")
if start < 0:
    raise SystemExit("cart js missing")

# Find where it was wrongly inserted (between scripts)
# Prefer wrapping: find from start back to see context
print("context before:")
print(repr(text[start-80:start]))
print("---")
# find end of cart IIFE
end = text.find("window.tulayCart={add,open,close,render};\n  render();\n})();", start)
if end < 0:
    end = text.find("window.tulayCart={add,open,close,render};", start)
    end = text.find("})();", end) + 5
else:
    end = end + len("window.tulayCart={add,open,close,render};\n  render();\n})();")

print("end context:")
print(repr(text[end:end+80]))

cart_block = text[start:end]
# Remove wrongly placed block
text2 = text[:start] + text[end:]

# Insert properly before the main script's closing tag that precedes Lenis
marker = "</script>\n<script>\n/* Lenis 1.3.11"
# After removal, marker should still exist once
if marker not in text2:
    marker = "</script>\r\n<script>\r\n/* Lenis 1.3.11"
if marker not in text2:
    # find any Lenis marker
    li = text2.find("/* Lenis 1.3.11")
    print("lenis at", li, "prev", repr(text2[li-40:li]))
    raise SystemExit("marker missing after removal")

wrapped = "\n<script>\n" + cart_block + "\n</script>\n"
# Avoid duplicate if already wrapped somehow
if "window.tulayCart" in text2:
    raise SystemExit("unexpected remaining cart")

text2 = text2.replace(marker, wrapped + marker, 1)
tmp = Path("_index.fixed.html")
tmp.write_text(text2, encoding="utf-8", newline="\n")
tmp.replace(Path("index.html"))
print("fixed: cart inside script tag")
# verify
t = Path("index.html").read_text(encoding="utf-8", errors="replace")
i = t.find("/* Bag — local boutique cart */")
print("wrapped ok?", "<script>" in t[i-30:i])
print("before lenis?", "Lenis" in t[i:i+5000])
