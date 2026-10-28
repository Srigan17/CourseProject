import typst
import pypdf
import os

with open("scripts/manuscript_template_calib.typ", "r", encoding="utf-8") as f:
    template = f.read()

# Test different parameter combinations
for fsz in ["9.3pt", "9.4pt", "9.5pt", "9.6pt", "9.7pt"]:
    for ld in ["0.48em", "0.49em", "0.50em", "0.51em"]:
        doc = template.replace("FONT_SIZE_PLACEHOLDER", fsz).replace("LEADING_PLACEHOLDER", ld)
        with open("test_calib.typ", "w", encoding="utf-8") as out:
            out.write(doc)
        try:
            typst.compile("test_calib.typ", output="test_calib.pdf")
            reader = pypdf.PdfReader("test_calib.pdf")
            pages = len(reader.pages)
            if pages == 8:
                p8_len = len(reader.pages[7].extract_text())
                print(f"MATCH: font_size={fsz}, leading={ld} -> EXACTLY 8 PAGES! (Page 8 text chars: {p8_len})")
            else:
                print(f"font_size={fsz}, leading={ld} -> {pages} pages")
        except Exception as e:
            print(f"Compile error with {fsz}, {ld}:", e)
            break
