import typst
import pypdf

with open("scripts/manuscript_template_calib.typ", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("FONT_SIZE_PLACEHOLDER", "9.4pt").replace("LEADING_PLACEHOLDER", "0.50em")
with open("test_fixed.typ", "w", encoding="utf-8") as f:
    f.write(text)

try:
    typst.compile("test_fixed.typ", output="test_fixed.pdf")
    r = pypdf.PdfReader("test_fixed.pdf")
    print(f"SUCCESS! Total pages: {len(r.pages)}")
    for i, p in enumerate(r.pages):
        print(f"Page {i+1} length: {len(p.extract_text().strip())}")
except Exception as e:
    print("Failed:", e)
