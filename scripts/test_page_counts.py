import typst
import pypdf

with open("test_calib.typ", "r", encoding="utf-8") as f:
    base_text = f.read()

# Let's test combinations of font size and leading to see page counts
results = []
for fsz in ["9.2pt", "9.3pt", "9.4pt", "9.5pt", "9.6pt", "9.7pt", "9.8pt"]:
    for ld in ["0.48em", "0.50em", "0.52em", "0.54em"]:
        # replace in base_text:
        # size: ...
        # leading: ...
        import re
        txt = re.sub(r'size:\s*[0-9\.]+pt', f'size: {fsz}', base_text)
        txt = re.sub(r'leading:\s*[0-9\.]+em', f'leading: {ld}', txt)
        try:
            typst.compile(txt.encode('utf-8'), output='t_out.pdf')
            r = pypdf.PdfReader('t_out.pdf')
            p = len(r.pages)
            p_last_chars = len(r.pages[-1].extract_text().strip())
            results.append((p, fsz, ld, p_last_chars))
            print(f"fsz={fsz:6s} ld={ld:6s} -> {p} pages (last page chars: {p_last_chars})")
        except Exception as e:
            print(f"fsz={fsz} ld={ld} error: {e}")

# Filter for exactly 8 pages
exact_8 = [r for r in results if r[0] == 8]
print(f"\nFound {len(exact_8)} combinations that produce EXACTLY 8 PAGES:")
for e in exact_8:
    print(f"  font_size={e[1]}, leading={e[2]} -> 8 pages, last page length={e[3]} chars")
