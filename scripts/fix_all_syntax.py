import re
import typst
import pypdf

with open('scripts/manuscript_template.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Escape literal asterisks in superscripts and footnotes:
# #super[*] -> #super[\*]
text = text.replace('#super[*]', '#super[\\*]')
text = text.replace('#footnote[#super[*]Corresponding', '#footnote[#super[\\*]Corresponding')

# 2. Escape emails:
# e.g. @vitstudent.ac.in -> \@vitstudent.ac.in
# @vit.ac.in -> \@vit.ac.in
text = text.replace('@vitstudent.ac.in', '\\@vitstudent.ac.in')
text = text.replace('@vit.ac.in', '\\@vit.ac.in')

# 3. Replace ($...$) with $(...)$
text = re.sub(r'\(\$([^$]+)\$\)', r'$(\1)$', text)

# 4. Clean up any LaTeXisms
text = text.replace(r'\epsilon', 'epsilon')
text = text.replace(r'\delta', 'delta')
text = text.replace(r'\sigma', 'sigma')
text = text.replace(r'\Delta', 'Delta')
text = text.replace(r'\pm', 'plus.minus')
text = text.replace(r'\{', '{')
text = text.replace(r'\}', '}')
text = text.replace(r'\times', 'times')
text = text.replace(r'\quad', 'quad')
text = text.replace(r'\le', '<=')
text = text.replace(r'\ge', '>=')
text = text.replace(r'\text{PRV}', '"PRV"')
text = text.replace(r'\text{Acc}', '"Acc"')
text = text.replace(r'\text{pp}', '"pp"')
text = text.replace(r'\text{mean}', '"mean"')
text = text.replace(r'\text{sample}', '"sample"')
text = text.replace(r'\text{pop}', '"pop"')
text = text.replace(r'\text{ pp}', '" pp"')
text = text.replace(r'\%', '%')

# 5. Fix equation labels or citations:
# In text: @akhmetov2025auto is a citation, which is valid because references.bib has it.

with open('journal_paper.typ', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved fixed journal_paper.typ. Now attempting compilation...")
try:
    typst.compile('journal_paper.typ', output='journal_paper.pdf')
    reader = pypdf.PdfReader('journal_paper.pdf')
    print(f"SUCCESSFULLY COMPILED! Total pages: {len(reader.pages)}")
except Exception as e:
    print("Compilation failed with error:", e)
