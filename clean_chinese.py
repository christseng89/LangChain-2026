import re
import sys


def is_keep(ch):
    cp = ord(ch)
    # CJK Unified Ideographs and extensions
    if 0x4E00 <= cp <= 0x9FFF:
        return True
    if 0x3400 <= cp <= 0x4DBF:
        return True
    if 0xF900 <= cp <= 0xFAFF:
        return True
    # CJK Symbols and Punctuation (。、…「」【】《》〈〉 etc.)
    if 0x3000 <= cp <= 0x303F:
        return True
    # Fullwidth forms (，！？；：""''（）etc.)
    if 0xFF00 <= cp <= 0xFFEF:
        return True
    # Common punctuation used in Chinese text
    if ch in '，。！？；：""（）【】《》〈〉、…—～·—…':
        return True
    # Newline and space
    if ch in "\n ":
        return True
    return False


src = sys.argv[1]
with open(src, encoding="utf-8") as f:
    text = f.read()

cleaned = "".join(ch for ch in text if is_keep(ch))

# Collapse 3+ consecutive newlines to 2
cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
# Strip trailing spaces on each line
cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())

with open(src, "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Done.")
